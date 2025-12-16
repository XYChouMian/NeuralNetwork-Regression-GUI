from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from .styles import StyleManager


class StartTab(QWidget):
    """开始界面选项卡"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 添加标题
        title_label = QLabel("神经网络数据拟合软件")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            f"{StyleManager.get_title_style()} margin-bottom: 32px; color: {StyleManager.PRIMARY_COLOR};")
        main_layout.addWidget(title_label)

        # 创建按钮容器
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(80)
        buttons_layout.setAlignment(Qt.AlignCenter)

        # 训练模型按钮 - 使用StyleManager样式
        self.train_model_button = QPushButton("训练神经网络")
        self.train_model_button.setFixedSize(300, 150)
        # 使用一级样式
        self.train_model_button.setStyleSheet(StyleManager.get_button_style("primary") + StyleManager.get_level1_style())
        self.train_model_button.clicked.connect(
            self.parent.show_training_screen)
        buttons_layout.addWidget(self.train_model_button)

        # 导入模型按钮 - 使用StyleManager样式
        self.load_model_button = QPushButton("导入神经网络")
        self.load_model_button.setFixedSize(300, 150)
        # 使用一级样式
        self.load_model_button.setStyleSheet(StyleManager.get_button_style("primary") + StyleManager.get_level1_style())
        self.load_model_button.clicked.connect(
            self.parent.load_model_from_start)
        buttons_layout.addWidget(self.load_model_button)

        # 添加按钮容器到主布局
        main_layout.addWidget(buttons_widget)
