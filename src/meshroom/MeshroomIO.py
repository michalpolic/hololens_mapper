import os
import sys
import numpy as np
import json


class MeshroomIO:

    def mat2str(self, M):
        '''
        Print a matrix to JSON
        '''
        M = M.reshape(-1)[0]
        Mstr = [""] * M.size
        for i in range(0, M.size):
            Mstr[i] = str(M[0, i])
        return Mstr


    def init_sfm_structure(self, camera):
        sfm_dict = {
                "version": ["1", "0", "0"],
                "featuresFolders": "",
                "matchesFolders": "",
                "views": [],
                "intrinsics": [{
                    "intrinsicId": str(camera['camera_id']),
                    "width": str(camera['width']),
                    "height": str(camera['height']),
                    "sensorWidth": "1.77777777777777",
                    "sensorHeight": "1.00000000000000",
                    "serialNumber": "",
                    "type": "radial3",
                    "initializationMode": "estimated",
                    "pxInitialFocalLength": str(camera['f']),
                    "pxFocalLength": str(camera['f']),
                    "principalPoint": [
                        str(camera['pp'][0]),
                        str(camera['pp'][1])
                    ],
                    "distortionParams": [
                        str(camera['rd'][0]),
                        str(camera['rd'][1]),
                        "0"
                    ],
                    "locked": "0"
                }],
                "poses": [],
                "structure": []
            }
        return sfm_dict


    def add_views_to_sfm_structure(self, sfm_dict, pv_path, images, camera):
        for img in images:
            sfm_dict["views"].append({
                "viewId": str(img['image_id']),
                "poseId": str(img['image_id']),
                "intrinsicId": str(img['camera_id']),
                "path": pv_path + img['name'],
                "width": str(camera['width']),
                "height": str(camera['height'])
            })

            R = img['R']
            C = img['C']
            sfm_dict["poses"].append({
                "poseId": str(img['image_id']),
                "pose": {
                    "transform": {
                        "rotation": self.mat2str(R.T),   # the transpose is because of row-major format
                        "center": self.mat2str(C)
                    },
                    "locked": 0
                }
            })
        
        return sfm_dict


    def transform_images_to_dictionary(self, images):
        images_dict = {}
        for img in images:
            images_dict[str(img['image_id'])] = img
        return images_dict


    def add_points_to_sfm_structure(self, sfm_dict, points, images):
        images_dict = self.transform_images_to_dictionary(images)
        for pt in points:
            if (len(pt['img_pt']) / 2) > 3 and pt['err'] < 2:
                landmark = {
                    "landmarkId": str(pt['point3D_id']),
                    "descType": "sift",
                    "color": [str(pt['rgb'][0]), str(pt['rgb'][1]), str(pt['rgb'][2])],
                    "X": [str(pt['X'][0]), str(pt['X'][1]), str(pt['X'][2])],
                    "observations": []
                }

                for j in range(int((len(pt['img_pt'])) / 2)):
                    image_id = int(pt['img_pt'][2*j])
                    observation_id = int(pt['img_pt'][2*j + 1])
                    img = images_dict[str(image_id)]
                    uv = img['uvs'][2*observation_id:2*observation_id+2]

                    landmark["observations"].append({
                        "observationId": str(image_id),
                        "featureId": str(observation_id),
                        "x": [str(uv[0]), str(uv[1])],
                        "scale": "0"
                    })
                sfm_dict["structure"].append(landmark)

        return sfm_dict


    def get_obs_hash(self, u, v):
        return "obs_" + str(u) + "_" + str(v)


    def add_xyz_to_sfm_structure(self, sfm_dict, xyz, visibility_map):
        print("Finding obs for feature point and num. of images.") 
        max_img_id = 0
        obs_for_feature = [[] for _ in range(0,np.shape(xyz)[1])]
        for i in range(0,int(len(visibility_map)/4)):
            k = visibility_map[4*i]
            obs_for_feature[k].append(visibility_map[4*i + 1])
            obs_for_feature[k].append(visibility_map[4*i + 2])
            obs_for_feature[k].append(visibility_map[4*i + 3])
            if visibility_map[4*i + 1] > max_img_id: 
                max_img_id = visibility_map[4*i + 1]
        
        print("Setting the observations ids.") 
        images_obs = [{} for _ in range(0,max_img_id+1)]
        images_obs_max = [0 for _ in range(0,max_img_id+1)]
        for i in range(0,int(len(visibility_map)/4)):
            img_id = visibility_map[4*i + 1]
            images_obs[img_id][self.get_obs_hash(visibility_map[4*i+2],visibility_map[4*i+3])] = images_obs_max[img_id]
            images_obs_max[img_id] += 1

        print("Saving the structure.") 
        for i in range(np.shape(xyz)[1]):
            if (len(obs_for_feature[i]) / 3) > 3:       # we want at least 3 obs for 3D point
                landmark = {
                    "landmarkId": str(i),
                    "descType": "sift",
                    "color": ["255", "255", "255"],
                    "X": [str(xyz[0,i]), str(xyz[1,i]), str(xyz[2,i])],
                    "observations": []
                }

                for j in range(int(len(obs_for_feature[i]) / 3)):
                    img_id = obs_for_feature[i][3*j]    
                    u = obs_for_feature[i][3*j + 1]
                    v = obs_for_feature[i][3*j + 2]
                    if self.get_obs_hash(u,v) in  images_obs[img_id]:
                        observation_id = images_obs[img_id][self.get_obs_hash(u,v)]
                        landmark["observations"].append({
                            "observationId": str(img_id),
                            "featureId": str(observation_id),
                            "x": [str(u), str(v)],
                            "scale": "0"
                        })
                sfm_dict["structure"].append(landmark)

        return sfm_dict


    def save_colmap_to_json(self, out_path, pv_path, camera, images, points):
        print("Saving COLMAP to Meshroom JSON.")
        sfm_dict = self.init_sfm_structure(camera)
        sfm_dict = self.add_views_to_sfm_structure(sfm_dict, pv_path, images, camera)
        sfm_dict = self.add_points_to_sfm_structure(sfm_dict, points, images)
        with open(out_path, 'w') as outfile:
            json.dump(sfm_dict, outfile)


    def save_merged_mvs_to_json(self, out_path, pv_path, camera, images, xyz, visibility_map):
        print("Saving Holo + MVS to Meshroom JSON.")
        sfm_dict = self.init_sfm_structure(camera)
        sfm_dict = self.add_views_to_sfm_structure(sfm_dict, pv_path, images, camera)
        sfm_dict = self.add_xyz_to_sfm_structure(sfm_dict, xyz, visibility_map)
        with open(out_path, 'w', buffering=2048) as outfile:
            json.dump(sfm_dict, outfile)


    def load_obj_vertices(self, obj_file_path):
        print("Load OBJ vertices: " + obj_file_path)
        f = open(obj_file_path, 'r')
        lines = f.readlines()
        count = 0
        for line in lines:
            if line.startswith('v'):  
                count += 1
                continue
            if line.startswith('f'):
                break

        count2 = 0
        xyz = np.zeros((3,count), dtype=float)
        for line in lines:
            if line.startswith('v'):    
                pt_str = line[2:].split(' ')
                xyz[0][count2] = float(pt_str[0])
                xyz[1][count2] = float(pt_str[1])
                xyz[2][count2] = float(pt_str[2])
                count2 += 1
                continue

            if line.startswith('f'):
                break

        f.close()
        return xyz

    def load_ply_vertices(self, ply_file_path):
        print("Load PLY vertices: " + ply_file_path)
        f = open(ply_file_path, 'r')
        lines = f.readlines()
        count = 0
        for line in lines:
            count += 1
            if line.startswith('end_header'):  
                break

        count2 = 0
        xyz = np.zeros((3,len(lines) - count), dtype=float)
        for line in lines:
            count2 += 1
            if count2 <= count:
                continue
            else:
                line = line.lstrip()
                line_len = len(line)
                line = line.replace("  ", " ")
                while len(line) < line_len:
                    line_len = len(line)
                    line = line.replace("  ", " ")
                    
                pt_str = line.split(" ")

                xyz[0][count2 - count - 1] = float(pt_str[0])
                xyz[1][count2 - count - 1]  = float(pt_str[1])
                xyz[2][count2 - count - 1] = float(pt_str[2]) 

        f.close()
        return xyz