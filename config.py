"""配置文件"""

# 数据源配置
# 使用体彩官方数据接口
DATA_SOURCE_URL = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"

# 请求头配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.sporttery.cn/",
    "Origin": "https://www.sporttery.cn",
    "Connection": "keep-alive",
}

# 游戏代码
GAME_NO = "85"  # 超级大乐透的游戏代码

# 默认配置
DEFAULT_DELAY = 1.5  # 请求延迟(秒)
DEFAULT_RETRY = 3    # 重试次数
DEFAULT_PAGE_SIZE = 30  # 每页数据条数

# 日志配置
LOG_FILE = "lottery_downloader.log"
LOG_ROTATION = "10 MB"
LOG_RETENTION = "7 days"
