import numpy as np

DepthNpy = np.load("im0.npy")
print(DepthNpy.shape)
print(np.max(DepthNpy), np.min(DepthNpy))
# print
# まさかの負の数
