#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本
用于在新的目录结构下运行神经网络回归GUI程序
"""

import sys

# 将src目录添加到Python路径
sys.path.insert(0, 'src')

from PySide6.QtWidgets import QApplication
from main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
