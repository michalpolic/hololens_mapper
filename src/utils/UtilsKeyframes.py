import os
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
    

    def kyeframe_selector_simple(self, source_dir, blur_threshold, min_frame_offset):
        """ Check which images are keyframes based on blur threshold and minimal frame offset
        Input: 
            source_dir - path to images folder
            blur_threshold - the threshold for variation of the Laplacian (higher threshold meand sharper images)
            min_frame_offset - min. number of skipped consequtive frames from input sequece
        Output: 
            keyframe_paths (list) - paths to keyframe images 
        """

        blur_filer = []
        filenames = os.listdir(source_dir)
        for filename in filenames:
            image = cv2.imread(source_dir + '/' + filename)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur_filer.append(self.blur_clasifyer_laplacian(gray, blur_threshold))

        k = 0
        set_zero = False
        for i in range(len(filenames)):
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
        return list(compress(filenames, blur_filer))


    def copy_keyframes(self, source_dir, destination_dir, blur_threshold = 25, 
        min_frame_offset = 13, logger = None):
        """ Select and copy the keyframes from a set of imges in recording directory
        Input: 
            source_dir - path to images folder
            destination_dir - path where to save keyframes
            blur_threshold - the threshold for variation of the Laplacian (higher threshold meand sharper images)
            min_frame_offset - min. number of skipped consequtive frames from input sequece
            logger - object for Meshroom loging
        """
        assert(os.path.isdir(source_dir), f"the recording images dir does not exist")
        assert(os.path.isdir(destination_dir), f"the destination dir does not exist")

        Path(destination_dir).mkdir(parents=True, exist_ok=True)
        images_to_copy = self.kyeframe_selector_simple(source_dir, blur_threshold, min_frame_offset)

        try:
            for image_path_src in images_to_copy:
                path_from = source_dir + '/' + image_path_src
                path_to = destination_dir + '/' + image_path_src
                if logger:
                    logger.info(f'Copy: {path_from} --> {path_to}')

                shutil.copy(path_from, path_to) 

        except:
            assert(False, "failed to copy selected keyframes into output directory")