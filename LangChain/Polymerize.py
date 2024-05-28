import os
import shutil

# 源文件目录
source_dir = "../HarmonyOS/Guide"
# 目标目录
target_dir = "../HarmonyOS/GuidePolymerize"

# 如果目标目录不存在，则创建它
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# 获取源文件列表
file_list = os.listdir(source_dir)
# 将文件列表分成每100个一组
chunks = [file_list[i:i + 100] for i in range(0, len(file_list), 100)]

# 将每组文件整合成一个文件
for i, chunk in enumerate(chunks):
    target_filename = os.path.join(target_dir, f"polymerized_{i}.txt")
    with open(target_filename, "w", encoding="utf-8") as target_file:
        for filename in chunk:
            source_filename = os.path.join(source_dir, filename)
            with open(source_filename, "r", encoding="utf-8") as source_file:
                shutil.copyfileobj(source_file, target_file)

print("Files have been polymerized successfully.")