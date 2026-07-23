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
            # 点击的圆圈稍微画小一点
            cv2.circle(param, (x, y), 3, color, -1)
            cv2.imshow("External Maze", param)

def solve_external_maze(image_path):
    global points
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"找不到图片 {image_path}！")
        return
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. 严格二值化 (稍微降低门槛，让更多灰色变成纯黑，加固墙壁)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    
    # ==========================================
    # 【核心修复】形态学腐蚀 (Erosion)：修补墙壁漏洞
    # ==========================================
    # 定义一个 3x3 像素的正方形“泥瓦匠工具”
    kernel = np.ones((3, 3), np.uint8)
    # 对白色的路面进行腐蚀，相当于给黑墙涂上一层水泥，强行加厚！
    thresh = cv2.erode(thresh, kernel, iterations=1)
    
    # 转换回彩色，用于显示
    display_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    
    print("====== 操作说明 ======")
    print("1. 请用鼠标左键点击选择【起点】（尽量点在白色路面正中间哦！）")
    print("2. 再次点击左键选择【终点】")
    print("3. 按键盘【任意键】开始求解！")
    
    cv2.namedWindow("External Maze", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("External Maze", 800, 800) 
    
    cv2.imshow("External Maze", display_img)
    cv2.setMouseCallback("External Maze", click_event, display_img)
    
    cv2.waitKey(0)
    
    if len(points) < 2:
        return
        
    start, end = points[0], points[1]
    
    queue = deque([start])
    visited = {start}
    parent_map = {}
    height, width = thresh.shape
    found = False
    step = 0
    
    while queue:
        current = queue.popleft()
        cx, cy = current
        
        if current == end:
            found = True
            break
            
        step += 1
        if current != start:
            display_img[cy, cx] = (255, 200, 0)
            
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
            # 【修复 2】不画粗圆圈了，只把当前这 1 个像素涂红！防止视觉“溢出穿墙”
            display_img[cy, cx] = (0, 0, 255)
            curr = parent_map[curr]
            
        cv2.imshow("External Maze", display_img)
        print("大功告成！没有任何漏水和穿墙！按任意键退出。")
        cv2.waitKey(0)
    else:
        print("找不到路！可能是起点/终点点到了加厚后的黑墙上了。")
        
    cv2.destroyAllWindows()

if __name__ == "__main__":
    solve_external_maze("test1.png")