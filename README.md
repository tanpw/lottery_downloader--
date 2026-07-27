# 超级大乐透历史开奖数据下载器

一个用于下载中国体育彩票"超级大乐透"历史开奖数据的Python工具。

## 功能特点

- 全量下载：获取从第一期至今的全部历史数据
- 增量更新：自动识别本地最新期号，仅下载新增数据
- 多种输出格式：支持CSV、JSON格式
- 反爬虫友好：合理的请求延迟，模拟真实浏览器访问
- 健壮的异常处理：网络重试、错误日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行参数

```bash
# 全量下载，输出CSV格式
python main.py -o data/lottery.csv -f csv

# 增量更新模式
python main.py -o data/lottery.csv -f csv -u

# 输出JSON格式
python main.py -o data/lottery.json -f json

# 指定起始和结束期号
python main.py -o data/lottery.csv --start 07001 --end 24150
```

### 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --output | -o | 输出文件路径 | lottery_data.csv |
| --format | -f | 输出格式(csv/json) | csv |
| --update | -u | 增量更新模式 | False |
| --start | | 起始期号 | 07001 |
| --end | | 结束期号 | 最新期 |
| --delay | -d | 请求延迟(秒) | 1.5 |
| --retry | -r | 重试次数 | 3 |

## 输出数据格式

### CSV格式示例

```csv
期号,开奖日期,前区号码,后区号码,奖池金额(元),全国销量(元)
24001,2024-01-01,03 15 19 27 34,05 10,1500000000,350000000
```

### JSON格式示例

```json
[
  {
    "期号": "24001",
    "开奖日期": "2024-01-01",
    "前区号码": "03 15 19 27 34",
    "后区号码": "05 10",
    "奖池金额": 1500000000,
    "全国销量": 350000000
  }
]
```

## 免责声明

本软件仅用于个人学习与研究目的，不用于任何商业或赌博用途。
请遵守相关法律法规，尊重网站robots.txt规则。
# lottery_downloader--
# DoubleColorBall1--
