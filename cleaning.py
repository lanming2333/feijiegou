import pandas as pd
import re

# 更新的处理比率函数，使用正则表达式来提取数字
def calculate_ratio(value):
    try:
        # 使用正则表达式查找所有数字
        numbers = re.findall(r'\d+', value)
        if len(numbers) == 2 and int(numbers[1]) != 0:  # 确保有两个数字且第二个数字（分母）不为0
            return float(numbers[0]) / float(numbers[1])
        else:
            return 0.5  # 如果数据格式不符合预期或分母为0，填充为0.5
    except:  # 如果解析出错（例如，值为NaN或其他问题）
        return 0.5  # 缺失值填充0.5


# 加载数据
df = pd.read_csv('tripadvisor_european_restaurants.csv')

# 1. 去除不必要的列
df.drop(columns=['keywords', 'claimed', 'price_range','original_open_hours','open_hours_per_week','working_shifts_per_week',
                 'open_days_per_week','popularity_detailed'], inplace=True)

# 将知名度改为0-1的数，越大越不出名
df['popularity_generic'] = df['popularity_generic'].apply(lambda x: calculate_ratio(x) if pd.notnull(x) else 0.5)

# 2. 处理price_level列的缺失值和其他值
df['price_level'].fillna(2, inplace=True)  # 将缺失值改为2
df['default_language'].fillna('All language', inplace=True)
# 将 '€', '€€-€€€', '€€€€' 分别改为 1, 2, 3
price_level_mapping = {'€': 1, '€€-€€€': 2, '€€€€': 3}
df['price_level'] = df['price_level'].replace(price_level_mapping)

# 删除没有菜系和评分的行
df.dropna(subset=['cuisines'], inplace=True)
df.dropna(subset=['avg_rating'], inplace=True)

# 对于 'food' 列，缺失值用同一行的 'avg_rating' 替代
df['food'] = df['food'].fillna(df['avg_rating'])
df['service'] = df['service'].fillna(df['avg_rating'])
df['value'] = df['value'].fillna(df['avg_rating'])
df['atmosphere'] = df['atmosphere'].fillna(df['avg_rating'])
# 保存清洗后的数据为新文件
df.to_csv('cleaned_data.csv', index=False)

print("数据清洗完成，已保存为 cleaned_data.csv")