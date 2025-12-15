import pandas as pd
from sklearn.preprocessing import StandardScaler


class DataProcessor:
    def __init__(self):
        self.df = None
        self.columns = []
        self.input_columns = []
        self.output_columns = []
        self.scaler_X = None
        self.scaler_y = None
        self.X = None
        self.y = None
        self.X_scaled = None
        self.y_scaled = None

    def load_file(self, file_path):
        """加载csv/xlsx/xls文件"""
        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(file_path)
            else:
                raise ValueError("不支持的文件格式，仅支持csv/xlsx/xls")

            self.columns = list(self.df.columns)
            return True, "文件加载成功"
        except Exception as e:
            return False, str(e)

    def set_columns(self, input_cols, output_cols):
        """设置输入输出列"""
        if not input_cols or not output_cols:
            return False, "输入列和输出列不能为空"
        try:
            # 对输入输出列进行排序，确保后续处理顺序一致
            self.input_columns = sorted(input_cols)
            self.output_columns = sorted(output_cols)

            self.X = self.df[self.input_columns].values
            self.y = self.df[self.output_columns].values
            
            # 当输入输出列改变时，将标准化后的数据重置为None，确保下次训练时会重新标准化
            self.X_scaled = None
            self.y_scaled = None

            return True, "列设置成功"
        except Exception as e:
            return False, f"列设置失败: {str(e)}"

    def scale_data(self):
        """标准化数据"""
        try:
            # 使用已经排序好的输入输出列
            self.X = self.df[self.input_columns].values
            self.y = self.df[self.output_columns].values
            
            self.scaler_X = StandardScaler()
            self.scaler_y = StandardScaler()

            self.X_scaled = self.scaler_X.fit_transform(self.X)
            self.y_scaled = self.scaler_y.fit_transform(self.y)

            return True, "数据标准化成功"
        except Exception as e:
            return False, str(e)

    def get_basic_info(self):
        """获取数据基本信息"""
        if self.df is None:
            return "未加载数据"

        info = f"数据集形状: {self.df.shape}\n"
        info += f"特征列: {self.df[self.input_columns].describe()}\n" if self.input_columns else ""
        info += f"目标变量: {self.df[self.output_columns].describe()}\n" if self.output_columns else ""

        return info

    def load_prediction_data(self, file_path, selected_cols):
        """加载预测数据"""
        try:
            if file_path.endswith('.csv'):
                pred_df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                pred_df = pd.read_excel(file_path)
            else:
                raise ValueError("不支持的文件格式，仅支持csv/xlsx/xls")

            X_pred = pred_df[selected_cols].values
            return True, X_pred, pred_df
        except Exception as e:
            return False, str(e), None

    def export_results(self, df, predictions, output_file):
        """导出预测结果"""
        try:
            pred_df = df.copy()

            # 只有当predictions不为None时才添加预测结果列
            if predictions is not None:
                for i, col in enumerate(self.output_columns):
                    pred_df[f'pred_{col}'] = predictions[:, i]

            # 确保文件扩展名正确
            if not output_file.endswith('.xlsx'):
                output_file += '.xlsx'
            
            # 使用pandas导出到Excel
            pred_df.to_excel(output_file, index=False)

            return True, "结果导出成功"
        except Exception as e:
            return False, str(e)
