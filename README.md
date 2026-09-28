# 🌟 MazeSolver: 智能迷宫生成与求解系统

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge&logo=opencv)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

本项目是一个集**算法可视化、计算机视觉处理、现代 GUI 交互**于一体的桌面应用程序。系统内置了多种经典的图论算法用于迷宫的自动生成与最优路径求解，同时具备强大的高鲁棒性 CV 引擎，能够读取、修复并破解含有噪点的真实世界迷宫图片。

## 📸 效果展示 (Demo)

| 迷宫生成动画 (Kruskal) | 智能寻路动画 (A-Star) |
| :---: | :---: |
| <img src="assets\Kruskal_generation.gif" alt="Generation" width="100%"> | <img src="assets\Astar_solvingKruskal.gif" alt="Solving" width="100%"> |
| *展示如繁星般打通墙壁的并查集算法* | *展示 A* 雷达制导躲避死胡同的寻路过程* |

| 外部脏图片智能解析 | 现代化暗黑 UI 界面 |
| :---: | :---: |
| <img src="assets\external.png" alt="external" width="100%"> | <img src="assets\GUI.png"  alt="GUI" width="100%"> |
| *自动裁边、腐蚀加固墙壁并完成鼠标交互选点* | *基于 MVC 架构与多线程无阻塞渲染* |

## ✨ 核心特性 (Features)

*   **🏰 四大迷宫生成算法**：
    *   `DFS (深度优先)`：生成深邃的长主干道迷宫。
    *   `Prim (随机普里姆)`：生成具有大量极短岔路的辐射状迷宫。
    *   `Recursive Division (递归分割)`：利用空间降维生成具有笔直长廊的街区型迷宫。
    *   `Kruskal (克鲁斯卡尔)`：基于并查集 (Union-Find) 生成纹理绝对随机、平衡的迷宫。
*   **🚀 三大智能寻路引擎**：
    *   `BFS (广度优先)`：基于队列实现，寻找绝对最短路径的泛洪搜索。
    *   `DFS (深度优先)`：基于栈实现，展示回溯特性的盲目探索。
    *   `A* (A-Star)`：引入曼哈顿距离启发函数，极大减少无用探索，直扑终点。
*   **🖼️ 计算机视觉 (CV) 智能预处理**：
    *   支持任意外部迷宫图片的导入。底层集成 `OpenCV`，通过**二值化阈值切割、形态学腐蚀 (Erosion)、最小包围矩形 (Bounding Rect) 遮罩裁边**等硬核 CV 操作，完美修复网络图片的 JPEG 伪影与破洞，杜绝“穿模漏水”及“外围绕界”现象。
*   **🎮 多线程 UI 与玩家挑战模式**：
    *   采用 `CustomTkinter` 打造极简暗黑风界面。
    *   底层采用 `Threading` 后台子线程结合 `Callback` 回调刷新图像，彻底解决算法计算时的界面假死问题。
    *   支持用户使用键盘 `WASD` 亲自挑战生成的迷宫。

## 🛠️ 安装与运行 (Installation)

本项目推荐使用现代化的 Python 包管理工具 `uv` 进行零配置极速部署：

**1. 克隆项目到本地**
```bash
git clone https://github.com/yourusername/maze-solver.git
cd maze-solver
```

**2. 安装依赖包**
```bash
# 如果使用 uv (推荐)
uv add opencv-python numpy customtkinter pillow

# 如果使用传统的 pip
pip install opencv-python numpy customtkinter pillow
```

**3. 启动应用**
```bash
uv run desktop_app.py
# 或 python desktop_app.py
```

## 📁 项目架构 (Project Structure)

项目遵循高内聚、低耦合的 **MVC (Model-View-Controller)** 架构：

```text
📦 maze-solver
 ┣ 📜 desktop_app.py    # GUI 客户端入口 (View & Controller)，处理线程与交互
 ┣ 📜 generate.py       # 迷宫生成引擎 (Model)，独立算法库
 ┣ 📜 solve.py          # 迷宫寻路与 CV 处理引擎 (Model)，独立算法库
 ┣ 📜 test1.png         # 用于测试的外部迷宫图片样本
 ┗ 📜 README.md         # 项目说明文档
```

## 🧠 技术原理解析

### 外部图片的“洗眼”流水线 (CV Pipeline)
针对外部导入的低质量迷宫图像，本项目设计了极具鲁棒性的预处理方案：
1. **自适应缩放**：微型原生矩阵采用 `INTER_NEAREST` 无损插值放大；超大型网图等比例缩小防止显存溢出。
2. **特征降维**：转化为灰度图后，应用 $T=200$ 的严格硬阈值进行 `cv2.threshold` 二值化处理。
3. **形态学加固**：使用 $3 \times 3$ 全1核进行局部最小值卷积（`cv2.erode` 腐蚀），物理填补 1 像素宽的墙壁破洞。
4. **智能遮罩**：利用 `cv2.findNonZero` 提取墙体极值点，构建 BBox，通过位运算 (`cv2.bitwise_and`) 清除迷宫外的留白高速公路。

---

**👨‍💻 Author:** [ is_mon3ter ]  
**📅 Date:** 2026.09