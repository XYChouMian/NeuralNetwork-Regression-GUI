from data_processor import DataProcessor
from visualization_window import VisualizationWindow
from start_tab import StartTab
from training_tab import TrainingTab
from prediction_tab import PredictionTab
from styles import StyleManager

# 选择默认使用哪个模型管理器
# # 移除静态导入，避免PyInstaller打包不必要的PyTorch依赖 as ModelManager
from model_manager_sklearn import ModelManagerSklearn as ModelManager
# from model_manager_torch import ModelManagerTorch as ModelManager


import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from PySide6.QtCore import Qt, QEvent

# 移除torch相关导入，统一使用神经网络模型接口
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QListWidget, QListWidgetItem, QGroupBox,
    QSplitter, QStackedWidget, QTextEdit, QMessageBox, QProgressBar, QTabWidget,
    QTableWidget, QTableWidgetItem, QSpinBox, QComboBox
)
from PySide6.QtGui import QIcon
import sys
import os

# 设置环境变量以确保matplotlib使用PySide6
os.environ['QT_API'] = 'PySide6'

matplotlib.use('Qt5Agg')  # 使用Qt5Agg后端以确保在PySide6中正常显示


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("神经网络数据拟合软件")
        self.resize(800, 600)

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

        # 初始化数据处理器和模型管理器
        self.data_processor = DataProcessor()
        self.model_manager = None  # 将在选择模型类型时初始化
        self.model = None

        # 初始化网络结构设置
        self.hidden_layer_spins = []

        # 创建主部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 创建选项卡界面
        self.create_tab_widget()

        # 创建界面组件后再调用update_hidden_layers
        self.update_hidden_layers()

    def create_tab_widget(self):
        """创建选项卡界面，包含开始界面、模型训练和预测结果三个选项卡"""
        # 创建选项卡
        self.tab_widget = QTabWidget()
        # 设置标签页字体略微加大
        font = self.tab_widget.font()
        font.setPointSize(font.pointSize() + 1)
        self.tab_widget.setFont(font)
        # 应用选项卡样式
        self.tab_widget.setStyleSheet(StyleManager.get_tab_widget_style())

        # 创建开始界面作为第一个选项卡
        self.start_tab = StartTab(self)
        self.tab_widget.addTab(self.start_tab, "开始")

        # 创建模型训练选项卡
        self.training_tab = TrainingTab(self)
        self.tab_widget.addTab(self.training_tab, "模型训练")

        # 创建预测结果选项卡
        self.prediction_tab = PredictionTab(self)
        self.tab_widget.addTab(self.prediction_tab, "预测结果")

        # 连接预测信号到对应的方法
        self.prediction_tab.manual_predict_signal.connect(self.manual_predict)
        self.prediction_tab.file_predict_signal.connect(self.file_predict)

        # 将选项卡添加到主布局
        self.main_layout.addWidget(self.tab_widget)

    def show_training_screen(self):
        """显示训练界面"""
        self.tab_widget.setCurrentIndex(1)  # 显示训练标签页

    def load_model_from_start(self):
        """从开始界面导入模型"""
        self.load_model()
        # 导入成功后直接显示预测界面
        if self.model_manager is not None:
            self.tab_widget.setCurrentIndex(2)  # 显示预测标签页

    def import_file(self):
        """导入数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择数据文件", "", "数据文件 (*.csv *.xlsx *.xls)"
        )

        if file_path:
            success, message = self.data_processor.load_file(file_path)
            if success:
                # 更新训练标签页
                self.training_tab.file_path_label.setText(
                    f"已导入: {os.path.basename(file_path)}")
                self.training_tab.info_text.append(f"文件导入成功: {file_path}")
                self.training_tab.info_text.append(
                    self.data_processor.get_basic_info())

                # 更新模型信息标签为"数据表已导入"
                self.training_tab.model_info_label.setText("数据表已导入")
                self.training_tab.model_info_label.setStyleSheet(
                    "QLabel { color: orange; font-style: italic; }")

                # 重置模型管理器和模型，删除原有模型
                self.model_manager = None
                self.model = None
                self.training_tab.info_text.append("已清除原有模型，准备训练新模型")

                self.update_columns_list()
            else:
                QMessageBox.warning(self, "导入失败", message)

    def update_columns_list(self):
        """更新列列表，每次导入新数据时清空输入列和输出列"""
        # 清空输入列和输出列列表
        self.training_tab.input_list.clear()
        self.training_tab.output_list.clear()
        # 更新可用列列表
        self.training_tab.available_list.clear()
        for col in self.data_processor.columns:
            item = QListWidgetItem(col)
            self.training_tab.available_list.addItem(item)

    def move_to_list(self, source_list, target_list):
        """将选中的项从一个列表移动到另一个列表"""
        for item in source_list.selectedItems():
            source_list.takeItem(source_list.row(item))
            target_list.addItem(item)

    def swap_input_output(self):
        """交换输入列和输出列"""
        # 保存当前的输入列和输出列
        input_items = [self.training_tab.input_list.item(
            i).text() for i in range(self.training_tab.input_list.count())]
        output_items = [self.training_tab.output_list.item(
            i).text() for i in range(self.training_tab.output_list.count())]

        # 清空两个列表
        self.training_tab.input_list.clear()
        self.training_tab.output_list.clear()

        # 交换列表内容
        for item in output_items:
            self.training_tab.input_list.addItem(item)

        for item in input_items:
            self.training_tab.output_list.addItem(item)

    def update_hidden_layers(self):
        """调用TrainingTab中的update_hidden_layers方法"""
        self.training_tab.update_hidden_layers()

    def scale_data(self):
        """标准化数据"""
        input_cols = [self.training_tab.input_list.item(
            i).text() for i in range(self.training_tab.input_list.count())]
        output_cols = [self.training_tab.output_list.item(
            i).text() for i in range(self.training_tab.output_list.count())]

        if not input_cols or not output_cols:
            QMessageBox.warning(self, "错误", "请先选择输入和输出列")
            return False

        # 设置输入输出列，排序在set_columns方法中完成
        success, message = self.data_processor.set_columns(
            input_cols, output_cols)
        if not success:
            QMessageBox.warning(self, "错误", message)
            return False

        # 标准化数据
        success, message = self.data_processor.scale_data()
        if success:
            self.training_tab.info_text.append("数据标准化成功")
            return True
        else:
            QMessageBox.warning(self, "标准化失败", message)
            return False



    def train_model(self):
        """训练模型"""
        # 获取参数并按界面显示的小数位数进行四舍五入处理
        learning_rate = round(
            self.training_tab.learning_rate_spin.value(), 4)  # 保留4位小数
        random_seed = round(
            self.training_tab.random_seed_spin.value(), 1)  # 保留1位小数
        test_ratio = round(
            self.training_tab.test_ratio_spin.value(), 2)  # 保留2位小数

        self.training_tab.info_text.append(f"使用学习率: {learning_rate}")
        self.training_tab.info_text.append(f"使用随机种子: {random_seed}")
        self.training_tab.info_text.append(f"使用测试集比例: {test_ratio}")

        # 训练开始前更新模型状态标签为"模型训练中"
        self.training_tab.model_info_label.setText("模型训练中")
        self.training_tab.model_info_label.setStyleSheet(
            "QLabel { color: orange; font-style: italic; }")
        QApplication.processEvents()  # 确保UI更新

        # 初始化模型管理器（类型由导入语句决定）
        self.model_manager = ModelManager()

        # 获取缩放后的数据
        X_scaled = self.data_processor.X_scaled
        y_scaled = self.data_processor.y_scaled

        # 构建网络层尺寸列表
        input_size = X_scaled.shape[1]
        output_size = y_scaled.shape[1] if len(y_scaled.shape) > 1 else 1
        layer_sizes = [input_size]
        for spin in self.training_tab.hidden_layer_spins:
            layer_sizes.append(spin.value())
        layer_sizes.append(output_size)

        # 显示进度条
        self.training_tab.progress_bar.setVisible(True)
        self.training_tab.progress_bar.setValue(0)  # 重置进度条
        QApplication.processEvents()

        # 定义进度回调函数
        def progress_callback(progress):
            self.training_tab.progress_bar.setValue(progress)
            QApplication.processEvents()

        # 训练模型
        try:
            # 构建可视化保存路径
            visualization_save_path = self.generate_visualization_save_path(layer_sizes)

            # 获取选择的优化算法
            solver = self.training_tab.solver_combo.currentText()

            model, train_losses, test_losses = self.model_manager.train(
                X_scaled, y_scaled, layer_sizes,
                epochs=self.training_tab.epochs_spin.value(),
                batch_size=16,  # 默认批次大小
                test_size=test_ratio,
                lr=learning_rate,
                random_seed=random_seed,
                progress_callback=progress_callback,
                scaler_y=self.data_processor.scaler_y,
                output_columns=self.data_processor.output_columns,
                visualization_save_path=visualization_save_path,
                solver=solver
            )

            # 保存数据处理器信息到模型管理器
            self.model_manager.scaler_X = self.data_processor.scaler_X
            self.model_manager.scaler_y = self.data_processor.scaler_y
            self.model_manager.input_columns = self.data_processor.input_columns
            self.model_manager.output_columns = self.data_processor.output_columns

            success = True
            self.training_tab.info_text.append(
                f"训练完成！训练损失: {train_losses[-1]:.6f}, 测试损失: {test_losses[-1]:.6f}")

            # 生成可视化图表
            fig = self.model_manager.generate_training_visualization(
                train_losses, test_losses,
                X_scaled=X_scaled,
                y_scaled=y_scaled,
                scaler_y=self.data_processor.scaler_y,
                output_columns=self.data_processor.output_columns
            )

        except Exception as e:
            success = False
            fig = None
            self.training_tab.info_text.append(f"训练失败: {str(e)}")
            QMessageBox.warning(self, "训练失败", f"模型训练失败: {str(e)}")

        if success and fig:
            # 使用新窗口显示图表，并在其中显示完成提示
            self.visualization_window = VisualizationWindow(
                fig, show_completion_message=True)
            # 更新预测表格以反映训练时的输入特征
            self.update_manual_input_table()
            # 更新文件导入预测界面中的列对应关系表格
            self.update_column_mappings()
            # 更新模型状态标签
            self.training_tab.model_info_label.setText("模型已训练")
            self.training_tab.model_info_label.setStyleSheet(
                "font-style: italic; color: green;")
        else:
            # 训练失败或被中断，恢复模型状态标签为"模型未训练"
            self.training_tab.model_info_label.setText("模型未训练")
            self.training_tab.model_info_label.setStyleSheet(
                "font-style: italic; color: red;")

        # 隐藏进度条
        self.training_tab.progress_bar.setVisible(False)

        return success

    def generate_visualization_save_path(self, layer_sizes):
        """生成可视化文件的保存路径"""
        # 生成包含输入输出列信息的文件名
        if hasattr(self, 'data_processor') and self.data_processor.input_columns:
            # 使用已经排序好的输入变量名
            input_columns_str = "_".join(self.data_processor.input_columns)
        else:
            input_columns_str = "unknown_input"

        if hasattr(self, 'data_processor') and self.data_processor.output_columns:
            # 使用已经排序好的输出变量名
            output_columns_str = "_".join(
                self.data_processor.output_columns)
        else:
            output_columns_str = "unknown_output"

        # 获取隐藏层数量
        # layer_sizes包含输入层、隐藏层和输出层
        hidden_layers_count = len(layer_sizes) - 2

        # 创建visualizations目录（如果不存在）
        visualization_dir = "NN_models"
        if not os.path.exists(visualization_dir):
            os.makedirs(visualization_dir)

        # 构建完整的保存路径
        visualization_name = f"evaluation_{input_columns_str}__{output_columns_str}__{hidden_layers_count}hidden_layers.png"
        visualization_save_path = os.path.join(
            visualization_dir, visualization_name)
        
        return visualization_save_path
    
    def generate_model_save_path(self):
        """生成模型文件的保存路径"""
        # 生成包含输入输出列信息的文件名
        if hasattr(self, 'data_processor') and self.data_processor.input_columns:
            # 使用已经排序好的输入特征
            input_columns_str = "_".join(self.data_processor.input_columns)
        else:
            input_columns_str = "unknown_input"

        if hasattr(self, 'data_processor') and self.data_processor.output_columns:
            # 使用已经排序好的输出特征
            output_columns_str = "_".join(
                self.data_processor.output_columns)
        else:
            output_columns_str = "unknown_output"

        # 获取隐藏层数量
        hidden_layers_count = 0
        if hasattr(self.model_manager, 'layer_sizes') and self.model_manager.layer_sizes:
            # layer_sizes包含输入层、隐藏层和输出层，所以隐藏层数量是总层数减2
            hidden_layers_count = len(self.model_manager.layer_sizes) - 2
            
        return input_columns_str, output_columns_str, hidden_layers_count
    
    def save_model(self):
        """保存模型"""
        if self.model_manager is None:
            self.training_tab.info_text.append("模型保存失败: 模型管理器未初始化")
            return False

        # 检查模型是否存在（同时支持model和trained_model属性）
        has_model = hasattr(self.model_manager,
                            'model') and self.model_manager.model is not None
        has_trained_model = hasattr(
            self.model_manager, 'trained_model') and self.model_manager.trained_model is not None

        if not has_model and not has_trained_model:
            self.training_tab.info_text.append("模型保存失败: 模型未训练或未加载")
            return False

        try:
            # 创建NN_models目录（如果不存在）
            model_dir = "NN_models"
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)

            # 确定模型类型
            model_type = "scikit-learn" if "Sklearn" in self.model_manager.__class__.__name__ else "PyTorch"
            extension = ".pkl" if "Sklearn" in self.model_manager.__class__.__name__ else ".pth"

            # 使用提取的方法生成模型保存路径的组成部分
            input_columns_str, output_columns_str, hidden_layers_count = self.generate_model_save_path()

            # 构建符合要求的文件名格式: model_Input__Output__{隐藏层数}hidden_layers
            model_name = f"model_{input_columns_str}__{output_columns_str}__{hidden_layers_count}hidden_layers{extension}"
            save_path = os.path.join(model_dir, model_name)

            # 保存模型
            self.model_manager.save_model(save_path)

            # 获取绝对路径并显示
            absolute_save_path = os.path.abspath(save_path)
            self.training_tab.info_text.append(
                f"模型已自动保存: {absolute_save_path}")
            return True
        except Exception as e:
            self.training_tab.info_text.append(f"模型保存失败: {str(e)}")
            return False

    def integrated_process(self):
        """集成标准化、训练、保存功能"""
        self.training_tab.info_text.append("开始集成处理：标准化、训练、保存")

        # 1. 标准化数据
        scale_success = self.scale_data()
        if not scale_success:
            self.training_tab.info_text.append("集成处理失败：数据标准化失败")
            QMessageBox.warning(self, "失败", "数据标准化失败，集成处理终止")
            return

        # 2. 训练模型
        train_success = self.train_model()
        if not train_success:
            self.training_tab.info_text.append("集成处理失败：模型训练失败")
            QMessageBox.warning(self, "失败", "模型训练失败，集成处理终止")
            return

        # 3. 保存模型
        save_success = self.save_model()
        if not save_success:
            self.training_tab.info_text.append("集成处理失败：模型保存失败")
            QMessageBox.warning(self, "失败", "模型保存失败，集成处理终止")
            return

        # 4. 完成所有步骤
        self.training_tab.info_text.append("集成处理完成：标准化、训练、保存均成功")

    def load_model(self):
        """导入模型"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入模型", "", "模型文件 (*.pth *.pkl);;所有文件 (*.*)"
        )

        if file_path:
            try:
                # 根据文件扩展名确定模型类型
                if file_path.endswith('.pth'):
                    model_type = "PyTorch"
                    # 动态导入PyTorch模型管理器
                    import importlib
                    model_manager_torch = importlib.import_module(
                        'model_manager_torch')
                    self.model_manager = model_manager_torch.ModelManagerTorch()
                elif file_path.endswith('.pkl'):
                    model_type = "scikit-learn"
                    # 使用已导入的ModelManager（别名为ModelManagerSklearn）
                    self.model_manager = ModelManager()
                else:
                    # 如果扩展名不确定，让用户选择
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Question)
                    msg.setText("请选择模型类型")
                    msg.setWindowTitle("模型类型选择")
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

                    # 创建模型类型选择下拉框
                    combo = QComboBox()
                    combo.addItems(["PyTorch", "scikit-learn"])
                    msg.layout().addWidget(combo, msg.layout().rowCount(),
                                           0, 1, msg.layout().columnCount())

                    if msg.exec_() == QMessageBox.Ok:
                        model_type = combo.currentText()
                        if model_type == "PyTorch":
                            # 动态导入PyTorch模型管理器
                            import importlib
                            model_manager_torch = importlib.import_module(
                                'model_manager_torch')
                            self.model_manager = model_manager_torch.ModelManagerTorch()
                        else:
                            # 使用已导入的ModelManager（别名为ModelManagerSklearn）
                            self.model_manager = ModelManager()
                    else:
                        return

                # 加载模型前清除原有训练数据
                self.data_processor.df = None
                self.data_processor.columns = []
                self.data_processor.X = None
                self.data_processor.y = None
                self.data_processor.X_scaled = None
                self.data_processor.y_scaled = None

                # 清除训练标签页上的文件路径信息
                self.training_tab.file_path_label.setText("未选择文件")

                # 在信息文本中记录清除操作
                self.training_tab.info_text.append("已清除原有训练数据")

                # 加载模型
                self.model_manager.load_model(file_path)

                # 移除对model_type_combo的引用，因为TrainingTab中没有这个属性

                self.training_tab.info_text.append(f"模型导入成功: {file_path}")
                self.training_tab.info_text.append(f"模型类型: {model_type}")
                # 设置模型状态标签为"已加载"并改变颜色
                self.training_tab.model_info_label.setText("模型已加载")
                self.training_tab.model_info_label.setStyleSheet(
                    "font-style: italic; color: green;")
                QApplication.processEvents()

                # 加载模型中的数据处理器信息到数据处理器
                if hasattr(self.model_manager, 'scaler_X') and self.model_manager.scaler_X is not None:
                    self.data_processor.scaler_X = self.model_manager.scaler_X
                    self.training_tab.info_text.append("已加载输入特征缩放器")

                if hasattr(self.model_manager, 'scaler_y') and self.model_manager.scaler_y is not None:
                    self.data_processor.scaler_y = self.model_manager.scaler_y
                    self.training_tab.info_text.append("已加载目标变量缩放器")

                if hasattr(self.model_manager, 'input_columns') and self.model_manager.input_columns is not None:
                    self.data_processor.input_columns = self.model_manager.input_columns
                    self.training_tab.info_text.append(
                        f"已加载输入列: {', '.join(self.model_manager.input_columns)}")

                if hasattr(self.model_manager, 'output_columns') and self.model_manager.output_columns is not None:
                    self.data_processor.output_columns = self.model_manager.output_columns
                    self.training_tab.info_text.append(
                        f"已加载输出列: {', '.join(self.model_manager.output_columns)}")

                # 更新界面
                self.update_input_output_columns()
                # 更新预测表格以反映导入模型的输入特征
                self.update_manual_input_table()
                # 更新文件导入预测界面中的列对应关系表格
                self.update_column_mappings()

                # 切换到预测选项卡
                self.switch_to_prediction()

                QMessageBox.information(self, "成功", "模型导入完成")

            except Exception as e:
                self.training_tab.info_text.append(f"模型导入失败: {str(e)}")
                QMessageBox.warning(self, "导入失败", f"模型导入失败: {str(e)}")

    def update_input_output_columns(self):
        """更新输入输出列显示"""
        # 清空现有列表
        self.training_tab.available_list.clear()
        self.training_tab.input_list.clear()
        self.training_tab.output_list.clear()

        # 添加所有列到可用列列表
        for col in self.data_processor.columns:
            item = QListWidgetItem(col)
            self.training_tab.available_list.addItem(item)

        # 添加输入列到输入列列表
        for col in self.data_processor.input_columns:
            item = QListWidgetItem(col)
            self.training_tab.input_list.addItem(item)

        # 添加输出列到输出列列表
        for col in self.data_processor.output_columns:
            item = QListWidgetItem(col)
            self.training_tab.output_list.addItem(item)

    def switch_to_prediction(self):
        """切换到预测界面"""
        if self.model_manager is None:
            QMessageBox.warning(self, "警告", "没有训练好的模型，是否继续？")

        # 切换到预测选项卡（索引2而不是1）
        self.tab_widget.setCurrentIndex(2)

        # 更新预测界面的输入表格
        self.update_manual_input_table()

    def switch_to_training(self):
        """切换到训练界面"""
        self.tab_widget.setCurrentIndex(0)

    def switch_to_manual_input(self):
        """切换到手动输入"""
        self.prediction_content.setCurrentIndex(0)

    def switch_to_file_input(self):
        """切换到文件输入"""
        self.prediction_content.setCurrentIndex(1)

    def update_manual_input_table(self):
        """更新手动输入表格"""
        if not self.data_processor.input_columns:
            return

        # 设置表格列数
        self.prediction_tab.manual_input_table.setColumnCount(
            len(self.data_processor.input_columns))

        # 设置表格行数等于输入变量的数量
        num_input_vars = len(self.data_processor.input_columns)
        self.prediction_tab.manual_input_table.setRowCount(num_input_vars)

        # 设置表头
        self.prediction_tab.manual_input_table.setHorizontalHeaderLabels(
            self.data_processor.input_columns)

        # 确保所有行都有单元格
        for row in range(self.prediction_tab.manual_input_table.rowCount()):
            for i, col in enumerate(self.data_processor.input_columns):
                if self.prediction_tab.manual_input_table.item(row, i) is None:
                    item = QTableWidgetItem("")
                    self.prediction_tab.manual_input_table.setItem(
                        row, i, item)

        # 自适应列宽
        self.prediction_tab.manual_input_table.resizeColumnsToContents()

    def add_input_row(self):
        """添加新的输入行"""
        if not self.data_processor.input_columns:
            return

        # 使用正确的表格引用
        table = self.prediction_tab.manual_input_table
        row_count = table.rowCount()
        table.insertRow(row_count)

        # 设置新行的单元格
        for i, col in enumerate(self.data_processor.input_columns):
            item = QTableWidgetItem("")
            table.setItem(row_count, i, item)

        # 自适应列宽
        table.resizeColumnsToContents()

    def remove_input_row(self):
        """删除选中的输入行"""
        # 使用正确的表格引用
        table = self.prediction_tab.manual_input_table
        selected_rows = set()
        for item in table.selectedItems():
            selected_rows.add(item.row())

        # 按行号降序删除，避免索引混乱
        for row in sorted(selected_rows, reverse=True):
            table.removeRow(row)

        # 如果没有行，添加一行
        if table.rowCount() == 0:
            table.setRowCount(1)
            for i, col in enumerate(self.data_processor.input_columns):
                item = QTableWidgetItem("")
                table.setItem(0, i, item)

    def manual_predict(self):
        """手动输入预测"""
        if self.model_manager is None:
            QMessageBox.warning(self, "错误", "请先训练或导入模型")
            return

        if not self.data_processor.input_columns:
            QMessageBox.warning(self, "错误", "模型没有输入列信息")
            return

        # 获取所有行的输入值，但只处理数据完整的行
        all_inputs = []
        valid_rows = []  # 记录有效行的索引

        for row in range(self.prediction_tab.manual_input_table.rowCount()):
            inputs = []
            is_valid = True

            for i in range(self.prediction_tab.manual_input_table.columnCount()):
                item = self.prediction_tab.manual_input_table.item(row, i)
                if item and item.text():
                    try:
                        inputs.append(float(item.text()))
                    except ValueError:
                        is_valid = False
                        break  # 该行有无效数字，跳过
                else:
                    is_valid = False
                    break  # 该行有空值，跳过

            if is_valid:
                all_inputs.append(inputs)
                valid_rows.append(row)

        if not all_inputs:
            QMessageBox.warning(self, "错误", "没有完整有效的输入数据行")
            return

        try:
            # 转换为numpy数组并标准化
            input_array = np.array(all_inputs)
            input_scaled = self.data_processor.scaler_X.transform(input_array)

            # 使用模型管理器进行预测
            outputs = self.model_manager.predict(input_scaled)

            # 对预测结果进行去标准化处理
            outputs = self.data_processor.scaler_y.inverse_transform(outputs)

            # 显示结果表格
            columns = self.data_processor.input_columns + self.data_processor.output_columns
            rows = outputs.shape[0]

            self.prediction_tab.manual_result_table.setRowCount(rows)
            self.prediction_tab.manual_result_table.setColumnCount(
                len(columns))
            self.prediction_tab.manual_result_table.setHorizontalHeaderLabels(
                columns)

            # 创建预测结果DataFrame
            self.pred_df = pd.DataFrame(
                columns=self.data_processor.input_columns + self.data_processor.output_columns)

            # 填充输入和输出数据到表格和DataFrame
            for row_idx in range(rows):
                # 填充输入数据
                for i, col in enumerate(self.data_processor.input_columns):
                    value = all_inputs[row_idx][i]
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # 设置为只读
                    self.prediction_tab.manual_result_table.setItem(
                        row_idx, i, item)
                    self.pred_df.at[row_idx, col] = value

                # 填充输出数据
                for i, col in enumerate(self.data_processor.output_columns):
                    # 处理一维或二维输出数组
                    if len(outputs.shape) > 1:
                        value = outputs[row_idx][i]
                    else:
                        # outputs是一维数组
                        if len(self.data_processor.output_columns) == 1:
                            value = outputs[row_idx]
                        else:
                            # 如果一维数组但有多个输出列，这是异常情况
                            # 使用outputs的第一个值作为所有输出列的值
                            value = outputs[row_idx]
                    item = QTableWidgetItem(f"{value:.6f}")
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # 设置为只读
                    self.prediction_tab.manual_result_table.setItem(
                        row_idx, i + len(self.data_processor.input_columns), item)
                    self.pred_df.at[row_idx, col] = value

            # 自适应列宽
            self.prediction_tab.manual_result_table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "预测失败", str(e))

    def select_prediction_file(self):
        """选择预测文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择预测文件", "", "数据文件 (*.csv *.xlsx *.xls)"
        )

        if file_path:
            self.pred_file_path = file_path
            # 使用正确的标签引用
            self.prediction_tab.file_path_label.setText(
                f"已选择: {os.path.basename(file_path)}")

            # 加载文件并获取列
            self.temp_processor = DataProcessor()
            success, message = self.temp_processor.load_file(file_path)
            if success:
                self.file_columns = self.temp_processor.columns
                self.update_column_mappings()
            else:
                QMessageBox.warning(self, "加载失败", message)

    def update_column_mappings(self):
        """更新列对应关系设置"""
        if not self.data_processor.input_columns:
            return

        # 获取预测选项卡中的输入列表格
        table = self.prediction_tab.input_columns_table

        # 设置表格行数和列数
        table.setRowCount(len(self.data_processor.input_columns))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["输入参数", "文件列"])

        # 为每个模型输入列创建下拉菜单
        self.column_mappings = {}
        for i, input_col in enumerate(self.data_processor.input_columns):
            # 设置输入参数列
            param_item = QTableWidgetItem(input_col)
            param_item.setFlags(param_item.flags() ^
                                Qt.ItemIsEditable)  # 设置为只读
            table.setItem(i, 0, param_item)

            # 设置文件列下拉菜单
            combo_box = QComboBox()
            combo_box.addItem("请选择列...")

            # 自动匹配相同列名
            matched_index = 0  # 默认选择第一个选项

            # 如果有file_columns，添加到下拉菜单中
            if hasattr(self, 'file_columns') and self.file_columns:
                # start=1 因为索引0是"请选择列..."
                for index, file_col in enumerate(self.file_columns, start=1):
                    combo_box.addItem(file_col)
                    if file_col == input_col:
                        matched_index = index  # 找到匹配的列名，记录索引

            combo_box.setCurrentIndex(matched_index)  # 设置默认选择
            self.column_mappings[input_col] = combo_box

            # 将下拉菜单添加到表格单元格
            table.setCellWidget(i, 1, combo_box)

        # 自适应列宽
        table.resizeColumnsToContents()

    def file_predict(self):
        """文件预测"""
        if self.model_manager is None:
            QMessageBox.warning(self, "错误", "请先训练或导入模型")
            return

        if not hasattr(self, 'pred_file_path'):
            QMessageBox.warning(self, "错误", "请先选择预测文件")
            return

        # 检查是否有模型输入列
        if not self.data_processor.input_columns:
            QMessageBox.warning(self, "错误", "模型没有输入列信息")
            return

        # 获取列对应关系
        selected_cols = []
        for input_col in self.data_processor.input_columns:
            if input_col not in self.column_mappings:
                QMessageBox.warning(self, "错误", "列对应关系设置不完整")
                return

            combo_box = self.column_mappings[input_col]
            selected_col = combo_box.currentText()
            if selected_col == "请选择列...":
                QMessageBox.warning(self, "错误", f"请为{input_col}选择对应的文件列")
                return
            selected_cols.append(selected_col)

        try:
            # 加载完整数据
            df = self.temp_processor.df

            # 检查所有选择的列是否存在
            for col in selected_cols:
                if col not in df.columns:
                    QMessageBox.warning(self, "错误", f"文件中不存在列: {col}")
                    return

            # 提取数据并转换为numpy数组
            data = df[selected_cols].values.astype(np.float64)

            # 数据验证：检查是否有无效值
            if np.isnan(data).any() or np.isinf(data).any():
                QMessageBox.warning(self, "错误", "数据中包含无效值（NaN或无穷大）")
                return

            # 标准化数据
            data_scaled = self.data_processor.scaler_X.transform(data)

            # 执行预测 - 使用模型管理器统一接口
            predictions = self.model_manager.predict(data_scaled)

            # 对预测结果进行去标准化处理
            predictions = self.data_processor.scaler_y.inverse_transform(
                predictions)

            # 创建结果DataFrame，保留原始表格并添加预测结果列
            self.pred_df = df.copy()

            # 为每个输出列添加预测结果，列名为'pred_'+输出参数名
            for i, output_col in enumerate(self.data_processor.output_columns):
                pred_col_name = f'pred_{output_col}'
                self.pred_df[pred_col_name] = predictions[:, i]

            # 显示结果表格
            self.display_prediction_results(self.pred_df)

            QMessageBox.information(self, "成功", "预测完成")

        except ValueError as e:
            QMessageBox.warning(self, "数据错误", f"数据格式错误: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "预测失败", str(e))

    def display_prediction_results(self, df):
        """显示预测结果表格，最多显示50行"""
        # 保存完整的预测结果
        self.pred_df = df.copy()

        # 设置表格行数列数
        table = self.prediction_tab.file_result_table

        # 清空表格并设置新的行列数
        table.setRowCount(0)
        table.setColumnCount(df.shape[1])

        # 设置表头
        table.setHorizontalHeaderLabels(df.columns)

        # 最多显示50行
        max_display_rows = 50
        display_rows = min(df.shape[0], max_display_rows)
        table.setRowCount(display_rows)

        # 保存当前显示的行数
        self.displayed_rows = display_rows

        # 填充数据
        for i in range(display_rows):
            for j in range(df.shape[1]):
                value = df.iloc[i, j]
                if isinstance(value, (float, np.float64)):
                    # 对浮点数进行适当的格式化，避免过长的小数位数
                    item = QTableWidgetItem(f"{value:.6f}")
                else:
                    item = QTableWidgetItem(str(value))
                table.setItem(i, j, item)

        # 显示提示信息
        if df.shape[0] > max_display_rows:
            QMessageBox.information(
                self, "提示", f"数据行数过多（共{df.shape[0]}行），只显示前{max_display_rows}行")

        # 只对显示的行进行自适应列宽，避免性能问题
        table.resizeColumnsToContents()

        # 设置表格为只读
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 连接信号
        try:
            table.customContextMenuRequested.disconnect()
        except (RuntimeError, AttributeError):
            pass
        table.customContextMenuRequested.connect(
            lambda pos: self.show_table_context_menu(table, pos))
        
        # 连接行和列删除信号
        try:
            # 移除旧的连接（如果存在）
            table.rows_deleted.disconnect()
        except (RuntimeError, AttributeError):
            pass
        try:
            table.columns_deleted.disconnect()
        except (RuntimeError, AttributeError):
            pass
        
        # 连接新的信号
        if hasattr(table, 'rows_deleted'):
            table.rows_deleted.connect(self.handle_table_rows_deleted)
        if hasattr(table, 'columns_deleted'):
            table.columns_deleted.connect(self.handle_table_columns_deleted)

    def show_table_context_menu(self, table, position):
        """显示表格上下文菜单"""
        menu = QMenu(table)

        copy_action = menu.addAction("复制")
        copy_action.triggered.connect(lambda: self.copy_table_content(table))

        # 预测结果表格允许删除行和列
        menu.addSeparator()
        delete_row_action = menu.addAction("删除选中行")
        delete_row_action.triggered.connect(
            lambda: self.delete_table_rows(table))

        delete_col_action = menu.addAction("删除选中列")
        delete_col_action.triggered.connect(
            lambda: self.delete_table_columns(table))

        menu.exec_(table.viewport().mapToGlobal(position))

    def copy_table_content(self, table):
        """复制表格内容"""
        selected_ranges = table.selectedRanges()
        if not selected_ranges:
            return

        selected_range = selected_ranges[0]
        start_row = selected_range.topRow()
        end_row = selected_range.bottomRow()
        start_col = selected_range.leftColumn()
        end_col = selected_range.rightColumn()

        clipboard_content = ""
        for row in range(start_row, end_row + 1):
            row_content = []
            for col in range(start_col, end_col + 1):
                item = table.item(row, col)
                row_content.append(item.text() if item else "")
            clipboard_content += "\t".join(row_content) + "\n"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_content)

    def delete_table_rows(self, table):
        """删除表格行，真实作用在完整的DataFrame上，并自动补充隐藏行"""
        if not hasattr(self, 'pred_df'):
            QMessageBox.warning(self, "错误", "没有可删除的数据")
            return

        selected_rows = set()

        # 从选中的项中获取行号
        for item in table.selectedItems():
            selected_rows.add(item.row())

        # 如果没有选中任何项，检查当前行
        if not selected_rows:
            current_row = table.currentRow()
            if current_row >= 0:
                selected_rows.add(current_row)

        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要删除的行")
            return

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的{len(selected_rows)}行吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 按降序删除，避免行索引变化影响后续删除
        sorted_rows = sorted(selected_rows, reverse=True)

        # 从完整的DataFrame中删除对应的行
        self.pred_df = self.pred_df.drop(index=self.pred_df.index[sorted_rows])
        # 重置索引
        self.pred_df = self.pred_df.reset_index(drop=True)

        # 从表格中删除行
        for row in sorted_rows:
            table.removeRow(row)

        # 检查是否需要补充显示行
        max_display_rows = 50
        current_display_rows = table.rowCount()
        total_rows = self.pred_df.shape[0]

        # 如果还有隐藏行，补充显示
        if current_display_rows < max_display_rows and total_rows > current_display_rows:
            rows_to_add = min(
                max_display_rows - current_display_rows, total_rows - current_display_rows)

            # 扩展表格行数
            table.setRowCount(current_display_rows + rows_to_add)

            # 填充新行数据
            for i in range(current_display_rows, current_display_rows + rows_to_add):
                for j in range(self.pred_df.shape[1]):
                    value = self.pred_df.iloc[i, j]
                    if isinstance(value, (float, np.float64)):
                        item = QTableWidgetItem(f"{value:.6f}")
                    else:
                        item = QTableWidgetItem(str(value))
                    table.setItem(i, j, item)

        # 更新显示的行数
        self.displayed_rows = table.rowCount()

        # 自适应列宽
        table.resizeColumnsToContents()

    def delete_table_columns(self, table):
        """删除表格列，真实作用在完整的DataFrame上"""
        if not hasattr(self, 'pred_df'):
            QMessageBox.warning(self, "错误", "没有可删除的数据")
            return

        selected_cols = set()

        # 从选中的项中获取列号
        for item in table.selectedItems():
            selected_cols.add(item.column())

        # 如果没有选中任何项，检查当前列
        if not selected_cols:
            current_col = table.currentColumn()
            if current_col >= 0:
                selected_cols.add(current_col)

        if not selected_cols:
            QMessageBox.information(self, "提示", "请先选择要删除的列")
            return

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的{len(selected_cols)}列吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 按降序删除，避免列索引变化影响后续删除
        sorted_cols = sorted(selected_cols, reverse=True)

        # 从完整的DataFrame中删除对应的列
        self.pred_df = self.pred_df.drop(
            columns=self.pred_df.columns[sorted_cols])

        # 从表格中删除列
        for col in sorted_cols:
            table.removeColumn(col)

        # 更新表头
        table.setHorizontalHeaderLabels(self.pred_df.columns)

        # 自适应列宽
        table.resizeColumnsToContents()

    def update_table_display(self, table):
        """更新表格显示，确保最多显示50行"""
        if not hasattr(self, 'pred_df'):
            return

        max_display_rows = 50
        display_rows = min(self.pred_df.shape[0], max_display_rows)

        # 清空表格
        table.setRowCount(0)
        table.setColumnCount(self.pred_df.shape[1])
        table.setHorizontalHeaderLabels(self.pred_df.columns)
        table.setRowCount(display_rows)

        # 填充数据
        for i in range(display_rows):
            for j in range(self.pred_df.shape[1]):
                value = self.pred_df.iloc[i, j]
                if isinstance(value, (float, np.float64)):
                    item = QTableWidgetItem(f"{value:.6f}")
                else:
                    item = QTableWidgetItem(str(value))
                table.setItem(i, j, item)

        # 自适应列宽
        table.resizeColumnsToContents()

    def eventFilter(self, source, event):
        """事件过滤器，用于处理表格的复制操作"""
        if event.type() == QEvent.KeyPress:
            # 检查是否按下了Ctrl+C（复制）
            if event.matches(QKeySequence.Copy):
                if isinstance(source, QTableWidget):
                    self.copy_table_content(source)
                    return True
        return super().eventFilter(source, event)

    def handle_table_rows_deleted(self, rows):
        """处理表格行删除事件，更新完整的DataFrame"""
        self.delete_table_rows(self.prediction_tab.file_result_table)
        
    def handle_table_columns_deleted(self, columns):
        """处理表格列删除事件，更新完整的DataFrame"""
        self.delete_table_columns(self.prediction_tab.file_result_table)


# 主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
