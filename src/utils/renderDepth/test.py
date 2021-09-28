import renderDepth
import numpy as np

# input data 
img_height = 5
img_width = 8
uv = np.array([[1, 4, 3],[2, 7, 2]])
d = np.array([10, 2, 1])
t = np.array([[5,2,0.5],[1,3,5]])
uv_length = np.shape(uv)[1]
t_length = np.shape(t)[1]


res = renderDepth.render(img_height, img_width, uv_length, t_length, uv.reshape(1,-1), d, t.reshape(1,-1))
print(res.reshape(img_height, img_width))