import os
from types import new_class
import cv2
import shutil
from itertools import compress
from pathlib import Path


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
    

    def keyframe_selector_simple(self, source_dir, blur_threshold, min_frame_offset, images_extension = ".jpg"):
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
        return list(compress(filenames_jpg, blur_filer))


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

            images_to_copy[i] = self.keyframe_selector_simple(source_dir, blur_threshold, \
                min_frame_offset, images_extension)

            try:
                for image_path_src in images_to_copy[i]:
                    path_from = source_dir + '/' + image_path_src
                    path_to = destination_dir + '/' + image_path_src
                    if logger:
                        logger.info(f'Copy: {path_from} --> {path_to}')

                    shutil.copy(path_from, path_to) 

            except:
                assert False, "failed to copy selected keyframes into output directory"

        return images_to_copy


    def filter_pv_csv(self, images_to_copy, pv_csv):
        """ Select the keyframes from a pv dictionary and cerate new pv with keyframes
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
        