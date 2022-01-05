import os
import sys
from ctypes import *
from src.utils.UtilsContainers import UtilsContainers


class Hloc():

    _hloc_container = None

    def __init__(self, hloc_container = None):
        """Init HLOC object to run predefined commands"""
        self._hloc_container = hloc_container

    def build_map(self, dataset_path, outputs_path):
        self._hloc_container.command_dict("python3 /app/build_dataset.py", 
            {"dataset": dataset_path, 
            "outputs": outputs_path})

    def update_image_names(self, images):
        for img_id in images:
            img = images[img_id]
            img['name'] = img['name'].replace('\\','/')
        return images
        