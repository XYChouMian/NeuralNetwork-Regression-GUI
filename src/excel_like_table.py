import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QHBoxLayout, QWidget, QHeaderView, QMessageBox,
                               QPushButton, QGroupBox, QLabel, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut, QClipboard, QAction, QFont


class ExcelLikeTableWidget(QTableWidget):
    """
    增强的表格控件，支持Excel风格操作和行列管理
    """

    def __init__(self, rows=10, cols=5, headers=None, parent=None,
                 expand_rows=True, expand_cols=True):
        super().__init__(rows, cols, parent)

        # 设置表格属性以实现框选和选择
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # 连接itemChanged信号，在内容更改时自动调整列宽
        self.itemChanged.connect(self.auto_adjust_columns)

        # 设置表头
        if headers is None:
            # 默认表头
            headers = ["姓名", "年龄", "城市", "职业", "薪资"]
        self.setHorizontalHeaderLabels(headers[:cols])

        # 设置初始列宽
        self.horizontalHeader().setDefaultSectionSize(120)

        # 只有当使用默认表头且有足够行列时，才填充示例数据
        if rows > 0 and cols > 0 and headers is None:
            self.populate_sample_data()

        # 自动扩展行和列
        self.expand_rows = expand_rows
        self.expand_cols = expand_cols

        # 设置快捷键
        self.setup_shortcuts()

        # 启用右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def populate_sample_data(self):
        """填充示例数据"""
        sample_data = [
            ["张三", "28", "北京", "软件工程师", "15000"],
            ["李四", "32", "上海", "UI设计师", "12000"],
            ["王五", "25", "广州", "产品经理", "18000"],
            ["赵六", "29", "深圳", "后端开发", "16000"],
            ["钱七", "35", "杭州", "系统架构师", "25000"]
        ]

        # 确保有足够的行
        if self.rowCount() < len(sample_data):
            self.setRowCount(len(sample_data))

        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                if col < self.columnCount():  # 确保不超出列数
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.setItem(row, col, item)

    def setup_shortcuts(self):
        """设置键盘快捷键"""
        # Ctrl+C和Ctrl+V快捷键在keyPressEvent方法中直接处理
        # 根据expand_rows和expand_cols参数设置相应的快捷键
        if self.expand_rows:
            self.add_row_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
            self.add_row_shortcut.activated.connect(self.add_row)

            self.del_row_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
            self.del_row_shortcut.activated.connect(self.delete_selected_rows)

    def keyPressEvent(self, event):
        """重写键盘事件处理，确保快捷键能被正确处理"""
        # 使用位运算检查Ctrl键是否按下，这样即使同时按下其他修饰键也能正常工作
        if event.key() == Qt.Key.Key_C and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.copy_selection()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_V and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.paste_to_selection()
            event.accept()
            return
        # 其他快捷键继续使用QShortcut处理
        super().keyPressEvent(event)

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)

        # 复制粘贴菜单项
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(self.copy_selection)
        menu.addAction(copy_action)

        paste_action = QAction("粘贴", self)
        paste_action.triggered.connect(self.paste_to_selection)
        menu.addAction(paste_action)

        # 根据expand_rows参数显示行操作菜单项
        if self.expand_rows:
            menu.addSeparator()  # 分隔线

            add_row_action = QAction("添加行", self)
            add_row_action.triggered.connect(self.add_row)
            menu.addAction(add_row_action)

            insert_row_action = QAction("插入行", self)
            insert_row_action.triggered.connect(self.insert_row)
            menu.addAction(insert_row_action)

            del_row_action = QAction("删除行", self)
            del_row_action.triggered.connect(self.delete_selected_rows)
            menu.addAction(del_row_action)

        # 根据expand_cols参数显示列操作菜单项
        if self.expand_cols:
            menu.addSeparator()  # 分隔线

            add_col_action = QAction("添加列", self)
            add_col_action.triggered.connect(self.add_column)
            menu.addAction(add_col_action)

            insert_col_action = QAction("插入列", self)
            insert_col_action.triggered.connect(self.insert_column)
            menu.addAction(insert_col_action)

            del_col_action = QAction("删除列", self)
            del_col_action.triggered.connect(self.delete_selected_columns)
            menu.addAction(del_col_action)

        # 显示菜单
        menu.exec(self.mapToGlobal(position))

    def get_selected_rows_range(self):
        """获取选中的行范围，返回(起始行, 结束行)"""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            current_row = self.currentRow()
            return (current_row, current_row) if current_row >= 0 else (self.rowCount(), self.rowCount())

        # 获取所有选中行中的最小和最大行号
        min_row = min(range_.topRow() for range_ in selected_ranges)
        max_row = max(range_.bottomRow() for range_ in selected_ranges)
        return (min_row, max_row)

    def get_selected_columns_range(self):
        """获取选中的列范围，返回(起始列, 结束列)"""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            current_col = self.currentColumn()
            return (current_col, current_col) if current_col >= 0 else (self.columnCount(), self.columnCount())

        # 获取所有选中列中的最小和最大列号
        min_col = min(range_.leftColumn() for range_ in selected_ranges)
        max_col = max(range_.rightColumn() for range_ in selected_ranges)
        return (min_col, max_col)

    def add_row(self):
        """在表格末尾添加新行"""
        new_row = self.rowCount()
        self.insertRow(new_row)
        return new_row

    def insert_row(self):
        """在当前选区上方插入新行"""
        start_row, end_row = self.get_selected_rows_range()
        if start_row < 0:
            start_row = self.rowCount()

        self.insertRow(start_row)
        return start_row

    def delete_selected_rows(self):
        """删除选中的行"""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            QMessageBox.information(self, "提示", "请先选择要删除的行")
            return

        # 收集所有要删除的行（去重）
        rows_to_delete = set()
        for range_ in selected_ranges:
            for row in range(range_.topRow(), range_.bottomRow() + 1):
                rows_to_delete.add(row)

        if not rows_to_delete:
            QMessageBox.information(self, "提示", "请先选择要删除的行")
            return

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的{len(rows_to_delete)}行吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 从大到小排序删除，避免索引变化
            for row in sorted(rows_to_delete, reverse=True):
                self.removeRow(row)

    def add_column(self):
        """在表格末尾添加新列"""
        new_col = self.columnCount()
        self.insertColumn(new_col)
        # 设置新列表头
        self.setHorizontalHeaderItem(
            new_col, QTableWidgetItem(f"列{new_col+1}"))
        return new_col

    def insert_column(self):
        """在当前选区左侧插入新列"""
        start_col, end_col = self.get_selected_columns_range()
        if start_col < 0:
            start_col = self.columnCount()

        self.insertColumn(start_col)
        self.setHorizontalHeaderItem(
            start_col, QTableWidgetItem(f"列{start_col+1}"))
        return start_col

    def delete_selected_columns(self):
        """删除选中的列"""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            QMessageBox.information(self, "提示", "请先选择要删除的列")
            return

        # 收集所有要删除的列（去重）
        cols_to_delete = set()
        for range_ in selected_ranges:
            for col in range(range_.leftColumn(), range_.rightColumn() + 1):
                cols_to_delete.add(col)

        if not cols_to_delete:
            QMessageBox.information(self, "提示", "请先选择要删除的列")
            return

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的{len(cols_to_delete)}列吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 从大到小排序删除，避免索引变化
            for col in sorted(cols_to_delete, reverse=True):
                self.removeColumn(col)

    def auto_adjust_columns(self):
        """自动调整列宽以适应内容"""
        self.resizeColumnsToContents()
        # 设置最小列宽
        for col in range(self.columnCount()):
            if self.columnWidth(col) < 100:
                self.setColumnWidth(col, 100)

    def copy_selection(self):
        """复制选中的单元格到剪贴板"""
        print("copy_selection method called")
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            print("No selection")
            QMessageBox.information(self, "提示", "请先选择要复制的区域")
            return

        range_ = selected_ranges[0]
        copied_text = ""

        for row in range(range_.topRow(), range_.bottomRow() + 1):
            row_data = []
            for col in range(range_.leftColumn(), range_.rightColumn() + 1):
                item = self.item(row, col)
                cell_text = item.text() if item and item.text() else ""
                row_data.append(cell_text)
            copied_text += "\t".join(row_data) + "\n"

        clipboard = QApplication.clipboard()
        clipboard.setText(copied_text.strip())
        print(f"Copied text: {copied_text.strip()}")

    def paste_to_selection(self):
        """从剪贴板粘贴数据到当前选区"""
        print("paste_to_selection method called")
        clipboard = QApplication.clipboard()
        pasted_text = clipboard.text().strip()

        if not pasted_text:
            print("Clipboard is empty")
            QMessageBox.information(self, "提示", "剪贴板为空或包含不可用数据")
            return

        print(f"Pasting text: {pasted_text}")
        # 获取粘贴起始位置
        current_row = self.currentRow() if self.currentRow() >= 0 else 0
        current_col = self.currentColumn() if self.currentColumn() >= 0 else 0

        rows = pasted_text.split('\n')
        current_table_rows = self.rowCount()
        current_table_cols = self.columnCount()

        # 计算需要扩展的最大行列数
        max_paste_rows = len(rows)
        max_paste_cols = max(len(row.split('\t'))
                             for row in rows if row.strip())

        # 批量扩展表格（如果允许的话）
        if self.expand_rows:
            needed_rows = max_paste_rows - (current_table_rows - current_row)
            if needed_rows > 0:
                for _ in range(needed_rows):
                    self.insertRow(self.rowCount())

        if self.expand_cols:
            needed_cols = max_paste_cols - (current_table_cols - current_col)
            if needed_cols > 0:
                for _ in range(needed_cols):
                    self.insertColumn(self.columnCount())

        # 计算实际可用的最大行列数（考虑扩展限制）
        available_rows = self.rowCount() - current_row
        available_cols = self.columnCount() - current_col

        # 粘贴数据
        for i, row_text in enumerate(rows[:available_rows]):
            if not row_text:
                continue
            target_row = current_row + i

            cols = row_text.split('\t')
            for j, cell_text in enumerate(cols[:available_cols]):
                target_col = current_col + j

                # 确保单元格存在
                if not self.item(target_row, target_col):
                    self.setItem(target_row, target_col, QTableWidgetItem())

                # 设置单元格内容
                self.item(target_row, target_col).setText(cell_text)

        # 粘贴完成后自动调整列宽
        self.auto_adjust_columns()
        print("Paste completed")


