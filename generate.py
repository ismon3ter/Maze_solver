import cv2
import numpy as np
import random
import sys
import time

sys.setrecursionlimit(10000)

# ==========================================
# 1. DFS 
# ==========================================
def generate_dfs(width, height, show_animation=False, callback=None):
    shape = (height * 2 + 1, width * 2 + 1)
    maze = np.zeros(shape, dtype=np.uint8)
    scale = 10

    def dfs_generate_from(cx, cy):
        maze[cy * 2 + 1, cx * 2 + 1] = 255
        
        if callback: callback(maze.copy()); time.sleep(0.01)
        elif show_animation:
            display_img = cv2.resize(maze, (shape[1] * scale, shape[0] * scale), interpolation=cv2.INTER_NEAREST)
            cv2.imshow("Generating DFS...", display_img)
            cv2.waitKey(10) 
            
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny * 2 + 1, nx * 2 + 1] == 0:
                maze[cy * 2 + 1 + dy, cx * 2 + 1 + dx] = 255
                
                if callback: callback(maze.copy()); time.sleep(0.01)
                elif show_animation:
                    display_img = cv2.resize(maze, (shape[1] * scale, shape[0] * scale), interpolation=cv2.INTER_NEAREST)
                    cv2.imshow("Generating DFS...", display_img)
                    cv2.waitKey(10)
                    
                dfs_generate_from(nx, ny)

    dfs_generate_from(0, 0)
    maze[1, 0] = 255
    maze[-2, -1] = 255
    if callback: callback(maze.copy())
    if show_animation and not callback: cv2.destroyWindow("Generating DFS...")
    return maze

# ==========================================
# 2. Prim 
# ==========================================
def generate_prim(width, height, show_animation=False, callback=None):
    shape = (height * 2 + 1, width * 2 + 1)
    maze = np.zeros(shape, dtype=np.uint8)
    scale = 10
    walls = []
    
    def add_walls(cx, cy):
        maze[cy * 2 + 1, cx * 2 + 1] = 255
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny * 2 + 1, nx * 2 + 1] == 0:
                walls.append((cx * 2 + 1 + dx, cy * 2 + 1 + dy, nx, ny))
                
    add_walls(0, 0)
    step = 0
    while len(walls) > 0:
        idx = random.randint(0, len(walls) - 1)
        wx, wy, nx, ny = walls.pop(idx)
        
        if maze[ny * 2 + 1, nx * 2 + 1] == 0:
            maze[wy, wx] = 255 
            add_walls(nx, ny)  
            
            step += 1
            if callback and step % 3 == 0: callback(maze.copy()); time.sleep(0.005)
            elif show_animation and step % 3 == 0:
                display_img = cv2.resize(maze, (shape[1] * scale, shape[0] * scale), interpolation=cv2.INTER_NEAREST)
                cv2.imshow("Generating Prim...", display_img)
                cv2.waitKey(5)
                
    maze[1, 0] = 255
    maze[-2, -1] = 255
    if callback: callback(maze.copy())
    if show_animation and not callback: cv2.destroyWindow("Generating Prim...")
    return maze

# ==========================================
# 3. 递归分割 
# ==========================================
def generate_division(width, height, show_animation=False, callback=None):
    shape = (height * 2 + 1, width * 2 + 1)
    maze = np.ones(shape, dtype=np.uint8) * 255
    maze[0, :] = 0; maze[-1, :] = 0; maze[:, 0] = 0; maze[:, -1] = 0
    scale = 10
    
    def divide(x, y, w, h):
        if w <= 1 or h <= 1: return
        horizontal = h > w if h != w else random.choice([True, False])
        
        if horizontal:
            wy = random.randint(1, h - 1)
            dx = random.randint(0, w - 1)
            wall_y = y * 2 + wy * 2
            maze[wall_y, (x * 2 + 1):(x * 2 + 1 + w * 2)] = 0
            maze[wall_y, x * 2 + 1 + dx * 2] = 255
            
            if callback: callback(maze.copy()); time.sleep(0.02)
            elif show_animation:
                display_img = cv2.resize(maze, (shape[1] * scale, shape[0] * scale), interpolation=cv2.INTER_NEAREST)
                cv2.imshow("Generating Division...", display_img)
                cv2.waitKey(20) 
                
            divide(x, y, w, wy)
            divide(x, y + wy, w, h - wy)
        else:
            wx = random.randint(1, w - 1)
            dy = random.randint(0, h - 1)
            wall_x = x * 2 + wx * 2
            maze[(y * 2 + 1):(y * 2 + 1 + h * 2), wall_x] = 0
            maze[y * 2 + 1 + dy * 2, wall_x] = 255
            
            if callback: callback(maze.copy()); time.sleep(0.02)
            elif show_animation:
                display_img = cv2.resize(maze, (shape[1] * scale, shape[0] * scale), interpolation=cv2.INTER_NEAREST)
                cv2.imshow("Generating Division...", display_img)
                cv2.waitKey(20)
                
            divide(x, y, wx, h)
            divide(x + wx, y, w - wx, h)

    divide(0, 0, width, height)
    maze[1, 0] = 255
    maze[-2, -1] = 255
    if callback: callback(maze.copy())
    if show_animation and not callback: cv2.destroyWindow("Generating Division...")
    return maze

