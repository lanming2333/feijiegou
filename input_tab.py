import csv
import happybase

# 读取 CSV 文件，并将数据存储在字典中
with open('C:/Users/zth/Desktop/cleaned_data_pro.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.DictReader(csvfile)
    data = list(csvreader)
print("111")
# 连接到 HBase
connection = happybase.Connection(host="localhost", port=9090)
table = connection.table('restaurants')

# 使用批处理插入数据
with table.batch(batch_size=1000) as batch:  # 每1000条数据提交一次
    for row in data:
        key_bytes = row.pop('restaurant_link').encode('utf-8')
        value_bytes = {f"details:{column}".encode('utf-8'): str(val).encode('utf-8') for column, val in row.items() if val is not None}
        batch.put(key_bytes, value_bytes)

connection.close()
print("Data imported into HBase successfully!")
