import cv2
import numpy as np
from collections import deque
import heapq  # A* 算法必须要用的“优先队列”工具

# ========================================================
# 算法 1：BFS 广度优先搜索
# ========================================================
def solve_mazeBFS():
    maze = cv2.imread("mazeprim.png", cv2.IMREAD_GRAYSCALE)
    if maze is None:
        print("错误：找不到 mazeprim.png！")
        return
    height, width = maze.shape
    maze_color = cv2.cvtColor(maze, cv2.COLOR_GRAY2BGR)
    start = (0, 1); end = (width - 1, height - 2)

    # BFS 的核心：队列 (先进先出)
    queue = deque([start])  
    visited = set([start])         
    parent_map = {}         
    scale = 10 
    
    print("\n▶ 开始演示 BFS 广度优先搜索...")
    found = False
    while len(queue) > 0:
        current = queue.popleft() # 【关键点】从左边拿，保证水波均匀扩散
        cx, cy = current

        if current == end:
            found = True; break
        
        if current != start: maze_color[cy, cx] = (255, 200, 0) 
        
        display_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Solving Maze (BFS)", display_img)
        cv2.waitKey(10)

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny, nx] == 255 and (nx, ny) not in visited:
                visited.add((nx, ny))       
                parent_map[(nx, ny)] = current 
                queue.append((nx, ny))      # 【关键点】加到右边

    if found:
        curr = end
        while curr != start:
            cx, cy = curr
            maze_color[cy, cx] = (0, 0, 255) 
            curr = parent_map[curr]          
        maze_color[start[1], start[0]] = (0, 0, 255) 
        
        final_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Solving Maze (BFS)", final_img)
        print("✅ BFS 求解完成！请按键盘【任意键】继续看下一个算法。")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# ========================================================
# 算法 2：DFS 深度优先搜索
# ========================================================
def solve_mazeDFS():
    maze = cv2.imread("mazeprim.png", cv2.IMREAD_GRAYSCALE)
    height, width = maze.shape
    maze_color = cv2.cvtColor(maze, cv2.COLOR_GRAY2BGR)
    start = (0, 1); end = (width - 1, height - 2)

    # DFS 的核心：栈 (后进先出)。其实就是个普通的 Python 列表
    stack = [start]  
    visited = set([start])         
    parent_map = {}         
    scale = 10 
    
    print("\n▶ 开始演示 DFS 深度优先搜索 (不撞南墙不回头)...")
    found = False
    while len(stack) > 0:
        current = stack.pop() # 【核心区别】从右边拿最新加进来的，一条路走到黑！
        cx, cy = current

        if current == end:
            found = True; break
        
        if current != start: maze_color[cy, cx] = (255, 200, 0) 
        
        display_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Solving Maze (DFS)", display_img)
        cv2.waitKey(10)

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny, nx] == 255 and (nx, ny) not in visited:
                visited.add((nx, ny))       
                parent_map[(nx, ny)] = current 
                stack.append((nx, ny))      # 【核心区别】新方向直接压入栈顶，下一步马上就走它

    if found:
        curr = end
        while curr != start:
            cx, cy = curr
            maze_color[cy, cx] = (0, 0, 255) 
            curr = parent_map[curr]          
        maze_color[start[1], start[0]] = (0, 0, 255) 
        
        final_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Solving Maze (DFS)", final_img)
        print("✅ DFS 求解完成！请按键盘【任意键】继续看下一个算法。")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# ========================================================
# 算法 3：A* 启发式搜索
# ========================================================
def solve_mazeASTAR():
    maze = cv2.imread("mazeprim.png", cv2.IMREAD_GRAYSCALE)
    height, width = maze.shape
    maze_color = cv2.cvtColor(maze, cv2.COLOR_GRAY2BGR)
    start = (0, 1); end = (width - 1, height - 2)

    # A* 专属雷达：曼哈顿距离（预估当前点到终点还要走多远）
    def heuristic(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    # A* 的核心：优先队列 (谁的综合代价小，谁优先)
    pq = [] 
    # 数据格式：(综合代价, 已经走的步数, 坐标)
    heapq.heappush(pq, (heuristic(start, end), 0, start))
    
    g_scores = {start: 0} # 字典：记录从起点走到各个格子，实际花的最少步数
    parent_map = {}         
    scale = 10 
    
    print("\n▶ 开始演示 A* 启发式搜索...")
    found = False
    while len(pq) > 0:
        # 【核心区别】不管谁先加进来，永远挑“看起来最靠近终点”的那个格子走！
        priority, current_g, current = heapq.heappop(pq)
        cx, cy = current

        if current == end:
            found = True; break
        
        if current != start: maze_color[cy, cx] = (255, 200, 0) 
        
        display_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Solving Maze (A-Star)", display_img)
        cv2.waitKey(10)

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny, nx] == 255:
                neighbor = (nx, ny)
                new_g = current_g + 1 # 走到邻居的实际步数 = 当前步数 + 1
                
                # 如果这个邻居之前没来过，或者这次找了一条更短的路过来
                if neighbor not in g_scores or new_g < g_scores[neighbor]:
                    g_scores[neighbor] = new_g # 刷新它的最短步数记录
                    parent_map[neighbor] = current
                    
                    # 综合代价 (F) = 实际步数 (G) + 雷达预估距离 (H)
                    f_score = new_g + heuristic(neighbor, end)
                    heapq.heappush(pq, (f_score, new_g, neighbor)) # 带着优先级排队去

    if found:
        curr = end
        while curr != start:
            cx, cy = curr
            maze_color[cy, cx] = (0, 0, 255) 
            curr = parent_map[curr]          
        maze_color[start[1], start[0]] = (0, 0, 255) 
        
        final_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Solving Maze (A-Star)", final_img)
        print("✅ A* 求解完成！")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# ========================================================
# 比赛指挥部
# ========================================================
if __name__ == "__main__":
    print("当前求解迷宫：mazeprim.png")
    
    solve_mazeBFS()
    solve_mazeDFS()
    solve_mazeASTAR()
    
    print("\n🏆 所有算法求解完成！")