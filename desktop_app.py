import cv2
import customtkinter as ctk
from PIL import Image
import threading

# 复用我们自己的库
import generate
import solve

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MazeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("迷宫自动生成与求解")
        self.geometry("900x650")
        self.minsize(800, 600)
        
        # 布局权重分配
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 用于在内存中传递生成的迷宫
        self.current_maze = None
        
        self.setup_sidebar()
        self.setup_main_area()

    def setup_sidebar(self):
        """左侧的控制面板"""
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1) 
        
        self.logo = ctk.CTkLabel(self.sidebar, text="Maze Solver", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        # ==================== 1. 生成模块 ====================
        self.lbl_gen = ctk.CTkLabel(self.sidebar, text="1. 选择迷宫生成算法", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_gen.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.gen_algo = ctk.StringVar(value="DFS")
        
        self.opt_gen = ctk.CTkOptionMenu(
            self.sidebar, 
            variable=self.gen_algo, 
            values=["DFS", "PRIM", "分割法", "Kruskal"]
        )
        self.opt_gen.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.btn_gen = ctk.CTkButton(self.sidebar, text="生 成 迷 宫", command=self.on_generate, height=40)
        self.btn_gen.grid(row=3, column=0, padx=20, pady=(0, 30), sticky="ew")
        
        # ==================== 2. 求解模块 ====================
        self.lbl_solve = ctk.CTkLabel(self.sidebar, text="2. 选择寻路算法", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_solve.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.solve_algo = ctk.StringVar(value="ASTAR")
        self.opt_solve = ctk.CTkOptionMenu(
            self.sidebar, 
            variable=self.solve_algo, 
            values=["BFS", "DFS", "ASTAR"]
        )
        self.opt_solve.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.btn_solve = ctk.CTkButton(self.sidebar, text="开 始 破 解", command=self.on_solve, height=40, fg_color="#2B8A3E", hover_color="#21662C")
        self.btn_solve.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="nwe")

    def setup_main_area(self):
        """右侧图像展示区"""
        self.display_frame = ctk.CTkFrame(self, corner_radius=15)
        self.display_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)
        
        self.img_label = ctk.CTkLabel(self.display_frame, text="👈 请在左侧选择算法并点击生成", font=ctk.CTkFont(size=16), text_color="gray")
        self.img_label.grid(row=0, column=0)

    def update_image(self, img_array):
        """核心：将 OpenCV 的矩阵无损转化为 UI 画面"""
        # 判断是黑白图(生成迷宫)还是彩色图(求解迷宫)，做相应的转换
        if len(img_array.shape) == 2:
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            
        # 强制最近邻放大，保留锐利的马赛克方块！
        pil_img = Image.fromarray(img_rgb).resize((550, 550), Image.NEAREST)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(550, 550))
        
        self.img_label.configure(image=ctk_img, text="")
        self.img_label.image = ctk_img # 保存引用防止被垃圾回收

    def set_ui_state(self, state):
        """控制按钮开关：动画播放时锁定按钮，防止手贱狂点"""
        self.btn_gen.configure(state=state)
        self.btn_solve.configure(state=state)
        self.opt_gen.configure(state=state)
        self.opt_solve.configure(state=state)

    def on_generate(self):
        algo = self.gen_algo.get()
        w, h = 25, 25 
        
        self.set_ui_state("disabled") # 锁死按钮
        
        def task():
            # 这个函数就是算法里的 callback！算法每算一帧，就会呼叫它
            def ui_callback(maze_state):
                # .after(0, ...) 是安全跨线程更新 UI 的终极绝招
                self.after(0, self.update_image, maze_state)
                
            # ⭐️ 通过我们刚刚引入的 generate.py 完美调用四大算法函数
            if "DFS" in algo:
                self.current_maze = generate.generate_dfs(w, h, callback=ui_callback)
            elif "PRIM" in algo:
                self.current_maze = generate.generate_prim(w, h, callback=ui_callback)
            elif "分割法" in algo:
                self.current_maze = generate.generate_division(w, h, callback=ui_callback)
            else:
                self.current_maze = generate.generate_kruskal(w, h, callback=ui_callback)
                
            self.after(0, self.set_ui_state, "normal") # 解锁按钮

        # 启动后台线程干活，坚决不阻塞界面
        threading.Thread(target=task, daemon=True).start()

    def on_solve(self):
        if self.current_maze is None:
            self.img_label.configure(text="⚠️ 请先点击上面的按钮生成迷宫！")
            return
            
        algo_text = self.solve_algo.get()
        if "BFS" in algo_text: algo = "BFS"
        elif "DFS" in algo_text: algo = "DFS"
        else: algo = "ASTAR"
            
        self.set_ui_state("disabled") 
        
        def task():
            def ui_callback(maze_state):
                self.after(0, self.update_image, maze_state)
                
            # ⭐️ 把内存里的 current_maze 直接喂给 solve.py！
            solve.solve_maze_algo(self.current_maze, algo=algo, callback=ui_callback)
            
            self.after(0, self.set_ui_state, "normal")

        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    app = MazeApp()
    app.mainloop()