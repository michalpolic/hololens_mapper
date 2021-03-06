from posixpath import join
import os
import sys
from itertools import compress
from argparse import Namespace
import numpy as np
from pathlib import Path
import sqlite3
from scipy.io import savemat

dir_path_root = __file__
for i in range(3):
    dir_path_root = os.path.dirname(dir_path_root)
# sys.path.append(dir_path_root + "/third_party")
# sys.path.append(dir_path_root + "/third_party/patch2pix")

# # import pydegensac
# from patch2pix.utils.common.plotting import plot_matches
# from patch2pix.utils.eval.model_helper import *
# from SuperGluePretrainedNetwork.models.matching import Matching
# from SuperGluePretrainedNetwork.models.utils import (compute_pose_error, compute_epipolar_error,
#                           estimate_pose, make_matching_plot,
#                           error_colormap, AverageTimer, pose_auc, read_image,
#                           rotate_intrinsics, rotate_pose_inplane,
#                           scale_intrinsics)

np.set_printoptions(precision=2)
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
# torch.set_grad_enabled(False)

class UtilsMatcher:

    _matcher = None
    _root_dir = ""
    _device = "cpu"
    _pvK = np.matrix([[1038.135254, 0, 664.387146],[0, 1036.468140, 396.142090],[0, 0, 1]])

    def __init__(self, matcher_name, colmap=None):
        self._root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        # self._device = 'cuda' if torch.cuda.is_available() else 'cpu'

        known_matcher = False
        self._matcher_name = matcher_name
        # if matcher_name == "patch2pix":
        #     known_matcher = True
        #     args = Namespace(io_thres=0.9, imsize=1344, ksize=2, ckpt=f'{self._root_dir}/lib/patch2pix/pretrained/patch2pix_pretrained.pth')
        #     self._matcher = init_patch2pix_matcher(args)
        
        # if matcher_name == "SuperGlue":
        #     known_matcher = True
        #     config = {
        #         'superpoint': {
        #             'nms_radius': 4,
        #             'keypoint_threshold': 0.005,
        #             'max_keypoints': 2048
        #         },
        #         'superglue': {
        #             'weights': 'indoor',
        #             'sinkhorn_iterations': 20,
        #             'match_threshold': 0.2,
        #         }
        #     }
        #     self._matcher = Matching(config).eval().to(self._device)
        
        if matcher_name == "COLMAP" and colmap != None:
            known_matcher = True
            self._matcher = colmap

        assert known_matcher, "The matcher is not defined properly ..."


    def cross(self, x):
        return np.matrix([[0, -x[2,0], x[1,0]], [x[2,0], 0, -x[0,0]], [-x[1,0], x[0,0], 0]])


    def holo_verificator(self, uv1, uv2, cam1, cam2, err_threshold = 10):
        nu1 = np.linalg.inv(self._pvK) * np.concatenate((uv1.T,np.ones((1,np.shape(uv1)[0]))))
        nu2 = np.linalg.inv(self._pvK) * np.concatenate((uv2.T,np.ones((1,np.shape(uv2)[0]))))

        P1 = np.diag([-1, 1, 1, 1]) * cam1["D2C"] * cam1["O2D"]
        P2 = np.diag([-1, 1, 1, 1]) * cam2["D2C"] * cam2["O2D"]
        R21 = P2[0:3,0:3] * P1[0:3,0:3].T
        t21 = P2[0:3,3] - R21 * P1[0:3,3]
        E = self.cross(-t21) * R21
        F = np.linalg.inv(self._pvK).T * E * np.linalg.inv(self._pvK)

        e1 = np.sum(np.multiply(nu1, (E.T * nu2)), axis=0)
        e2 = np.sum(np.multiply(nu2, (E * nu1)), axis=0)
        inliers = np.ndarray.tolist(np.multiply(np.abs(e1)*self._pvK[0,0] < err_threshold, np.abs(e2)*self._pvK[0,0] < err_threshold))[0]
        return (inliers, E, F)


    def cam_to_calibration_matrix(self, cam):
        if cam['model'] == 'PINHOLE':
            return np.matrix([[cam['f'][0], 0, cam['pp'][0]],[0, cam['f'][1], cam['pp'][1]], [0, 0, 1]])
        if cam['model'] == 'RADIAL':
            return np.matrix([[cam['f'], 0, cam['pp'][0]],[0, cam['f'], cam['pp'][1]], [0, 0, 1]])
        assert False, 'Unknown camera model.'
        

    def holo_verificator2(self, uv1, uv2, cam1, cam2, img1, img2, err_threshold = 10):
        K1 = self.cam_to_calibration_matrix(cam1)
        K2 = self.cam_to_calibration_matrix(cam2)
        iK1 = np.linalg.inv(K1)
        iK2 = np.linalg.inv(K2)
        nu1 = iK1 * np.concatenate((uv1.T,np.ones((1,np.shape(uv1)[0]))))
        nu2 = iK2 * np.concatenate((uv2.T,np.ones((1,np.shape(uv2)[0]))))
        t1 = -img1['R'] * img1['C']
        t2 = -img2['R'] * img2['C']
        R21 = img2['R'] * img1['R'].T
        t21 = t2 - R21 * t1
        E = self.cross(-t21) * R21
        F = iK2.T * E * iK1
        e1 = np.sum(np.multiply(nu1, (E.T * nu2)), axis=0)
        e2 = np.sum(np.multiply(nu2, (E * nu1)), axis=0)
        inliers = np.ndarray.tolist(np.multiply(np.abs(e1)*K1[0,0] < err_threshold, np.abs(e2)*K2[0,0] < err_threshold))[0]
        return (inliers, E, F)


    def corresp_clustering(self, all_matches, radius = 4):
        obs_for_image = {}
        match_ids_for_image = {}
        for img_pair in all_matches:
            # imgs_names = img_pair.split("-")
            # img1_name = imgs_names[0]
            # img2_name = imgs_names[1]
            img1_id, img2_id = self.pair_id_to_image_ids(img_pair)
            matches = all_matches[img_pair]
            if not img1_id in obs_for_image:
                obs_for_image[img1_id] = matches["matches"][::,0:2]
            else:
                obs_for_image[img1_id] = np.append(obs_for_image[img1_id], matches["matches"][::,0:2], axis=0)

            if not img2_id in obs_for_image:
                obs_for_image[img2_id] = matches["matches"][::,2:4] 
            else:
                obs_for_image[img2_id] = np.append(obs_for_image[img2_id], matches["matches"][::,2:4], axis=0)

        # cluster the observations within an radius and calculate mean observations
        for img_name in obs_for_image:
            obs = obs_for_image[img_name]
            obs_hash, unique_indices, unique_inverse = np.unique(np.round(obs * (1/(2*radius))), return_index=True, return_inverse=True, axis=0)
            match_ids_for_image[img_name] = unique_inverse

            obs_sum = np.zeros((np.shape(unique_indices)[0],2))
            obs_num = np.zeros((np.shape(unique_indices)[0],1))
            for i in range(np.shape(unique_inverse)[0]):
                obs_sum[unique_inverse[i],::] += obs[i,::]
                obs_num[unique_inverse[i]] += 1
            
            obs_mean = np.zeros((np.shape(unique_indices)[0],2))
            for i in range(np.shape(obs_num)[0]):
                obs_mean[i,::] = obs_sum[i,::] / obs_num[i]
            
            obs_for_image[img_name] = obs_mean

        # assign the ids of obs to matches
        num_registered_obs = {}
        for img_name in obs_for_image:
            num_registered_obs[img_name] = 0
        for img_pair in all_matches:
            # imgs_names = img_pair.split("-")
            img1_id, img2_id = self.pair_id_to_image_ids(img_pair)
            match_ids1 = match_ids_for_image[img1_id]
            match_ids2 = match_ids_for_image[img2_id]
            n_ids = np.shape(all_matches[img_pair]["matches"])[0]
            all_matches[img_pair]["obs_ids1"] = match_ids1[num_registered_obs[img1_id]:num_registered_obs[img1_id]+n_ids]
            all_matches[img_pair]["obs_ids2"] = match_ids2[num_registered_obs[img2_id]:num_registered_obs[img2_id]+n_ids]
            num_registered_obs[img1_id] += n_ids
            num_registered_obs[img2_id] += n_ids
        
        return (obs_for_image, all_matches)


    # def holo_matcher(self, images_dir, holo_cameras, radius = 4, err_threshold = 10, database_path=""):
    #     all_matches = {}
    #     filenames = os.listdir(images_dir)
    #     for i in range(len(filenames)):
    #         for j in range(i+1, len(filenames)):
    #             im1_path = images_dir + '/' + filenames[i]
    #             im2_path = images_dir + '/' + filenames[j]
    #             pair_id = filenames[i][:-4] + '-' + filenames[j][:-4]

    #             # run matching
    #             if self._matcher_name == "SuperGlue":
    #                 image0, inp0, scales0 = read_image(im1_path, self._device, [1344, 756], 0, False)
    #                 image1, inp1, scales1 = read_image(im2_path, self._device, [1344, 756], 0, False)
    #                 pred = self._matcher({'image0': inp0, 'image1': inp1})
    #                 pred = {k: v[0].cpu().numpy() for k, v in pred.items()}
    #                 kpts0, kpts1 = pred['keypoints0'], pred['keypoints1']
    #                 matches_ids1, conf = pred['matches0'], pred['matching_scores0']
    #                 n = np.sum(np.array([1 for t in range(np.shape(kpts0)[0]) if matches_ids1[t] != -1]))
    #                 k = 0 
    #                 matches = np.zeros((n,4))
    #                 for t in range(np.shape(kpts0)[0]):
    #                     if matches_ids1[t] != -1:
    #                         matches[k,::] = np.concatenate((kpts0[t,::],kpts1[matches_ids1[t],::]), axis=0)
    #                         k += 1

    #             if self._matcher_name == "patch2pix":
    #                 matches, _, _ = self._matcher(im1_path, im2_path)

    #             if self._matcher_name == "SIFT":
    #                 matches = self._matcher.load_matches_from_db(database_path, filenames[i], filenames[j])

    #             if np.shape(matches)[0] < 4:
    #                 continue

    #             # verify matches by hololens geometry
    #             inls, E, F = self.holo_verificator(matches[:, 0:2], matches[:, 2:4], holo_cameras[filenames[i][:-4]], holo_cameras[filenames[j][:-4]], err_threshold)
    #             print(f'{pair_id}     matches={len(matches)}, inliers={np.sum(inls)}')
                
    #             all_matches[pair_id] = {"matches": matches, "inliers": inls, "E": E, "F": F}
                
    #             # debuging plot of the matches
    #             # Path(f'{self._root_dir}/tmp/patch2pix').mkdir(parents=True, exist_ok=True)
    #             #inls = [i for i in range(len(inls)) if inls[i]]     # range(np.shape(matches)[0])]
    #             # plot_matches(im1_path, im2_path, matches, inliers=inls, lines=True, radius=1, sav_fig=f'{self._root_dir}/tmp/patch2pix/{filenames[i][:-4]}__{filenames[j][:-4]}.jpg')

    #     return self.corresp_clustering(all_matches, radius)

    def pair_id_to_image_ids(self, pair_id):
        image_id2 = pair_id % 2147483647
        image_id1 = int((pair_id - image_id2) / 2147483647)
        return image_id1, image_id2

    def holo_matcher2(self, images_dir, cameras, images, err_threshold = 10, database_path=""):
        all_matches = {}

        # load image pairs from database of tentative matches 
        all_matches = {}
        con = sqlite3.connect(database_path)
        cursor = con.cursor()
        cursor.execute("SELECT pair_id FROM matches")
        row = cursor.fetchall()
        image_ids = list(images.keys())
        for i in range(len(row)):
            pair_id = row[i][0]
            # if pair_id == 302795194379:
            #     a = 1
            img1_id, img2_id = self.pair_id_to_image_ids(pair_id)
            matches = self._matcher.load_matches_for_pair_of_images(database_path, img1_id, img2_id)
            
            if matches.any() and img1_id in image_ids and img2_id in image_ids:
                img1 = images[img1_id]
                img2 = images[img2_id]
                inls, E, F = self.holo_verificator2(matches[:, 0:2], matches[:, 2:4], \
                    cameras[int(img1['camera_id'])], cameras[int(img2['camera_id'])], img1, img2, err_threshold)
                
                print(f'{pair_id}     matches={len(matches)}, inliers={np.sum(inls)}')
                all_matches[pair_id] = {"matches": matches, "inliers": inls, "E": E, "F": F}

                # debuging plot of the matches
                img1_name = os.path.basename(images_dir + '/' + img1["name"])
                img2_name = os.path.basename(images_dir + '/' + img2["name"])
                data = {
                    "img1": images_dir + '/' + img1["name"], 
                    "img2": images_dir + '/' + img2["name"], 
                    "matches": matches, "inliers": inls
                    }
                # Path(images_dir + '/debug').mkdir(parents=True, exist_ok=True)
                # savemat(f'{images_dir}/debug/{img1_name[:-4]}__{img2_name[:-4]}.mat', data)

        return self.corresp_clustering(all_matches, 1)
 

    def update_image_pairs_paths(self, image_pars_path, prefix =  "", replace = ""):
        image_pairs = []
        images_pairs_file = open(image_pars_path, "r")
        data_lines = images_pairs_file.read().split("\n")
        for line in data_lines:
            if len(line) == 0:
                break
            if line[0] == "#":
                continue
            p = line.split(" ")
            image_pairs.append(prefix + p[0].replace(replace[0],replace[1]) + ' ')
            image_pairs.append(prefix + p[1].replace(replace[0],replace[1]) + '\n')
        images_pairs_file.close()

        images_pairs_file = open(image_pars_path, "w")
        images_pairs_file.write(''.join(image_pairs))
        images_pairs_file.close()

    def update_images_observations(self, images, obs_for_images):
        for img_id in obs_for_images:
            obs = obs_for_images[img_id]
            images[img_id]['uvs'] = np.ndarray.tolist(obs.reshape(-1))
            images[img_id]['point3D_ids'] = [-1 for i in range(int(len(images[img_id]['uvs'])/2))]

        return images

    def synchronize_images_ids_with_database(self, images, images_db):
        images_by_name = {}
        for img in images.values():
            img['image_id'] = -1
            images_by_name[img['name'].replace('\\','/')] = img

        for image_db in images_db:
            if image_db['name'] in images_by_name:
                images_by_name[image_db['name']]['image_id'] = image_db['image_id']

        images = {}
        for i in images_by_name:
            if images_by_name[i]['image_id'] >= 0:
                images[images_by_name[i]['image_id']] = images_by_name[i]

        return images