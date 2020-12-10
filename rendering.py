#!env python

# レンダリング三枚の縮尺を揃える（max minを共有すれば行けそう）
# 実際にW座標系で統合を行う（両方の点群を足し合わせるだけで良い）


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import cv2

# from evaluation import checkMaxMin
# from setVerts import setVertsFromPly, cvtVerts
from verts import setVerts

# from libs.variable import saveName, imgName1, imgName2, renderingMode, renderingPly
# from libs import capture

LeftButtonOn = False
RightButtonOn = False
Angle1 = 0
Angle2 = 0
Distance = 1.0
px, py = -1, -1
windowSize = 1023
angleRange = 5.0

# if renderingMode == 1:
#     plyName = imgName1
# elif renderingMode == 2:
#     plyName = imgName2
# elif renderingMode == 3:
#     plyName = saveName
# elif renderingMode == 4:
#     plyName = saveName + "_integrated"
# mesh_fi = "./mesh/" + plyName + ".ply"
plyName = "moon"
plyName = "IMG_4653"
plyName = "tower2"
mesh_fi = "./mesh/%s.ply" % plyName
# print(mesh_fi, renderingMode)
# print(renderingPly[renderingMode])


def capture():
    if not os.path.isdir("./capture/%s" % plyName):
        os.makedirs("./capture/%s" % plyName)
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    # キャプチャ
    print(height)
    glReadBuffer(GL_FRONT)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_BGRA, GL_UNSIGNED_BYTE, None)

    image = np.frombuffer(data, dtype=np.uint8).reshape(width, height, 4)
    # capturePath = mesh_fi.replace("ply", "png")
    cv2.imwrite(
        "./capture/%s/%s_%.1f_%.1f_%d.png"
        % (plyName, plyName, Angle1, Angle2, Distance),
        np.flipud(image),
    )
    print("capture now...")


def mouse(button, state, x, y):
    global LeftButtonOn, RightButtonOn
    if button == GLUT_LEFT_BUTTON:
        if state == 1:
            LeftButtonOn = False
        elif state == 0:
            LeftButtonOn = True

    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_UP:
            RightButtonOn = False
        elif state == GLUT_DOWN:
            RightButtonOn = True


def motion(x, y):
    global RightButtonOn, LeftButtonOn, Angle1, Angle2, Distance, px, py
    if LeftButtonOn == True and RightButtonOn == True:
        Angle1 = 0
        Angle2 = 0
        Distance = 1.0
        gluLookAt(0, 0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    elif LeftButtonOn == True:
        if py >= 0 and px >= 0:
            Angle1 += float(-(y - py) / 50)
            Angle2 += float((x - px) / 50)
        px = x
        py = y
    elif RightButtonOn == True:
        if px >= 0 and py >= 0:
            Distance += float(y - py) / 200
        px = x
        py = y
    else:
        px = -1
        py = -1

    glutPostRedisplay()


def keyboard(key, x, y):
    global Angle2, Angle1, Distance
    if key.decode() == "\033":  # Escape
        sys.exit()
    elif key.decode() == "q":
        sys.exit()
    elif key.decode() == "d":
        Angle2 += 1.0
        glutPostRedisplay()
    elif key.decode() == "a":
        Angle2 -= 1.0
        glutPostRedisplay()
    elif key.decode() == "w":
        Angle1 += 1.0
        glutPostRedisplay()

    elif key.decode() == "s":
        Angle1 -= 1.0
        glutPostRedisplay()
    elif key.decode() == "-":
        Distance += 0.1
        glutPostRedisplay()

    elif key.decode() == "+":
        Distance -= 0.1
        glutPostRedisplay()

    elif key.decode() == "c":
        capture()
    else:
        print(key.decode())


buffers = 0


def create_vbo():
    buffers = glGenBuffers(2)  # バッファを作成３つ？２つで行けそうだけど
    glBindBuffer(
        GL_ARRAY_BUFFER, buffers[0]
    )  # GLコンテキストにvertex_vboをGL_ARRAY_BUFFERでバインド。
    glBufferData(  # 実データを格納
        GL_ARRAY_BUFFER,
        len(vertices) * 4,  # byte size
        (ctypes.c_float * len(vertices))(*vertices),  # 謎のctypes
        GL_STATIC_DRAW,
    )
    glBindBuffer(GL_ARRAY_BUFFER, buffers[1])
    glBufferData(
        GL_ARRAY_BUFFER,
        len(colors) * 4,  # byte size
        (ctypes.c_float * len(colors))(*colors),  # 謎のctypes
        GL_STATIC_DRAW,
    )
    return buffers


def draw_vbo():
    glEnableClientState(GL_VERTEX_ARRAY)  # GL_VERTEX_ARRAY配列を有効化する
    glEnableClientState(GL_COLOR_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, buffers[0])
    glVertexPointer(3, GL_FLOAT, 0, None)
    # 頂点配列を定義　buffers[0]という名称のバッファオブジェクトの内容を変更している、もちろん名称は変わっていない
    # size type stride pointer sizeはvx,vy,vzなら3 typeはfloatとか stride1 ならvx,vy vz,wからwを消したやつとかで計算可能0は隙間なし

    glBindBuffer(GL_ARRAY_BUFFER, buffers[1])
    # glColorPointer(3, GL_FLOAT, 0, None)
    glColorPointer(4, GL_FLOAT, 0, None)  # これで不透明度変化

    glPointSize(3)
    glDrawArrays(GL_POINTS, 0, len(vertices))
    glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)


def draw_cube2():
    global buffers
    if isinstance(buffers, int):
        buffers = create_vbo()  # bufferに頂点情報と色情報を格納
    draw_vbo()


def draw():
    global Angle1, Angle2

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, Distance, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0)
    glRotatef(Angle1, 0, 1, 0)
    glRotatef(Angle2, 1, 0, 0)
    draw_cube2()
    glFlush()
    glutSwapBuffers()


def initialize():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)


def GLresize(Width, Height):
    # viewport
    if Height == 0:
        Height = 1
    glViewport(0, 0, Width, Height)
    # projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width) / float(Height), 0.1, 100.0)


def reshape_func(w, h):
    GLresize(w, h == 0 and 1 or h)


def disp_func():
    draw()
    glutSwapBuffers()


colors, vertices = setVerts(mesh_fi)
print("verts loaded")
glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(windowSize, windowSize)
# glutCreateWindow(renderingPly[renderingMode])
glutCreateWindow(plyName)
glutDisplayFunc(disp_func)
glutIdleFunc(disp_func)
glutReshapeFunc(reshape_func)
initialize()

glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glutMainLoop()
