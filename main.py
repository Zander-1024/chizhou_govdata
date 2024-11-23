import re
from time import sleep
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 目标URL
url = "https://gaj.chizhou.gov.cn"
base_url = "https://gaj.chizhou.gov.cn"

# 请求头，模拟浏览器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}



def get_page_links():
    page_links = []
    for i in range(1, 3):
        url = f"{base_url}/OpennessContent/showList/15/85522/page_{i}.html"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            links = soup.find_all("a",attrs={"href": re.compile(r"/OpennessContent/show/\d+\.html"), "title": re.compile("确认结果")})  # 修改为实际的标签和类名

            # 提取 href 属性并打印
            for i, link in enumerate(links, 1):
                href = link.get("href")
                title = link.get("title")  # 如果需要标题
                if title and "池州市公安局行政确认结果公开" in title:
                    month = re.search(r"（(.*?)）",title).group(1)
                    page_links.append((href, month))
        else:
            print(f"请求失败: {response.status_code}")
    return page_links
                    
def get_get_page_data(links):
    data_dict = {}
    for link, month in links:
        full_url = base_url+link
        response = requests.get(full_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            tbody = soup.find_all("tbody")[1]
            if tbody:
                # 遍历所有行 <tr>
                rows = tbody.find_all("tr")
                for row in rows[1:]:  # 跳过表头
                    cells = row.find_all("td")
                    if len(cells) >= 4:  # 确保列数足够
                        title = cells[1].get_text(strip=True) 
                        value = cells[3].get_text(strip=True)  
                        if value.isdigit():  # 只保留数字数据
                            value = int(value)
                            if title not in data_dict:
                                data_dict[title] = {}  # 每个事项对应一个月份字典
                            data_dict[title][month] = value
        else:
            print(f"请求失败: {response.status_code} - {full_url}")
        sleep(0.3)

    df = pd.DataFrame(data_dict).T 
    df.to_excel("chizhougovdata.xlsx")

    # 查看结果
    print(df)
if __name__ == "__main__":
    page_links = get_page_links()
    get_get_page_data(page_links)
    