import cv2

# frame = cv2.imread("form2.jpg")
frame = cv2.imread("./image/test.png")
# gray画像を作成
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# 二極化
ret2, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print(th.shape)
cv2.imwrite("min_conr.jpg", th)

cimg = th

# contours, hierarchy = cv2.findContours(cimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours, hierarchy = cv2.findContours(cimg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
print(len(contours))

pointList = []
for i, cnt in enumerate(contours):
    # 輪郭の面積を計算する。
    area = cv2.contourArea(cnt)
    # 　抽出する範囲を指定
    if area > 1 and area < 1000:
        # 最小外接円を計算する
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 3)
        pointList.append([x, y])

print(len(pointList))
cv2.imshow("frame", frame)
cv2.imwrite("min_contour.jpg", frame)

# キー入力を待つ
cv2.waitKey(0)
# 全ての開いたウインドウ閉じる
cv2.destroyAllWindows()