if __name__ == "__main__":
    class ControlPanel(QWidget):
        """控制面板：包含所有行列操作按钮"""

        def __init__(self, table_widget, parent=None):
            super().__init__(parent)
            self.table = table_widget
            self.init_ui()

        def init_ui(self):
            layout = QVBoxLayout(self)

            # 根据expand_rows参数显示行操作组
            if self.table.expand_rows:
                # 行操作组
                row_group = QGroupBox("行操作")
                row_layout = QHBoxLayout()

                self.add_row_btn = QPushButton("添加行 (Ctrl++)")
                self.add_row_btn.clicked.connect(self.table.add_row)

                self.insert_row_btn = QPushButton("插入行")
                self.insert_row_btn.clicked.connect(self.table.insert_row)

                self.delete_rows_btn = QPushButton("删除行 (Ctrl+-)")
                self.delete_rows_btn.clicked.connect(
                    self.table.delete_selected_rows)

                row_layout.addWidget(self.add_row_btn)
                row_layout.addWidget(self.insert_row_btn)
                row_layout.addWidget(self.delete_rows_btn)
                row_group.setLayout(row_layout)
                layout.addWidget(row_group)

            # 根据expand_cols参数显示列操作组
            if self.table.expand_cols:
                # 列操作组
                col_group = QGroupBox("列操作")
                col_layout = QHBoxLayout()

                self.add_col_btn = QPushButton("添加列")
                self.add_col_btn.clicked.connect(self.table.add_column)

                self.insert_col_btn = QPushButton("插入列")
                self.insert_col_btn.clicked.connect(self.table.insert_column)

                self.delete_cols_btn = QPushButton("删除列")
                self.delete_cols_btn.clicked.connect(
                    self.table.delete_selected_columns)

                col_layout.addWidget(self.add_col_btn)
                col_layout.addWidget(self.insert_col_btn)
                col_layout.addWidget(self.delete_cols_btn)
                col_group.setLayout(col_layout)
                layout.addWidget(col_group)

            # 其他操作组
            other_group = QGroupBox("其他操作")
            other_layout = QHBoxLayout()

            self.copy_btn = QPushButton("复制 (Ctrl+C)")
            self.copy_btn.clicked.connect(self.table.copy_selection)

            self.paste_btn = QPushButton("粘贴 (Ctrl+V)")
            self.paste_btn.clicked.connect(self.table.paste_to_selection)

            other_layout.addWidget(self.copy_btn)
            other_layout.addWidget(self.paste_btn)
            other_group.setLayout(other_layout)
            layout.addWidget(other_group)

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("PySide6 增强表格控件 - 支持完整行列管理")
            self.resize(1000, 700)

            # 创建中央部件和布局
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            print(type(layout))

            # 创建表格
            self.table = ExcelLikeTableWidget(
                8, 5, expand_rows=True, expand_cols=False)

            # 创建控制面板
            # self.control_panel = ControlPanel(self.table)

            # layout.addWidget(self.control_panel)
            layout.addWidget(self.table)

            # 状态栏
            self.statusBar().showMessage("✅ 表格已就绪 - 支持行列管理、框选、复制粘贴 | 提示：可使用右键菜单快速操作")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
