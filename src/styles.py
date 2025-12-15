class StyleManager:
    """
    样式管理器类，用于集中管理应用程序的颜色主题和样式定义
    """
    # 主题色
    PRIMARY_COLOR = "#00468c"  # 主蓝色
    BACKGROUND_COLOR = "#ffffff"  # 白色背景
    TEXT_COLOR = "#333333"  # 深色文本

    # 辅助色（尽量少用）
    ACCENT_COLOR = "#ffc800"  # 金色强调色
    DANGER_COLOR = "#962800"  # 红色（危险/错误）
    WARNING_COLOR = "#7d5014"  # 棕色（警告）
    SUCCESS_COLOR = "#005a1e"  # 绿色（成功）

    @classmethod
    def get_button_style(cls, button_type="primary"):
        """
        获取按钮样式

        参数:
            button_type: 按钮类型，可选值：primary, secondary, accent, danger, warning, success

        返回:
            str: 按钮的样式表
        """
        def adjust_color(color_hex, offset):
            """调整颜色，确保在有效范围内"""
            color_int = int(color_hex[1:], 16)
            new_color = color_int + offset
            # 确保颜色在0x000000到0xFFFFFF之间
            new_color = max(0x000000, min(0xFFFFFF, new_color))
            return f"#{new_color:06x}"

        if button_type == "primary":
            hover_color = adjust_color(cls.PRIMARY_COLOR, 0x111111)
            return f"""
            QPushButton {{
                background-color: {cls.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            """
        elif button_type == "secondary":
            return f"""
            QPushButton {{
                background-color: white;
                color: {cls.PRIMARY_COLOR};
                border: 1px solid {cls.PRIMARY_COLOR};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #{0xf0f0f0:06x};
            }}
            """
        elif button_type == "blue_border":
            return f"""
            QPushButton {{
                background-color: {cls.BACKGROUND_COLOR};
                color: {cls.PRIMARY_COLOR};
                border: 1px solid {cls.PRIMARY_COLOR};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #{0xf0f0f0:06x};
            }}
            """
        elif button_type == "green_border":
            return f"""
            QPushButton {{
                background-color: {cls.BACKGROUND_COLOR};
                color: {cls.SUCCESS_COLOR};
                border: 1px solid {cls.SUCCESS_COLOR};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #{0xf0f0f0:06x};
            }}
            """
        elif button_type == "green_border_red_text":
            return f"""
            QPushButton {{
                background-color: {cls.BACKGROUND_COLOR};
                color: {cls.DANGER_COLOR};
                border: 1px solid {cls.SUCCESS_COLOR};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #{0xf0f0f0:06x};
            }}
            """
        elif button_type == "red_border":
            return f"""
            QPushButton {{
                background-color: {cls.BACKGROUND_COLOR};
                color: {cls.DANGER_COLOR};
                border: 1px solid {cls.DANGER_COLOR};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #{0xf0f0f0:06x};
            }}
            """
        elif button_type == "accent":
            hover_color = adjust_color(cls.ACCENT_COLOR, 0x111111)
            return f"""
            QPushButton {{
                background-color: {cls.ACCENT_COLOR};
                color: {cls.TEXT_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            """
        elif button_type == "danger":
            hover_color = adjust_color(cls.DANGER_COLOR, 0x111111)
            return f"""
            QPushButton {{
                background-color: {cls.DANGER_COLOR};
                color: {cls.BACKGROUND_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            """
        elif button_type == "warning":
            hover_color = adjust_color(cls.WARNING_COLOR, 0x111111)
            return f"""
            QPushButton {{
                background-color: {cls.WARNING_COLOR};
                color: {cls.BACKGROUND_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            """
        elif button_type == "success":
            hover_color = adjust_color(cls.SUCCESS_COLOR, 0x111111)
            return f"""
            QPushButton {{
                background-color: {cls.SUCCESS_COLOR};
                color: {cls.BACKGROUND_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            """
        else:
            return ""

    @classmethod
    def get_label_style(cls, label_type="normal"):
        """
        获取标签样式

        参数:
            label_type: 标签类型，可选值：normal, primary, accent, danger, warning, success

        返回:
            str: 标签的样式表
        """
        if label_type == "primary":
            return f"""
            QLabel {{
                color: {cls.PRIMARY_COLOR};
                font-weight: bold;
            }}
            """
        elif label_type == "accent":
            return f"""
            QLabel {{
                color: {cls.ACCENT_COLOR};
                font-weight: bold;
            }}
            """
        elif label_type == "danger":
            return f"""
            QLabel {{
                color: {cls.DANGER_COLOR};
                font-weight: bold;
            }}
            """
        elif label_type == "warning":
            return f"""
            QLabel {{
                color: {cls.WARNING_COLOR};
                font-weight: bold;
            }}
            """
        elif label_type == "success":
            return f"""
            QLabel {{
                color: {cls.SUCCESS_COLOR};
                font-weight: bold;
            }}
            """
        else:
            return f"""
            QLabel {{
                color: {cls.TEXT_COLOR};
            }}
            """

    @classmethod
    def get_title_style(cls):
        """
        获取标题样式（最大字号）

        返回:
            str: 标题的样式表
        """
        return """
        QLabel, QPushButton {
            font-size: 36px;
            font-weight: bold;
        }
        """

    @classmethod
    def get_level1_style(cls):
        """
        获取一级样式（次大字号）

        返回:
            str: 一级样式的样式表
        """
        return """
        QLabel, QPushButton {
            font-size: 24px;
            font-weight: bold;
        }
        """

    @classmethod
    def get_level2_style(cls):
        """
        获取二级样式（中等字号）

        返回:
            str: 二级样式的样式表
        """
        return """
        QLabel, QPushButton {
            font-size: 20px;
            font-weight: bold;
        }
        """

    @classmethod
    def get_level3_style(cls):
        """
        获取三级样式（较小字号）

        返回:
            str: 三级样式的样式表
        """
        return """
        QLabel, QPushButton {
            font-size: 16px;
            font-weight: bold;
        }
        """

    @classmethod
    def get_text_edit_style(cls):
        """
        获取文本编辑框样式

        返回:
            str: 文本编辑框的样式表
        """
        return f"""
        QTextEdit {{
            background-color: {cls.BACKGROUND_COLOR};
            color: {cls.TEXT_COLOR};
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 8px;
        }}
        """

    @classmethod
    def get_tab_widget_style(cls):
        """
        获取选项卡控件样式

        返回:
            str: 选项卡控件的样式表
        """
        # 直接使用固定的灰色作为未选中和hover状态的背景色
        return f"""
        QTabWidget::pane {{
            border: 1px solid #cccccc;
            background: {cls.BACKGROUND_COLOR};
        }}
        
        QTabBar::tab {{
            background-color: #f0f0f0;
            color: {cls.TEXT_COLOR};
            padding: 8px 16px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.BACKGROUND_COLOR};
            color: {cls.PRIMARY_COLOR};
            border-bottom: 2px solid {cls.PRIMARY_COLOR};
        }}
        
        QTabBar::tab:hover {{
            background-color: #e0e0e0;
        }}
        """

    @classmethod
    def get_group_box_style(cls):
        """
        获取分组框样式

        返回:
            str: 分组框的样式表
        """
        return f"""
        QGroupBox {{
            border: 1px solid #cccccc;
            border-radius: 4px;
            margin-top: 10px;
            padding: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {cls.PRIMARY_COLOR};
            font-weight: bold;
        }}
        """

    @classmethod
    def get_input_style(cls):
        """
        获取输入控件样式（适用于QSpinBox、QDoubleSpinBox等）

        返回:
            str: 输入控件的样式表
        """
        return f"""
        QSpinBox, QDoubleSpinBox {{
            background-color: {cls.BACKGROUND_COLOR};
            color: {cls.TEXT_COLOR};
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px 8px;
        }}
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {cls.PRIMARY_COLOR};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {cls.PRIMARY_COLOR};
            outline: none;
        }}
        """

    @classmethod
    def get_progress_bar_style(cls):
        """
        获取进度条样式

        返回:
            str: 进度条的样式表
        """
        return f"""
        QProgressBar {{
            background-color: #e0e0e0;
            color: {cls.TEXT_COLOR};
            border: none;
            border-radius: 4px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {cls.SUCCESS_COLOR};
            border-radius: 4px;
        }}
        """
