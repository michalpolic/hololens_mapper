import os
import sys
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import renderDepth


# input data 
img_height = 5
img_width = 8
uv = np.array([[1, 4, 3],[2, 7, 2]])
d = np.array([10, 2, 1])
t = np.array([[5,2,0.5],[1,3,5]])
uv_length = np.shape(uv)[1]
t_length = np.shape(t)[1]


res = renderDepth.render(img_height, img_width, uv_length, t_length, uv.reshape(1,-1), d, t.reshape(1,-1))
print(res)