"""数据存储模块"""

import os
import json
from typing import List, Dict, Any, Optional
import pandas as pd
from loguru import logger


class DataStorage:
    """数据存储器"""
    
    def __init__(self, output_path: str, format_type: str = "csv"):
        self.output_path = output_path
        self.format_type = format_type.lower()
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def save(self, data: List[Dict[str, Any]]) -> bool:
        """保存数据"""
        if not data:
            logger.warning("没有数据需要保存")
            return False
        
        try:
            if self.format_type == "csv":
                return self._save_csv(data)
            elif self.format_type == "json":
                return self._save_json(data)
            else:
                logger.error(f"不支持的格式: {self.format_type}")
                return False
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return False
    
    def _save_csv(self, data: List[Dict[str, Any]]) -> bool:
        """保存为CSV格式"""
        df = pd.DataFrame(data)
        # 按期号排序（从旧到新）
        df = df.sort_values("期号", ascending=True)
        df.to_csv(self.output_path, index=False, encoding="utf-8-sig")
        logger.info(f"数据已保存到: {self.output_path}")
        return True
    
    def _save_json(self, data: List[Dict[str, Any]]) -> bool:
        """保存为JSON格式"""
        # 按期号排序（从旧到新）
        sorted_data = sorted(data, key=lambda x: x["期号"])
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存到: {self.output_path}")
        return True
    
    def load_existing(self) -> Optional[List[Dict[str, Any]]]:
        """加载已有数据"""
        if not os.path.exists(self.output_path):
            return None
        
        try:
            if self.format_type == "csv":
                df = pd.read_csv(self.output_path, dtype=str)
                return df.to_dict("records")
            elif self.format_type == "json":
                with open(self.output_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"加载已有数据失败: {e}")
        
        return None
    
    def get_latest_issue(self) -> Optional[str]:
        """获取本地最新期号"""
        existing_data = self.load_existing()
        if not existing_data:
            return None
        
        # 找到最大的期号
        issues = [record.get("期号", "") for record in existing_data if record.get("期号")]
        if issues:
            return max(issues)
        return None
    
    def merge_data(self, new_data: List[Dict[str, Any]], existing_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并新旧数据"""
        existing_issues = {record["期号"] for record in existing_data}
        
        # 添加不重复的新数据
        merged = existing_data.copy()
        added_count = 0
        for record in new_data:
            if record["期号"] not in existing_issues:
                merged.append(record)
                added_count += 1
        
        logger.info(f"新增 {added_count} 期数据")
        return merged
