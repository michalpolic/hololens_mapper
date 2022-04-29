import sys
import os
import poselib
import numpy as np

# input
corresp_path = sys.argv[1]
query_poses_path = sys.argv[2]
q_2d3d_cp = np.load(corresp_path, allow_pickle=True).flat[0]

# read query poses 
qposes = {}
with open(query_poses_path,'r') as qposes_file:
    lines = qposes_file.read().split('\n')
    for line in lines:
        qdata = line.split(' ')
        qposes[qdata[0]] = {'q': list(map(float, qdata[1:5])), \
            't': list(map(float, qdata[5:]))}

p2ds = []
p3ds = []
camera_ext = []
cameras = []
ransac_opt = {'max_reproj_error': 10.0}
bundle_opt = {}
for qname in q_2d3d_cp:
    corresp = q_2d3d_cp[qname]
    p2ds.append(corresp['mkpq'])
    p3ds.append(corresp['mp3d'])
    cameras.append(corresp['result']['cfg'])

    camera_pose = poselib.CameraPose()
    camera_pose.q = np.array(qposes[qname]['q']).astype(dtype=np.float64).reshape(4,1)
    camera_pose.t = np.array(qposes[qname]['t']).astype(dtype=np.float64).reshape(3,1)
    camera_ext.append(camera_pose)

pose, info = poselib.estimate_generalized_absolute_pose(p2ds, p3ds, camera_ext, cameras, ransac_opt, bundle_opt)
num_inliers = info['num_inliers']
inlier_ratio = info['inlier_ratio']
print(f'Generalized absolute pose: num_inliers: {num_inliers}, inlier_ratio: {inlier_ratio}')

# save results
results_path = os.path.join(os.path.dirname(corresp_path),'generalized_absolute_pose.txt')
with open(results_path,'w') as results_file:
    results_file.write(' '.join(map(str,pose.q)) + ' ' + ' '.join(map(str,pose.t)))
