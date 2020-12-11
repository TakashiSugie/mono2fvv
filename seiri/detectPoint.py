import cv2
import numpy as np


def main():
    img = cv2.imread("image/field_resize.png")
    dst = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    flagMap = np.where(dst < 30, 1, 0)
    flagList = np.where(dst < 30)
    print(len(flagList[0]))
    checkFlagMap(flagMap)


def checkFlagMap(flagMap):
    # print(flagMap)
    kernel = np.array([[0.0, 0.5, 0.0], [0.5, 1.0, 0.5], [0.0, 0.5, 0.0]])
    print(kernel)
    convolved = np.convolve(flagMap, kernel,)
    print(convolved.shape)
    cv2.imwrite("./image/flagMap.png", flagMap * 255)
    for x in range(flagMap.shape[0]):
        for y in range(flagMap.shape[1]):
            if flagMap[x][y]:
                pass


if __name__ == "__main__":
    main()
