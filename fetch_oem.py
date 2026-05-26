#!/usr/bin/env python3
"""
自动从 CMSE 官网抓取最新 CSS OEM 文件并解压到 ./data/CSS_OEM.dat
建议用 cron 每12小时跑一次：0 */12 * * * /usr/bin/python3 /path/to/fetch_oem.py
"""
import re, zipfile, io, os, requests
from pathlib import Path
from bs4 import BeautifulSoup

BASE_URL = "https://www.cmse.gov.cn"
LIST_URL = f"{BASE_URL}/gfgg/zgkjzgdcs/"
DATA_DIR = Path(__file__).parent / "data"
OUT_FILE = DATA_DIR / "CSS_OEM.dat"
DATA_DIR.mkdir(exist_ok=True)

def fetch_latest():
    resp = requests.get(LIST_URL, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # 找所有 .zip 链接，取最新（页面按时间倒序）
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.search(r'CSS_OEM.*\.zip', a.text, re.I) or re.search(r'CSS_OEM.*\.zip', href, re.I):
            links.append(href)
    
    if not links:
        print("[fetch_oem] 未找到 OEM zip 链接")
        return False

    zip_href = links[0]  # 第一个即最新
    # 处理相对路径（./202605/xxx.zip → https://www.cmse.gov.cn/gfgg/zgkjzgdcs/202605/xxx.zip）
    if zip_href.startswith("./"):
        zip_url = LIST_URL + zip_href[2:]
    elif zip_href.startswith("http"):
        zip_url = zip_href
    else:
        zip_url = BASE_URL + "/" + zip_href.lstrip("/")

    print(f"[fetch_oem] 下载: {zip_url}")
    r = requests.get(zip_url, timeout=30)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        # zip 内找 .dat 文件
        dat_names = [n for n in z.namelist() if n.lower().endswith(".dat")]
        if not dat_names:
            print("[fetch_oem] zip 内无 .dat 文件")
            return False
        content = z.read(dat_names[0])
        OUT_FILE.write_bytes(content)
        print(f"[fetch_oem] 已更新 {OUT_FILE}（{len(content)} bytes，来自 {dat_names[0]}）")
        return True

if __name__ == "__main__":
    fetch_latest()
