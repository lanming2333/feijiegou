import happybase

# HBase 服务器地址和端口
HBASE_SERVER_IP = 'localhost'
HBASE_PORT =9090


# 连接到 HBase
connection = happybase.Connection(HBASE_SERVER_IP, port=HBASE_PORT)

# 定义列族的配置
families = {
    'details': dict()
}

# 表名
table_name = 'restaurants'

# 如果表已存在，则删除
if table_name in connection.tables():
    print(f"Table '{table_name}' already exists, deleting it.")
    connection.delete_table(table_name, disable=True)

# 创建表
connection.create_table(table_name, families)
print(f"Table '{table_name}' with column family 'details' created successfully.")

# 关闭与 HBase 的连接
connection.close()