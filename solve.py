import cv2
import numpy as np
from collections import deque

def solve_maze():
    # 1. 读入迷宫图片（灰度图模式）
    # 0 代表黑（墙），255 代表白（路）
    maze = cv2.imread("maze.png", cv2.IMREAD_GRAYSCALE)
    if maze is None:
        print("错误：找不到 maze.png，请确认迷宫图片是否存在！")
        return
    
    height, width = maze.shape

    # 2. 把黑白图转换成彩色图，便于可视化显示
    maze_color = cv2.cvtColor(maze, cv2.COLOR_GRAY2BGR)

    # 3. 确定起点和终点
    # 起点开在左上角 (列x=0, 行y=1)，终点在右下角 (列x=width-1, 行y=height-2)
    start = (0, 1)
    end = (width - 1, height - 2)

    # 4. BFS
    queue = deque([start])  # 队列：用来存放像水一样向外蔓延的“水滴”位置
    visited = set()         # 集合：记录哪些地方已经流过水了，不走回头路
    visited.add(start)
    parent_map = {}         # 字典：记录“当前格子是从哪个格子走过来的”，为了最后画红线

    # 放大倍数，为了让动画足够大，能看清
    scale = 10 
    
    print("开始搜索迷宫...")

    # 5. 开始像水流一样蔓延搜索
    found = False
    while len(queue) > 0:
        current = queue.popleft() # 取出一滴水
        cx, cy = current

        # 如果这滴水到了终点，搜索结束！
        if current == end:
            found = True
            break
        
        # 为了让动画好看，走过的路涂成浅蓝色 (OpenCV 颜色是 BGR，所以是 [255, 200, 0])
        if current != start:
            maze_color[cy, cx] = (255, 200, 0) 
        
        # 求解可视化显示
        # 每走一步，就把当前画面放大并显示出来，暂停 10 毫秒
        display_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Solving Maze (BFS)", display_img)
        cv2.waitKey(10) # 暂停 10 毫秒

        # 看看上下左右四个方向哪里还可以流水
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            
            # 如果没有越界
            if 0 <= nx < width and 0 <= ny < height:
                # 如果前方的像素是白色的路(255)，并且之前没去过
                if maze[ny, nx] == 255 and (nx, ny) not in visited:
                    visited.add((nx, ny))       # 标记为去过
                    parent_map[(nx, ny)] = current # 记住是从哪来的
                    queue.append((nx, ny))      # 把新位置加入队列接着搜索

    # 6. 回溯：画出最终的最短路径
    if found:
        print("找到出口！正在绘制最终路径...")
        curr = end
        # 只要还没退回到起点，就一直往回找
        while curr != start:
            cx, cy = curr
            maze_color[cy, cx] = (0, 0, 255) # 最终路径涂成红色 (BGR: 0, 0, 255)
            curr = parent_map[curr]          # 回溯找上一步
        
        maze_color[start[1], start[0]] = (0, 0, 255) # 起点也涂红
        
        # 显示最终结果
        final_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Solving Maze (BFS)", final_img)
        print("求解完成！请按键盘任意键关闭窗口。")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("没有找到出口！")

if __name__ == "__main__":
    solve_maze()