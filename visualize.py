import happybase
import matplotlib.pyplot as plt


def visualize_hbase_table_data(table_name, column_family, column):
    """
    连接到HBase数据库，读取特定表中的数据，并使用matplotlib绘制直方图。

    :param table_name: HBase表名
    :param column_family: 列族名
    :param column: 列名
    """
    # 连接到HBase服务器（替换为你的HBase服务器地址）
    connection = happybase.Connection('127.0.0.1')
    table = connection.table(table_name)

    # 初始化数据字典，用于存储键值对
    data_dict = {}

    # 从表中扫描数据，假设每行数据的列族和列名已知
    for key, data in table.scan(columns=[column_family + ':' + column]):
        # 假设每个键的值都是整数型
        value = int(data[column_family.encode() + b':' + column.encode()])
        # 存储或更新数据
        data_dict[key.decode()] = value

    # 关闭HBase连接
    connection.close()

    # 使用获取的数据绘制直方图
    plt.figure(figsize=(10, 6))
    plt.bar(data_dict.keys(), data_dict.values(), color='skyblue')
    plt.xlabel('Keys')
    plt.ylabel('Values')
    plt.title('HBase Table Data Visualization: ' + table_name)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


# 示例使用，调用函数并传入参数：表名、列族和列名
# 请根据实际情况替换 'your_table_name', 'your_column_family', 和 'your_column'
visualize_hbase_table_data('your_table_name', 'your_column_family', 'your_column')