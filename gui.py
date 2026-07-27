#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
超级大乐透历史开奖数据下载器 - 图形界面版本
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
from loguru import logger

from fetcher import LotteryFetcher
from storage import DataStorage


class LogHandler:
    """日志处理器，将日志输出到GUI文本框"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
    
    def write(self, message):
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")
    
    def flush(self):
        pass


class LotteryDownloaderGUI:
    """彩票数据下载器GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("超级大乐透历史开奖数据下载器")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        self.is_running = False
        self.setup_ui()
        self.setup_logger()
    
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 输出路径
        path_frame = ttk.Frame(settings_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="保存位置:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value="lottery_data.csv")
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(path_frame, text="浏览...", command=self.browse_path).pack(side=tk.LEFT)
        
        # 格式选择
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="csv")
        ttk.Radiobutton(format_frame, text="CSV", variable=self.format_var, value="csv").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(format_frame, text="JSON", variable=self.format_var, value="json").pack(side=tk.LEFT)
        
        # 更新模式
        self.update_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="增量更新模式（仅下载新增数据）", variable=self.update_var).pack(anchor=tk.W, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.download_btn = ttk.Button(button_frame, text="开始下载", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="停止", command=self.stop_download, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="打开文件位置", command=self.open_file_location).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.StringVar(value="就绪")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled", wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def setup_logger(self):
        """配置日志输出到GUI"""
        logger.remove()
        logger.add(
            LogHandler(self.log_text).write,
            format="{time:HH:mm:ss} | {level: <8} | {message}\n",
            level="INFO"
        )
    
    def browse_path(self):
        """浏览保存路径"""
        format_type = self.format_var.get()
        if format_type == "csv":
            filetypes = [("CSV文件", "*.csv"), ("所有文件", "*.*")]
            default_ext = ".csv"
        else:
            filetypes = [("JSON文件", "*.json"), ("所有文件", "*.*")]
            default_ext = ".json"
        
        path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=f"lottery_data{default_ext}"
        )
        if path:
            self.path_var.set(path)
    
    def start_download(self):
        """开始下载"""
        if self.is_running:
            return
        
        output_path = self.path_var.get().strip()
        if not output_path:
            messagebox.showerror("错误", "请指定保存位置")
            return
        
        self.is_running = True
        self.download_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.progress_bar.start()
        self.progress_var.set("正在下载...")
        
        # 在新线程中执行下载
        thread = threading.Thread(target=self.download_task, daemon=True)
        thread.start()
    
    def download_task(self):
        """下载任务（在后台线程执行）"""
        try:
            output_path = self.path_var.get()
            format_type = self.format_var.get()
            update_mode = self.update_var.get()
            
            storage = DataStorage(output_path, format_type)
            fetcher = LotteryFetcher(delay=1.5, retry=3)
            
            start_issue = None
            existing_data = []
            
            if update_mode:
                start_issue = storage.get_latest_issue()
                if start_issue:
                    logger.info(f"本地最新期号: {start_issue}")
                    existing_data = storage.load_existing() or []
            
            logger.info("开始获取数据...")
            new_data = fetcher.fetch_all(start_issue=start_issue)
            
            if not self.is_running:
                logger.info("下载已取消")
                return
            
            if not new_data:
                if update_mode and existing_data:
                    logger.info("没有新数据需要更新")
                    self.root.after(0, lambda: messagebox.showinfo("完成", "没有新数据需要更新"))
                else:
                    logger.error("未能获取到任何数据")
                    self.root.after(0, lambda: messagebox.showerror("错误", "未能获取到任何数据"))
                return
            
            if update_mode and existing_data:
                final_data = storage.merge_data(new_data, existing_data)
            else:
                final_data = new_data
            
            if storage.save(final_data):
                logger.info(f"成功保存 {len(final_data)} 期数据")
                self.root.after(0, lambda: messagebox.showinfo("完成", f"成功保存 {len(final_data)} 期数据"))
            else:
                logger.error("保存数据失败")
                self.root.after(0, lambda: messagebox.showerror("错误", "保存数据失败"))
                
        except Exception as e:
            logger.exception(f"发生错误: {e}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"发生错误: {e}"))
        finally:
            fetcher.close()
            self.root.after(0, self.download_complete)
    
    def download_complete(self):
        """下载完成"""
        self.is_running = False
        self.download_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_var.set("完成")
        self.status_var.set(f"上次运行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def stop_download(self):
        """停止下载"""
        self.is_running = False
        logger.info("正在停止下载...")
        self.progress_var.set("正在停止...")
    
    def open_file_location(self):
        """打开文件所在位置"""
        output_path = self.path_var.get()
        if output_path:
            folder = os.path.dirname(os.path.abspath(output_path))
            if os.path.exists(folder):
                os.startfile(folder)
            else:
                messagebox.showinfo("提示", "文件夹不存在")
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    app = LotteryDownloaderGUI()
    app.run()


if __name__ == "__main__":
    main()
