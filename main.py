#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
超级大乐透历史开奖数据下载器

用于下载中国体育彩票"超级大乐透"历史开奖数据。
仅用于个人学习与研究，不用于任何商业或赌博用途。
"""

import argparse
import sys
from loguru import logger

from config import LOG_FILE, LOG_ROTATION, LOG_RETENTION, DEFAULT_DELAY, DEFAULT_RETRY
from fetcher import LotteryFetcher
from storage import DataStorage


def setup_logger():
    """配置日志"""
    logger.remove()  # 移除默认处理器
    
    # 控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    # 文件输出
    logger.add(
        LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation=LOG_ROTATION,
        retention=LOG_RETENTION,
        encoding="utf-8",
        level="DEBUG"
    )


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="超级大乐透历史开奖数据下载器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py -o data/lottery.csv -f csv      # 全量下载CSV格式
  python main.py -o data/lottery.csv -u          # 增量更新
  python main.py -o data/lottery.json -f json    # 输出JSON格式
        """
    )
    
    parser.add_argument(
        "-o", "--output",
        default="lottery_data.csv",
        help="输出文件路径 (默认: lottery_data.csv)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json"],
        default="csv",
        help="输出格式 (默认: csv)"
    )
    
    parser.add_argument(
        "-u", "--update",
        action="store_true",
        help="增量更新模式，仅下载新增数据"
    )
    
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"请求延迟秒数 (默认: {DEFAULT_DELAY})"
    )
    
    parser.add_argument(
        "-r", "--retry",
        type=int,
        default=DEFAULT_RETRY,
        help=f"请求重试次数 (默认: {DEFAULT_RETRY})"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    setup_logger()
    args = parse_args()
    
    logger.info("=" * 50)
    logger.info("超级大乐透历史开奖数据下载器")
    logger.info("=" * 50)
    logger.info(f"输出文件: {args.output}")
    logger.info(f"输出格式: {args.format}")
    logger.info(f"更新模式: {'增量更新' if args.update else '全量下载'}")
    
    # 初始化存储器
    storage = DataStorage(args.output, args.format)
    
    # 确定起始期号（增量更新模式）
    start_issue = None
    existing_data = []
    
    if args.update:
        start_issue = storage.get_latest_issue()
        if start_issue:
            logger.info(f"本地最新期号: {start_issue}")
            existing_data = storage.load_existing() or []
        else:
            logger.info("本地无数据，将执行全量下载")
    
    # 初始化获取器
    fetcher = LotteryFetcher(delay=args.delay, retry=args.retry)
    
    try:
        # 获取数据
        logger.info("开始获取数据...")
        new_data = fetcher.fetch_all(start_issue=start_issue)
        
        if not new_data:
            if args.update and existing_data:
                logger.info("没有新数据需要更新")
            else:
                logger.error("未能获取到任何数据")
            return
        
        # 合并数据（增量更新模式）
        if args.update and existing_data:
            final_data = storage.merge_data(new_data, existing_data)
        else:
            final_data = new_data
        
        # 保存数据
        if storage.save(final_data):
            logger.info(f"成功保存 {len(final_data)} 期数据")
        else:
            logger.error("保存数据失败")
            
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
    except Exception as e:
        logger.exception(f"发生错误: {e}")
    finally:
        fetcher.close()
    
    logger.info("程序结束")


if __name__ == "__main__":
    main()
