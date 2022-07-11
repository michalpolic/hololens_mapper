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

class Transform:
  def __init__(self, translation, rotation, scale):
    self.translation = translation
    self.rotation = rotation
    self.scale = scale

class Matterport2Vicon(desc.Node):

    category = 'ARTwin'
    documentation = '''
Transforms Matterport to Vicon coordinate system
                    
'''
    inputs = [
        desc.File(
            name="matterportModel",
            label="Path to Matterport",
            description="Path to Matterport point cloud file (.ply )",
            value="",
            uid=[0],
        ),
        desc.File(
            name="matterportPointFile",
            label="Path to Matterport points",
            description="Path to file with Matterport points (.txt)",
            value="",
            uid=[0],
        ),
        desc.File(
            name="viconPointFile",
            label="Path to Vicon points",
            description="Path to file with Vicon points (.txt)",
            value="",
            uid=[0],
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
            name="output",
            label="Output folder",
            description="",
            value=desc.Node.internalFolder,
            uid=[],
            ),
    ]

    def procrustes(self, X, Y):
        (n,m) = X.shape
        (ny,my) = Y.shape

        print("------------------")
        print("n = " + str(n) + ", m = " + str(m) + ", ny = " + str(ny) + ", my = " + str(my))
        print("")

        #muX = allHol.transpose().mean(axis=1)
        #muY = allCol.transpose().mean(axis=1)

        muX = X.mean(axis=0)
        muY = Y.mean(axis=0)


        X0 = X - np.tile(muX, (n, 1))
        Y0 = Y - np.tile(muY, (n, 1))



        ssqX = np.square(X0)
        ssqX = sum(ssqX)

        ssqY = np.square(Y0)
        ssqY = sum(ssqY)


        constX = np.all(ssqX <= abs((np.finfo(type(X[0, 0])).eps * n * muX)) ** 2)
        constY = np.all(ssqY <= abs((np.finfo(type(Y[0, 0])).eps * n * muY)) ** 2)

        ssqX = np.sum(ssqX)

        ssqY = np.sum(ssqY)

        print("------------------")
        print("ssqX = " + str(ssqX) + ", ssqY = " + str(ssqY) + ", constX = " + str(constX) + ", constY = " + str(constY))
        print("")


        if not constX and not constY:
            normX = np.sqrt(ssqX)
            normY = np.sqrt(ssqY)

            print("------------------")
            print("normX = " + str(normX) + ", normY = " + str(normY))
            print("")

            X0 = X0 / normX
            Y0 = Y0 / normY

            A = np.matmul(X0.transpose(), Y0)
            U, S, V = np.linalg.svd(A)
            V = V.transpose()
            R = np.matmul(V, np.transpose(U))


            if np.linalg.det(R) < 0:
                V[:, -1] = -V[:,-1]
                S[-1] = -S[-1]
                R = np.matmul(V, np.transpose(U))
            traceTA = np.sum(S)
            b = traceTA * normX / normY
            d = 1 - traceTA * traceTA
            Z = normX * traceTA * np.matmul(Y0, R) + np.tile(muX, (n, 1))
            c = muX - b * np.matmul(muY, R)
            
        return Transform(c, R, b)

    def transform_pc(self, pc, T):
        (n,m) = pc.shape
        t_pc = T.scale * np.matmul(np.transpose(pc), T.rotation) + np.tile(T.translation, (m, 1))
        return np.transpose(t_pc)

    def r2q(self, R):
        c = np.trace(R) + 1
        qw= np.sqrt(c) / 2
        qx = (R[2,1] - R[1,2]) / ( 4 * qw)
        qy = (R[0,2] - R[2,0]) / ( 4 * qw)
        qz = (R[1,0] - R[0,1])/( 4 * qw)
        return (qw, qx, qy, qz)

    def save_transform(self, filepath, T):
        q = self.r2q(T.rotation)
        with open(filepath, 'w') as f:
            f.write('# translation (x, y, z), rotation (w, x, y, z), scale (s)\n')
            f.write(str(T.translation[0]) + ' ' + str(T.translation[1]) + ' ' + str(T.translation[2]) + '\n')
            f.write(str(q[0]) + ' ' + str(q[1]) + ' ' + str(q[2]) + ' ' + str(q[3]) + '\n')
            f.write(str(T.scale) + '\n')


    def load_points(self, filepath):
        return np.loadtxt(filepath)
        


    def processChunk(self, chunk):
        try:
            chunk.logManager.start(chunk.node.verboseLevel.value)
            
            if not chunk.node.output.value or not chunk.node.matterportModel or not chunk.node.matterportPointFile or not chunk.node.viconPointFile:
                chunk.logger.warning('Missing one or more inputs')
                return

            
            holo_io = HoloIO()
            meshroom_io = MeshroomIO()
            utils_math = UtilsMath()
            outfile = chunk.node.output.value + '/matterport.obj'

            matterport_pc_xyz, matterport_pc_rgb = meshroom_io.load_vertices(chunk.node.matterportModel.value)
            matterport_xyz = self.load_points(chunk.node.matterportPointFile.value)
            vicon_xyz = self.load_points(chunk.node.viconPointFile.value)

            mat_2_vic_t = self.procrustes(vicon_xyz, matterport_xyz)
            self.save_transform(chunk.node.output.value + '/matterport2vicon.txt', mat_2_vic_t)

            transformed_matterport = self.transform_pc(matterport_pc_xyz, mat_2_vic_t)
            holo_io.write_pointcloud_to_file(transformed_matterport, outfile, rgb = matterport_pc_rgb)

            chunk.logger.info('Matterport to Vicon aligner done.') 

        except AssertionError as err:
            chunk.logger.error("Error in Matterport to Vicon aligner: " + err)
        finally:
            chunk.logManager.end()
