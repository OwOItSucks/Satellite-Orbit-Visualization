import urllib.request
from pathlib import Path

# 目标卫星 NORAD ID (FYBB#1)
CATNR = "57696"
# CelesTrak 标准 GP TLE 请求接口
URL = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={CATNR}&FORMAT=tle"
OUT = Path("data/FYBB1.tle")

# 确保 data 目录存在
OUT.parent.mkdir(exist_ok=True)

def fetch_tle():
    print(f"正在从 CelesTrak 获取卫星 {CATNR} 的最新 TLE 数据...")
    
    # 模拟浏览器 User-Agent，防止被防爬虫机制拦截
    req = urllib.request.Request(
        URL, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            if r.status != 200:
                raise RuntimeError(f"HTTP 请求失败，状态码: {r.status}")
            
            tle_data = r.read().decode("utf-8").strip()
            
        # 按行切分数据
        lines = tle_data.splitlines()
        
        # ─── 核心修改：强行将第一行（卫星名）洗成 FYBB#1 ───
        if len(lines) >= 3:
            print(f"[改名] 成功将官方名称 '{lines[0].strip()}' 替换为 'FYBB#1'")
            lines[0] = "FYBB#1"
        elif len(lines) == 2:
            # 万一 CelesTrak 只返回了两行，在最前面补上名字
            lines.insert(0, "FYBB#1")
            
        # 重新拼接成字符串
        tle_data = "\n".join(lines)
        
        # 简单校验数据是否包含 TLE 的特征（第二行通常以 1 开头，第三行以 2 开头）
        if f"1 {CATNR}" not in tle_data and f"2 {CATNR}" not in tle_data:
            raise ValueError(f"获取到的数据似乎不是有效的 TLE 格式:\n{tle_data}")
            
        # 写入文件
        OUT.write_text(tle_data, encoding="utf-8")
        print(f"成功写入 {OUT}！最新 TLE 内容如下：\n{tle_data}")
        
    except Exception as e:
        print(f"抓取 TLE 失败: {e}")
        raise e

if __name__ == "__main__":
    fetch_tle()
