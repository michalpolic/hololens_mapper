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
    
    def compose_localization_query_from_model(self, lquery_path, cameras, images):
        out_file = open(lquery_path, 'w')
        lquery_list = []
        for img in images.values():
            cam = cameras[int(img['camera_id'])]
            known_camera_model = False
            if cam['model'] == 'SIMPLE_PINHOLE':
                known_camera_model = True
                params = ' SIMPLE_PINHOLE ' + str(cam['width']) + \
                    ' ' + str(cam['height']) + ' ' + str(cam['f']) + \
                    ' ' + str(cam['pp'][0]) + ' ' + str(cam['pp'][1])
            if cam['model'] == 'SIMPLE_RADIAL':
                known_camera_model = True
                params = ' SIMPLE_RADIAL ' + str(cam['width']) + \
                    ' ' + str(cam['height']) + ' ' + str(cam['f']) + \
                    ' ' + str(cam['pp'][0]) + ' ' + str(cam['pp'][1]) + \
                    ' ' + str(cam['rd'][0])
            if cam['model'] == 'RADIAL':
                known_camera_model = True
                params = ' RADIAL ' + str(cam['width']) + \
                    ' ' + str(cam['height']) + ' ' + str(cam['f']) + \
                    ' ' + str(cam['pp'][0]) + ' ' + str(cam['pp'][1]) + \
                    ' ' + str(cam['rd'][0]) + ' ' + str(cam['rd'][1])
            assert known_camera_model, 'Unknown camera model in exporing localization query.'
            lquery_list.append('query/' + img['name'] + params + '\n') 

        out_file.write("".join(lquery_list))
        out_file.close() 