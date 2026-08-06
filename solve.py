import cv2
import numpy as np
from collections import deque
import heapq
import time

# ========================================================
# 终极引擎：支持三种算法的高内聚寻路器
# ========================================================
def solve_maze_algo(maze_input, algo="BFS", show_animation=False, callback=None, start_pos=None, end_pos=None):
    if isinstance(maze_input, str):
        maze = cv2.imread(maze_input, cv2.IMREAD_GRAYSCALE)
        if maze is None:
            print(f"错误：找不到 {maze_input}！")
            return None
    else:
        maze = maze_input

    height, width = maze.shape
    maze_color = cv2.cvtColor(maze, cv2.COLOR_GRAY2BGR)
    
    start = start_pos if start_pos else (0, 1)
    end = end_pos if end_pos else (width - 1, height - 2)
    
    parent_map = {}; found = False
    
    # ==========================================
    # 【核心修复】智能动态缩放，防止大图撑爆屏幕！
    # ==========================================
    max_dim = max(width, height)
    if max_dim <= 100:
        scale = 10  # 微型迷宫放大 10 倍
    elif max_dim <= 400:
        scale = 2   # 中型迷宫放大 2 倍
    else:
        scale = 1   # 外部大图片保持 1:1 原尺寸，绝不放大！
        
    if algo == "BFS": 
        struct = deque([start])
    elif algo == "DFS": 
        struct = [start]
    elif algo == "ASTAR":
        def heuristic(p1, p2): return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])
        struct = []
        heapq.heappush(struct, (heuristic(start, end), 0, start))
        g_scores = {start: 0}
        
    visited = set([start])
    step = 0

    while len(struct) > 0:
        if algo == "BFS": current = struct.popleft()
        elif algo == "DFS": current = struct.pop()
        elif algo == "ASTAR": _, current_g, current = heapq.heappop(struct)
        
        cx, cy = current
        if current == end: found = True; break
        if current != start: maze_color[cy, cx] = (255, 200, 0) 
        
        step += 1
        if callback and step % 15 == 0: 
            callback(maze_color.copy()); time.sleep(0.01)
        elif show_animation and not callback and step % 15 == 0:
            display_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
            cv2.imshow(f"Solving Maze ({algo})", display_img)
            # 稍微调快了一点动画刷新速度
            cv2.waitKey(1)

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny, nx] == 255:
                if algo in ["BFS", "DFS"] and (nx, ny) not in visited:
                    visited.add((nx, ny))       
                    parent_map[(nx, ny)] = current 
                    struct.append((nx, ny))      
                elif algo == "ASTAR":
                    new_g = current_g + 1
                    if (nx, ny) not in g_scores or new_g < g_scores[(nx, ny)]:
                        g_scores[(nx, ny)] = new_g 
                        parent_map[(nx, ny)] = current
                        f_score = new_g + heuristic((nx, ny), end)
                        heapq.heappush(struct, (f_score, new_g, (nx, ny)))

    if found:
        curr = end
        while curr != start:
            cx, cy = curr
            maze_color[cy, cx] = (0, 0, 255) 
            
            # 【视觉优化】如果原图很大没被放大过，我们把红线加粗一点，方便你一眼看清
            if scale == 1:
                cv2.circle(maze_color, (cx, cy), 1, (0, 0, 255), -1)
                
            curr = parent_map[curr]          
            if callback: callback(maze_color.copy()); time.sleep(0.01)
            
        maze_color[start[1], start[0]] = (0, 0, 255) 
        if callback: callback(maze_color.copy())
        
        if show_animation and not callback:
            final_img = cv2.resize(maze_color, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)
            cv2.imshow(f"Solving Maze ({algo})", final_img)
            print(f"✅ {algo} 求解完成！请按键盘【任意键】关闭窗口。")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
    return maze_color

if __name__ == "__main__":
    print("====== 算法寻路大比拼开始！======")
    solve_maze_algo("mazeprim.png", algo="BFS", show_animation=True)
    solve_maze_algo("mazeprim.png", algo="DFS", show_animation=True)
    solve_maze_algo("mazeprim.png", algo="ASTAR", show_animation=True)
    print("\n🏆 所有算法求解完成！")