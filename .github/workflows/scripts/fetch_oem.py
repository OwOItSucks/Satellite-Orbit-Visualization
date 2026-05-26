import re, zipfile, io, os
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

LIST_URL = "https://www.cmse.gov.cn/gfgg/zgkjzgdcs/"
OUT = Path("data/CSS_OEM.dat")
OUT.parent.mkdir(exist_ok=True)

# 简单 HTML 解析，不需要 bs4
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            href = attrs.get("href", "")
            text = ""
            self._cur_href = href
    def handle_data(self, data):
        if hasattr(self, "_cur_href") and re.search(r"CSS_OEM", data, re.I):
            self.links.append(self._cur_href)

# 获取页面
req = urllib.request.Request(LIST_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as r:
    html = r.read().decode("utf-8", errors="replace")

# 直接用正则找 zip 链接（更可靠）
# 匹配 href="./202605/W0....zip" 这类
matches = re.findall(r'href=["\']([^"\']*\.zip)["\']', html, re.I)
oem_links = [m for m in matches if "CSS_OEM" in html[max(0, html.find(m)-200):html.find(m)+10]]

# 如果上面没匹配到，用更宽松的：找页面上所有 zip
if not oem_links:
    oem_links = [m for m in matches]

if not oem_links:
    raise RuntimeError("未找到任何 zip 链接，页面结构可能已变化")

zip_href = oem_links[0]

# 拼完整 URL
if zip_href.startswith("./"):
    zip_url = LIST_URL + zip_href[2:]
elif zip_href.startswith("http"):
    zip_url = zip_href
else:
    zip_url = "https://www.cmse.gov.cn/" + zip_href.lstrip("/")

print(f"下载: {zip_url}")
req2 = urllib.request.Request(zip_url, headers={"User-Agent": "Mozilla/5.0", "Referer": LIST_URL})
with urllib.request.urlopen(req2, timeout=30) as r:
    content = r.read()

with zipfile.ZipFile(io.BytesIO(content)) as z:
    dat_files = [n for n in z.namelist() if n.lower().endswith(".dat")]
    if not dat_files:
        raise RuntimeError(f"zip 内无 .dat 文件，包含: {z.namelist()}")
    data = z.read(dat_files[0])
    OUT.write_bytes(data)
    print(f"已写入 {OUT}（{len(data)} bytes，来自 {dat_files[0]}）")
