import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 初始化 Chrome 浏览器
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
chrome_options.add_argument("--no-sandbox")  # 以沙盒模式运行
chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用 /dev/shm 使用
driver = webdriver.Chrome(options=chrome_options, service=Service())
# 基本网址，替换为您要爬取的实际文档网址
base_url = "https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V2/syscap-0000001408089368-V2"

# 递归爬取文档并保存内容到文件
def crawl_documentation(url, output_dir=r".\apidata", depth=0, start_crawling=False, unchanged_count=0):
    if depth >= 5 or unchanged_count >= 10:
        return

    # 计算目录中的文件数量
    num_files_start = len(os.listdir(output_dir))
    # 发送请求获取网页内容
    driver.get(url)
    time.sleep(5)  # 等待动态内容加载完毕

    # 使用 Beautiful Soup 解析 HTML 源码
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 查找左侧目录的 div
    doctree_div = soup.find("div", class_="doctree")

    # 查找所有子目录链接
    subdirectory_links = doctree_div.find_all("a")

    # 如果输出目录不存在，则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历子目录
    for link in subdirectory_links:
        subdirectory_url = str(link["href"])
        subdirectory_url = subdirectory_url.split("?")[0]
        url = url.split("?")[0]
        # 当在目录中找到当前 URL 时开始爬取
        if str(url).startswith(subdirectory_url):
            start_crawling = True
        # 如果 start_crawling 为 False，跳过当前迭代
        if not start_crawling:
            continue

        subdirectory_name = link.text.strip()

        # 发送请求获取子目录的内容
        driver.get(subdirectory_url)
        time.sleep(5)  # 等待动态内容加载完毕
        subdirectory_soup = BeautifulSoup(driver.page_source, "html.parser")

        # 查找子目录的内容
        content_divs = subdirectory_soup.find_all("div", class_="layout-content")
        content = "\\n\\n".join([div.text.strip() for div in content_divs])
        # 将 content 分割成多行
        lines = content.split("\n")
        # 只保留非空的行
        lines = [line for line in lines if line.strip() != ""]
        # 将所有的行重新组合成一个字符串
        content = "\n".join(lines)
        # 从 URL 中提取文件名（不包含查询参数部分）
        filename = os.path.basename(subdirectory_url).split("?")[0] + ".txt"

        # 将内容写入文件
        output_file_path = os.path.join(output_dir, filename)
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"已保存 {subdirectory_name} 的内容到 {output_file_path}")
        print(f"链接：{subdirectory_url}")

        num_files_end = len(os.listdir(output_dir))
        # 如果文件数量没有变化，增加计数
        if num_files_start == num_files_end:
            unchanged_count += 1
        else:
            unchanged_count = 0
        # 递归爬取子目录的内容，并增加深度计数器
        crawl_documentation(subdirectory_url, output_dir, depth=depth + 1, start_crawling=start_crawling)

# 调用函数开始爬取文档
crawl_documentation(base_url)

# 关闭浏览器
driver.quit()
