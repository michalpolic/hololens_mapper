import os
import cv2
import shutil
from itertools import compress
from pathlib import Path


class UtilsKeyframes():

    def __init__(self):
        pass

    def blur_clasifyer_laplacian(self, image, blur_threshold):
        score = cv2.Laplacian(image, cv2.CV_64F).var()
        print(f"{score} \n")
        if score > blur_threshold:
            return True
        return False
    
    def kyeframe_selector_simple(self, dir_path, blur_threshold, min_frame_offset):
        blur_filer = []
        filenames = os.listdir(dir_path)
        filenames_jpg = []
        for filename in filenames:
            if filename[-4::] == ".jpg":
                filenames_jpg.append(filename)
                image = cv2.imread(dir_path + '/' + filename)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                blur_filer.append(self.blur_clasifyer_laplacian(gray, blur_threshold))

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



    def copy_keyframes(self, source_dir, destination_dir, blur_threshold, min_frame_offset):
        Path(destination_dir).mkdir(parents=True, exist_ok=True)
        images_to_copy = self.kyeframe_selector_simple(source_dir, blur_threshold, min_frame_offset)
        for image_path_src in images_to_copy:
            shutil.copy(source_dir + '/' + image_path_src, destination_dir + '/' + image_path_src) 