# ==========================================
# 4. Kruskal 
# ==========================================
def generate_kruskal(width, height, show_animation=False, callback=None):
    shape = (height * 2 + 1, width * 2 + 1)
    maze = np.zeros(shape, dtype=np.uint8)
    scale = 10
    
    for y in range(height):
        for x in range(width):
            maze[y * 2 + 1, x * 2 + 1] = 255
            
    total_rooms = width * height
    parent = [i for i in range(total_rooms)]
    
    def find(i):
        if parent[i] == i: return i
        parent[i] = find(parent[i]) 
        return parent[i]
        
    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            return True 
        return False   

    walls = []
    for y in range(height):
        for x in range(width):
            current_room_id = y * width + x 
            if x < width - 1:
                walls.append({"wall_pos": (y * 2 + 1, x * 2 + 2), "room1": current_room_id, "room2": current_room_id + 1})
            if y < height - 1:
                walls.append({"wall_pos": (y * 2 + 2, x * 2 + 1), "room1": current_room_id, "room2": current_room_id + width})
                
    random.shuffle(walls)
    step = 0
    for wall in walls:
        if union(wall["room1"], wall["room2"]):
            wy, wx = wall["wall_pos"]
            maze[wy, wx] = 255 
            
            step += 1
            if callback and step % 5 == 0: callback(maze.copy()); time.sleep(0.001)
            elif show_animation and step % 5 == 0:
                display_img = cv2.resize(maze, (shape[1] * scale, shape[0] * scale), interpolation=cv2.INTER_NEAREST)
                cv2.imshow("Generating Kruskal...", display_img)
                cv2.waitKey(1)
            
    maze[1, 0] = 255
    maze[-2, -1] = 255
    if callback: callback(maze.copy())
    if show_animation and not callback: cv2.destroyWindow("Generating Kruskal...")
    return maze

# ==========================================
# 测试模块 (单独运行此文件时执行)
# ==========================================
if __name__ == "__main__":
    w, h = 20, 20
    
    print("1. 正在演示 DFS 生成...")
    maze_imgdfs = generate_dfs(w, h, show_animation=True)

    print("2. 正在演示 Prim 生成...")
    maze_imgprim = generate_prim(w, h, show_animation=True)

    print("3. 正在演示 分割法 生成...")
    maze_imgdivison = generate_division(w, h, show_animation=True)

    print("4. 正在演示 Kruskal 生成...")
    maze_imgkruskal = generate_kruskal(w, h, show_animation=True)

    scale = 10
    maze_img_largedfs = cv2.resize(maze_imgdfs, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    maze_img_largeprim = cv2.resize(maze_imgprim, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    maze_img_largedivison = cv2.resize(maze_imgdivison, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    maze_img_largekruskal = cv2.resize(maze_imgkruskal, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

    cv2.imshow("Final: DFS", maze_img_largedfs)
    cv2.imshow("Final: PRIM", maze_img_largeprim)
    cv2.imshow("Final: DIVISION", maze_img_largedivison)
    cv2.imshow("Final: KRUSKAL", maze_img_largekruskal)

    cv2.imwrite("mazedfs.png", maze_imgdfs)
    cv2.imwrite("mazeprim.png", maze_imgprim)
    cv2.imwrite("mazedivison.png", maze_imgdivison)
    cv2.imwrite("mazekruskal.png", maze_imgkruskal) 
    
    print("所有迷宫展示并保存完毕！请按任意键退出。")
    cv2.waitKey(0)
    cv2.destroyAllWindows()