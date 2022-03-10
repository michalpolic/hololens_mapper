import sys
import math
import os
from pathlib import Path
import re
import multiprocessing as mp
from distutils.dir_util import copy_tree
from plyfile import PlyData, PlyElement

import numpy as np

class HoloIO2:

    def __init__(self):
        pass

    def compose_common_pointcloud(self, pointclouds_dir, logger=None):
        """Read and concatenate the pointcloud in Long Throw Depth folder.
        Input: 
            pointclouds_dir - path to pointclouds directory
        Output: 
            xyz - single common pointcloud
        """
        if not pointclouds_dir[-1] == '/':
            pointclouds_dir = pointclouds_dir + '/'

        xyz = []
        for r, d, f in os.walk(pointclouds_dir):
            for filename in f:
                if ".ply" in filename:
                    if logger:
                        logger.info(f'Loading: {filename}')

                    plydata = PlyData.read(pointclouds_dir + filename)
                    for pt in plydata['vertex'].data:
                        xyz.append(pt[0])
                        xyz.append(pt[1])
                        xyz.append(pt[2])

        return np.array(xyz,dtype=float).reshape((3,-1),order='F') 