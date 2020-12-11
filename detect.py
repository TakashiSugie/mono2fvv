import cv2


def detectPoint(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 二極化
    ret2, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cimg = th
    contours, hierarchy = cv2.findContours(cimg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    pointList = []
    for i, cnt in enumerate(contours):
        # 輪郭の面積を計算する。
        area = cv2.contourArea(cnt)
        # 　抽出する範囲を指定
        if area > 5 and area < 1000:
            # 最小外接円を計算する
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 1)
            pointList.append([int(x), int(y)])

    cv2.imwrite("./img/min_contour.jpg", frame)
    return pointList


if __name__ == "__main__":
    frame = cv2.imread("./img/test.png")
    pointList = detectPoint(frame)
    print(len(pointList))
