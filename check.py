import pandas as pd

# CSV文件的路径
file_path = 'cleaned_data_pro.csv'

# 读取CSV文件
df = pd.read_csv(file_path)

# 将NaN值替换为空字符串（如果还需要这一步，请取消注释以下代码）
# df = df.fillna(' ')

# 对于latitude和longitude列，如果为空字符串，则用同一列上一行的值填充
for col in ['latitude', 'longitude']:
    for i in range(1, len(df)):
        if df.loc[i, col] == ' ':
            df.loc[i, col] = df.loc[i-1, col]

# 将结果保存到新文件中，也可以覆盖原文件
df.to_csv('cleaned_data_pro.csv', index=False)  # 设置index=False确保不添加索引列