import sys
import os
from PySide6.QtWidgets import (QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QPushButton,
                               QLabel, QTableWidget, QStackedWidget, QFileDialog, QMenu, QMessageBox,
                               QAbstractItemView, QHeaderView, QTableWidgetItem, QApplication)
from PySide6.QtCore import Qt, Signal, QEvent, QPoint, QItemSelection
from PySide6.QtGui import (QAction, QKeySequence, QGuiApplication, QClipboard,
                           QFont, QColor, QPalette, QBrush, QShortcut)
import pandas as pd

# 导入新创建的表格类
from excel_like_table import ExcelLikeTableWidget
from styles import StyleManager


class PredictionTab(QWidget):
    manual_predict_signal = Signal()
    file_predict_signal = Signal()
    export_results_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.prediction_data = None
        self.setup_ui()

    def setup_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建预测方式选择区域
        prediction_mode_layout = QHBoxLayout()

        manual_input_btn = QPushButton("手动输入")
        manual_input_btn.setStyleSheet(StyleManager.get_button_style("blue_border") + StyleManager.get_level2_style())
        manual_input_btn.clicked.connect(self.switch_to_manual_input)

        file_input_btn = QPushButton("文件导入")
        file_input_btn.setStyleSheet(StyleManager.get_button_style("blue_border") + StyleManager.get_level2_style())
        file_input_btn.clicked.connect(self.switch_to_file_input)
        
        # 设置按钮字体与标签页字体相同
        if self.parent and hasattr(self.parent, 'tab_widget'):
            tab_font = self.parent.tab_widget.font()
            manual_input_btn.setFont(tab_font)
            file_input_btn.setFont(tab_font)

        prediction_mode_layout.addWidget(manual_input_btn)
        prediction_mode_layout.addWidget(file_input_btn)
        prediction_mode_layout.addStretch()

        # 创建预测内容堆叠窗口
        self.prediction_content = QStackedWidget()

        # 创建手动输入界面
        self.manual_input_widget = QWidget()
        self.setup_manual_input_ui()

        # 创建文件输入界面
        self.file_input_widget = QWidget()
        self.setup_file_input_ui()

        # 添加界面到堆叠窗口
        self.prediction_content.addWidget(self.manual_input_widget)
        self.prediction_content.addWidget(self.file_input_widget)

        # 添加所有组件到主布局
        main_layout.addLayout(prediction_mode_layout)
        main_layout.addWidget(self.prediction_content)

    def setup_manual_input_ui(self):
        # 创建手动输入界面布局
        manual_layout = QVBoxLayout(self.manual_input_widget)

        # 创建表格区域的水平布局（左：输入表格，右：结果表格）
        tables_layout = QHBoxLayout()

        # 创建输入表格
        input_group = QGroupBox("输入参数")
        input_layout = QVBoxLayout(input_group)

        # 使用新创建的ExcelLikeTableWidget代替QTableWidget，设置允许行扩展但禁止列扩展
        self.manual_input_table = ExcelLikeTableWidget(4, 4, ["参数", "值", "单位", "说明"], self, expand_rows=True, expand_cols=False)
        self.manual_input_table.setMinimumHeight(300)
        # 确保表格控件获得焦点，以便快捷键正常工作
        self.manual_input_table.setFocusPolicy(Qt.StrongFocus)
        self.manual_input_table.setFocus()
        # 为表格重新设置快捷键，确保在prediction_tab上下文中正常工作
        self.setup_table_shortcuts(self.manual_input_table)
        # 为表格安装事件过滤器，确保快捷键能被正确处理
        self.manual_input_table.installEventFilter(self)

        input_layout.addWidget(self.manual_input_table)

        # 添加行操作按钮，位于左侧
        button_layout = QHBoxLayout()# 添加行操作按钮，位于左侧
        add_row_btn = QPushButton("添加行")
        add_row_btn.setStyleSheet(StyleManager.get_button_style("green_border") + StyleManager.get_level3_style())
        add_row_btn.clicked.connect(self.add_manual_input_row)
        button_layout.addWidget(add_row_btn)
        
        delete_row_btn = QPushButton("删除行")
        delete_row_btn.setStyleSheet(StyleManager.get_button_style("red_border") + StyleManager.get_level3_style())
        delete_row_btn.clicked.connect(self.delete_manual_input_row)
        button_layout.addWidget(delete_row_btn)
        
        input_layout.addLayout(button_layout)
        input_layout.setAlignment(button_layout, Qt.AlignLeft)

        # 创建结果显示区域
        result_group = QGroupBox("预测结果")
        result_layout = QVBoxLayout(result_group)

        # 使用ExcelLikeTableWidget类支持区域选择和列扩展
        self.manual_result_table = ExcelLikeTableWidget(1, 2, ["指标", "预测值"], self, expand_rows=True, expand_cols=False)
        self.manual_result_table.setMinimumHeight(300)

        # 设置表格不可编辑但支持区域选择
        self.manual_result_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers)
        self.manual_result_table.setAlternatingRowColors(True)  # 交替行颜色
        # 确保表格控件获得焦点，以便快捷键正常工作
        self.manual_result_table.setFocusPolicy(Qt.StrongFocus)
        # 为表格重新设置快捷键，确保在prediction_tab上下文中正常工作
        self.setup_table_shortcuts(self.manual_result_table)
        # 为表格安装事件过滤器，确保快捷键能被正确处理
        self.manual_result_table.installEventFilter(self)

        result_layout.addWidget(self.manual_result_table)

        # 为输出表格添加行操作按钮，位于左侧
        result_button_layout = QHBoxLayout()# 为输出表格添加行操作按钮，位于左侧
        result_add_row_btn = QPushButton("添加行")
        result_add_row_btn.setStyleSheet(StyleManager.get_button_style("green_border") + StyleManager.get_level3_style())
        result_add_row_btn.clicked.connect(self.manual_result_table.add_row)
        result_button_layout.addWidget(result_add_row_btn)
        
        result_delete_row_btn = QPushButton("删除行")
        result_delete_row_btn.setStyleSheet(StyleManager.get_button_style("red_border") + StyleManager.get_level3_style())
        result_delete_row_btn.clicked.connect(self.manual_result_table.delete_selected_rows)
        result_button_layout.addWidget(result_delete_row_btn)
        
        result_layout.addLayout(result_button_layout)
        result_layout.setAlignment(result_button_layout, Qt.AlignLeft)

        # 移除原有的导出按钮，将在底部与预测按钮一起排版

        # 将输入和结果表格添加到水平布局
        tables_layout.addWidget(input_group, stretch=1)
        tables_layout.addWidget(result_group, stretch=1)

        # 创建底部按钮布局
        bottom_button_layout = QHBoxLayout()
        
        # 创建大尺寸的预测按钮
        predict_btn = QPushButton("开始预测")
        predict_btn.clicked.connect(self.manual_predict_signal.emit)
        predict_btn.setMinimumHeight(50)
        predict_btn.setStyleSheet(StyleManager.get_button_style("primary") + StyleManager.get_level2_style())
        
        # 创建大尺寸的导出结果按钮
        export_btn = QPushButton("导出结果")
        export_btn.clicked.connect(self.export_results)
        export_btn.setMinimumHeight(50)
        export_btn.setStyleSheet(StyleManager.get_button_style("primary") + StyleManager.get_level2_style())
        
        # 将按钮添加到底部布局，各占一半空间
        bottom_button_layout.addWidget(predict_btn, stretch=1)
        bottom_button_layout.addWidget(export_btn, stretch=1)

        # 添加所有组件到手动输入界面布局
        manual_layout.addLayout(tables_layout)
        manual_layout.addLayout(bottom_button_layout)

    def setup_file_input_ui(self):
        # 创建文件输入界面布局
        file_layout = QVBoxLayout(self.file_input_widget)

        # 创建水平布局来容纳文件选择和列对应关系区域
        top_layout = QHBoxLayout()

        # 创建文件选择区域（左边一半）
        file_group = QGroupBox("文件选择")
        # 不设置固定最大宽度，使用stretch参数控制宽度比例
        file_vertical_layout = QVBoxLayout(file_group)

        self.file_path_label = QLabel("未选择文件")
        self.file_path_label.setStyleSheet("color: gray;")
        self.file_path_label.setAlignment(Qt.AlignCenter)

        browse_btn = QPushButton("导入表格文件")
        browse_btn.setStyleSheet(StyleManager.get_button_style("green_border") + StyleManager.get_level3_style())
        browse_btn.clicked.connect(self.select_prediction_file_signal)
        browse_btn.setMinimumHeight(50)

        # 文件选择区域采用垂直布局：第一行文件名，第二行导入按钮
        file_vertical_layout.addWidget(self.file_path_label)
        file_vertical_layout.addWidget(browse_btn, alignment=Qt.AlignCenter)

        # 创建列对应关系设置区域（右边一半）
        column_group = QGroupBox("列对应关系")
        # 设置列对应关系框的最大高度，使其只占用小区域
        column_group.setMaximumHeight(200)
        column_layout = QHBoxLayout(column_group)

        # 使用ExcelLikeTableWidget代替QTableWidget
        self.input_columns_table = ExcelLikeTableWidget(1, 2, ["输入参数", "文件列"], self)
        # 确保表格控件获得焦点，以便快捷键正常工作
        self.input_columns_table.setFocusPolicy(Qt.StrongFocus)
        # 为表格重新设置快捷键，确保在prediction_tab上下文中正常工作
        self.setup_table_shortcuts(self.input_columns_table)
        # 为表格安装事件过滤器，确保快捷键能被正确处理
        self.input_columns_table.installEventFilter(self)

        # 将文件选择和列对应关系区域添加到水平布局
        top_layout.addWidget(file_group, stretch=1)
        top_layout.addWidget(column_group, stretch=1)

        column_layout.addWidget(self.input_columns_table)

        # 将顶部水平布局（文件选择和列对应关系）添加到主布局
        file_layout.addLayout(top_layout)

        # 创建结果显示区域
        result_group = QGroupBox("预测结果")
        file_layout.addWidget(result_group)

        result_layout = QVBoxLayout(result_group)

        # 使用ExcelLikeTableWidget类支持区域选择
        self.file_result_table = ExcelLikeTableWidget(1, 2, ["指标", "预测值"], self)
        self.file_result_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers)
        # 确保表格控件获得焦点，以便快捷键正常工作
        self.file_result_table.setFocusPolicy(Qt.StrongFocus)
        # 为表格重新设置快捷键，确保在prediction_tab上下文中正常工作
        self.setup_table_shortcuts(self.file_result_table)
        # 为表格安装事件过滤器，确保快捷键能被正确处理
        self.file_result_table.installEventFilter(self)

        result_layout.addWidget(self.file_result_table)

        # 添加操作按钮到结果表格
        result_button_layout = QHBoxLayout()
        
        # 添加删除行按钮
        delete_row_btn = QPushButton("删除行")
        delete_row_btn.setStyleSheet(StyleManager.get_button_style("red_border") + StyleManager.get_level3_style())
        delete_row_btn.clicked.connect(self.file_result_table.delete_selected_rows)
        delete_row_btn.setMaximumWidth(80)

        # 添加删除列按钮
        delete_col_btn = QPushButton("删除列")
        delete_col_btn.setStyleSheet(StyleManager.get_button_style("red_border") + StyleManager.get_level3_style())
        delete_col_btn.clicked.connect(self.file_result_table.delete_selected_columns)
        delete_col_btn.setMaximumWidth(80)
        
        # 将按钮添加到布局
        result_button_layout.addWidget(delete_row_btn)
        result_button_layout.addWidget(delete_col_btn)
        result_button_layout.addStretch(1)  # 添加弹性空间
        
        result_layout.addLayout(result_button_layout)
        result_layout.setAlignment(result_button_layout, Qt.AlignRight)

        # 创建底部按钮布局
        bottom_button_layout = QHBoxLayout()
        
        # 创建大尺寸的导出结果按钮
        export_btn = QPushButton("导出结果")
        export_btn.setStyleSheet(StyleManager.get_button_style("primary") + StyleManager.get_level2_style())
        export_btn.clicked.connect(self.export_results)
        export_btn.setMinimumHeight(50)
        
        # 创建大尺寸的预测按钮
        predict_btn = QPushButton("开始预测")
        predict_btn.setStyleSheet(StyleManager.get_button_style("primary") + StyleManager.get_level2_style())
        predict_btn.clicked.connect(self.file_predict_signal.emit)
        predict_btn.setMinimumHeight(50)
        
        # 将按钮添加到底部布局，各占一半空间
        bottom_button_layout.addWidget(predict_btn, stretch=1)
        bottom_button_layout.addWidget(export_btn, stretch=1)
        
        # 添加底部布局到文件布局
        file_layout.addLayout(bottom_button_layout)

    def switch_to_manual_input(self):
        """切换到手动输入"""
        self.prediction_content.setCurrentIndex(0)

    def switch_to_file_input(self):
        """切换到文件输入"""
        self.prediction_content.setCurrentIndex(1)

    def update_manual_input_table(self):
        """更新手动输入表格"""
        pass  # 这个方法会在MainWindow中实现

    def add_manual_input_row(self):
        """添加新的手动输入行"""
        # 直接使用ExcelLikeTableWidget的add_row方法
        self.manual_input_table.add_row()
                
    def delete_manual_input_row(self):
        """删除手动输入行"""
        # 直接使用ExcelLikeTableWidget的delete_selected_rows方法
        self.manual_input_table.delete_selected_rows()

    def select_prediction_file_signal(self):
        """选择预测文件的信号"""
        if hasattr(self.parent, 'select_prediction_file'):
            self.parent.select_prediction_file()

    def export_selected_results_signal(self):
        """导出选中结果的信号"""
        self.export_results()

    def export_results(self):
        """导出预测结果，支持xlsx、csv、xls格式"""
        # 检查是否是文件输入模式，且存在完整的预测结果
        if self.prediction_content.currentIndex() == 1 and hasattr(self.parent, 'pred_df'):
            # 文件输入模式，使用完整的预测结果DataFrame
            df = self.parent.pred_df
        else:
            # 手动输入模式，从表格中获取数据
            table = self.manual_result_table
            
            # 获取当前表格数据
            data = []
            headers = []

            # 获取表头
            for col in range(table.columnCount()):
                header_item = table.horizontalHeaderItem(col)
                headers.append(header_item.text() if header_item else f"列{col+1}")

            # 获取数据
            for row in range(table.rowCount()):
                row_data = []
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            if not data:
                QMessageBox.information(self, "提示", "表格中没有数据可导出")
                return

            # 创建DataFrame
            df = pd.DataFrame(data, columns=headers)

        # 选择导出文件路径和格式，默认路径为当前文件夹
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_file_path = os.path.join(current_dir, "output.xlsx")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出预测结果", default_file_path,
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # 根据文件扩展名选择导出格式
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                # 使用pandas导出到Excel
                df.to_excel(file_path, index=False)
            elif file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                # 默认导出为xlsx
                if '.' not in file_path:
                    file_path += '.xlsx'
                # 使用pandas导出到Excel
                df.to_excel(file_path, index=False)

            QMessageBox.information(self, "导出成功", f"数据已成功导出到:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"导出文件时出错:\n{str(e)}")

    def setup_table_shortcuts(self, table):
        """为表格设置快捷键，实现与Excel一致的操作"""
        # 注意：Ctrl+C和Ctrl+V快捷键已经在ExcelLikeTableWidget类的keyPressEvent方法中处理
        # 这里不再重复设置，避免冲突
        
        # 根据表格的expand_rows参数来决定是否设置行操作快捷键
        if hasattr(table, 'expand_rows') and table.expand_rows:
            table.add_row_shortcut = QShortcut(QKeySequence("Ctrl++"), table)
            table.add_row_shortcut.activated.connect(table.add_row)
            
            table.del_row_shortcut = QShortcut(QKeySequence("Ctrl+-"), table)
            table.del_row_shortcut.activated.connect(table.delete_selected_rows)
        
        # 根据表格的expand_cols参数来决定是否设置列操作快捷键
        if hasattr(table, 'expand_cols') and table.expand_cols:
            table.add_col_shortcut = QShortcut(QKeySequence("Ctrl+Shift++"), table)
            table.add_col_shortcut.activated.connect(table.add_column)
            
            table.del_col_shortcut = QShortcut(QKeySequence("Ctrl+Shift+-"), table)
            table.del_col_shortcut.activated.connect(table.delete_selected_columns)
    
    def eventFilter(self, obj, event):
        """事件过滤器，处理表格的快捷键，实现与Excel一致的操作"""
        # 注意：Ctrl+C和Ctrl+V快捷键已经在ExcelLikeTableWidget类的keyPressEvent方法中处理
        # 这里不再重复处理，避免冲突
        return super().eventFilter(obj, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 设置与excel_like_table.py相同的应用样式
    window = PredictionTab(None)
    window.show()
    sys.exit(app.exec())