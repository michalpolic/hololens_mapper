import ctypes
import pathlib
import numpy as np
from numpy import Inf, linalg
import numpy.matlib
from scipy.io import savemat
import scipy.spatial as spatial
import os
import sys
import multiprocessing as mp
import cv2
import matplotlib.pyplot as plt

from PIL import Image
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
            r = np.sqrt(np.abs(c))
            q = np.matrix([[r/2],
                [(R[2,1]-R[1,2])/r/2],
                [(R[0,2]-R[2,0])/r/2],
                [(R[1,0]-R[0,1])/r/2]])
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


    def estimate_colmap_to_colmap_transformation(self, reference_images, transformed_images):
        reference_C = np.array([]).reshape(3,0)
        transformed_C = np.array([]).reshape(3,0)

        reference_images_by_name = {}
        for img in reference_images.values():
            reference_images_by_name[img['name'].replace('\\','/')] = img

        for img in transformed_images.values():
            transformed_img_name = img['name'].replace('\\','/')
            if transformed_img_name in reference_images_by_name:
                ref_img = reference_images_by_name[transformed_img_name]
                reference_C = np.concatenate((reference_C, ref_img["C"]), axis=1)
                transformed_C = np.concatenate((transformed_C, img["C"]), axis=1)

        # savemat('/local1/projects/artwin/mapping/hololens_mapper/pipelines/MeshroomCache/HlocLocalizer/78e3afadb7ad4b73fff4d28b47372162efb55e9e', \
        #     {'reference_C':reference_C, 'transformed_C': transformed_C})

        return self.estimate_euclidean_transformation(reference_C, transformed_C)


    def merge_common_cameras(self, cameras1, cameras2, eps = 10^-4):
        common_cameras = {}
        cam2_to_common_ids = {}
        
        max_id = np.max(list(cameras1.keys()))
        common_cameras = cameras1
        for cam2_id in cameras2:
            cam2 = cameras2[cam2_id]
            pp1 = np.matrix(cam2['pp'])
            rd1 = np.matrix(cam2['rd'])
            unknown_camera = True
            for cam in common_cameras.values():
                pp2 = np.matrix(cam['pp'])
                rd2 = np.matrix(cam['rd'])
                if cam2['model'] == cam['model'] and cam2['width'] == cam['width'] and \
                    cam2['height'] == cam['height'] and abs(cam2['f']-cam['f']) < eps and \
                    np.linalg.norm(pp1 - pp2) < 2*eps and np.linalg.norm(rd1 - rd2) < 2*eps:
                    unknown_camera = False
                    break

            if unknown_camera:
                cam2_to_common_ids[cam2['camera_id']] = max_id+1
                cam2['camera_id'] = max_id+1
                common_cameras[max_id+1] = cam2
                max_id += 1

        return (common_cameras, cam2_to_common_ids)
                    

    def align_local_and_global_sfm(self, db_cameras, db_images, db_points3D, q_cameras, q_images, q_points3D, transform):
        cameras, qcam_to_cam_id = self.merge_common_cameras(db_cameras, q_cameras)

        images = {}
        for qimg_id in q_images:
            qimg = q_images[qimg_id]
            qimg['camera_id'] = str(qcam_to_cam_id[int(qimg['camera_id'])])
            qimg['C'] = transform['R'].T * (qimg['C'] - np.matrix(transform['t']).T)
            qimg['R'] = qimg['R'] * transform['R']
            #qimg['point3D_ids'] = [-1 for i in range(len(qimg['point3D_ids']))]
            images[qimg_id] = qimg
            
        max_id = np.max(list(images.keys()))
        for dbimg_id in db_images:
            dbimg = db_images[dbimg_id]
            if dbimg_id in images.keys():
                dbimg['image_id'] = max_id + 1
                max_id += 1
            dbimg['point3D_ids'] = [-1 for i in range(len(dbimg['point3D_ids']))]
            images[dbimg['image_id']] = dbimg

        points3D = []
        for pt3D in q_points3D:
            X = transform['R'].T * (np.matrix(pt3D['X']).reshape(3,1) - np.matrix(transform['t']).T)
            pt3D['X'] = np.matrix.tolist(X.T)[0]
            points3D.append(pt3D)

        return (cameras, images, points3D)


    def estimate_colmap_to_holo_transformation(self, colmap_cameras, holo_cameras):
        print('Estimate COLMAP to HoloLens transformation.')
        colmap_C, holo_C = self.compose_coresponding_camera_centers(colmap_cameras, holo_cameras)
        return self.estimate_euclidean_transformation(holo_C, colmap_C)


    def estimate_euclidean_transformation(self, X_ref, X_transformed):
        # scale input points
        mc = np.mean(X_transformed, axis=1)
        mh = np.mean(X_ref, axis=1)
        c0 = X_transformed - mc
        h0 = X_ref - mh
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

    def transform_pointcloud(self, xyz, transform):
        for i in range(0,np.shape(xyz)[1]):
            xyz[:,i] = np.asarray(transform["scale"] * transform["rotation"] * np.matrix(xyz[:,i]).T + transform["translation"]).T[0]
        return xyz

    def transform_colmap_images(self, cameras, transform):
        for cam_id in cameras:
            cameras[cam_id]["R"] = cameras[cam_id]["R"] * transform["rotation"].T
            cameras[cam_id]["C"] =  transform["scale"] * transform["rotation"] * cameras[cam_id]["C"] + transform["translation"]
        return cameras 


    def filter_dense_pointcloud_noise_KDtree(self, xyz, radius, npts, rgb = np.array(0)):
        print('Filter noise in dense pointcloud using KDtree.')
        xyzT = xyz.T
        point_tree = spatial.cKDTree(xyzT)
        num_neighbours = point_tree.query_ball_point(xyzT, radius, workers = -1, return_length = True)
        filter = [num_neighbours[i] > npts for i in range(np.shape(xyz)[1])]
        xyz = xyz[::,filter]
        if rgb.any():
            rgb = rgb[::,filter]
        return (xyz, rgb)


    def get_sorted_and_filtered_observations_and_depth(self, xyz, K, R, C, w, h):
        # project points
        uvl = K * R * (xyz - C)
        u = uvl[0,::] / uvl[2,::]
        v = uvl[1,::] / uvl[2,::]
        uv = np.concatenate((u, v), axis=0)
        depth = np.linalg.norm(xyz - C, axis=0)

        # get data in image
        filter = np.array(renderDepth.is_visible(h, w, np.shape(uv)[1], uv), dtype=np.bool8)
        filter = filter & (np.array(uvl[2,:])[0] > 0)
        depth_filtered = depth[filter]
        uv_filtered = uv[::,filter]
        xyz_filtered = xyz[::,filter]
        xyz_ids = renderDepth.get_ids(np.shape(uv)[1])

        xyz_ids_filtered = xyz_ids[filter]
        
        # sort points wrt. depth
        depth_order = np.flip(np.argsort(depth_filtered))
        depth_sorted = depth_filtered[depth_order]
        uv_sorted = uv_filtered[::,depth_order]
        # xyz_sorted = xyz_filtered[::,depth_order]
        xyz_ids_sorted = xyz_ids_filtered[depth_order]
        
        return (uv_sorted, depth_sorted, xyz_ids_sorted)


    def estimate_visibility_for_image(self, data):
        img_id = data["image_id"]
        print(f'Estimate visibility for image: {img_id}')
        K  = data["K"] 
        R  = data["R"] 
        C  = data["C"] 
        h  = data["h"]
        w  = data["w"]
        xyz  = data["xyz"] 
        new_xyz_grid =  data["new_xyz_grid"] 
        new_xyz_mean =  data["new_xyz_mean"] 
        ids_old_to_new_xyz =  data["ids_old_to_new_xyz"] 
        t  = data["t"]
        distance_threshold = data["dt"] 

        # if all_points = True return visibility to all xyz, othervise new_xyz_mean
        all_points = data["all_points"]  
        visibility_xyz = [] 
        save_depthmaps = data['save_depthmaps']
        depthmaps_path = data['depthmaps_path']
        img_name = data['image_name']
        renderScale = data['renderScale']

        # run cpp to render visibility information
        t[0,::] = t[0,::]*renderScale*1.3
        uv_sorted, depth_sorted, _ = self.get_sorted_and_filtered_observations_and_depth(new_xyz_grid, K, R, C, w, h)
        holo_depth_img = renderDepth.render(renderScale * h, renderScale * w, \
            np.shape(renderScale * uv_sorted)[1], np.shape(t)[1], \
            renderScale * uv_sorted.reshape(1,-1), depth_sorted, t.reshape(1,-1)) 
        

        # downscale the depth
        if renderScale == 1:
            np_depthmap = holo_depth_img.reshape(h, w).astype('float16')
            downscaled_holo_depth_img = holo_depth_img
        else:
            holo_depth_img2 = holo_depth_img.reshape(renderScale * h, renderScale * w).astype('float32')
            upscaled_depthmap = Image.fromarray(holo_depth_img2, mode='F')
            depthmap = upscaled_depthmap.resize((w,h), resample=Image.BICUBIC)
            np_depthmap = numpy.array(depthmap).astype('float16')
            downscaled_holo_depth_img = np_depthmap.astype('float64').reshape(-1,)

        #  debug output
        if save_depthmaps:
            folder, name = os.path.split(img_name)
            np.save(os.path.join(depthmaps_path, name[:-4] + ".npy"), np_depthmap)
            plt.imsave(os.path.join(depthmaps_path, name[:-4] + ".png"), np_depthmap)


        if all_points:
            uv_sorted, depth_sorted, xyz_ids_sorted = self.get_sorted_and_filtered_observations_and_depth( \
                xyz, K, R, C, w, h)
        else:
            uv_sorted, depth_sorted, xyz_ids_sorted = self.get_sorted_and_filtered_observations_and_depth( \
                new_xyz_mean, K, R, C, w, h)

        visibility_xyz = renderDepth.compose_visibility(int(img_id), w, np.shape(uv_sorted)[1], \
                np.floor(uv_sorted).reshape(1,-1), depth_sorted, downscaled_holo_depth_img, \
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
        focal_length = camera["f"]
        if isinstance(focal_length, list):
            if len(focal_length) > 1:
                focal_length = (focal_length[0] + focal_length[1]) / 2
            else:
                focal_length = focal_length[0]
        return np.matrix([[focal_length, 0, camera["pp"][0]],[0, focal_length, camera["pp"][1]],[0, 0, 1]])


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


    def estimate_visibility(self, cameras, images, xyz, xyz_hash_scale = -1, all_points = False, 
        save_grid_pts = False, save_grid_mean_pts = False, save_depthmaps = False, out_path='',
        renderScale = 1):
        
        # hash points
        new_xyz_grid, new_xyz_mean, ids_old_to_new_xyz = self.hash_points(xyz, xyz_hash_scale)

        # debug output
        depthmaps_path = ''
        if not out_path and (save_grid_pts or save_grid_mean_pts or save_depthmaps):
            print('Missing the output path for depthmaps or points. The result will not be saved.')
        if out_path:
            holoio = HoloIO()
            if save_grid_pts:
                holoio.write_pointcloud_to_file(new_xyz_grid, os.path.join(out_path,"pts_grid.obj"))
            if save_grid_mean_pts:
                holoio.write_pointcloud_to_file(new_xyz_mean, os.path.join(out_path,"pts_mean.obj"))

            if save_depthmaps:
                depthmaps_path = os.path.join(out_path, 'depth_maps')
                if not os.path.isdir(depthmaps_path):
                    os.mkdir(depthmaps_path)
            
        # hash cameras
        cameras_hash = cameras
        if isinstance(cameras, list):
            cameras_hash = {}
            for cam in cameras:
                cameras_hash[int(cam["camera_id"])] = cam

        visibility_xyz = []
        all_data = []        
        for image in images.values():
            camera = cameras_hash[int(image["camera_id"])]
            t = self.distance_to_radius_mapping(camera['f'], xyz_hash_scale)
            all_data.append({"image_id": image["image_id"], \
                "K": self.get_calibration_matrix(camera), "R": image["R"], \
                "C": image["C"], "h": camera["height"], \
                "w": camera["width"], "xyz": xyz, "new_xyz_grid": new_xyz_grid, \
                "new_xyz_mean": new_xyz_mean, "ids_old_to_new_xyz": ids_old_to_new_xyz, \
                "t": t, "dt": 1.0/xyz_hash_scale, "all_points": all_points, \
                'save_depthmaps':save_depthmaps, 'depthmaps_path':depthmaps_path, \
                'image_name':image["name"], 'renderScale': renderScale})
        # test = self.estimate_visibility_for_image(all_data[0])
        # savemat(f"/local1/projects/artwin/outputs/hololens_mapper/LibrarySmall_Holo2/data.mat", all_data[0])

        for i in range(len(all_data)):
            visibility_xyz.extend(self.estimate_visibility_for_image(all_data[i]))

        # chunksize = 16  #mp.cpu_count()
        # with mp.Pool(chunksize) as pool:
        #     for ind, res in enumerate(pool.imap(self.estimate_visibility_for_image, all_data), chunksize):
        #         visibility_xyz.extend(res)              # pt3d_id = res[4*i + 0]    img_id = res[4*i + 1]    u = res[4*i + 2]    v = res[4*i + 3]
                # for i in range(0,len(res)):
                #     visibility_xyz.append(res[i])       # pt3d_id = res[4*i + 0]    img_id = res[4*i + 1]    u = res[4*i + 2]    v = res[4*i + 3]

        if all_points: 
            return (visibility_xyz, xyz)
        else:
            return (visibility_xyz, new_xyz_mean)


    def get_view_graph(self, images, points3D):
        
        # images may have any ids
        images_to_ids = {}  
        i = 0
        for image in images.values(): 
            images_to_ids[image['image_id']] = i
            i += 1

        view_graph = np.zeros((i,i),dtype=int)
        for pt in points3D:
            pt_visible_in_images = list(map(int, pt['img_pt'][0::2]))

            for i in range(len(pt_visible_in_images)):
                if pt_visible_in_images[i] in images_to_ids:
                    image_id1 = images_to_ids[pt_visible_in_images[i]]
                    for j in range(i+1,len(pt_visible_in_images)):
                        if pt_visible_in_images[j] in images_to_ids:
                            image_id2 = images_to_ids[pt_visible_in_images[j]]
                            # print('image_id2:' + str(image_id2) + '\n')
                            # if image_id1 == 0 and image_id2 == 1309:
                            #     print('xxx')
                            view_graph[image_id1, image_id2] += 1
        
        return (images_to_ids, view_graph)


    def add_colors_to_dict(self, colors_of_points3D, distance_of_points3D, rgb, img, points3D):
        for i, pt_id in enumerate(img['point3D_ids']):
            if not pt_id in colors_of_points3D:
                colors_of_points3D[pt_id] = []
                distance_of_points3D[pt_id] = []
            pt_rgb = rgb[int(round(img['uvs'][2*i+1])),int(round(img['uvs'][2*i])),:]    
            colors_of_points3D[pt_id].append(pt_rgb[0])
            colors_of_points3D[pt_id].append(pt_rgb[1])
            colors_of_points3D[pt_id].append(pt_rgb[2])
            d_tmp = (points3D[pt_id]['X'] - img['C'].T)
            distance_of_points3D[pt_id].append(np.sqrt(d_tmp * d_tmp.T)[0,0])
        return (colors_of_points3D,distance_of_points3D)


    def estimate_colors_of_points3D(self, images_folder, images, points3D):
        colors_of_points3D = {}
        gray_of_points3D = {}
        distance_of_rgb_points3D = {}
        distance_of_gray_points3D = {}

        for img in images.values():
            img_data = cv2.imread(images_folder + "/" + img["name"])
            if not 'vlc' in img["name"]:
                colors_of_points3D, distance_of_rgb_points3D = \
                    self.add_colors_to_dict(colors_of_points3D, distance_of_rgb_points3D, img_data, img, points3D)
            else:
                gray_of_points3D, distance_of_gray_points3D = \
                    self.add_colors_to_dict(gray_of_points3D, distance_of_gray_points3D, img_data, img, points3D)
        
        for pt in points3D:
            found_colors = False
            if pt['point3D_id'] in colors_of_points3D.keys():
                found_colors = True
                pt_colors = np.reshape(np.matrix(colors_of_points3D[pt['point3D_id']]),(3,-1), order='F')
                distances = np.matrix(distance_of_rgb_points3D[pt['point3D_id']])
            else: 
                if pt['point3D_id'] in gray_of_points3D.keys():
                    found_colors = True
                    pt_colors = np.reshape(np.array(gray_of_points3D[pt['point3D_id']]),(3,-1))
                    distances = np.matrix(distance_of_gray_points3D[pt['point3D_id']])
            if found_colors:
                pt['rgb'] = np.matrix.tolist(pt_colors[:,np.argmin(distances)])
                # score = 1/distances
                # weights = np.exp(score)/np.sum(np.exp(score))
                # pt_rgb = np.round(np.sum(np.multiply(pt_colors,np.matlib.repmat(weights,3,1)), axis=1).T)
                # pt['rgb'] = np.matrix.tolist(pt_rgb.astype(dtype=int))[0]

        return points3D


    shared_array = None

    def add_colors_to_array(self, data):
        rgb = cv2.imread(data["path"])
        for i in range(len(data['point3D_ids'])):
            pt_id = data['point3D_ids'][i]
            if pt_id >= 0:
                d_tmp = np.array([self.shared_array[1,pt_id] - data['C'][0,0], 
                    self.shared_array[2,pt_id] - data['C'][1,0], 
                    self.shared_array[3,pt_id] - data['C'][2,0]])
                d = np.sqrt(np.sum(d_tmp * d_tmp))

                if d < self.shared_array[0,pt_id]:
                    pt_bgr = rgb[int(round(data['uvs'][2*i+1])),int(round(data['uvs'][2*i])),:]    
                    if self.shared_array[4,pt_id] != self.shared_array[5,pt_id] or self.shared_array[5,pt_id] != self.shared_array[6,pt_id]:
                        if pt_bgr[0] != pt_bgr[1] or pt_bgr[1] != pt_bgr[2]:
                            self.shared_array[4,pt_id] = pt_bgr[2]
                            self.shared_array[5,pt_id] = pt_bgr[1]
                            self.shared_array[6,pt_id] = pt_bgr[0]
                            self.shared_array[0,pt_id] = d
                    else:
                        self.shared_array[4,pt_id] = pt_bgr[2]
                        self.shared_array[5,pt_id] = pt_bgr[1]
                        self.shared_array[6,pt_id] = pt_bgr[0]
                        self.shared_array[0,pt_id] = d

    def init_shared_array_for_coloring_points(self, shared_array_base, points3D):
        self.shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
        self.shared_array = self.shared_array.reshape(7, -1)
        for pt in points3D:
            self.shared_array[0,pt['point3D_id']] = Inf
            self.shared_array[1,pt['point3D_id']] = pt['X'][0]
            self.shared_array[2,pt['point3D_id']] = pt['X'][1]
            self.shared_array[3,pt['point3D_id']] = pt['X'][2]
            self.shared_array[4,pt['point3D_id']] = pt['rgb'][0]
            self.shared_array[5,pt['point3D_id']] = pt['rgb'][1]
            self.shared_array[6,pt['point3D_id']] = pt['rgb'][2]

    def estimate_colors_of_points3D_fast(self, images_folder, images, points3D):
        max_pt_id = -1
        for pt in points3D:
            if pt['point3D_id'] > max_pt_id:
                max_pt_id = pt['point3D_id']
        shared_array_base = mp.Array(ctypes.c_double, 7*(max_pt_id + 1))  # [distance, x, y, z, r, g, b]
        self.init_shared_array_for_coloring_points(shared_array_base, points3D)

        all_data = []
        for img in images.values():
            all_data.append({'path': (images_folder + "/" + img["name"]).replace("\\","/"), \
                'uvs': img['uvs'], 'point3D_ids': img['point3D_ids'], 'C': img['C']})

        # pool = mp.Pool(processes=mp.cpu_count())
        # self.add_colors_to_array(all_data[0])     # test
        # # pool.map(self.add_colors_to_array, all_data)

        for data in all_data:
            self.add_colors_to_array(data)
        
        for pt in points3D:
            pt['X'][0] = self.shared_array[1,pt['point3D_id']]
            pt['X'][1] = self.shared_array[2,pt['point3D_id']]
            pt['X'][2] = self.shared_array[3,pt['point3D_id']]
            pt['rgb'][0] = int(self.shared_array[4,pt['point3D_id']])
            pt['rgb'][1] = int(self.shared_array[5,pt['point3D_id']])
            pt['rgb'][2] = int(self.shared_array[6,pt['point3D_id']])

        return points3D

    def update_camera_ids(self, cameras, images):
        '''Update the camera ids. Change camera ids if some images are missing in SfM.'''
        # compose new camera ids, if some camera miss, the ids will go from zero to len(cameras)
        camera_keys = list(cameras.keys())
        camera_map = dict()
        for i in range(0,len(camera_keys)):
            camera_map[camera_keys[i]] = i

        # get dict of cameras with new ids
        new_cameras = dict()
        for camera in cameras.values():
            camera['camera_id'] = camera_map[camera['camera_id']]
            new_cameras[camera['camera_id']] = camera
        
        # update references in the images 
        new_images = dict()
        for img in images.values():
            img['camera_id'] = str(camera_map[int(img['camera_id'])])
            new_images[img['image_id']] = img

        return (new_cameras, new_images)