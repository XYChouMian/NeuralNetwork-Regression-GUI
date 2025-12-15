from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
class VisualizationWindow(QMainWindow):
    """专门用于显示训练可视化结果的窗口"""
    def __init__(self, fig, show_completion_message=False):
        super().__init__()
        self.setWindowTitle("训练结果可视化")
        
        # 设置窗口图标
        try:
            # 构建图标文件路径
            icon_path = os.path.join("resources", "NeuralNetwork.ico")
            
            # 检查图标文件是否存在
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                print(f"图标文件不存在: {icon_path}")
        except Exception as e:
            # 记录错误但不中断程序
            print(f"设置窗口图标失败: {e}")
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 如果需要显示完成提示，添加提示标签
        if show_completion_message:
            completion_label = QLabel("标准化、训练、保存集成处理已完成")
            completion_label.setAlignment(Qt.AlignCenter)
            completion_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E8B57;")
            layout.addWidget(completion_label)
        
        # 创建画布并添加到布局
        self.canvas = FigureCanvas(fig)
        layout.addWidget(self.canvas)
        
        # 创建关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        # 显示窗口并置于顶层
        self.showMaximized()  # 自动全屏显示
        self.raise_()  # 将窗口置于顶层
        self.activateWindow()  # 激活窗口

    def closeEvent(self, event):
        """关闭窗口时释放资源"""
        plt.close(self.canvas.figure)
        event.accept()
