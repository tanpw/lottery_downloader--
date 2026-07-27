"""数据获取模块"""

import time
import requests
from typing import Optional, List, Dict, Any
from loguru import logger

from config import DATA_SOURCE_URL, HEADERS, GAME_NO, DEFAULT_PAGE_SIZE


class LotteryFetcher:
    """彩票数据获取器"""
    
    def __init__(self, delay: float = 1.5, retry: int = 3):
        self.delay = delay
        self.retry = retry
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def fetch_page(self, page_no: int, page_size: int = DEFAULT_PAGE_SIZE) -> Optional[Dict[str, Any]]:
        """获取单页数据"""
        params = {
            "gameNo": GAME_NO,
            "provinceId": "0",
            "pageSize": page_size,
            "isVerify": "1",
            "pageNo": page_no,
        }
        
        for attempt in range(self.retry):
            try:
                logger.debug(f"正在获取第 {page_no} 页数据 (尝试 {attempt + 1}/{self.retry})")
                response = self.session.get(DATA_SOURCE_URL, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if data.get("success"):
                    return data.get("value", {})
                else:
                    logger.warning(f"API返回失败: {data.get('errorMessage', '未知错误')}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.retry}): {e}")
                if attempt < self.retry - 1:
                    time.sleep(self.delay * 2)
            except Exception as e:
                logger.error(f"解析数据失败: {e}")
                
        return None
    
    def fetch_all(self, start_issue: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有数据（支持增量更新）"""
        all_data = []
        page_no = 1
        
        # 首先获取第一页以确定总页数
        first_page = self.fetch_page(page_no)
        if not first_page:
            logger.error("无法获取数据，请检查网络连接")
            return []
        
        total_count = first_page.get("total", 0)
        page_size = DEFAULT_PAGE_SIZE
        total_pages = (total_count + page_size - 1) // page_size
        
        logger.info(f"共有 {total_count} 期数据，{total_pages} 页")
        
        # 处理第一页数据
        records = first_page.get("list", [])
        for record in records:
            parsed = self._parse_record(record)
            if parsed:
                if start_issue and parsed["期号"] <= start_issue:
                    logger.info(f"已到达本地最新期号 {start_issue}，停止获取")
                    return all_data
                all_data.append(parsed)
        
        time.sleep(self.delay)
        
        # 获取剩余页面
        for page_no in range(2, total_pages + 1):
            logger.info(f"正在获取第 {page_no}/{total_pages} 页...")
            
            page_data = self.fetch_page(page_no)
            if not page_data:
                logger.warning(f"第 {page_no} 页获取失败，跳过")
                continue
            
            records = page_data.get("list", [])
            should_stop = False
            
            for record in records:
                parsed = self._parse_record(record)
                if parsed:
                    if start_issue and parsed["期号"] <= start_issue:
                        logger.info(f"已到达本地最新期号 {start_issue}，停止获取")
                        should_stop = True
                        break
                    all_data.append(parsed)
            
            if should_stop:
                break
                
            time.sleep(self.delay)
        
        logger.info(f"共获取 {len(all_data)} 期数据")
        return all_data
    
    def _parse_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析单条记录"""
        try:
            # 解析开奖号码
            draw_result = record.get("lotteryDrawResult", "")
            numbers = draw_result.split()
            
            if len(numbers) >= 7:
                front_numbers = " ".join(numbers[:5])  # 前区5个号码
                back_numbers = " ".join(numbers[5:7])  # 后区2个号码
            else:
                front_numbers = draw_result
                back_numbers = ""
            
            # 解析日期
            draw_time = record.get("lotteryDrawTime", "")
            if draw_time:
                draw_date = draw_time.split(" ")[0] if " " in draw_time else draw_time
            else:
                draw_date = ""
            
            return {
                "期号": record.get("lotteryDrawNum", ""),
                "开奖日期": draw_date,
                "前区号码": front_numbers,
                "后区号码": back_numbers,
                "奖池金额": record.get("poolBalanceAfterdraw", 0),
                "全国销量": record.get("totalSaleAmount", 0),
            }
        except Exception as e:
            logger.error(f"解析记录失败: {e}, 原始数据: {record}")
            return None
    
    def close(self):
        """关闭会话"""
        self.session.close()
