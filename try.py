import happybase


def get_first_20_rows_from_hbase(table_name):
    """
    从HBase表中提取并打印前20行数据。

    :param table_name: HBase表名
    """
    # 连接到HBase服务器（假设为本地HBase服务器）
    connection = happybase.Connection(host='localhost', port=9090)
    table = connection.table(table_name)

    # 从表中扫描数据，获取前20条记录
    for key, data in table.scan(limit=20):
        # 解码数据并打印
        row_key = key.decode('utf-8')
        decoded_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
        print(decoded_data)
        print(f"Row Key: {row_key}")

    # 关闭HBase连接
    connection.close()


# 调用函数来提取‘restaurants’表的前20行
get_first_20_rows_from_hbase('restaurants')
