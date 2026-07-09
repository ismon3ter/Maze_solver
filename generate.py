import cv2
import numpy as np
import random
import sys

# 增加递归深度，防止迷宫太大时报错
sys.setrecursionlimit(10000)

def generate_maze(width, height, show_animation=False):
    # 1. 准备一块“实心土地”
    # 迷宫的结构是：墙-路-墙-路-墙，所以实际像素尺寸是 (宽*2+1) x (高*2+1)
    # dtype=np.uint8 是图片标准格式。0 代表墙（黑），255 代表路（白）
    shape = (height * 2 + 1, width * 2 + 1)
    maze = np.zeros(shape, dtype=np.uint8)

    scale = 10

    # 2. DFS
    def dfs_generate_from(cx, cy):
        # 把当前站的地方变成白色的路 (255)
        # cx，cy 是当前格子的逻辑坐标，需要乘以 2 再加 1来得到像素坐标
        # 例如：墙0 - 路1 - 墙2 - 路3 - 墙4
        # 路1对应的数组逻辑坐标是0，实际像素坐标是(0*2+1)=1
        maze[cy * 2 + 1, cx * 2 + 1] = 255

        #（由show_animation可选）可视化生成迷宫
        if show_animation:
            # 放大当前正在生成的迷宫，显示出来
            display_img = cv2.resize(maze, (shape[1] * scale, shape[0] * scale), interpolation=cv2.INTER_NEAREST)
            cv2.imshow("Generating Maze (DFS)...", display_img)
            cv2.waitKey(10) # 停顿 10 毫秒
        
        # 上、下、左、右四个方向数组
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        # 随机生成方向
        random.shuffle(directions)

        # 尝试向四个方向挖
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            # 判断条件：如果没有越界，并且那个方向的前方是一堵没挖过的墙 (0)
            if 0 <= nx < width and 0 <= ny < height and maze[ny * 2 + 1, nx * 2 + 1] == 0:
                # 打通两点之间的那堵墙
                maze[cy * 2 + 1 + dy, cx * 2 + 1 + dx] = 255

                #（由show_animation可选）可视化生成迷宫
                if show_animation:
                    display_img = cv2.resize(maze, (shape[1] * scale, shape[0] * scale), interpolation=cv2.INTER_NEAREST)
                    cv2.imshow("Generating Maze (DFS)...", display_img)
                    cv2.waitKey(10)
                
                # 递归调用
                dfs_generate_from(nx, ny)

    # 3. 从左上角的格子 (0, 0) 开始挖
    dfs_generate_from(0, 0)
    
    # 4. 手动开一个入口和出口
    maze[1, 0] = 255      # 左上角外墙开洞
    maze[-2, -1] = 255    # 右下角外墙开洞

    if show_animation:
        cv2.destroyWindow("Generating Maze (DFS)...")

    return maze

if __name__ == "__main__":
    # 生成一个 20x20 格子的迷宫（实际对应 41x41 的像素图片）
    maze_img = generate_maze(20, 20, show_animation=True)

    # cv2.INTER_NEAREST (最近邻插值) 等比例放大图片
    maze_img_large = cv2.resize(maze_img, (410, 410), interpolation=cv2.INTER_NEAREST)

    # 显示迷宫
    cv2.imshow("Generated Maze", maze_img_large)

    # 保存迷宫
    cv2.imwrite("maze.png", maze_img) 
    
    print("迷宫已生成！并且保存为 maze.png")
    cv2.waitKey(0)
    cv2.destroyAllWindows()