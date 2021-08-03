import ctypes
import pathlib
import numpy as np
from numpy import linalg
import numpy.matlib
from scipy.io import savemat
import scipy.spatial as spatial
import os
import sys
sys.path.append(os.path.dirname(__file__) )
import renderDepth
from multiprocessing import Pool


class UtilsMath:

    def q2r(self, q):
        q = q / linalg.norm(np.matrix(q))
        return np.matrix([
            [q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3], 2 * (q[1] * q[2] - q[0] * q[3]),
             2 * (q[1] * q[3] + q[0] * q[2])],
            [2 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] - q[1] * q[1] + q[2] * q[2] - q[3] * q[3],
             2 * (q[2] * q[3] - q[0] * q[1])],
            [2 * (q[1] * q[3] - q[0] * q[2]), 2 * (q[2] * q[3] + q[0] * q[1]),
             q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3]]])


    def r2q(self, R):
        pass 


    def compose_coresponding_camera_centers(self, colmap_cameras, holo_cameras):
        colmap_C = np.array([]).reshape(3,0)
        holo_C = np.array([]).reshape(3,0)

        for i in range(0,len(colmap_cameras)):
            colmap_camera = colmap_cameras[i]
            holo_camera = holo_cameras[colmap_camera["name"][0:-4]]
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


    def filter_dense_pointcloud_noise_KDtree(self, xyz, radius, npts):
        print('Filter noise in dense pointcloud using KDtree.')
        xyzT = xyz.T
        point_tree = spatial.cKDTree(xyzT)
        xyz_filter = []
        for i in range(0,np.shape(xyz)[1]):
            pts_ids = point_tree.query_ball_point(xyzT[i,::], radius)
            if np.max(np.shape(pts_ids)) > npts:
                xyz_filter.append(True)
            else:
                xyz_filter.append(False)
        
        xyz = xyz[::,xyz_filter]
        return xyz


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
        filter = [(uv[0,j] > 0 and uv[1,j] > 0 and uv[0,j] < w and uv[1,j] < h) for j in range(0,np.shape(uv)[1])]
        depth_filtered = depth[filter]
        uv_filtered = uv[::,filter]
        xyz_filtered = xyz[::,filter]
        xyz_ids = np.array([j for j in range(0,np.shape(uv)[1])])
        xyz_ids_filtered = xyz_ids[filter]
        
        # sort points wrt. depth
        depth_order = np.flip(np.argsort(depth_filtered))
        depth_sorted = depth_filtered[depth_order]
        uv_sorted = uv_filtered[::,depth_order]
        xyz_sorted = xyz_filtered[::,depth_order]
        xyz_ids_sorted = xyz_ids_filtered[depth_order]

        # run cpp to render visibility information
        holo_depth_img = renderDepth.render(h, w, np.shape(uv_sorted)[1], \
                np.shape(t)[1], uv_sorted.reshape(1,-1), depth_sorted, t.reshape(1,-1)) 
        holo_depth_img = holo_depth_img.reshape(h,w)
        
        # # test
        # mdic = {"holo_depth_img": holo_depth_img, "uv": uv_sorted, "depth": depth_sorted, "t": t}
        # savemat("/local/artwin/mapping/codes/mapper/src/utils/renderDepth/matlab_matrix.mat", mdic)

        # save the visibility information to observations
        for j in range(0,np.shape(uv_sorted)[1]):
            loc_uv = np.floor(uv_sorted[::,j]).tolist()
            loc_depth = depth_sorted[j]
            if ( np.abs(holo_depth_img[int(loc_uv[1][0]),int(loc_uv[0][0])] - loc_depth) < distance_threshold ):
                visibility_xyz.append(xyz_ids_sorted[j])
                visibility_xyz.append(img_id)
                visibility_xyz.append(loc_uv[0][0])
                visibility_xyz.append(loc_uv[1][0])
        
        return visibility_xyz


    def estimate_visibility(self, camera, images, xyz):
        distance_threshold = 0.1
        chunksize = 20
        t = np.array([[8.0, 5.6, 3.2, 0.8, 0],[1, 3, 5, 7, 9]])

        # get visibility estimate
        w = camera["width"]
        h = camera["height"]
        K = np.matrix([[camera["f"], 0, camera["pp"][0]],[0, camera["f"], camera["pp"][1]],[0, 0, 1]])
        visibility_xyz = [] 
        
        all_data = []
        for image in images:
            all_data.append({"image_id": image["image_id"], "K": K, "R": image["R"], "C": image["C"], "h": h, "w": w, "xyz": xyz, "t": t, "dt": distance_threshold})

        with Pool() as pool:
            for ind, res in enumerate(pool.imap(self.estimate_visibility_for_image, all_data), chunksize):
                for i in range(0,len(res)):
                    visibility_xyz.append(res[i])       # pt3d_id = res[4*i + 0]    img_id = res[4*i + 1]    u = res[4*i + 2]    v = res[4*i + 3]
                    
        return visibility_xyz




        
