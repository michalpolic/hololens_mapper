from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import sys
import numpy as np
import enum

# import mapper packages
dir_path = __file__
for i in range(6):
    dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)
from src.holo.HoloIO import HoloIO
from src.utils.UtilsMath import UtilsMath
from src.meshroom.MeshroomIO import MeshroomIO
from src.utils.UtilsContainers import UtilsContainers

class ICP(enum.Enum):
    ICP = 0
    AA_ICP = 1
    FICP = 2
    RICP = 3
    ICP_P2P = 4
    RICP_P2P = 5
    SICP = 6
    SICP_P2P = 7

class DensePointcloudsAligner(desc.Node):

    category = 'Alignment'
    documentation = '''
This filter loads two dense pointclouds and merge them into one. \n
Merging algorithms: \n
                    concatenation - merges pointclouds exactly as they are\n
                    ICP - Iterative closest point\n
                    RICP - Robust ICP\n
                    AA_ICP - Anderson Acceleration ICP\n
                    FICP - Fast ICP\n
                    ICP_P2P - ICP point-to-plane\n
                    RICP_P2P - Robust ICP point-to-plane\n
                    SICP - Sparse ICP\n
                    SICP_P2P - Sparse ICP point-to-plane\n
                    
'''
    # TODO: add the merging strategy, i.e., the order of merging the pointclouds

    inputs = [
        desc.ListAttribute(
            name="pointclouds",
            elementDesc=desc.StringParam(name="pointcloudPath", label="PointcloudPath", description="Path to pointclouds (.obj or .ply)", value="", uid=[0]),
            label="Pointclouds",
            description="Paths to pointcloud files (.obj or .ply)",
            group="",
        ),
        desc.ChoiceParam(
            name='alignmentMehod',
            label='Alignment method',
            description="Method for aligning the pointclouds.",
            value='RICP',
            values=['concatenation', 'RICP', 'ICP', 'AA_ICP', 'FICP', 'ICP_P2P', 'RICP_P2P', 'SICP', 'SICP_P2P', 'OverlapPredator'], # TODO: R-ICP, ICP, ...., Predator, Teaserpp-Magsacpp, ...
            exclusive=True,
            uid=[],
        ),
        desc.ChoiceParam(
            name='alignmentStrategy',
            label='Alignment strategy',
            description="Method for aligning more pointclouds.",
            value='Sequential alignment',
            values=['Sequential alignment'], # TODO: more strategies
            exclusive=True,
            uid=[],
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
        desc.File(
            name="configFile",
            label="Path to OverlapPredator config",
            description="Path to OverlapPredator configuration file (.yaml)",
            value="",
            uid=[0],
        ),
        desc.IntParam(
            name="sampling", 
            label="Sampling", 
            description="Sampling of pointclouds", 
            value=1000, 
            uid=[0], 
            range=(0, 1000000, 1)),
        ]

    outputs = [
        desc.File(
            name="output",
            label="Output folder",
            description="",
            value=desc.Node.internalFolder + "/model.obj",
            uid=[],
            ),
    ]

    def concatenate(self, chunk, holo_io, meshroom_io, outfile, pc1, pc2):
        # load the pointclouds
        chunk.logger.info('Loading dense pointcloud 1.')
        xyz1, rgb1 = meshroom_io.load_vertices(pc1) 
        chunk.logger.info('Loading dense pointcloud 2.')
        xyz2, rgb2 = meshroom_io.load_vertices(pc2) 
        # alignment
        common_xyz = np.array((3,0), dtype=float)
        common_rgb = np.array((3,0), dtype=np.uint8)

        common_xyz = np.concatenate((xyz1, xyz2), axis=1)
        common_rgb = np.concatenate((rgb1, rgb2), axis=1)

        # save the common pointcloud
        chunk.logger.info('Saving filtered pointcloud.')
        holo_io.write_pointcloud_to_file(common_xyz, \
            outfile, rgb = common_rgb)
        
    def iterative_closest_point(self, chunk, outfile, pc1, pc2):
        method = ICP[chunk.node.alignmentMehod.value].value
        chunk.logger.info('Setting values for R-ICP.')          
        out_dir = outfile.split('model.obj')[0]
        ricp_container = UtilsContainers("singularity", dir_path + "/ricp.sif", './third_party/Fast-Robust-ICP/')
        chunk.logger.info('Running R-ICP.')   
        ricp_container.command_dict("/app/build/FRICP " + pc1 + " " + pc2 + " " + out_dir + " " + str(method), {})

    def build_config_file(self, chunk, out_dir, config_path, pc1, pc2, s):
        chunk.logger.info('Writing Predator config file.') 
        config_file = open(config_path, 'r')
        data = config_file.read()
        config_file.close()

        config = data.split('demo:\n')

        new_config =   'demo:\n  src_pcd: ' + pc2 + '\n  tgt_pcd: ' + pc1 + '\n  n_points: ' + str(s) +'\n\n'
        
        new_config_path = out_dir + 'predator_config.yaml'
        new_config_file = open(new_config_path, 'w')
        new_config_file.write(config[0] + new_config)
        new_config_file.close()

        return new_config_path

    def overlap_predator(self, chunk, outfile, config_path, pc1, pc2, s):
        out_dir = outfile.split('model.obj')[0]
        new_config_file = self.build_config_file(chunk, out_dir, config_path, pc1, pc2, s)
        predator_container = UtilsContainers("singularity", dir_path + "/predator.sif", './third_party/OverlapPredator/')
        chunk.logger.info('Running Predator.') 
        predator_container.command_dict("pip3 freeze", {})
        predator_container.command_dict("python3 /app/scripts/demo.py " + new_config_file, {}) #TODO, at to ulozi vysledky

    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.output.value:
                return

            pointclouds = chunk.node.pointclouds.getPrimitiveValue(exportDefault=True)

            if len(pointclouds) < 2:
                chunk.logger.warning('Nothing to process, at least 2 pointclouds required')
                return
            
            holo_io = HoloIO()
            meshroom_io = MeshroomIO()
            utils_math = UtilsMath()
            outfile = chunk.node.output.value
            


            if chunk.node.alignmentMehod.value == "concatenation":
                pc1 = pointclouds[0]
                pc2 = pointclouds[1]
                self.concatenate(chunk, holo_io, meshroom_io, outfile, pc1, pc2)
                for i in range(2, len(pointclouds)):
                    self.concatenate(chunk, holo_io, meshroom_io, outfile, outfile, pointclouds[i])

                    
            elif chunk.node.alignmentMehod.value in ICP.__members__:
                pc1 = pointclouds[0]
                pc2 = pointclouds[1]
                self.iterative_closest_point(chunk, outfile, pc1, pc2)
                aligned_file = outfile.split('model.obj')[0] + 'm3reg_pc.ply'
                self.concatenate(chunk, holo_io, meshroom_io, outfile, pc1, aligned_file)
                
                for i in range(2, len(pointclouds)):
                    self.iterative_closest_point(chunk, outfile, outfile, pointclouds[i])
                    aligned_file = outfile.split('model.obj')[0] + 'm3reg_pc.ply'
                    self.concatenate(chunk, holo_io, meshroom_io, outfile, outfile, aligned_file)

            elif chunk.node.alignmentMehod.value == "OverlapPredator":
                pc1 = pointclouds[0]
                pc2 = pointclouds[1] 
                config_path = chunk.node.configFile.value
                s = chunk.node.sampling.value
                self.overlap_predator(chunk, outfile, config_path, pc1, pc2, s)
                # TODO concat + vic pointcloudu
                for i in range(2, len(pointclouds)):
                    self.overlap_predator(chunk, outfile, config_path, outfile, pointclouds[i], s)
                    aligned_file = outfile.split('model.obj')[0] + 'm3reg_pc.ply'
                    self.concatenate(chunk, holo_io, meshroom_io, outfile, outfile, aligned_file)          

            chunk.logger.info('Dense pointcloud alignment done.') 

        except AssertionError as err:
            chunk.logger.error("Error in keyframe selector: " + err)
        finally:
            chunk.logManager.end()
