import cv2
import numpy as np

# 1. 创建一张 500x500 的纯黑色图片 (0代表黑，255代表白)
# 在 Numpy 中，图片其实就是一个二维数组
maze_image = np.zeros((500, 500), dtype=np.uint8)

# 2. 我们在中间画一个白色的正方形，模拟迷宫的一条“路”
# 把纵坐标 200到300，横坐标 200到300 的区域变成白色 (255)
maze_image[200:300, 200:300] = 255

# 3. 显示这张图片
cv2.imshow("My First Image", maze_image)

# 4. 等待用户按键盘上的任意键，然后关闭窗口
cv2.waitKey(0)
cv2.destroyAllWindows()