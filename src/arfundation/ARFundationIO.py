import os
import sys
import io
import numpy as np
from tqdm import tqdm
from PIL import Image
import xml.etree.ElementTree as ET
from pathlib import Path
from scipy.io import savemat

class ARFundationIO:

    def get_pose_parameters(self, one_record):
        index = one_record.get('index')
        pose = one_record.find('pos')
        q = one_record.find('rot')
        return (index, pose.get('x'), pose.get('y'), pose.get('z'), q.get('w'), q.get('x'), q.get('y'), q.get('z'))


    def convert_rgb_images(self, color_images_path, xml, output_folder):
        print('Convert color.bin to images + images.txt ...')
        id_to_pose = {}
        for pose in xml.findall('pose'):
            id_to_pose[pose.attrib['index']] = pose
        N = len(id_to_pose)

        images_path = Path(output_folder) / 'images.txt'
        images_lines = []
        with open(images_path, 'w+') as images_file:
            images_lines.append('# Image list with two lines of data per image:\n')
            images_lines.append('#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n')
            images_lines.append('#   POINTS2D[] as (X, Y, POINT3D_ID)\n')
            images_lines.append(f'# Number of images: {N}, mean observations per image: 0\n')

            for xml_record in tqdm(xml.findall('color')):
                # save the image
                with open(color_images_path, mode='rb') as file:
                    numpy_data = np.fromfile(file, np.dtype('B'), \
                        int(xml_record.attrib['length']), sep='', offset=int(xml_record.attrib['position']))
                    #np_image = np.reshape(numpy_data, (int(xml_record.attrib['height']), int(xml_record.attrib['width']), 4))
                    img_name = xml_record.attrib['index'].zfill(5) + '.jpg'
                    image_path = Path(output_folder) / 'images' / img_name
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                    # Image.fromarray(np_image).save(image_path)
                    image = Image.open(io.BytesIO(numpy_data))
                    image.transpose(Image.FLIP_TOP_BOTTOM).save(image_path)

                # add the image.txt record
                index, tx, ty, tz, qw, qx, qy, qz = self.get_pose_parameters(id_to_pose[xml_record.attrib['index']])
                images_lines.append(f'{index} {qw} {qx} {qy} {qz} {tx} {ty} {tz} 0 images/{img_name}\n \n')
            images_txt = ''.join(images_lines)
            images_file.write(images_txt)
                

    def convert_depth_images(self, depth_images_path, xml, output_folder):
        print('Convert depth.bin to numpy arrays ...')
        for xml_record in tqdm(xml.findall('depth')):
            with open(depth_images_path, mode='rb') as file:
                numpy_data = np.fromfile(file, np.dtype('B'), \
                    int(xml_record.attrib['length']), sep='', offset=int(xml_record.attrib['position']))
            np_image = np.reshape(np.frombuffer(numpy_data, dtype=np.float32), \
                 (int(xml_record.attrib['height']), int(xml_record.attrib['width'])))
            np_depthmap_path = Path(output_folder) / 'depth' / (xml_record.attrib['index'].zfill(5) + '.npy')
            np_depthmap_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(np_depthmap_path, np_image)
            mat_depthmap_path = Path(output_folder) / 'depth' / (xml_record.attrib['index'].zfill(5) + '.mat')
            savemat(mat_depthmap_path, {"depth": np_image})

