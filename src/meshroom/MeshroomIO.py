import os
import sys
import numpy as np

try:
    import ujson as json
except ImportError:
    import json
import src.meshroom.MeshroomCpp as MeshroomCpp

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


    def init_sfm_structure(self):
        sfm_dict = {
                "version": ["1", "0", "0"],
                "featuresFolders": "",
                "matchesFolders": "",
                "views": [],
                "intrinsics": [],
                "poses": [],
                "structure": []
            }
        return sfm_dict

    def get_focal(self, camera):
        if camera['model'] == 'RADIAL':
            return camera['f']
        if camera['model'] == 'PINHOLE':
            return (camera['f'][0] + camera['f'][1]) / 2 
        assert False, "Unknown camera model."

    def get_radial_distortion(self, camera, out_model = 'radial3'):
        if out_model == 'radial3':
            if camera['model'] == 'RADIAL':
                return [camera['rd'][0], camera['rd'][1], 0]
            if camera['model'] == 'PINHOLE':
                return [0, 0, 0]
        assert False, "Unknown camera model."

    def add_cameras_to_sfm_structure(self, sfm_dict, cameras):
        intrinsics_list = []
        for camera_id in cameras:
            cam = cameras[camera_id]
            rd = self.get_radial_distortion(cam)
            intrinsics_list.append({
                "intrinsicId": str(cam['camera_id']),
                "width": str(cam['width']),
                "height": str(cam['height']),
                "sensorWidth": "1.77777777777777",
                "sensorHeight": "1.00000000000000",
                "serialNumber": "",
                "type": "radial3",
                "initializationMode": "estimated",
                "pxInitialFocalLength": str(self.get_focal(cam)),
                "pxFocalLength": str(self.get_focal(cam)),
                "principalPoint": [
                    str(cam['pp'][0]),
                    str(cam['pp'][1])
                ],
                "distortionParams": [
                    str(rd[0]),
                    str(rd[1]),
                    str(rd[2])
                ],
                "locked": "0"
            })
        sfm_dict['intrinsics'] = intrinsics_list
        return sfm_dict


    def add_views_to_sfm_structure(self, sfm_dict, images_path, images, cameras):

        for img in images:
            cam = cameras[int(img['camera_id'])]

            sfm_dict["views"].append({
                "viewId": str(img['image_id']),
                "poseId": str(img['image_id']),
                "intrinsicId": str(img['camera_id']),
                "path": images_path + img['name'].replace('\\','/'),
                "width": str(cam['width']),
                "height": str(cam['height'])
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

    def add_points_to_sfm_structure(self, sfm_dict, points3D, images):
        images_dict = {}
        for img in images:
            images_dict[int(img['image_id'])] = img

        for pt in points3D:
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
                    img = images_dict[image_id]
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
        visibility_map = visibility_map.astype(dtype=int)
        for i in range(0,int(len(visibility_map)/4)):
            k = visibility_map[4*i]
            obs_for_feature[k].append(visibility_map[4*i + 1])
            obs_for_feature[k].append(visibility_map[4*i + 2])
            obs_for_feature[k].append(visibility_map[4*i + 3])
            if visibility_map[4*i + 1] > max_img_id: 
                max_img_id = visibility_map[4*i + 1]
        
        print("Setting the observations ids.") 
        images_obs = [{} for _ in range(max_img_id+1)]
        images_obs_max = [0 for _ in range(max_img_id+1)]
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


    def save_colmap_to_json(self, out_path, pv_path, cameras, images, points):
        print("Composition of Meshroom JSON.")
        sfm_dict = self.init_sfm_structure()
        sfm_dict = self.add_cameras_to_sfm_structure(sfm_dict, cameras)
        sfm_dict = self.add_views_to_sfm_structure(sfm_dict, pv_path, images, cameras)
        sfm_dict = self.add_points_to_sfm_structure(sfm_dict, points, images)
        with open(out_path, 'w') as outfile:
            json.dump(sfm_dict, outfile)

    def write_model(self, out_path, images_dir, cameras, images, points3D):
        print("Composition of Meshroom JSON.")
        sfm_dict = self.init_sfm_structure()
        sfm_dict = self.add_cameras_to_sfm_structure(sfm_dict, cameras)
        sfm_dict = self.add_views_to_sfm_structure(sfm_dict, images_dir, images, cameras)
        sfm_dict = self.add_points_to_sfm_structure(sfm_dict, points3D, images)
        with open(out_path, 'w') as outfile:
            json.dump(sfm_dict, outfile)

    def save_merged_mvs_to_json(self, out_path, pv_path, cameras, images, xyz, visibility_map, rgb):
        print("Saving Holo + MVS to Meshroom JSON.")
        sfm_dict = self.init_sfm_structure()
        sfm_dict = self.add_cameras_to_sfm_structure(sfm_dict, cameras)
        sfm_dict = self.add_views_to_sfm_structure(sfm_dict, pv_path, images, cameras)
        
        rgb2 = np.ndarray.tolist(np.ndarray.flatten(rgb.astype(dtype=np.float64).T))
        xyz2 = np.ndarray.tolist(np.ndarray.flatten(np.array(xyz).T))
        str_structure = MeshroomCpp.encode_structure(np.shape(xyz)[1], \
            int(np.shape(visibility_map)[0] / 4), xyz2, rgb2, visibility_map)
        str_dict = json.dumps(sfm_dict)
        outfile = open(out_path, 'w')
        outfile.write(str_dict[0:-3] + str_structure + "}")
        outfile.close()

        # visibility_map = np.array(visibility_map)
        # sfm_dict = self.add_xyz_to_sfm_structure(sfm_dict, xyz, visibility_map)
        # str_dict = json.dumps(sfm_dict)
        # outfile = open(out_path, 'w')
        # outfile.write(str_dict)
        # outfile.close()


    def load_vertices(self, file_path):
        if file_path[-4::] == ".obj":
            return self.load_obj_vertices(file_path)
        if file_path[-4::] == ".ply":
            return self.load_ply_vertices(file_path)
        return np.array((0,3))


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
        rgb = np.zeros((3,count), dtype=np.uint8)
        for line in lines:
            if line.startswith('v'):    
                pt_str = line[2:].split(' ')
                xyz[0][count2] = float(pt_str[0])
                xyz[1][count2] = float(pt_str[1])
                xyz[2][count2] = float(pt_str[2])
                if len(pt_str) >= 6:
                    rgb[0][count2] = np.uint8(float(pt_str[3]))
                    rgb[1][count2]  = np.uint8(float(pt_str[4]))
                    rgb[2][count2] = np.uint8(float(pt_str[5]))
                else:
                    rgb[0][count2] = np.uint8(255)
                    rgb[1][count2]  = np.uint8(255)
                    rgb[2][count2] = np.uint8(255)
                count2 += 1
                continue

            if line.startswith('f'):
                break

        f.close()
        return (xyz, rgb)

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
        rgb = np.zeros((3,len(lines) - count), dtype=np.uint8)
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

                if len(pt_str) >= 6:
                    rgb[0][count2 - count - 1] = np.uint8(pt_str[3])
                    rgb[1][count2 - count - 1]  = np.uint8(pt_str[4])
                    rgb[2][count2 - count - 1] = np.uint8(pt_str[5])  
                else:
                    rgb[0][count2 - count - 1] = np.uint8(255)
                    rgb[1][count2 - count - 1]  = np.uint8(255)
                    rgb[2][count2 - count - 1] = np.uint8(255)

        f.close()
        return (xyz, rgb)