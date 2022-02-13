import ctypes
import pathlib
import numpy as np
from numpy import linalg
import numpy.matlib
from scipy.io import savemat
import scipy.spatial as spatial
import os
import sys
import multiprocessing as mp

from src.holo.HoloIO import HoloIO

sys.path.append(os.path.dirname(__file__))
import renderDepth



class UtilsMath:

    def q2r(self, q):
        q = q / linalg.norm(np.matrix(q))
        return np.matrix([
            [
                q[0] ** 2 + q[1] ** 2 - q[2] ** 2 - q[3] ** 2,
                2 * (q[1] * q[2] - q[0] * q[3]),
                2 * (q[1] * q[3] + q[0] * q[2])
            ],
            [
                2 * (q[1] * q[2] + q[0] * q[3]),
                q[0] ** 2 - q[1] ** 2 + q[2] ** 2 - q[3] ** 2,
                2 * (q[2] * q[3] - q[0] * q[1])
            ],
            [
                2 * (q[1] * q[3] - q[0] * q[2]),
                2 * (q[2] * q[3] + q[0] * q[1]),
                q[0] ** 2 - q[1] ** 2 - q[2] ** 2 + q[3] ** 2
            ]
        ])


    def a2h(self, pts):
        """Affine to homogeneous coordinates, (3, N) -> (4, N) shape."""
        return np.vstack((pts, np.ones((1, pts.shape[1]))))

    def h2a(self, pts):
        """Homogeneous to affine coordinates, (4, N) -> (3, N) shape."""
        return (pts / pts[3,:])[:3,:]


    def clip_view_frustrum(self, xyz, rgb, affine_transform):
        """Clip points and colors to view frustrum (without znear and zfar clipping)."""
        pairs = np.array([[0, 1, 2, 3], [1, 2, 3, 0]])
        pts_cam = np.array([[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]]).T
        pts_world = self.h2a(affine_transform @ self.a2h(pts_cam))
        R = affine_transform[:3, :3].T
        t = affine_transform[:3, -1:]

        Ndpts = xyz.shape[1]
        vpts = xyz - t
        D = np.ones((1, Ndpts), dtype=np.bool)
        for j in range(1, 4):
            v2 = pts_world[:, pairs[0, j]] - t
            v1 = pts_world[:, pairs[1, j]] - t
            D = D & (((v2[0] * v1[1]) * vpts[2, :] - (v2[2] * v1[1]) * vpts[0, :] +
                    (v2[2] * v1[0]) * vpts[1, :] - (v2[0] * v1[2]) * vpts[1, :] +
                    (v2[1] * v1[2]) * vpts[0, :] - (v2[1] * v1[0]) * vpts[2, :]) > 0)
        return xyz[:, D], rgb[:, D]


    def r2q(self, R):
        c = np.trace(R) + 1
        if np.abs(c) < 10^-10:
            S = R + np.eye(3)
            nS = np.linalg.norm(S, axis=0)
            col_id = np.argmax(nS)
            q = np.append([0], S[::,col_id] / nS[col_id])
        else:
            r = np.sqrt(c)/2
            q = np.matrix([[r],
                [(R[2,1]-R[1,2])/r],
                [(R[0,2]-R[2,0])/r],
                [(R[1,0]-R[0,1])/r]])
            q = q / np.linalg.norm(q, 2)
        return q

    def extract_camera_name(self, cameara_path):
        return cameara_path.replace("pv/","").replace(".jpg","")

    def compose_coresponding_camera_centers(self, colmap_cameras, holo_cameras):
        colmap_C = np.array([]).reshape(3,0)
        holo_C = np.array([]).reshape(3,0)

        for i in range(0,len(colmap_cameras)):
            colmap_camera = colmap_cameras[i]
            holo_camera = holo_cameras[self.extract_camera_name(colmap_camera["name"])]
            colmap_C = np.concatenate((colmap_C, colmap_camera["C"]), axis=1)
            holo_C = np.concatenate((holo_C, holo_camera["C"]), axis=1)
        
        return (colmap_C, holo_C)


    def estimate_colmap_to_holo_transformation(self, colmap_cameras, holo_cameras):
        print('Estimate COLMAP to HoloLens transformation.')
        colmap_C, holo_C = self.compose_coresponding_camera_centers(colmap_cameras, holo_cameras)

        # scale input points
        mc = np.mean(colmap_C, axis=1)
        mh = np.mean(holo_C, axis=1)
        c0 = colmap_C - mc
        h0 = holo_C - mh
        normc = np.sqrt(np.sum(np.multiply(c0,c0)))
        normh = np.sqrt(np.sum(np.multiply(h0,h0)))
        c0 = c0 * (1/normc)
        h0 = h0 * (1/normh)

        # find transform. minimize LSQ
        A = h0 * c0.T
        U, S, V = linalg.svd(A)     # numpy uses: A = U * np.diag(S) * V
        R = U * V
        if linalg.det(R) < 0:
            V[2,::] = -V[2,::]
            S[2] = -S[2]
            R = U * V
        s = np.sum(S) * normh / normc
        t = mh - s*R*mc

        return {"scale": s, "rotation": R, "translation": t}


    def transform_colmap_points(self, colmap_points, transform):
        for i in range(0,len(colmap_points)):
            colmap_points[i]["X"] =  (transform["scale"] * transform["rotation"] * np.matrix(colmap_points[i]["X"]).T + transform["translation"]).T.tolist()[0]

        return colmap_points

    def transform_colmap_images(self, colmap_cameras, transform):
        for i in range(0,len(colmap_cameras)):
            colmap_cameras[i]["R"] = colmap_cameras[i]["R"] * transform["rotation"].T
            colmap_cameras[i]["C"] =  transform["scale"] * transform["rotation"] * colmap_cameras[i]["C"] + transform["translation"]

        return colmap_cameras 


    def filter_dense_pointcloud_noise_KDtree(self, xyz, radius, npts, rgb = None):
        print('Filter noise in dense pointcloud using KDtree.')
        xyzT = xyz.T
        point_tree = spatial.cKDTree(xyzT)
        num_neighbours = point_tree.query_ball_point(xyzT, radius, workers = -1, return_length = True)
        filter = [num_neighbours[i] > npts for i in range(np.shape(xyz)[1])]
        xyz = xyz[::,filter]
        if rgb != None and rgb.any():
            rgb = rgb[::,filter]
        return (xyz, rgb)


    def estimate_visibility_for_image(self, data):
        img_id = data["image_id"]
        print(f'Estimate visibility for image: {img_id}')
        K  = data["K"]
        R  = data["R"]
        C  = data["C"]
        h  = data["h"]
        w  = data["w"]
        xyz  = data["xyz"]
        t  = data["t"]
        distance_threshold = data["dt"]
        visibility_xyz = []

        # project points
        uvl = K * R * (xyz - C)
        u = uvl[0,::] / uvl[2,::]
        v = uvl[1,::] / uvl[2,::]
        uv = np.concatenate((u, v), axis=0)
        depth = np.linalg.norm(xyz - C, axis=0)

        # get data in image
        f = renderDepth.is_visible(h, w, uv) & (np.array(uvl[2,:])[0] < 0)
        depth_filtered = depth[f]
        uv_filtered = uv[:, f]
        xyz_filtered = xyz[:, f]
        xyz_ids = np.arange(np.shape(uv)[1], dtype=np.float64)

        xyz_ids_filtered = xyz_ids[f]
        
        # sort points wrt. depth
        depth_order = np.flip(np.argsort(depth_filtered))
        depth_sorted = depth_filtered[depth_order]
        uv_sorted = uv_filtered[::,depth_order]
        xyz_sorted = xyz_filtered[::,depth_order]
        xyz_ids_sorted = xyz_ids_filtered[depth_order]

        # run cpp to render visibility information
        holo_depth_img = renderDepth.render(h, w, np.shape(uv_sorted)[1], np.shape(t)[1], \
                 uv_sorted.reshape(1,-1), depth_sorted, t.reshape(1,-1)) 
        
        #  test
        # holo_depth_img2 = holo_depth_img.reshape(h,w)
        # mdic = {"holo_depth_img": holo_depth_img2, "uv": uv_sorted, "depth": depth_sorted, "t": t}
        # savemat("/local/artwin/mapping/codes/mapper/src/utils/renderDepth/matlab_matrix.mat", mdic)
        
        visibility_xyz = renderDepth.compose_visibility(int(img_id), w, np.shape(uv_sorted)[1], \
            np.floor(uv_sorted).reshape(1,-1), depth_sorted, holo_depth_img, \
            xyz_ids_sorted, distance_threshold)

        return visibility_xyz

    def render_image(self, data, max_radius=5):
        """Render image the same way as the rest of this codebase."""
        K   = data["K"]
        R   = data["R"]
        C   = data["C"]
        h   = data["h"]
        w   = data["w"]
        xyz = data["xyz"]
        rgb = data["rgb"]

        # project points
        xyz_t = xyz - C
        uvl = K * R * xyz_t.copy()
        uv = (uvl / uvl[2, :])[:2, :]
        u = uv[0, :]
        v = uv[1, :]
        depth = np.linalg.norm(xyz_t, axis=0)

        # get data in image
        filtering = np.array((u >= 0) & (v >= 0) & (u < w) & (v < h) & (uvl[2, :] < 0)).squeeze()
        depth_filtered = depth[filtering.squeeze()]
        # sort according to depth
        ordering = np.flip(np.argsort(depth_filtered))

        depth = depth_filtered[ordering.squeeze()]
        uv = uv[:, filtering][:, ordering]
        rgb = rgb[:, filtering][:, ordering]

        # trivial linear interpolation
        k = (max_radius - 1) / (max(depth) - min(depth))
        q = 1 - k * min(depth)
        radii = np.round((k * depth + q + 1) / 2).astype(np.uint16)

        # run cpp to render visibility information
        img = renderDepth.render_image(h, w, uv, radii, rgb)

        return img

    def render_colmap_image(self, data, max_radius=5):
        """Render image so that it agrees with artwin reference images."""
        K   = data["K"]
        R   = data["R"]
        C   = data["C"]
        h   = data["h"]
        w   = data["w"]
        xyz = data["xyz"]
        rgb = data["rgb"]

        # project points
        camera2world = np.eye(4)
        camera2world[:3, :3] = R.T
        camera2world[:3, -1:] = C
        camera2world[:, 1:3] *= -1

        xyz_camera_homogeneous = np.linalg.inv(camera2world) @ self.a2h(xyz)
        xyz_camera = self.h2a(xyz_camera_homogeneous)
        depth = np.linalg.norm(xyz_camera, axis=0)

        # focal_length = (float(K[0, 0]) + float(K[1, 1])) / 2
        # df = depth > focal_length
        # print(max(depth))
        # print(min(depth))
        # depth = depth[df]
        # xyz_camera = xyz_camera[:, df]

        uv_homogeneous = K @ xyz_camera
        uv = (uv_homogeneous / uv_homogeneous[2, :])[:2, :]
        u = uv[0, :]
        v = uv[1, :]

        # get data in image
        filtering = np.array((u >= 0) & (v >= 0) & (u < w) & (v < h) & (uv_homogeneous[2, :] < 0)).squeeze()
        depth_filtered = depth[filtering.squeeze()]
        # sort according to depth
        ordering = np.flip(np.argsort(depth_filtered))

        depth = depth_filtered[ordering.squeeze()]
        uv = uv[:, filtering][:, ordering]
        rgb = rgb[:, filtering][:, ordering]

        # Linear interpolation between points (min(depth), min_radius) and (max(depth), max_radius),
        # coefficients computation
        min_radius = 5
        k = (max_radius - min_radius) / (max(depth) - min(depth))
        q = min_radius - k * min(depth)
        # Linear interpolation itself + ensuring only odd radii are present (C++ impl requirement)
        radii = np.round((k * depth + q + 1) / 2).astype(np.uint16)

        # run cpp to render visibility information
        uv[0,:] = w - uv[0,:]  # Flip so that it agrees with reference images from artwin
        img = renderDepth.render_image(h, w, uv, radii, rgb)

        return img


    def get_calibration_matrix(self, camera):
        try:
            fx, fy = camera["f"][0], camera["f"][1]
        except TypeError:
            fx, fy = camera["f"], camera["f"]
        return np.matrix([
            [fx, 0,  camera["pp"][0]],
            [0,  fy, camera["pp"][1]],
            [0,  0,  1]])

    def hash_points(self,  xyz, xyz_hash_scale = -1.):
        new_xyz_mean = []
        new_xyz_grid = []
        ids_old_to_new_xyz = []
        if xyz_hash_scale > 0:
            xyz_hashed = np.round(xyz * xyz_hash_scale).astype(dtype=int)
            for t in range(3):
                index_array = np.argsort(xyz_hashed[2-t,::], kind='stable')
                xyz = xyz[::,index_array]
                xyz_hashed = xyz_hashed[::,index_array]

            num_pts = 1.0
            pt = xyz_hashed[::,0]
            pt_sum = xyz[::,0]
            j = 0
            ids_old_to_new_xyz.append(j)
            for i in range(1,np.shape(xyz_hashed)[1]):
                if xyz_hashed[0,i] == pt[0] and xyz_hashed[1,i] == pt[1] and xyz_hashed[2,i] == pt[2]:
                    num_pts += 1.0
                    pt_sum += xyz[::,i]
                else:
                    new_pt = pt_sum / num_pts
                    new_xyz_grid.append(float(xyz_hashed[0,i-1]) / float(xyz_hash_scale))
                    new_xyz_grid.append(float(xyz_hashed[1,i-1]) / float(xyz_hash_scale))
                    new_xyz_grid.append(float(xyz_hashed[2,i-1]) / float(xyz_hash_scale))
                    new_xyz_mean.append(new_pt[0])
                    new_xyz_mean.append(new_pt[1])
                    new_xyz_mean.append(new_pt[2])
                    
                    j += 1
                    num_pts = 1.0
                    pt = xyz_hashed[::,i]
                    pt_sum = xyz[::,i]
                ids_old_to_new_xyz.append(j)

            # add the last point
            new_pt = pt_sum / num_pts
            new_xyz_grid.append(float(xyz_hashed[0,-1]) / float(xyz_hash_scale))
            new_xyz_grid.append(float(xyz_hashed[1,-1]) / float(xyz_hash_scale))
            new_xyz_grid.append(float(xyz_hashed[2,-1]) / float(xyz_hash_scale))
            new_xyz_mean.append(new_pt[0])
            new_xyz_mean.append(new_pt[1])
            new_xyz_mean.append(new_pt[2])

            return (np.reshape(new_xyz_grid, (3,-1), order='F'), np.reshape(new_xyz_mean, (3,-1), order='F'), ids_old_to_new_xyz) 
        else:
            ids_old_to_new_xyz = np.arange(np.shape(xyz)[1], dtype=np.float64)
            return (xyz, xyz, ids_old_to_new_xyz)


    def distance_to_radius_mapping(self, focal_length, xyz_hash_scale, min_distance_to_camera = 0.01):
        if isinstance(focal_length, list):
            if len(focal_length) > 1:
                focal_length = (focal_length[0] + focal_length[1]) / 2
            else:
                focal_length = focal_length[0]
        radius_world = 1/xyz_hash_scale

        max_radius = np.round(focal_length * radius_world / (5*radius_world))
        if int(max_radius % 2) != 1:
            max_radius += 1
        max_radius = int(max_radius)

        radius_thresholds = []
        for i in range(1, max_radius+2, 2):
            d_i = focal_length * radius_world / i
            d_i2 = focal_length * radius_world / (i+2)
            radius_thresholds.append(0.5 * (d_i + d_i2))
            radius_thresholds.append(i)
        
        return np.array(radius_thresholds).reshape((2,-1),order='F')


    def estimate_visibility(self, cameras, images, xyz, xyz_hash_scale = -1, distance_threshold = 0.1, all_points = False):
        # hash points
        new_xyz_grid, new_xyz_mean, ids_old_to_new_xyz = self.hash_points(xyz, xyz_hash_scale)

        # holoio = HoloIO()
        # holoio.write_pointcloud_to_file(new_xyz_grid, "d:/tmp/hololens_mapper/pipelines/MeshroomCache/HoloLensIO/b18939407270cdb88931e57772a1383582c6a1c5/model_grid.obj" )
        # holoio.write_pointcloud_to_file(new_xyz_mean, "d:/tmp/hololens_mapper/pipelines/MeshroomCache/HoloLensIO/b18939407270cdb88931e57772a1383582c6a1c5/model_mean.obj" )

        # calculate projection scales
        t = np.array([[8.0, 5.6, 3.2, 0.8, 0],[1, 3, 5, 7, 9]])  # TODO: d1 / d * f ... px size for d, d1 is size of radius in space

        # hash cameras
        cameras_hash = {}
        for cam in cameras:
            cameras_hash[cam["camera_id"]] = cam

        visibility_xyz = []
        all_data = []
        for image in images:
            camera = cameras_hash[image["camera_id"]]
            t = self.distance_to_radius_mapping(camera['f'], xyz_hash_scale)
            all_data.append({"image_id": image["image_id"], \
                "K": self.get_calibration_matrix(camera), "R": image["R"], \
                "C": image["C"], "h": camera["height"], \
                "w": camera["width"], "xyz": new_xyz_grid, "t": t, "dt": distance_threshold})
        test = self.estimate_visibility_for_image(all_data[0])

        chunksize = mp.cpu_count()
        with mp.Pool(chunksize) as pool:
            for ind, res in enumerate(pool.imap(self.estimate_visibility_for_image, all_data), chunksize):
                for i in range(0,len(res)):
                    visibility_xyz.append(res[i])       # pt3d_id = res[4*i + 0]    img_id = res[4*i + 1]    u = res[4*i + 2]    v = res[4*i + 3]
                    
        return visibility_xyz




        
