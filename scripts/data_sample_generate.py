import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# 设置随机种子保证结果可重现
np.random.seed(42)
# 设置中文字体（SimHei）和负号正常显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def generate_complex_dataset(n_samples=500):
    """
    生成复杂的数据集，包含多个相关特征、输出变量和干扰项

    参数:
    n_samples: 样本数量

    返回:
    df: 包含所有特征的DataFrame
    """

    # 生成6个基础输入特征（大于3个要求）
    n_features = 6

    # 生成多元正态分布的特征，引入特征间的相关性
    mean = np.zeros(n_features)
    # 创建协方差矩阵，使特征间有一定相关性
    cov = np.array([
        [1.0, 0.6, 0.3, 0.1, -0.2, 0.4],   # 特征0与其他特征的相关性
        [0.6, 1.0, 0.5, 0.2, 0.1, 0.3],    # 特征1
        [0.3, 0.5, 1.0, 0.4, 0.3, 0.2],    # 特征2
        [0.1, 0.2, 0.4, 1.0, 0.6, 0.1],    # 特征3
        [-0.2, 0.1, 0.3, 0.6, 1.0, 0.5],   # 特征4
        [0.4, 0.3, 0.2, 0.1, 0.5, 1.0]     # 特征5
    ])

    # 生成相关特征
    features = np.random.multivariate_normal(mean, cov, n_samples)

    # 为特征命名
    feature_names = [f'feature_{i}' for i in range(n_features)]

    # 创建4个输出变量（大于2个要求），包含复杂关系
    outputs = np.zeros((n_samples, 4))

    # 输出1: 线性组合 + 非线性变换
    outputs[:, 0] = (2.5 * features[:, 0] +
                     1.8 * features[:, 1] -
                     0.9 * features[:, 2] +
                     0.5 * np.sin(2 * features[:, 0]) +
                     0.3 * np.exp(0.5 * features[:, 1]))

    # 输出2: 多项式关系 + 交互项
    outputs[:, 1] = (1.2 * features[:, 0]**2 -
                     0.8 * features[:, 1] * features[:, 2] +
                     0.6 * features[:, 3]**3 +
                     0.4 * np.tanh(features[:, 4]))

    # 输出3: 更复杂的非线性组合
    outputs[:, 2] = (np.sin(features[:, 0] + features[:, 1]) +
                     np.log(1 + np.abs(features[:, 2] * features[:, 4])) -
                     0.5 * features[:, 3] * features[:, 5])

    # 输出4: 周期性模式与线性组合
    outputs[:, 3] = (0.7 * np.cos(2 * features[:, 2]) +
                     1.1 * np.sin(3 * features[:, 3]) -
                     0.9 * features[:, 4] +
                     0.3 * features[:, 5])

    # 添加两个干扰项（与输出有弱相关性）
    noise_1 = np.random.normal(0, 0.5, n_samples) + 0.1 * features[:, 0]
    noise_2 = np.random.normal(0, 0.3, n_samples) - \
        0.05 * features[:, 1] * features[:, 2]

    # 为输出添加噪声，使问题更具挑战性
    output_noise = np.random.normal(0, 0.2, outputs.shape)
    outputs += output_noise

    # 创建DataFrame
    data_dict = {}

    # 添加特征列
    for i, name in enumerate(feature_names):
        data_dict[name] = features[:, i]

    # 添加输出列
    output_names = [f'target_{i}' for i in range(4)]
    for i, name in enumerate(output_names):
        data_dict[name] = outputs[:, i]

    # 添加干扰项
    data_dict['noise_1'] = noise_1
    data_dict['noise_2'] = noise_2

    df = pd.DataFrame(data_dict)

    return df, feature_names, output_names


def analyze_dataset(df, feature_names, target_names):
    """
    分析生成的数据集，显示基本统计信息和相关性
    """
    print("数据集形状:", df.shape)
    print("\n前5行数据:")
    print(df.head())

    print("\n基本统计信息:")
    print(df.describe())

    # 计算并显示特征与目标变量的相关性
    plt.figure(figsize=(8, 6))
    correlation_matrix = df.corr()
    plt.imshow(correlation_matrix, cmap='coolwarm',
               aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(label='相关系数')
    plt.title('特征与目标变量相关性热图')
    plt.tight_layout()
    plt.axis('equal')
    plt.show()

    # 显示前几个特征与第一个目标变量的关系
    fig, axes = plt.subplots(2, 3, figsize=(9, 6))
    axes = axes.ravel()

    for i, feature in enumerate(feature_names[:6]):
        axes[i].scatter(df[feature], df[target_names[0]], alpha=0.6)
        axes[i].set_xlabel(feature)
        axes[i].set_ylabel(target_names[0])
        axes[i].set_title(f'{feature} vs {target_names[0]}')

    plt.tight_layout()
    plt.show()

    return correlation_matrix


if __name__ == "__main__":
    # 生成数据集
    df, feature_names, target_names = generate_complex_dataset(500)
    # 分析数据集
    correlation_matrix = analyze_dataset(df, feature_names, target_names)

    # 保存数据集到CSV文件
    df.to_csv('./data/data_sample.csv', index=False)
    print("数据集已保存为 'data_sample.csv'")
    # 保存到xlsx
    df.to_excel('./data/data_sample.xlsx', index=False)
    print("数据集已保存为 'data_sample.xlsx'")
