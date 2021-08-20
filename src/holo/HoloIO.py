import sys
import numpy as np
import math
import os
from pathlib import Path

class HoloIO:

    def read_uv(self, uvdata_path):
        uvfile = open(uvdata_path, 'r')
        uvdata = uvfile.read()
        uvlines = uvdata.split("\n")
        uvdata = {}

        for line in uvlines:
            if not "inf, inf" in line:
                parsed = line.split(" ")
                uvdata[parsed[1] + parsed[2]] = (float(parsed[4].split(",")[0]), float(parsed[5]))
        
        return uvdata


    def read_csv(self, csvfilepath):
        csvfile = open(csvfilepath, 'r')
        csvheader = csvfile.readline()
        csvdata = csvfile.read()
        csvfile.close()

        parsedcsvdata = csvdata.split("\n")
        parsedcsvdata = [x for x in parsedcsvdata if x]
        camerainfo = {}
        for csvline in parsedcsvdata:
            splitted = csvline.split(",")
            name = splitted[1].split("\\")[-1].split(".")[0]
            camerainfo[name] = csvline

        return camerainfo


    def parse_poseinfo_to_cameras(self, poseinfo):
        cameras = {}
        view_id = 0
        for k, line in poseinfo.items():
            vals = line.split(",")
            D2C = np.matrix([float(num_str) for num_str in vals[25:41]]).reshape((4, 4)).T
            D2O = np.matrix([float(num_str) for num_str in vals[9:25]]).reshape((4, 4)).T
            O2D = np.linalg.inv(D2O)
            Rt = np.matrix([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) * D2C * O2D
            R = Rt[0:3, 0:3]
            C = - R.T * Rt[0:3, 3]
            cameras[k] = {
                "id": view_id,
                "timestamp": vals[0],
                "file_path": vals[1].replace(".ppm", ".jpg"),
                "D2C": D2C,
                "O2D": O2D,
                "C2D": np.linalg.inv(D2C),
                "D2O": D2O,
                "R": R,
                "C": C,
                "t": Rt[0:3, 3],
                "Rt": Rt
            }
            view_id += 1

        return cameras

    def read_depthmap(self, depthmap_path, uvdata):   
        if ".pgm" in depthmap_path:
            print('Reading depthmap: ' + depthmap_path)
            file = open(depthmap_path, 'rb')
 
            line = file.readline()
            while(not b'65535' in line):
                line = file.readline()

            data = file.read()

            values = np.frombuffer(data, np.short)
            values = np.reshape(values, (450, -1))

            xyz1 = []
            for i in range(0, 450):
                for j in range(0, 448):
                    r = values[i, j]
                    if not r == 0:
                        uv = uvdata["(" + str(j) + "," + str(i) + ")"]
                        d = r / (math.sqrt(uv[0] * uv[0] + uv[1] * uv[1] + 1) * -1000)
                        xyz1.append(d * uv[0])
                        xyz1.append(d * uv[1])
                        xyz1.append(d) 
                        xyz1.append(1)

            return xyz1


    def transform_depthmap_to_world(self, xyz1, poseinfo):
        pi = poseinfo.split(",")
        frametoorigin = np.matrix([float(num_str) for num_str in pi[9:25]]).reshape((4, 4))
        cameraviewtransform = np.matrix([float(num_str) for num_str in pi[25:41]]).reshape((4, 4))
        C2W = frametoorigin.T * np.linalg.inv(cameraviewtransform.T)
        return C2W * xyz1


    def read_dense_pointcloud(self, depthmaps_dir, uvdata_path, depthmap_poses_path):
        if not depthmaps_dir[-1] == '/':
            depthmaps_dir = depthmaps_dir + '/'
        
        uvdata = self.read_uv(uvdata_path)
        csv = self.read_csv(depthmap_poses_path)

        wold_xyz = np.array([]).reshape(3,0)
        for r, d, f in os.walk(depthmaps_dir):
            for filename in f:
                timestamp = filename.split(".")[0]
                xyz1 = self.read_depthmap(depthmaps_dir + filename, uvdata)
                xyz1 = np.matrix(np.reshape(xyz1, (-1, 4)).T)
                xyz1 = np.array(self.transform_depthmap_to_world(xyz1, csv[timestamp]))
                wold_xyz = np.concatenate((wold_xyz, xyz1[0:3,::]), axis=1)

        return wold_xyz

    def write_pointcloud_to_file(self, xyz, file_path):
        print('Save dense pointcloud.')
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        objfile = open(file_path, 'w')
        objfile.write("o Object.1\n")
        for i in range(0, np.shape(xyz)[1]):
            objfile.write(f"v {xyz[0,i]} {xyz[1,i]} {xyz[2,i]} \n")
        objfile.close()

    def read_cameras(self, csv_file_path):
        print('Reading holo camera poses.')
        csv = self.read_csv(csv_file_path)
        return self.parse_poseinfo_to_cameras(csv)