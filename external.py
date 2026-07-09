import cv2
import numpy as np
from collections import deque

points = []

def click_event(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 2:
            points.append((x, y))
            color = (0, 255, 0) if len(points) == 1 else (0, 0, 255)
            # 因为不再缩放图片，原图可能很大，所以我们把鼠标标记画大一点（半径10）
            cv2.circle(param, (x, y), 10, color, -1)
            cv2.imshow("External Maze", param)

def solve_external_maze(image_path):
    global points
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"找不到图片 {image_path}！")
        return
        
    # 【修复重点 1】不再破坏性缩放原图，直接处理原始像素
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 【修复重点 2】提高阈值到 200（大于200才算白色的路，小于200统统变成黑色的墙），防止抗锯齿导致的穿墙
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    display_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    
    print("====== 操作说明 ======")
    print("1. 请在弹出的窗口中，用鼠标左键点击选择【起点】")
    print("2. 再次点击左键选择【终点】")
    print("3. 选完两个点后，在窗口上按键盘【任意键】开始求解！")
    
    # 【修复重点 3】创建一个可以被鼠标自由拉伸的窗口（WINDOW_NORMAL），用来适配屏幕大小
    cv2.namedWindow("External Maze", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("External Maze", 800, 800) # 窗口初始大小设置为 800x800
    
    cv2.imshow("External Maze", display_img)
    cv2.setMouseCallback("External Maze", click_event, display_img)
    
    cv2.waitKey(0)
    
    if len(points) < 2:
        print("你还没选够两个点呢，退出。")
        return
        
    start, end = points[0], points[1]
    
    queue = deque([start])
    visited = {start}
    parent_map = {}
    height, width = thresh.shape
    found = False
    step = 0
    
    print("正在像水流一样寻找出口，请稍候...")
    
    while queue:
        current = queue.popleft()
        cx, cy = current
        
        if current == end:
            found = True
            break
            
        step += 1
        if current != start:
            display_img[cy, cx] = (255, 200, 0)
            
        # 原图现在像素很多，为了不卡顿，我们每探索 5000 个像素才刷新一次动画
        if step % 5000 == 0: 
            cv2.imshow("External Maze", display_img)
            cv2.waitKey(1)
            
        for dx, dy in [(0,-1), (0,1), (-1,0), (1,0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if thresh[ny, nx] == 255 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent_map[(nx, ny)] = current
                    queue.append((nx, ny))
                    
    if found:
        print("找到出口！正在绘制最终路径...")
        curr = end
        while curr != start:
            cx, cy = curr
            # 把红线画粗一点 (半径3)
            cv2.circle(display_img, (cx, cy), 3, (0, 0, 255), -1)
            curr = parent_map[curr]
            
        cv2.imshow("External Maze", display_img)
        print("大功告成！按任意键退出。")
        cv2.waitKey(0)
    else:
        print("找不到路！可能是起点/终点点到黑色的墙上了，或者这是一个没有出口的死迷宫。")
        
    cv2.destroyAllWindows()

if __name__ == "__main__":
    solve_external_maze("test.png")