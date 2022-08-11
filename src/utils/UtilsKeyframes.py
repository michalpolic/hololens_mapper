import os
from types import new_class
import cv2
import shutil
from itertools import compress
from pathlib import Path
from igraph import *
from tqdm import tqdm
import numpy as np
from plyfile import PlyData, PlyElement

from src.holo.HoloIO2 import HoloIO2
from src.utils.UtilsMath import UtilsMath

class UtilsKeyframes():

    def __init__(self):
        pass

    def blur_clasifyer_laplacian(self, image, blur_threshold):
        """ Calculate the score for image and check if it is higher than the threshold
        Input: 
            image - image data
            blur_threshold - the threshold for variation of the Laplacian (higher threshold meand sharper images)
            min_frame_offset - min. number of skipped consequtive frames from input sequece
        Output: 
            is_sharp (bool) - boolen if variance of Laplacian of the image is higher than threshold 
        """
        score = cv2.Laplacian(image, cv2.CV_64F).var()
        if score > blur_threshold:
            return True
        return False
    

    def keyframe_selector_simple(self, source_dir, blur_threshold, min_frame_offset, images_extension = ".jpg", logger=None):
        """ Check which images are keyframes based on blur threshold and minimal frame offset
        Input: 
            source_dir - path to images folder
            blur_threshold - the threshold for variation of the Laplacian (higher threshold meand sharper images),
                            for negative values is the blur evaluation skiped
            min_frame_offset - min. number of skipped consequtive frames from input sequece
            images_extension - filter other image formats than selected, e.g., ".jpg"
        Output: 
            keyframe_paths (list) - paths to keyframe images 
        """

        blur_filer = []
        filenames = os.listdir(source_dir)
        filenames_jpg = []
        for filename in filenames:
            if filename[-len(images_extension)::] == images_extension:
                filenames_jpg.append(filename)
                if blur_threshold > 0:
                    image = cv2.imread(source_dir + '/' + filename)
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    blur_filer.append(self.blur_clasifyer_laplacian(gray, blur_threshold))
                else:
                    blur_filer.append(True)

        if min_frame_offset > 1:
            k = 0
            set_zero = False
            for i in range(len(filenames_jpg)):
                k += 1
                if not set_zero:
                    if blur_filer[i]:
                        set_zero = True
                        k = 0
                else:    
                    if (k / min_frame_offset) < 1:
                        blur_filer[i] = False
                    else:
                        set_zero = False
                        if blur_filer[i]:
                            set_zero = True
                            k = 0

        remaining_images = list(compress(filenames_jpg, blur_filer))
        if logger:
            logger.info(f'{len(remaining_images)} images selected out of {len(filenames_jpg)}')
        return remaining_images


    def copy_keyframes(self, source_dirs, destination_dirs, blur_thresholds, min_frame_offsets, \
        images_extensions, logger = None):
        """ Select and copy the keyframes from a set of imges in recording directory
        Input: 
            source_dirs - path to images folders
            destination_dirs - path where to save keyframes
            blur_thresholds - the threshold for variation of the Laplacian (higher threshold meand sharper images),
                              for negative values is the blur evaluation skiped
            min_frame_offsets - min. number of skipped consequtive frames from input sequece
            images_extensions - filter other image formats than selected, e.g., ".jpg"
            logger - object for Meshroom loging
        """
        images_to_copy = [[] for i in range(len(source_dirs))]
        for i in range(len(source_dirs)):
            source_dir = source_dirs[i]
            destination_dir = destination_dirs[i]
            blur_threshold = blur_thresholds[i]
            min_frame_offset = min_frame_offsets[i]
            images_extension = images_extensions[i]

            assert os.path.isdir(source_dir), f"the recording images dir does not exist"
            Path(destination_dir).mkdir(parents=True, exist_ok=True)
            assert os.path.isdir(destination_dir), f"the destination dir does not exist"

            logger.info(f'Selecting keyframes from {source_dir}')
            images_to_copy[i] = self.keyframe_selector_simple(source_dir, blur_threshold, \
                min_frame_offset, images_extension, logger)
            
            logger.info(f'Copying {len(images_to_copy[i])} selected keyframes from {source_dir} to {destination_dir}.')
            try:
                for image_path_src in images_to_copy[i]:
                    path_from = source_dir + '/' + image_path_src
                    path_to = destination_dir + '/' + image_path_src
                    if logger:
                        logger.debug(f'Copy: {path_from} --> {path_to}')

                    shutil.copy(path_from, path_to) 

            except:
                assert False, "failed to copy selected keyframes into output directory"

        return images_to_copy


    def filter_pv_csv(self, images_to_copy, pv_csv):
        """ Select the keyframes from a pv dictionary and create new pv with keyframes
        Input: 
            images_to_copy - keyframe names
            pv_csv - the dictionary with original pv records
        Output:
            new_pv_csv - dictionary with keyframe records
        """
        new_pv_csv = {}
        for img_name in images_to_copy:
            img_id = img_name.replace(".jpg","")
            new_pv_csv[img_id] = pv_csv[img_id]

        return new_pv_csv
        
    def update_img_names(self, pv_csv, replace_from, replace_to):
        """ Select the keyframes from a pv dictionary and cerate new pv with keyframes
        Input: 
            pv_csv - the dictionary with original pv records
            replace_from - replace from the part of filename
            replace_to - replace to the part of filename
        Output:
            new_pv_csv - dictionary with adjusted keyframe records
        """
        new_pv_csv = {}
        for img_key, img_record in pv_csv.items():
            new_pv_csv[img_key] = img_record.replace(replace_from,replace_to)

        return new_pv_csv
        
    def estimate_images_blur(self, source_dir: Path, images: dict) -> list:
        """ Calculate the weights for each image in images as the inverse 
        of the variance of the Laplacian of the image.
        Input: 
            source_dir - the recording directory
            images - the images structure
        Output:
            weights - the inverse of the variance of the Laplacian of the images
        """
        source_path = Path(source_dir)
        weights = []
        print('Computing the weights of images:')
        for img in tqdm(images.values()):
            image = cv2.imread(str(source_path / img['name']))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            weights.append(1/cv2.Laplacian(gray, cv2.CV_64F).var())
        return weights

    def get_subsampled_depth(self, depth_cache: dict, depth_paht: Path, \
        hash_scale: float = 1.) -> np.array:
        if str(depth_paht) not in depth_cache:
            holo2 = HoloIO2()
            pts = holo2.load_ply(str(depth_paht))
            if hash_scale > 0:
                utils_math = UtilsMath()
                pts, _, _ = utils_math.hash_points(pts, hash_scale)
            depth_cache[str(depth_paht)] = pts 
        return (depth_cache, depth_cache[str(depth_paht)])

    def compose_view_graph(self, images: dict, depth_images_folder: Path, \
        cameras: float, min_images_overlap: float, min_spatial_distance: float, \
        max_spatial_distance: float) -> Graph:
        """Compose the view graph out of the images. Images are vertices and edges 
        are between all the image pairs that fullfill minimal images overlap and 
        maximal spatial distance thresholds.
        Input: 
            images - the dictionary of image objects
            fov - the fov of input camera to measure the images overlap
            min_images_overlap - threshold for minimal overlap between images
            max_spatial_distance - threshold for maximal spatial distance 
                between images.
        Output:
            G - the Graph object containig the images as vertices and edges 
            that fulfill input constrains
        """
        N = len(images)
        g = Graph()
        g.add_vertices(N)
        
        print('Check the positional constrains ...')
        C = np.empty([N,3])    #[img['C'] for img in images.values()]
        for i, img in enumerate(images.values()):
            C[i,:] = img['C'].reshape(3,)
        C = np.matrix(C).T

        start_id = 0
        K = int(((N-1)*N) / 2)
        tmp_dist1 = np.empty([3,K])
        tmp_dist2 = np.empty([3,K])
        for i, img in enumerate(images.values()):
            step = N-1-i
            end_id = start_id + step
            tmp_dist1[:,start_id:end_id] = C[:,i] * np.ones([1,step])
            tmp_dist2[:,start_id:end_id] = C[:,i+1:N]
            start_id = end_id
        diff = tmp_dist1 - tmp_dist2
        dist_squared = np.multiply(diff[0,:], diff[0,:]) + \
            np.multiply(diff[1,:], diff[1,:]) + np.multiply(diff[2,:], diff[2,:])
        dist_filter = (dist_squared > (min_spatial_distance**2)) * (dist_squared < (max_spatial_distance**2))
        ids = [(i, j) for i in range(N) for j in range(i+1,N)]
        spatial_valid_pairs = np.array(ids)[dist_filter]   

        print('Check the image overlap constrains ...')
        um = UtilsMath()
        hash_scale = 5
        depth_cache = {}
        overlap_filter = []
        list_images = list(images.values())
        depth_images_folder = Path(depth_images_folder)
        ply_times = np.sort(np.array([int(f[:-4]) for f in os.listdir(depth_images_folder) \
            if (depth_images_folder / f).is_file() and f[-4:] == '.ply']))
        for img_pair_ids in tqdm(spatial_valid_pairs):
            img1 = list_images[img_pair_ids[0]]
            img2 = list_images[img_pair_ids[1]]
            cam1 = cameras[img1['camera_id']]
            cam2 = cameras[img2['camera_id']]
            K1 = um.get_calibration_matrix(cam1)
            K2 = um.get_calibration_matrix(cam2)
            img1_time = int(img1['name'].replace('\\','/').split('/')[1][:-4])
            img2_time = int(img2['name'].replace('\\','/').split('/')[1][:-4])
            depth1_time = ply_times[np.argmin(np.abs(ply_times - img1_time))]
            depth2_time = ply_times[np.argmin(np.abs(ply_times - img2_time))]
            depth_cache, pts1 = self.get_subsampled_depth(depth_cache, \
                depth_images_folder / (str(depth1_time) + '.ply'), hash_scale)
            depth_cache, pts2 = self.get_subsampled_depth(depth_cache, \
                depth_images_folder / (str(depth2_time) + '.ply'), hash_scale)
            _, _, p1i1 = um.get_sorted_and_filtered_observations_and_depth(pts1, K, img1['R'], img1['C'], cam1['width'], cam1['height'])
            _, _, p1i2 = um.get_sorted_and_filtered_observations_and_depth(pts1, K, img2['R'], img2['C'], cam2['width'], cam2['height'])
            _, _, p2i1 = um.get_sorted_and_filtered_observations_and_depth(pts2, K, img1['R'], img1['C'], cam1['width'], cam1['height'])
            _, _, p2i2 = um.get_sorted_and_filtered_observations_and_depth(pts2, K, img2['R'], img2['C'], cam2['width'], cam2['height'])
            count1 = np.shape(np.intersect1d(p1i1.astype(dtype=int), p1i2.astype(dtype=int), assume_unique=True))[0]
            count2 = np.shape(np.intersect1d(p2i1.astype(dtype=int), p2i2.astype(dtype=int), assume_unique=True))[0]
            images_overlap = 100 * (count1 + count2) / (np.shape(p1i1)[0] + np.shape(p2i2)[0])
            if images_overlap > min_images_overlap:
                overlap_filter.append(True)
            else:
                overlap_filter.append(False)
        valid_pairs = spatial_valid_pairs[overlap_filter]   
        g.add_edges(valid_pairs)
        return g

    def convert_edges_to_vertices(self, g: Graph, vs_weights: list = None) -> Graph:
        """The edges of Graph will be stored as vertices and vertices as edges.
        Input: 
            G - input graph
            vs_weights - the weights of original vertices (smaller is better)
        Output:
            EG - output graph
        """
        # mapping
        vertices2edges = [edge.tuple for edge in g.es]
        edges2vertices = {}
        for i, v2e in enumerate(vertices2edges):
            edges2vertices[v2e] = i
        
        # compose new graph
        eg = Graph()
        eg.add_vertices(g.ecount())
        eg.vs["orig_es"] = vertices2edges
        new_es = []
        new_es_weights = []
        new_es_names = []
        print('Compose new graph with exchanged vertices <-> edges ...')
        for e in tqdm(vertices2edges):
            new_v1 = edges2vertices[e]
            for new_e in g.vs[e[0]].out_edges():    # output edges from v1
                if new_e.tuple != e:
                    new_v2 = edges2vertices[new_e.tuple]
                    new_es.append((new_v1,new_v2))
                    new_es_weights.append(vs_weights[e[0]])
                    new_es_names.append(e[0])
            for new_e in g.vs[e[1]].out_edges():    # output edges from v2
                if new_e.tuple != e:
                    new_v2 = edges2vertices[new_e.tuple]
                    new_es.append((new_v1,new_v2))
                    new_es_weights.append(vs_weights[e[1]])
                    new_es_names.append(e[1])
        eg.add_edges(new_es)
        eg.es['orig_vs'] = new_es_names
        return (eg,new_es_weights)

    def get_utilized_images(self, images: dict, eg: Graph) -> dict:
        imgs_order = np.unique(np.array(eg.es['orig_vs']))
        new_images = {}
        for i, img in enumerate(images.values()):
            if i in imgs_order:
                new_images[img['image_id']] = img
        return new_images