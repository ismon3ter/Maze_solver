import cv2
import customtkinter as ctk
from PIL import Image
import threading
from tkinter import messagebox
import os

# 导入底层引擎
import generate
import solve

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MazeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("迷宫自动生成与求解系统")
        self.geometry("950x700")
        self.minsize(850, 650)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.current_maze = None
        self.is_playing = False # 记录是否处于“玩家手动挑战”模式
        self.player_pos = [1, 0] # 玩家坐标 (x, y)
        self.maze_with_player = None # 带有玩家痕迹的迷宫
        
        self.setup_sidebar()
        self.setup_main_area()
        
        # 绑定键盘事件用于手动挑战
        self.bind("<KeyPress>", self.handle_keypress)

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="Maze Solver", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.pack(pady=(30, 20))
        
        # ==================== 1. 生成模块 ====================
        self.lbl_gen = ctk.CTkLabel(self.sidebar, text="1. 地形生成配置", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_gen.pack(anchor="w", padx=20, pady=(10, 0))
        
        # 【新增】尺寸调节滑动条
        self.size_var = ctk.IntVar(value=20)
        self.lbl_size = ctk.CTkLabel(self.sidebar, text="迷宫尺寸: 20x20")
        self.lbl_size.pack(padx=20, pady=(5,0))
        self.slider_size = ctk.CTkSlider(self.sidebar, from_=10, to=50, variable=self.size_var, command=self.update_size_label)
        self.slider_size.pack(padx=20, pady=(0,10))
        
        self.gen_algo = ctk.StringVar(value="DFS")
        self.opt_gen = ctk.CTkOptionMenu(self.sidebar, variable=self.gen_algo, values=["DFS", "PRIM", "分割法", "Kruskal"])
        self.opt_gen.pack(padx=20, pady=(0, 15), fill="x")
        
        self.btn_gen = ctk.CTkButton(self.sidebar, text="🔨 生 成 迷 宫", command=self.on_generate, height=35)
        self.btn_gen.pack(padx=20, pady=(0, 20), fill="x")
        
        # ==================== 2. 求解模块 ====================
        self.lbl_solve = ctk.CTkLabel(self.sidebar, text="2. 智能寻路算法", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_solve.pack(anchor="w", padx=20, pady=(10, 0))
        
        self.solve_algo = ctk.StringVar(value="ASTAR")
        self.opt_solve = ctk.CTkOptionMenu(self.sidebar, variable=self.solve_algo, values=["BFS", "DFS", "ASTAR"])
        self.opt_solve.pack(padx=20, pady=(10, 15), fill="x")
        
        self.btn_solve = ctk.CTkButton(self.sidebar, text="🚀 算 法 破 解", command=self.on_solve, height=35, fg_color="#2B8A3E", hover_color="#21662C")
        self.btn_solve.pack(padx=20, pady=(0, 20), fill="x")
        
        # ==================== 3. 互动与拓展 ====================
        self.lbl_extra = ctk.CTkLabel(self.sidebar, text="3. 互动与拓展", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_extra.pack(anchor="w", padx=20, pady=(10, 0))
        
        # 【新增】我自己玩按钮
        self.btn_play = ctk.CTkButton(self.sidebar, text="🎮 我 要 挑 战!", command=self.start_manual_play, height=35, fg_color="#E67700", hover_color="#C92A2A")
        self.btn_play.pack(padx=20, pady=(10, 10), fill="x")
        
        # 【新增】保存图片按钮
        self.btn_save = ctk.CTkButton(self.sidebar, text="💾 保 存 迷 宫", command=self.save_maze, height=35, fg_color="#1971C2", hover_color="#1864AB")
        self.btn_save.pack(padx=20, pady=(0, 20), fill="x")

    def setup_main_area(self):
        self.display_frame = ctk.CTkFrame(self, corner_radius=15)
        self.display_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)
        
        self.img_label = ctk.CTkLabel(self.display_frame, text="👈 请在左侧选择算法并点击生成", font=ctk.CTkFont(size=16), text_color="gray")
        self.img_label.grid(row=0, column=0)

    def update_size_label(self, value):
        size = int(value)
        self.lbl_size.configure(text=f"迷宫尺寸: {size}x{size}")

    def update_image(self, img_array):
        if len(img_array.shape) == 2:
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            
        pil_img = Image.fromarray(img_rgb).resize((550, 550), Image.NEAREST)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(550, 550))
        
        self.img_label.configure(image=ctk_img, text="")
        self.img_label.image = ctk_img 

    def set_ui_state(self, state):
        self.btn_gen.configure(state=state)
        self.btn_solve.configure(state=state)
        self.btn_play.configure(state=state)
        self.slider_size.configure(state=state)
        self.opt_gen.configure(state=state)
        self.opt_solve.configure(state=state)

    def on_generate(self):
        self.is_playing = False # 中断玩家操作
        algo = self.gen_algo.get()
        size = self.size_var.get()
        self.set_ui_state("disabled")
        
        def task():
            def ui_callback(maze_state):
                self.after(0, self.update_image, maze_state)
                
            if "DFS" in algo: self.current_maze = generate.generate_dfs(size, size, callback=ui_callback)
            elif "PRIM" in algo: self.current_maze = generate.generate_prim(size, size, callback=ui_callback)
            elif "分割法" in algo: self.current_maze = generate.generate_division(size, size, callback=ui_callback)
            else: self.current_maze = generate.generate_kruskal(size, size, callback=ui_callback)
                
            self.after(0, self.set_ui_state, "normal")

        threading.Thread(target=task, daemon=True).start()

    def on_solve(self):
        self.is_playing = False
        if self.current_maze is None:
            messagebox.showwarning("提示", "请先生成迷宫！")
            return
            
        algo_text = self.solve_algo.get()
        if "BFS" in algo_text: algo = "BFS"
        elif "DFS" in algo_text: algo = "DFS"
        else: algo = "ASTAR"
            
        self.set_ui_state("disabled") 
        
        def task():
            def ui_callback(maze_state):
                self.after(0, self.update_image, maze_state)
            solve.solve_maze_algo(self.current_maze, algo=algo, callback=ui_callback)
            self.after(0, self.set_ui_state, "normal")

        threading.Thread(target=task, daemon=True).start()

    # ========================================================
    # 新增拓展：保存迷宫功能
    # ========================================================
    def save_maze(self):
        if self.current_maze is None:
            messagebox.showwarning("提示", "当前没有迷宫可以保存哦！")
            return
        filename = "my_maze.png"
        cv2.imwrite(filename, self.current_maze)
        messagebox.showinfo("成功", f"迷宫已成功保存至当前文件夹：{filename}")

    # ========================================================
    # 新增拓展：我自己玩 (手动挑战模式)
    # ========================================================
    def start_manual_play(self):
        if self.current_maze is None:
            messagebox.showwarning("提示", "请先生成一个迷宫再挑战！")
            return
            
        messagebox.showinfo("游戏开始", "请使用键盘的【上 下 左 右】键控制红色小人走出迷宫！")
        self.is_playing = True
        
        # 修正：我们的迷宫外墙开口在左侧第一行，所以起点是 x=0, y=1
        self.player_pos = [0, 1] 
        self.render_player()

    def render_player(self):
        if not self.is_playing: return
        
        # 【关键优化】每次重绘时，都拿一张干干净净的原版黑白迷宫转成彩色！
        # 这样走过的历史路径就会自动消失，绝不会拖着长长的“红尾巴”
        display_maze = cv2.cvtColor(self.current_maze, cv2.COLOR_GRAY2BGR)
        
        x, y = self.player_pos
        # 只将玩家当前所在的位置画成红色 (BGR格式)
        display_maze[y, x] = (0, 0, 255)
        
        # 【视觉小优化】如果你想让玩家更显眼，可以取消下面这行的注释，给玩家加个小光晕
        # cv2.circle(display_maze, (x, y), 1, (0, 0, 255), -1)
        
        self.update_image(display_maze)

    def handle_keypress(self, event):
        if not self.is_playing: return
        
        x, y = self.player_pos
        dx, dy = 0, 0
        
        # 支持方向键 和 WASD 键
        if event.keysym in ['Up', 'w', 'W']: dy = -1
        elif event.keysym in ['Down', 's', 'S']: dy = 1
        elif event.keysym in ['Left', 'a', 'A']: dx = -1
        elif event.keysym in ['Right', 'd', 'D']: dx = 1
        else: return
        
        nx, ny = x + dx, y + dy
        height, width = self.current_maze.shape
        
        # 判断前方是否是白色的路 (255)
        if 0 <= nx < width and 0 <= ny < height and self.current_maze[ny, nx] == 255:
            self.player_pos = [nx, ny]
            # 只有坐标合法，才更新画面
            self.render_player()
            
            # 判断是否到达右下角的出口 (x=width-1, y=height-2)
            if ny == height - 2 and nx == width - 1:
                self.is_playing = False
                messagebox.showinfo("🎉 挑战成功！", "恭喜你走出了迷宫！")

if __name__ == "__main__":
    app = MazeApp()
    app.mainloop()