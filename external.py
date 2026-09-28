import cv2
import numpy as np

# 导入我们的寻路模块
import solve 

points = []
display_img = None
clean_img = None
thresh_img = None

def click_event(event, x, y, flags, param):
    global points, display_img, clean_img
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 2:
            points.append((x, y))
    elif event == cv2.EVENT_RBUTTONDOWN:
        if len(points) > 0:
            points.pop()
            
    if event in [cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN]:
        display_img = clean_img.copy() 
        for i, p in enumerate(points):
            color = (0, 255, 0) if i == 0 else (0, 0, 255)
            cv2.circle(display_img, p, 6, color, -1)
            text = "START" if i == 0 else "END"
            cv2.putText(display_img, text, (p[0]+10, p[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.imshow("External Maze Preprocessor", display_img)

# 增加了一个 algo 参数，供我们在外部随便换算法
def solve_external_maze(image_path, algo="ASTAR"):
    global points, display_img, clean_img, thresh_img
    
    points = []
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ 找不到图片 {image_path}，请检查路径！")
        return
        
    h, w = img.shape[:2]
    
    # 智能预处理与裁边
    if w < 150 or h < 150:
        img = cv2.resize(img, (w * 15, h * 15), interpolation=cv2.INTER_NEAREST)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh_img = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    else:
        max_size = 800
        if w > max_size or h > max_size:
            scale = max_size / max(w, h)
            img = cv2.resize(img, (0, 0), fx=scale, fy=scale)
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh_img = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        kernel = np.ones((3, 3), np.uint8)
        thresh_img = cv2.erode(thresh_img, kernel, iterations=1)
        
        walls_only = cv2.bitwise_not(thresh_img)
        coords = cv2.findNonZero(walls_only)
        if coords is not None:
            bx, by, bw, bh = cv2.boundingRect(coords)
            mask = np.zeros_like(thresh_img)
            mask[by:by+bh, bx:bx+bw] = 255
            thresh_img = cv2.bitwise_and(thresh_img, mask)
    
    clean_img = cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR)
    display_img = clean_img.copy()
    
    print("\n====== 操作说明 ======")
    print(f"当前准备使用的算法为：【{algo}】")
    print("1. 请用【鼠标左键】点击选择起点和终点。")
    print("2. 如果手滑点错了，请按【鼠标右键】撤销！")
    print("3. 选完两个点后，按键盘【任意键】将图像交给底层引擎求解！")
    
    cv2.namedWindow("External Maze Preprocessor", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("External Maze Preprocessor", display_img)
    cv2.setMouseCallback("External Maze Preprocessor", click_event)
    
    cv2.waitKey(0)
    
    if len(points) < 2:
        print("⚠️ 未选择足够的起点和终点，已退出。")
        return
        
    start, end = points[0], points[1]
    
    # 关闭预处理窗口
    cv2.destroyAllWindows()
    print(f"\n🚀 正在调用底层 solve.py 引擎使用 {algo} 算法求解，请看新弹出的窗口...")
    
    # 核心调用
    solve.solve_maze_algo(
        maze_input=thresh_img, 
        algo=algo, 
        show_animation=True, 
        start_pos=start, 
        end_pos=end
    )


if __name__ == "__main__":
    # 切换算法(例如 "BFS", "DFS", "ASTAR")
    solve_external_maze("extest.png", algo="BFS")
