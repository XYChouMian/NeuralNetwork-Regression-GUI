import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from PIL import Image
import os


def create_icon(save_path="app.ico", dpi=300):
    """
    创建极简主义版本的无边框图标
    """
    fig = plt.figure(figsize=(6, 6), frameon=False)
    gs = fig.add_gridspec(1, 1)
    ax = gs.subplots()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    # 添加居中的半透明圆形背景，提高图标可见度
    circle_bg = Circle((5, 5), radius=5, facecolor='#e0e0e0',
                       edgecolor='none', alpha=0.5)
    ax.add_patch(circle_bg)

    # 简约拟合曲线
    x = np.linspace(0.8, 9.2, 50)
    y = 5 + 2 * np.sin((x-4)*0.7)
    ax.plot(x, y, color='#222222', linewidth=30, alpha=1, zorder=2)

    x = np.linspace(1, 9, 6)
    print(x)

    np.random.seed(1)
    nodes = [
        ((1., 4.9), 0.84),
        ((2.6, 2.8), 1.06),
        ((4.2, 8.6), 1.25),
        ((5.8, 6.8), 0.67),
        ((7.4, 4.3), 1.19),
        ((9., 5.8), 0.89)
    ]
    colors = ['#D64545', '#3AB5A5', '#3A9BC4', '#E6B15A', '#E6C64A', '#8A4FA1']
    for i, (p, s) in enumerate(nodes):
        color = colors[i % len(colors)]
        node = Circle(p, radius=s,
                      facecolor=color, edgecolor='none', alpha=0.9, zorder=1)
        ax.add_patch(node)
    print(nodes)

    plt.tight_layout(pad=0)

    # 先保存为PNG临时文件
    png_path = save_path.replace('.ico', '.png')
    plt.savefig(png_path, dpi=dpi, bbox_inches='tight',
                transparent=True, pad_inches=0)
    plt.close(fig)  # 关闭图形，释放资源

    # 使用PIL将PNG转换为ICO
    img = Image.open(png_path)
    # 确保图片是RGBA模式（支持透明度）
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    # 保存为ICO格式
    img.save(save_path, format='ICO', sizes=[
             (256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

    # 删除临时PNG文件
    os.remove(png_path)

    return save_path


# 生成图标
if __name__ == "__main__":
    print("正在生成无边框神经网络数据拟合图标...")
    # 生成极简版本
    icon2 = create_icon("./resources/NeuralNetwork.ico")
    print(f"图标生成完成: {icon2}")
