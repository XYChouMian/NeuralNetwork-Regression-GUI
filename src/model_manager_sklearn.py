import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pickle
import os
import random
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
import random


class ModelManagerSklearn:
    def __init__(self):
        """初始化模型管理器，用于scikit-learn模型"""
        self.model = None
        self.scaler_X = None
        self.scaler_y = None
        self.input_size = None
        self.output_size = None
        self.layer_sizes = None
        self.data_processor = None

    def train(self, X_scaled, y_scaled, layer_sizes, epochs=2000, batch_size=16, test_size=0.2, lr=0.001, random_seed=1.0, progress_callback=None, scaler_y=None, output_columns=None, visualization_save_path=None, solver='adam'):
        """
        训练scikit-learn模型

        参数:
            X_scaled: 缩放后的输入特征数据 (numpy数组)
            y_scaled: 缩放后的目标数据 (numpy数组)
            layer_sizes: 神经网络各层尺寸列表
            epochs: 训练轮数
            batch_size: 批次大小
            test_size: 测试集比例
            lr: 学习率
            progress_callback: 进度回调函数
            scaler_y: 目标数据的缩放器
            output_columns: 输出列名列表
            visualization_save_path: 可视化保存路径

        返回:
            model: 训练好的模型
            train_losses: 训练损失列表
            test_losses: 测试损失列表
        """
        self.input_size = X_scaled.shape[1]
        self.output_size = y_scaled.shape[1] if len(y_scaled.shape) > 1 else 1
        self.layer_sizes = layer_sizes

        # 训练模型
        self.model, train_losses, test_losses = train_model(
            X_scaled, y_scaled, layer_sizes,
            epochs=epochs,
            batch_size=batch_size,
            test_size=test_size,
            lr=lr,
            random_seed=random_seed,
            progress_callback=progress_callback,
            solver=solver
        )

        # 生成训练可视化
        fig = self.generate_training_visualization(
            train_losses,
            test_losses,
            X_scaled=X_scaled,
            y_scaled=y_scaled,
            scaler_y=scaler_y,
            output_columns=output_columns
        )

        # 保存可视化结果
        if visualization_save_path:
            plt.savefig(visualization_save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return self.model, train_losses, test_losses

    def predict(self, X):
        """
        使用scikit-learn模型进行预测

        参数:
            X: 输入特征数据 (numpy数组)

        返回:
            y_pred: 预测结果 (numpy数组)
        """
        if self.model is None:
            raise ValueError("模型未训练或未加载")

        # 确保输入是numpy数组
        if not isinstance(X, np.ndarray):
            X = np.array(X)

        # 进行预测
        y_pred = self.model.predict(X)

        return y_pred

    def save_model(self, model_path):
        """
        保存scikit-learn模型到文件

        参数:
            model_path: 模型保存路径
        """
        if self.model is None:
            raise ValueError("模型未训练或未加载")

        # 保存模型和相关信息
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'layer_sizes': self.layer_sizes,
                'input_size': self.input_size,
                'output_size': self.output_size,
                'scaler_X': getattr(self, 'scaler_X', None),
                'scaler_y': getattr(self, 'scaler_y', None),
                'input_columns': getattr(self, 'input_columns', None),
                'output_columns': getattr(self, 'output_columns', None)
            }, f)

    def load_model(self, model_path):
        """
        从文件加载scikit-learn模型

        参数:
            model_path: 模型加载路径
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件 {model_path} 不存在")

        # 加载模型和相关信息
        with open(model_path, 'rb') as f:
            checkpoint = pickle.load(f)

        self.model = checkpoint['model']
        self.layer_sizes = checkpoint['layer_sizes']
        self.input_size = checkpoint['input_size']
        self.output_size = checkpoint['output_size']
        self.scaler_X = checkpoint.get('scaler_X', None)
        self.scaler_y = checkpoint.get('scaler_y', None)
        self.input_columns = checkpoint.get('input_columns', None)
        self.output_columns = checkpoint.get('output_columns', None)

    def generate_training_visualization(self, train_losses, test_losses, X_scaled=None, y_scaled=None, scaler_y=None, output_columns=None):
        """
        生成训练过程可视化，包括损失曲线、预测对比和误差分布

        参数:
            train_losses: 训练损失列表
            test_losses: 测试损失列表
            X_scaled: 缩放后的输入特征数据（用于生成预测可视化）
            y_scaled: 缩放后的目标数据（用于生成预测可视化）
            scaler_y: 目标数据的缩放器（用于逆缩放）
            output_columns: 输出列名列表
            save_path: 可视化保存路径，若为None则不保存

        返回:
            fig: 生成的matplotlib图形对象
        """

        # 设置中文显示
        plt.rcParams["font.sans-serif"] = ["SimHei"]
        plt.rcParams["axes.unicode_minus"] = False

        # 确定输出数量
        n_outputs = 1
        if output_columns:
            # 使用已经排序的输出特征列
            n_outputs = len(output_columns)
        elif y_scaled is not None:
            n_outputs = y_scaled.shape[1] if len(y_scaled.shape) > 1 else 1

        # 计算图形大小，确保每个子图的高宽比接近方形
        subplot_size = 3
        fig_width = max(subplot_size * n_outputs, 6)
        fig_height = subplot_size * 3

        fig = plt.figure(figsize=(fig_width, fig_height))

        # 使用gridspec进行布局
        if n_outputs == 1:
            gs = gridspec.GridSpec(3, 1, figure=fig)
            gs.update(hspace=0.3)
        else:
            gs = gridspec.GridSpec(3, n_outputs, figure=fig)
            gs.update(hspace=0.3, wspace=0.3)

        # 第一行：损失曲线
        if n_outputs == 1:
            ax1 = fig.add_subplot(gs[0, 0])
        else:
            # 损失曲线居中显示，保持方形比例
            loss_curve_cols = min(n_outputs, 3)
            start_col = (n_outputs - loss_curve_cols) // 2
            ax1 = fig.add_subplot(gs[0, start_col:start_col+loss_curve_cols])

        ax1.plot(train_losses, label="训练损失", alpha=0.7,
                 color='#1f77b4', linewidth=2)
        ax1.plot(test_losses, label="测试损失", alpha=0.7,
                 color='#ff7f0e', linewidth=2)
        ax1.set_title("训练和测试损失曲线")
        ax1.set_xscale('log')
        ax1.set_xlabel("Epoch (对数坐标)")
        ax1.set_ylabel("损失值")
        ax1.set_ylim(0, 1)
        ax1.legend()
        ax1.grid(True, which='both', alpha=0.3)
        ax1.grid(True, alpha=0.3)

        # 只在提供了完整数据时生成预测可视化
        if X_scaled is not None and y_scaled is not None and scaler_y is not None:
            # 进行预测
            y_pred_scaled = self.model.predict(X_scaled)

            # 逆缩放预测结果
            y_pred = scaler_y.inverse_transform(
                y_pred_scaled.reshape(-1, 1) if len(y_pred_scaled.shape) == 1 else y_pred_scaled)
            targets = scaler_y.inverse_transform(
                y_scaled.reshape(-1, 1) if len(y_scaled.shape) == 1 else y_scaled)

            # 随机分割训练集和测试集（与训练时保持一致）
            test_size = 0.2
            train_features, test_features, train_targets, test_targets, train_pred, test_pred = train_test_split(
                X_scaled, targets, y_pred, test_size=test_size, random_state=10
            )
            
            # 使用已经排序的数据

            # 第二行：训练集/测试集对比
            for i in range(n_outputs):
                ax = fig.add_subplot(gs[1, i])

                # 训练集
                ax.scatter(train_targets[:, i] if len(train_targets.shape) > 1 else train_targets,
                           train_pred[:, i] if len(
                               train_pred.shape) > 1 else train_pred,
                           color="#1f77b4", label="训练集", alpha=0.6)
                # 测试集
                ax.scatter(test_targets[:, i] if len(test_targets.shape) > 1 else test_targets,
                           test_pred[:, i] if len(
                               test_pred.shape) > 1 else test_pred,
                           color="#ff7f0e", label="测试集", alpha=0.6)
                # 理想线
                min_val = min(min(train_targets[:, i] if len(train_targets.shape) > 1 else train_targets),
                              min(test_targets[:, i] if len(test_targets.shape) > 1 else test_targets))
                max_val = max(max(train_targets[:, i] if len(train_targets.shape) > 1 else train_targets),
                              max(test_targets[:, i] if len(test_targets.shape) > 1 else test_targets))
                ax.plot([min_val, max_val], [min_val, max_val], "r--", lw=2)

                ax.set_xlabel("实际值")
                ax.set_ylabel("预测值")
                title = f"{output_columns[i]} 预测对比" if output_columns else f"输出 {i+1} 预测对比"
                ax.set_title(title)
                ax.legend()
                ax.grid(True, alpha=0.3)

            # 第三行：预测误差分布
            for i in range(n_outputs):
                ax = fig.add_subplot(gs[2, i])

                # 计算预测误差
                train_error = (train_pred[:, i] if len(train_pred.shape) > 1 else train_pred) - (
                    train_targets[:, i] if len(train_targets.shape) > 1 else train_targets)
                test_error = (test_pred[:, i] if len(test_pred.shape) > 1 else test_pred) - (
                    test_targets[:, i] if len(test_targets.shape) > 1 else test_targets)

                # 计算RMS误差
                train_rms = np.sqrt(np.mean(train_error ** 2))
                test_rms = np.sqrt(np.mean(test_error ** 2))

                # 绘制预测误差分布，使用weights参数计算频率（频数/总数）
                # 将RMS误差信息添加到图例标签中，保留3位有效数字
                # 计算权重，使每个直方图的高度之和等于1
                train_weights = np.ones_like(train_error) / len(train_error)
                test_weights = np.ones_like(test_error) / len(test_error)
                
                ax.hist(train_error, bins=20, alpha=0.5,
                        label=f"训练集误差 (RMS: {train_rms:.3g})", color="#1f77b4", weights=train_weights)
                ax.hist(test_error, bins=20, alpha=0.5,
                        label=f"测试集误差 (RMS: {test_rms:.3g})", color="#ff7f0e", weights=test_weights)

                ax.set_xlabel("预测误差")
                ax.set_ylabel("频率")
                title = f"{output_columns[i]} 预测误差分布" if output_columns else f"输出 {i+1} 预测误差分布"
                ax.set_title(title)
                ax.legend()
                ax.grid(True, alpha=0.3)

                # 添加零线
                ax.axvline(x=0, color='r', linestyle='--', alpha=0.7)

        # 调整布局
        plt.subplots_adjust(left=0.05, right=0.95, top=0.9,
                            bottom=0.05, hspace=0.3, wspace=0.3)

        return fig


# 设置随机数种子


def set_seed(seed=10):
    random.seed(seed)
    np.random.seed(seed)

# 模拟数据集类 - 与PyTorch版本保持接口一致


class RegressionDataset:
    def __init__(self, features, targets):
        self.features = np.array(features)
        self.targets = np.array(targets)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]

# 动态神经网络模型设计（使用sklearn的MLPRegressor）


class DynamicNet:
    """
    动态层数的神经网络模型（使用sklearn实现）
    """

    def __init__(self, layer_sizes, random_state=10, solver='lbfgs'):
        """
        初始化动态神经网络

        参数:
            layer_sizes: 列表，包含各层神经元数量，例如 [input_size, hidden1_size, hidden2_size, output_size]
                        至少需要2层（输入层和输出层）
            random_state: 随机数种子，用于保证实验可重复性
        """
        if len(layer_sizes) < 2:
            raise ValueError("神经网络至少需要2层（输入层和输出层）")

        # 为了与PyTorch版本保持一致，添加这些属性
        self.layers = []  # 虽然在sklearn中不需要，但为了接口一致保留

        # 准备隐藏层结构，注意sklearn的MLPRegressor不需要指定输入层大小
        hidden_layer_sizes = tuple(
            layer_sizes[1:-1]) if len(layer_sizes) > 2 else ()

        # 创建MLPRegressor模型
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            activation='relu',
            solver=solver,
            learning_rate_init=0.001,  # 默认学习率
            batch_size='auto',
            learning_rate='adaptive',  # 类似于PyTorch的ReduceLROnPlateau
            max_iter=1,  # 每次调用fit只训练一个epoch
            shuffle=True,
            random_state=random_state,
            alpha=1e-5,  # L2正则化参数，对应PyTorch的weight_decay
            verbose=False
        )

        self.layer_sizes = layer_sizes
        self.trained = False
        self.random_state = random_state
        self.solver = solver
        # 为了与PyTorch兼容，添加必要的属性
        self.input_size = layer_sizes[0]
        self.output_size = layer_sizes[-1]

    def forward(self, x):
        """前向传播，预测输出"""
        # 确保输入是numpy数组
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        return self.model.predict(x)

    def __call__(self, x):
        """支持直接调用模型进行预测，与PyTorch的nn.Module保持一致"""
        return self.forward(x)

    def predict(self, x):
        """直接实现predict方法，与scikit-learn接口保持一致"""
        result = self.forward(x)
        # 确保返回二维数组
        if len(result.shape) == 1:
            result = result.reshape(-1, 1)
        return result

    def train(self):
        """模拟PyTorch的train()方法，实际在sklearn中不需要"""
        return self

    def eval(self):
        """模拟PyTorch的eval()方法，实际在sklearn中不需要"""
        return self

    def state_dict(self):
        """模拟PyTorch的state_dict()方法，返回模型的状态"""
        # 对于sklearn模型，我们可以返回模型的参数
        return {
            'coefs_': self.model.coefs_,
            'intercepts_': self.model.intercepts_,
            'n_iter_': self.model.n_iter_,
            'layer_sizes': self.layer_sizes,
            'solver': self.solver
        }

    def load_state_dict(self, state_dict):
        """模拟PyTorch的load_state_dict()方法，加载模型的状态"""
        # 对于sklearn模型，我们需要重新创建模型
        self.layer_sizes = state_dict['layer_sizes']
        self.solver = state_dict.get('solver', 'lbfgs')
        hidden_layer_sizes = tuple(
            self.layer_sizes[1:-1]) if len(self.layer_sizes) > 2 else ()

        # 重新初始化模型
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            activation='relu',
            solver=self.solver,
            learning_rate_init=0.001,
            batch_size='auto',
            learning_rate='adaptive',
            max_iter=1,
            shuffle=True,
            random_state=getattr(self, 'random_state', 10),
            alpha=1e-5,
            verbose=False
        )

        # 设置模型参数
        self.model.coefs_ = state_dict['coefs_']
        self.model.intercepts_ = state_dict['intercepts_']
        self.model.n_iter_ = state_dict['n_iter_']
        self.model._hidden_layer_sizes = hidden_layer_sizes

        # 设置必要的属性以确保模型功能正常
        self.model.n_layers_ = len(state_dict['coefs_']) + 1
        self.model.n_features_in_ = self.layer_sizes[0]
        self.model.n_outputs_ = self.layer_sizes[-1]
        self.model.hidden_layer_sizes = hidden_layer_sizes

        # 添加更多必要的属性
        self.model.out_activation_ = 'identity'  # 回归任务的输出激活函数
        self.model.activation = 'relu'  # 隐藏层激活函数
        self.model.loss_ = 'mse'  # 损失函数
        self.model.solver = 'adam'  # 优化器

        # 设置其他可能需要的属性
        self.model.alpha = 1e-5
        self.model.batch_size = 'auto'
        self.model.early_stopping = False
        self.model.epsilon = 1e-08
        self.model.learning_rate = 'constant'
        self.model.learning_rate_init = 0.001
        self.model.max_fun = 15000
        self.model.max_iter = 1
        self.model.momentum = 0.9
        self.model.n_iter_no_change = 10
        self.model.power_t = 0.5
        self.model.random_state = 42
        self.model.shuffle = True
        self.model.tol = 0.0001
        self.model.validation_fraction = 0.1
        self.model.verbose = False
        self.model.warm_start = False
        self.model.solver = self.solver

        self.trained = True
        return self


def train_model(X_scaled, y_scaled, layer_sizes, epochs=2000, batch_size=16, test_size=0.2, lr=0.001, random_seed=1.0, progress_callback=None, solver='lbfgs'):
    """训练模型的函数（使用sklearn实现）"""
    # 将浮点数种子转换为整数（保留一位小数信息）
    seed = int(random_seed * 10)
    set_seed(seed)

    # 创建输入数据的副本，避免修改原始数据
    X_scaled_copy = X_scaled.copy()
    y_scaled_copy = y_scaled.copy()

    # 创建数据集并划分
    dataset = RegressionDataset(X_scaled_copy, y_scaled_copy)

    # 按照比例划分训练集和测试集（与PyTorch版本保持一致的方式）
    train_size = int((1 - test_size) * len(dataset))
    test_size = len(dataset) - train_size
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled_copy, y_scaled_copy, test_size=test_size, random_state=seed
    )

    # 检查y的形状，如果是单输出且为列向量，则转换为1维数组
    if len(y_scaled_copy.shape) > 1 and y_scaled_copy.shape[1] == 1:
        # 单输出回归，将y转换为1维数组
        y_scaled_copy = y_scaled_copy.ravel()
        y_train = y_train.ravel()
        y_test = y_test.ravel()

    # 创建模型
    model = DynamicNet(layer_sizes, random_state=seed, solver=solver)

    # 设置学习率
    model.model.learning_rate_init = lr

    # 为了与PyTorch版本保持一致，添加model.train()调用
    model.train()

    # 训练参数
    train_losses = []
    test_losses = []

    for epoch in range(epochs):
        # 在训练集上训练一个epoch
        model.model.partial_fit(X_train, y_train)

        # 计算训练损失
        y_train_pred = model.model.predict(X_train)
        train_loss = mean_squared_error(y_train, y_train_pred)
        train_losses.append(train_loss)

        # 计算测试损失
        y_test_pred = model.model.predict(X_test)
        test_loss = mean_squared_error(y_test, y_test_pred)
        test_losses.append(test_loss)

        # 更新进度条
        if progress_callback is not None:
            progress = int(((epoch + 1) / epochs) * 100)
            progress_callback(progress)

        # 每50个epoch打印一次进度
        if (epoch + 1) % 50 == 0:
            # 与PyTorch版本保持一致的打印格式，不显示学习率
            print(f"Epoch [{epoch+1:03d}/{epochs}], "
                  f"Train Loss: {train_loss:.6f}, "
                  f"Test Loss: {test_loss:.6f}")

    model.trained = True
    return model, train_losses, test_losses
