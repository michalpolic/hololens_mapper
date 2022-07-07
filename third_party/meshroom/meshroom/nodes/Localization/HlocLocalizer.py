from __future__ import print_function

from src.holo.HoloIO import HoloIO

__version__ = '0.1'

from meshroom.core import desc
import shutil
import os
import shutil
import sys
import numpy as np
from pathlib import Path
from shutil import copy2

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.utils.UtilsContainers import UtilsContainers
from src.utils.UtilsMath import UtilsMath
from src.colmap.ColmapIO import ColmapIO
from src.holo.HoloIO import HoloIO
from src.hloc.Hloc import Hloc

class HlocLocalizer(desc.Node):

    category = 'Localization'
    documentation = '''
Runs Hloc localization on input images.
'''

    inputs = [
        desc.File(
            name='hlocMapDir',
            label='Hloc Map directory',
            description='Hloc map directory (database, images, features)',
            value='',
            uid=[0],
        ),
        desc.File(
            name='queryFile',
            label='Query file path',
            description='Path to Hloc query file (.txt)',
            value='',
            uid=[0],
        ),
        desc.File(
            name='localSfM',
            label='Local SfM',
            description='Path to folder with images and local SfM.',
            value='',
            uid=[0],
        ),
        desc.BoolParam(
            name='imagesRig',
            label='Use rig of images',
            description='''
            Compute generalized absolute pose for the rig of cameras.
            Require at the input camera poses of the query images.''',
            value='True',
            uid=[],
        ),
        desc.BoolParam(
            name='copyDensePts', 
            label='Copy dense points',
            description='''Copy dense point cloud if available in map folder.''',
            value=False, 
            uid=[0]
        ),
        desc.ChoiceParam(
            name='verboseLevel',
            label='Verbose Level',
            description='''verbosity level (critical, error, warning, info, debug).''',
            value='info',
            values=['critical', 'error', 'warning', 'info', 'debug'],
            exclusive=True,
            uid=[],
            ),
        ]

    outputs = [
        desc.File(
            name='output',
            label='Output folder',
            description='',
            value=desc.Node.internalFolder,
            uid=[],
        ),
        desc.File(
            name='image_pairs',
            label='Image Pairs',
            description='',
            value=os.path.join(desc.Node.internalFolder,'image_pairs.txt'),
            uid=[],
        ),
        desc.File(
            name='localization',
            label='Localization results',
            description='',
            value=os.path.join(desc.Node.internalFolder,'query_localization_results.txt'),
            uid=[],
        ),
        desc.File(
            name='densePts',
            label='Dense point cloud',
            description='',
            value=os.path.join(desc.Node.internalFolder,'model.obj'),
            uid=[],
        )
    ]

    def copy_map_images(self, images, map_folder, output_folder):
        for img in images.values():
            new_img_path = os.path.join(output_folder, img['name'])
            Path(new_img_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(os.path.join(map_folder,img['name']), new_img_path)

    def get_image_pairs_from_viewgraph(self, images, view_graph, min_common_pts = 50):
        order_to_image_id = {}  
        for i, image_id in enumerate(images): 
            order_to_image_id[i] = image_id

        list_image_pairs = []
        img_pair_ids = np.where(view_graph>min_common_pts)
        for i in range(np.shape(img_pair_ids)[1]):
            image1_id = order_to_image_id[img_pair_ids[0][i]]
            image2_id = order_to_image_id[img_pair_ids[1][i]]
            list_image_pairs.append(f"{images[image1_id]['name']} {images[image2_id]['name']}\n") 
        
        return list_image_pairs


    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            if not chunk.node.hlocMapDir.value:
                chunk.logger.warning('Nothing to process, Hloc map required')
                return
            if not chunk.node.queryFile.value:
                chunk.logger.warning('Nothing to process, query file required')
                return

            # setup paths
            output_folder = chunk.node.output.value
            cache_dir = os.path.dirname(os.path.dirname(output_folder))
            map_folder = chunk.node.hlocMapDir.value
            query_file = chunk.node.queryFile.value
            relative_output_folder = output_folder.replace(cache_dir, '/data')
            relative_map_folder = map_folder.replace(cache_dir, '/data')
            relative_query_file = query_file.replace(cache_dir, '/data')
            relative_corresp_path = os.path.join(relative_output_folder,'corresp_2d-3d.npy')
            relative_query_poses_path = relative_query_file.replace('hloc_queries.txt', 'hloc_queries_poses.txt')

            chunk.logger.info('Init containers ...')
            if sys.platform == 'win32':
                cache_dir = cache_dir[0].lower() + cache_dir[1::]
                cache_dir_win = cache_dir.replace(':','')
                hloc_container = UtilsContainers('docker', 'hloc', '/host_mnt/' + cache_dir_win)
                poselib_container = UtilsContainers('docker', 'poselib', '/host_mnt/' + cache_dir_win)
            else:
                hloc_container = UtilsContainers('singularity', dir_path + '/hloc.sif', cache_dir)
                poselib_container = UtilsContainers('singularity', dir_path + '/poselib.sif', cache_dir)


            chunk.logger.info('Running localization ...')   
            hloc_container.command('sh /app/eval.sh ' + relative_map_folder + ' ' + relative_query_file + ' ' + relative_output_folder)
            

            if chunk.node.imagesRig.value:
                
                chunk.logger.info('Running generalized absolute pose ...')   
                poselib_container.command('sh /app/eval.sh ' + relative_corresp_path + ' ' + relative_query_poses_path)

                chunk.logger.info('Copy employed images from map to working directory ...')  
                colmap_io = ColmapIO()
                db_cameras, db_images, db_points3D = colmap_io.load_model(output_folder)
                self.copy_map_images(db_images, map_folder, output_folder)

                chunk.logger.info('Copy employed images from local sfm to working directory ...')  
                um = UtilsMath()
                if chunk.node.localSfM.value:
                    holo_io = HoloIO()
                    holo_io.copy_all_images(chunk.node.localSfM.value, output_folder)
                    
                    chunk.logger.info('Updating the local sfm ...') 
                    hloc = Hloc()
                    q_cameras, q_images, q_points3D = colmap_io.load_model(chunk.node.localSfM.value)
                    # loc_images = hloc.get_imgs_from_localization_results(chunk.node.localization.value)   # localization of individual images
                    gap_file_path = os.path.join(output_folder,'generalized_absolute_pose.txt')
                    transform = hloc.read_generalized_absolute_pose_results(gap_file_path)
                    cameras, images, points3D = um.align_local_and_global_sfm(db_cameras, db_images, db_points3D, \
                        q_cameras, q_images, q_points3D, transform)
                    colmap_io.write_model(output_folder, cameras, images, points3D)

                chunk.logger.info('Extract and write down image pairs to match ...') 
                _, db_view_graph = um.get_view_graph(db_images, db_points3D)
                db_pairs = self.get_image_pairs_from_viewgraph(db_images, db_view_graph)
                _, q_view_graph = um.get_view_graph(q_images, q_points3D)
                q_pairs = self.get_image_pairs_from_viewgraph(q_images, q_view_graph)
                with open(chunk.node.image_pairs.value, 'a') as image_pairs_file:
                    image_pairs_file.write(''.join(db_pairs))
                    image_pairs_file.write(''.join(q_pairs))

            # copy dense point cloud if available
            if chunk.node.copyDensePts.value and os.path.isfile(chunk.node.hlocMapDir.value + '/model.obj'):
                copy2(chunk.node.hlocMapDir.value + '/model.obj' , output_folder)

            chunk.logger.info('Localization done.') 

        except AssertionError as err:
            chunk.logger.error('Error in hlocLocalizer selector: ' + err)
        finally:
            chunk.logManager.end()
