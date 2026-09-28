import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image
import threading
from tkinter import messagebox, filedialog

# 导入我们的底层引擎
import generate
import solve

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MazeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("迷宫自动生成与求解系统")
        self.geometry("950x750")
        self.minsize(850, 650)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.current_maze = None
        self.maze_source = "internal" # 标记当前迷宫是内部生成的还是外部导入的
        self.custom_points = []       # 存放外部导入时的起点和终点
        
        self.is_playing = False 
        self.player_pos = [0, 1] 
        
        self.setup_sidebar()
        self.setup_main_area()
        
        # 绑定键盘事件用于手动挑战
        self.bind("<KeyPress>", self.handle_keypress)

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="Maze Solver", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.pack(pady=(20, 15))
        
        # ==================== 1. 生成模块 ====================
        self.lbl_gen = ctk.CTkLabel(self.sidebar, text="1. 地形生成配置", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_gen.pack(anchor="w", padx=20, pady=(5, 0))
        
        self.size_var = ctk.IntVar(value=20)
        self.lbl_size = ctk.CTkLabel(self.sidebar, text="迷宫尺寸: 20x20")
        self.lbl_size.pack(padx=20, pady=(5,0))
        self.slider_size = ctk.CTkSlider(self.sidebar, from_=10, to=50, variable=self.size_var, command=self.update_size_label)
        self.slider_size.pack(padx=20, pady=(0,10))
        
        self.gen_algo = ctk.StringVar(value="DFS")
        self.opt_gen = ctk.CTkOptionMenu(self.sidebar, variable=self.gen_algo, values=["DFS", "PRIM", "分割法", "Kruskal"])
        self.opt_gen.pack(padx=20, pady=(0, 10), fill="x")
        
        self.btn_gen = ctk.CTkButton(self.sidebar, text="🔨 生 成 迷 宫", command=self.on_generate, height=35)
        self.btn_gen.pack(padx=20, pady=(0, 15), fill="x")
        
        # ==================== 2. 求解模块 ====================
        self.lbl_solve = ctk.CTkLabel(self.sidebar, text="2. 智能寻路算法", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_solve.pack(anchor="w", padx=20, pady=(5, 0))
        
        self.solve_algo = ctk.StringVar(value="ASTAR")
        self.opt_solve = ctk.CTkOptionMenu(self.sidebar, variable=self.solve_algo, values=["BFS", "DFS", "ASTAR"])
        self.opt_solve.pack(padx=20, pady=(10, 10), fill="x")
        
        self.btn_solve = ctk.CTkButton(self.sidebar, text="🚀 算 法 破 解", command=self.on_solve, height=35, fg_color="#2B8A3E", hover_color="#21662C")
        self.btn_solve.pack(padx=20, pady=(0, 15), fill="x")
        
        # ==================== 3. 互动与拓展 ====================
        self.lbl_extra = ctk.CTkLabel(self.sidebar, text="3. 互动与拓展", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_extra.pack(anchor="w", padx=20, pady=(5, 0))
        
        # 【整合外部图片识别功能】
        self.btn_import = ctk.CTkButton(self.sidebar, text="📁 导 入 外 部 图 片", command=self.import_external_maze, height=35, fg_color="#5C7CFA", hover_color="#3B5BDB")
        self.btn_import.pack(padx=20, pady=(10, 10), fill="x")
        
        self.btn_play = ctk.CTkButton(self.sidebar, text="🎮 我 自 己 玩 !", command=self.start_manual_play, height=35, fg_color="#E67700", hover_color="#C92A2A")
        self.btn_play.pack(padx=20, pady=(0, 10), fill="x")
        
        self.btn_save = ctk.CTkButton(self.sidebar, text="💾 保 存 迷 宫", command=self.save_maze, height=35, fg_color="#1971C2", hover_color="#1864AB")
        self.btn_save.pack(padx=20, pady=(0, 10), fill="x")

    def setup_main_area(self):
        self.display_frame = ctk.CTkFrame(self, corner_radius=15)
        self.display_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)
        
        self.img_label = ctk.CTkLabel(self.display_frame, text="👈 请在左侧选择操作", font=ctk.CTkFont(size=16), text_color="gray")
        self.img_label.grid(row=0, column=0)
        
        # 【交互核心】绑定鼠标点击事件，用于外部图片的起终点选择
        self.img_label.bind("<Button-1>", self.on_left_click)
        self.img_label.bind("<Button-3>", self.on_right_click)

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
        self.btn_import.configure(state=state)
        self.slider_size.configure(state=state)
        self.opt_gen.configure(state=state)
        self.opt_solve.configure(state=state)

    # ========================================================
    # 核心一：生成迷宫
    # ========================================================
    def on_generate(self):
        self.is_playing = False 
        self.maze_source = "internal" # 标记为内部生成
        self.custom_points = []       # 清空手动选点
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

    # ========================================================
    # 核心二：外部图片 CV 识别与导入
    # ========================================================
    def import_external_maze(self):
        # 弹出文件选择框
        file_path = filedialog.askopenfilename(
            title="选择要识别的迷宫图片", 
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if not file_path:
            return
            
        self.is_playing = False
        img = cv2.imread(file_path)
        if img is None:
            messagebox.showerror("错误", "无法读取图片！")
            return
            
        h, w = img.shape[:2]
        
        # 【CV预处理大礼包：缩放、二值化、腐蚀、裁边】
        if w < 150 or h < 150:
            img = cv2.resize(img, (w * 15, h * 15), interpolation=cv2.INTER_NEAREST)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        else:
            max_size = 800
            if w > max_size or h > max_size:
                scale = max_size / max(w, h)
                img = cv2.resize(img, (0, 0), fx=scale, fy=scale)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            kernel = np.ones((3, 3), np.uint8)
            thresh = cv2.erode(thresh, kernel, iterations=1)
            walls_only = cv2.bitwise_not(thresh)
            coords = cv2.findNonZero(walls_only)
            if coords is not None:
                bx, by, bw, bh = cv2.boundingRect(coords)
                mask = np.zeros_like(thresh)
                mask[by:by+bh, bx:bx+bw] = 255
                thresh = cv2.bitwise_and(thresh, mask)
                
        self.current_maze = thresh
        self.maze_source = "external" # 标记为外部导入
        self.custom_points = []       # 清空之前的选点
        self.render_custom_points()
        
        messagebox.showinfo("识别成功", "图片处理完毕！\n\n请在右侧画面上：\n1. 【左键】依次点击指定起点和终点。\n2. 【右键】可撤销选点。\n选完后点击左侧【算法破解】即可自动寻路！")

    # 鼠标交互：UI界面上的坐标选点映射
    # 鼠标交互：UI界面上的坐标选点映射
    def on_left_click(self, event):
        if self.current_maze is None or self.maze_source != "external":
            return
        
        h, w = self.current_maze.shape
        
        # 动态获取相框的真实渲染尺寸，
        actual_w = event.widget.winfo_width()
        actual_h = event.widget.winfo_height()
        
        # 降维映射：用鼠标真实坐标除以真实的相框尺寸
        cx = int(event.x / actual_w * w)
        cy = int(event.y / actual_h * h)
        
        # 安全防线：强行把坐标限制在矩阵范围内，防止点到边缘外导致崩溃
        cx = max(0, min(cx, w - 1))
        cy = max(0, min(cy, h - 1))
        
        if len(self.custom_points) >= 2:
            self.custom_points = [] # 点第三下自动重置
            
        self.custom_points.append((cx, cy))
        self.render_custom_points()

    def on_right_click(self, event):
        if self.current_maze is None or self.maze_source != "external":
            return
        if len(self.custom_points) > 0:
            self.custom_points.pop()
            self.render_custom_points()

    def render_custom_points(self):
        display_maze = cv2.cvtColor(self.current_maze, cv2.COLOR_GRAY2BGR)
        for i, p in enumerate(self.custom_points):
            color = (0, 255, 0) if i == 0 else (0, 0, 255)
            # 自适应点的大小
            radius = max(2, int(self.current_maze.shape[1] / 100))
            cv2.circle(display_maze, p, radius, color, -1)
        self.update_image(display_maze)

    # ========================================================
    # 核心三：算法破解
    # ========================================================
    def on_solve(self):
        self.is_playing = False
        if self.current_maze is None:
            messagebox.showwarning("提示", "请先生成或导入迷宫！")
            return
            
        start_pos, end_pos = None, None
        
        # 如果是外部图片，检查是否选好了起终点
        if self.maze_source == "external":
            if len(self.custom_points) < 2:
                messagebox.showwarning("提示", "这是外部导入的图片，请先用鼠标左键点击出【起点】和【终点】！")
                return
            start_pos = self.custom_points[0]
            end_pos = self.custom_points[1]
            
        algo_text = self.solve_algo.get()
        if "BFS" in algo_text: algo = "BFS"
        elif "DFS" in algo_text: algo = "DFS"
        else: algo = "ASTAR"
            
        self.set_ui_state("disabled") 
        
        def task():
            def ui_callback(maze_state):
                self.after(0, self.update_image, maze_state)
            
            # 直接把矩阵和坐标塞给我们的强大引擎！
            solve.solve_maze_algo(self.current_maze, algo=algo, callback=ui_callback, start_pos=start_pos, end_pos=end_pos)
            self.after(0, self.set_ui_state, "normal")

        threading.Thread(target=task, daemon=True).start()

    # ========================================================
    # 互动拓展：我自己玩 & 保存迷宫
    # ========================================================
    def save_maze(self):
        if self.current_maze is None:
            messagebox.showwarning("提示", "当前没有迷宫可以保存哦！")
            return
        filename = "my_maze.png"
        cv2.imwrite(filename, self.current_maze)
        messagebox.showinfo("成功", f"迷宫已成功保存至当前文件夹：{filename}")

    def start_manual_play(self):
        if self.current_maze is None:
            messagebox.showwarning("提示", "请先生成或导入一个迷宫！")
            return
            
        if self.maze_source == "external":
            if len(self.custom_points) < 2:
                messagebox.showwarning("提示", "请先在图上点击出起点和终点，然后再进行挑战！")
                return
            self.player_pos = list(self.custom_points[0])
        else:
            self.player_pos = [0, 1] 
            
        messagebox.showinfo("游戏开始", "请点击确定后，使用键盘的【上 下 左 右】键控制红色方块走出迷宫！")
        self.is_playing = True
        self.render_player()

    def render_player(self):
        if not self.is_playing: return
        display_maze = cv2.cvtColor(self.current_maze, cv2.COLOR_GRAY2BGR)
        x, y = self.player_pos
        
        if self.maze_source == "external":
            radius = max(1, int(self.current_maze.shape[1] / 150))
            cv2.circle(display_maze, (x, y), radius, (0, 0, 255), -1)
        else:
            display_maze[y, x] = (0, 0, 255)
            
        self.update_image(display_maze)

    def handle_keypress(self, event):
        if not self.is_playing: return
        
        x, y = self.player_pos
        dx, dy = 0, 0
        if event.keysym in ['Up', 'w', 'W']: dy = -1
        elif event.keysym in ['Down', 's', 'S']: dy = 1
        elif event.keysym in ['Left', 'a', 'A']: dx = -1
        elif event.keysym in ['Right', 'd', 'D']: dx = 1
        else: return
        
        nx, ny = x + dx, y + dy
        height, width = self.current_maze.shape
        
        if 0 <= nx < width and 0 <= ny < height and self.current_maze[ny, nx] == 255:
            self.player_pos = [nx, ny]
            self.render_player()
            
            # 判断目标点
            end_target = self.custom_points[1] if self.maze_source == "external" else (width - 1, height - 2)
            
            if abs(nx - end_target[0]) <= 2 and abs(ny - end_target[1]) <= 2:
                self.is_playing = False
                messagebox.showinfo("🎉 挑战成功！", "恭喜你凭借自己的智慧走出了迷宫！")

if __name__ == "__main__":
    app = MazeApp()
    app.mainloop()