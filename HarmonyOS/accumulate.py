import os

def count_files(directory):
    """统计指定目录下的文件数量"""
    # 获取目录下的所有文件和文件夹列表
    entries = os.listdir(directory)
    # 过滤掉文件夹，仅计算文件
    file_count = sum(1 for entry in entries if os.path.isfile(os.path.join(directory, entry)))
    return file_count

# 指定需要统计的文件夹路径
folder_path = './Guide'  # 请替换成你的文件夹路径
# 调用函数并打印结果
print(f"文件夹 '{folder_path}' 中有 {count_files(folder_path)} 个文件")
