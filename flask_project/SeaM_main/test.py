from datasets import load_dataset
import pyarrow.parquet as pq

# # 加载数据集
# dataset = load_dataset("code_search_net",'php')
#
# # 保存到磁盘
# dataset.save_to_disk("C:/Users/bxh/Downloads")
dataset = load_dataset("EleutherAI/pile",'github')

# dataset.save_to_disk("D:/pile")

# dataset = load_dataset("code_search_net", "php")
print(dataset['train'][0])  # 打印训练集的第一个样本

