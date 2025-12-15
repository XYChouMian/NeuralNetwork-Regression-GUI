from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QGroupBox, QSplitter, QTextEdit, QProgressBar, QSpinBox,
    QComboBox, QGridLayout, QDoubleSpinBox, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt
from styles import StyleManager


class TrainingTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # 引用MainWindow实例
        self.setup_ui()

    def setup_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)  # 设置主布局间距
        main_layout.setContentsMargins(12, 12, 12, 12)  # 设置主布局边距

        # 创建顶部的文件导入和列选择部分
        top_group = QGroupBox("数据准备")
        top_layout = QVBoxLayout(top_group)
        top_layout.setSpacing(8)
        top_layout.setContentsMargins(8, 8, 8, 8)

        # 文件路径显示
        file_path_layout = QHBoxLayout()
        file_path_layout.setSpacing(8)
        file_path_layout.addWidget(QLabel("当前文件:"))
        self.file_path_label = QLabel("未选择文件")
        self.file_path_label.setStyleSheet("font-style: italic; color: gray;")
        file_path_layout.addWidget(self.file_path_label, 1)
        top_layout.addLayout(file_path_layout)

        # 创建列选择部分
        column_layout = QHBoxLayout()
        column_layout.setSpacing(10)

        # 可用列列表
        available_group = QGroupBox("可用列")
        available_layout = QVBoxLayout(available_group)
        available_layout.setSpacing(6)
        available_layout.setContentsMargins(6, 6, 6, 6)
        self.available_list = QListWidget()
        self.available_list.setSelectionMode(
            QListWidget.ExtendedSelection)  # 支持多选
        self.available_list.setMinimumHeight(140)  # 设置最小高度
        available_layout.addWidget(self.available_list)

        # 可用列框内的按钮
        available_buttons_layout = QHBoxLayout()
        available_buttons_layout.setSpacing(5)
        # 可用列 -> 输入列
        self.to_input_btn = QPushButton("加入到输入特征 >")
        self.to_input_btn.setStyleSheet(StyleManager.get_button_style("blue_border") + StyleManager.get_level3_style())
        self.to_input_btn.clicked.connect(
            lambda: self.parent.move_to_list(self.available_list, self.input_list))
        # 可用列 -> 输出列
        self.to_output_btn = QPushButton("加入到输出特征 >")
        self.to_output_btn.setStyleSheet(StyleManager.get_button_style("blue_border") + StyleManager.get_level3_style())
        self.to_output_btn.clicked.connect(
            lambda: self.parent.move_to_list(self.available_list, self.output_list))
        available_buttons_layout.addWidget(self.to_input_btn)
        available_buttons_layout.addWidget(self.to_output_btn)
        available_layout.addLayout(available_buttons_layout)

        column_layout.addWidget(available_group, 1)

        # 输入列列表
        input_group = QGroupBox("输入列")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(6)
        input_layout.setContentsMargins(6, 6, 6, 6)
        self.input_list = QListWidget()
        self.input_list.setSelectionMode(QListWidget.ExtendedSelection)  # 支持多选
        self.input_list.setMinimumHeight(140)
        input_layout.addWidget(self.input_list)

        # 输入列框内的移出按钮
        self.remove_input_btn = QPushButton("移出")
        self.remove_input_btn.setStyleSheet(StyleManager.get_button_style("blue_border") + StyleManager.get_level3_style())
        self.remove_input_btn.clicked.connect(
            lambda: self.parent.move_to_list(self.input_list, self.available_list))
        input_layout.addWidget(self.remove_input_btn)

        column_layout.addWidget(input_group, 1)

        # 输出列列表
        output_group = QGroupBox("输出列")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(6)
        output_layout.setContentsMargins(6, 6, 6, 6)
        self.output_list = QListWidget()
        self.output_list.setSelectionMode(
            QListWidget.ExtendedSelection)  # 支持多选
        self.output_list.setMinimumHeight(140)
        output_layout.addWidget(self.output_list)

        # 输出列框内的移出按钮
        self.remove_output_btn = QPushButton("移出")
        self.remove_output_btn.setStyleSheet(StyleManager.get_button_style("blue_border") + StyleManager.get_level3_style())
        self.remove_output_btn.clicked.connect(
            lambda: self.parent.move_to_list(self.output_list, self.available_list))
        output_layout.addWidget(self.remove_output_btn)

        column_layout.addWidget(output_group, 1)

        top_layout.addLayout(column_layout)
        main_layout.addWidget(top_group)

        # 创建中间的网络结构设置和数据处理部分
        middle_layout = QGridLayout()
        middle_layout.setSpacing(10)
        middle_layout.setColumnStretch(0, 1)  # 神经网络结构占左1/3
        middle_layout.setColumnStretch(1, 2)  # 数据信息框占右2/3

        # 网络结构设置
        network_group = QGroupBox("神经网络参数设置")
        network_scroll_area = QScrollArea()
        network_scroll_area.setWidgetResizable(True)  # 滚动区域内容自适应大小
        network_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 只显示垂直滚动条
        
        # 创建一个容器widget来放置所有网络参数控件
        network_widget = QWidget()
        self.network_layout = QGridLayout(network_widget)  # 使用表格布局，保存为实例变量
        self.network_layout.setSpacing(8)
        self.network_layout.setContentsMargins(8, 8, 8, 8)
        self.network_layout.setColumnStretch(0, 1)  # 标签列占2份
        self.network_layout.setColumnStretch(1, 1)  # 控件列占1份
        
        # 将容器widget设置为滚动区域的widget
        network_scroll_area.setWidget(network_widget)
        
        # 将滚动区域添加到network_group
        network_group_layout = QVBoxLayout(network_group)
        network_group_layout.setSpacing(0)
        network_group_layout.setContentsMargins(0, 0, 0, 0)
        network_group_layout.addWidget(network_scroll_area)
        
        # 设置网络组的最大高度
        network_group.setMaximumHeight(400)

        # 隐藏层数量
        hidden_layers_label = QLabel("隐藏层数量:")
        hidden_layers_label.setStyleSheet(StyleManager.get_label_style())
        self.hidden_layers_spin = QSpinBox()
        self.hidden_layers_spin.setStyleSheet(StyleManager.get_input_style())
        self.hidden_layers_spin.setRange(1, 5)
        self.hidden_layers_spin.setValue(2)  # 默认2个隐藏层
        self.hidden_layers_spin.valueChanged.connect(self.parent.update_hidden_layers)
        self.network_layout.addWidget(hidden_layers_label, 0, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.network_layout.addWidget(self.hidden_layers_spin, 0, 1)

        # 学习率
        learning_rate_label = QLabel("学习率:")
        learning_rate_label.setStyleSheet(StyleManager.get_label_style())
        self.learning_rate_spin = QDoubleSpinBox()
        self.learning_rate_spin.setStyleSheet(StyleManager.get_input_style())
        self.learning_rate_spin.setDecimals(4)  # 只保留4位小数
        self.learning_rate_spin.setRange(0.0001, 1.0)
        self.learning_rate_spin.setSingleStep(0.0001)  # 按钮以0.0001变化
        self.learning_rate_spin.setValue(0.001)  # 默认学习率为0.001（1e-3）
        self.learning_rate_widgets = (learning_rate_label, self.learning_rate_spin)
        
        # 训练轮次
        epochs_label = QLabel("训练轮次:")
        epochs_label.setStyleSheet(StyleManager.get_label_style())
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setStyleSheet(StyleManager.get_input_style())
        self.epochs_spin.setRange(10, 10000)
        self.epochs_spin.setValue(2000)  # 默认2000轮
        self.epochs_spin.setSingleStep(100)  # 按钮以100变化
        self.epochs_widgets = (epochs_label, self.epochs_spin)
        
        # 测试集比例
        test_ratio_label = QLabel("测试集比例:")
        test_ratio_label.setStyleSheet(StyleManager.get_label_style())
        self.test_ratio_spin = QDoubleSpinBox()
        self.test_ratio_spin.setStyleSheet(StyleManager.get_input_style())
        self.test_ratio_spin.setRange(0.1, 0.5)
        self.test_ratio_spin.setValue(0.15)  # 默认0.15
        self.test_ratio_spin.setDecimals(2)
        self.test_ratio_spin.setSingleStep(0.01)  # 按钮以0.01变化
        self.test_ratio_widgets = (test_ratio_label, self.test_ratio_spin)
        
        # 随机数种子
        random_seed_label = QLabel("随机数种子:")
        random_seed_label.setStyleSheet(StyleManager.get_label_style())
        self.random_seed_spin = QDoubleSpinBox()
        self.random_seed_spin.setStyleSheet(StyleManager.get_input_style())
        self.random_seed_spin.setRange(0.0, 100.0)
        self.random_seed_spin.setValue(1.0)  # 默认1.0
        self.random_seed_spin.setDecimals(1)
        self.random_seed_spin.setSingleStep(0.1)  # 按钮以0.1变化
        self.random_seed_widgets = (random_seed_label, self.random_seed_spin)
        
        # 优化算法选择
        solver_label = QLabel("优化算法:")
        solver_label.setStyleSheet(StyleManager.get_label_style())
        self.solver_combo = QComboBox()
        self.solver_combo.setStyleSheet(StyleManager.get_input_style())
        # 添加sklearn回归任务的所有求解器
        self.solver_combo.addItems(["adam", "lbfgs", "sgd"])
        self.solver_combo.setCurrentText("adam")  # 默认使用adam算法
        self.solver_widgets = (solver_label, self.solver_combo)
        
        # 所有其他设置项
        self.other_settings = [
            self.learning_rate_widgets,
            self.epochs_widgets,
            self.test_ratio_widgets,
            self.random_seed_widgets,
            self.solver_widgets
        ]
        
        # 隐藏层神经元数量
        self.hidden_layer_labels = []  # 存储隐藏层标签
        self.hidden_layer_spins = []   # 存储隐藏层输入框
        
        # 初始化隐藏层设置
        self.update_hidden_layers()

        middle_layout.addWidget(network_group, 0, 0)

        # 数据处理部分
        data_process_group = QGroupBox("数据信息")  # 简化为只有一个标题
        data_process_layout = QVBoxLayout(data_process_group)
        data_process_layout.setSpacing(8)
        data_process_layout.setContentsMargins(8, 8, 8, 8)

        self.info_text = QTextEdit()
        self.info_text.setStyleSheet(StyleManager.get_text_edit_style())
        self.info_text.setReadOnly(True)
        self.info_text.setMinimumHeight(200)  # 增加高度以填满空间
        data_process_layout.addWidget(self.info_text)

        middle_layout.addWidget(data_process_group, 0, 1)

        # 添加网格布局到主布局
        main_layout.addLayout(middle_layout)

        # 创建底部的训练控制部分
        bottom_group = QGroupBox()  # 移除标题
        bottom_layout = QVBoxLayout(bottom_group)
        bottom_layout.setSpacing(8)
        bottom_layout.setContentsMargins(8, 8, 8, 8)

        # 三个大按钮横向三等分排列，占据整行
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # 导入文件按钮
        self.import_btn = QPushButton("导入文件")
        self.import_btn.clicked.connect(self.parent.import_file)
        self.import_btn.setMinimumHeight(50)
        self.import_btn.setStyleSheet(StyleManager.get_button_style("primary") + StyleManager.get_level2_style())
        buttons_layout.addWidget(self.import_btn)
        buttons_layout.setStretch(0, 1)  # 占1份

        # 开始训练按钮 - 点击后执行标准化、训练、保存模型全部功能
        self.train_btn = QPushButton("开始训练")
        self.train_btn.clicked.connect(self.parent.integrated_process)
        self.train_btn.setMinimumHeight(50)
        self.train_btn.setStyleSheet(StyleManager.get_button_style("primary") + StyleManager.get_level2_style())
        buttons_layout.addWidget(self.train_btn)
        buttons_layout.setStretch(1, 1)  # 占1份

        # 跳转到预测结果按钮
        self.predict_btn = QPushButton("预测结果")
        # 连接到现有的switch_to_prediction方法
        self.predict_btn.clicked.connect(self.parent.switch_to_prediction)
        self.predict_btn.setMinimumHeight(50)
        self.predict_btn.setStyleSheet(StyleManager.get_button_style("primary") + StyleManager.get_level2_style())
        buttons_layout.addWidget(self.predict_btn)
        buttons_layout.setStretch(2, 1)  # 占1份

        bottom_layout.addLayout(buttons_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(StyleManager.get_progress_bar_style())
        self.progress_bar.setVisible(False)
        bottom_layout.addWidget(self.progress_bar)

        # 模型保存信息
        self.model_info_label = QLabel("模型未训练")
        self.model_info_label.setStyleSheet("font-style: italic; color: gray;")
        bottom_layout.addWidget(self.model_info_label)

        main_layout.addWidget(bottom_group)
        main_layout.addStretch()

    def update_hidden_layers(self):
        """根据选择的层数更新隐藏层设置界面"""
        # 清除现有隐藏层控件
        for label in self.hidden_layer_labels:
            if label is not None and label.parentWidget():
                self.network_layout.removeWidget(label)
                label.deleteLater()
        for spin in self.hidden_layer_spins:
            if spin is not None and spin.parentWidget():
                self.network_layout.removeWidget(spin)
                spin.deleteLater()
        
        # 清空列表
        self.hidden_layer_labels.clear()
        self.hidden_layer_spins.clear()
        
        # 获取层数
        num_layers = self.hidden_layers_spin.value()
        
        # 创建隐藏层神经元数量设置
        for i in range(num_layers):
            label = QLabel(f"隐藏层{i+1}神经元数量:")
            label.setStyleSheet(StyleManager.get_label_style())
            spin_box = QSpinBox()
            spin_box.setStyleSheet(StyleManager.get_input_style())
            spin_box.setRange(1, 256)
            if i == 0:
                spin_box.setValue(64)  # 第一层默认64
            elif i == 1:
                spin_box.setValue(32)  # 第二层默认32
            else:
                spin_box.setValue(16)  # 更多层默认16
            
            # 添加到列表
            self.hidden_layer_labels.append(label)
            self.hidden_layer_spins.append(spin_box)
            
            # 直接添加到network_layout中，与其他设置项对齐
            self.network_layout.addWidget(label, i+1, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
            self.network_layout.addWidget(spin_box, i+1, 1)
        
        # 更新其他设置项的位置
        self.update_other_settings_position()
        
    def update_other_settings_position(self):
        """根据隐藏层数量更新其他设置项的位置"""
        # 清除现有其他设置项
        for settings in self.other_settings:
            label, widget = settings
            if label.parentWidget():
                self.network_layout.removeWidget(label)
            if widget.parentWidget():
                self.network_layout.removeWidget(widget)
        
        # 获取隐藏层数量
        num_layers = self.hidden_layers_spin.value()
        
        # 重新添加其他设置项，调整行位置
        for i, settings in enumerate(self.other_settings):
            label, widget = settings
            self.network_layout.addWidget(label, num_layers + 1 + i, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
            self.network_layout.addWidget(widget, num_layers + 1 + i, 1)
