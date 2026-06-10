# -*- coding: utf-8 -*-
"""
数据清洗模块
对爬取的原始数据进行清洗、去重、格式化
"""

import re
import json
from typing import List, Dict, Set, Any
from datetime import datetime


class DataCleaner:
    """数据清洗器"""

    # URL正则表达式
    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )

    # HTML标签正则
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')

    # 邮箱正则
    EMAIL_PATTERN = re.compile(r'\S+@\S+\.\S+')

    # 手机号正则
    PHONE_PATTERN = re.compile(r'1[3-9]\d{9}')

    # 特殊符号（保留中文、英文、数字）
    SPECIAL_CHARS_PATTERN = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]')

    def __init__(self):
        """初始化清洗器"""
        self.seen_ids: Set[str] = set()

    def reset_seen_ids(self):
        """重置已见ID集合"""
        self.seen_ids = set()

    def remove_urls(self, text: str) -> str:
        """移除URL"""
        if not text:
            return ''
        return self.URL_PATTERN.sub('', text)

    def remove_html_tags(self, text: str) -> str:
        """移除HTML标签"""
        if not text:
            return ''
        return self.HTML_TAG_PATTERN.sub('', text)

    def remove_emails(self, text: str) -> str:
        """移除邮箱"""
        if not text:
            return ''
        return self.EMAIL_PATTERN.sub('', text)

    def remove_phone_numbers(self, text: str) -> str:
        """移除手机号"""
        if not text:
            return ''
        return self.PHONE_PATTERN.sub('', text)

    def remove_special_chars(self, text: str, keep_spaces: bool = True) -> str:
        """移除特殊字符"""
        if not text:
            return ''
        if keep_spaces:
            return self.SPECIAL_CHARS_PATTERN.sub('', text)
        else:
            return re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', text)

    def normalize_whitespace(self, text: str) -> str:
        """规范化空白字符"""
        if not text:
            return ''
        # 多个空格合并为一个
        text = re.sub(r'\s+', ' ', text)
        # 去除首尾空白
        return text.strip()

    def clean_content(self, content: str) -> str:
        """
        清洗微博内容

        Args:
            content: 原始内容

        Returns:
            清洗后的内容
        """
        if not content:
            return ''

        # 移除URL
        content = self.remove_urls(content)
        # 移除HTML标签
        content = self.remove_html_tags(content)
        # 移除邮箱
        content = self.remove_emails(content)
        # 移除手机号
        content = self.remove_phone_numbers(content)
        # 规范化空白
        content = self.normalize_whitespace(content)

        return content

    def is_valid_content(self, content: str, min_length: int = 5, max_length: int = 2000) -> bool:
        """
        检查内容是否有效

        Args:
            content: 内容
            min_length: 最小长度
            max_length: 最大长度

        Returns:
            是否有效
        """
        if not content:
            return False

        # 移除空白后的长度
        length = len(content.strip())

        if length < min_length or length > max_length:
            return False

        # 检查是否包含有效字符
        chinese_count = len(re.findall(r'[\u4e00-\u9fa5]', content))
        if chinese_count < 3:  # 至少包含3个中文字符
            return False

        return True

    def deduplicate(self, data_list: List[Dict], id_field: str = 'weibo_id') -> List[Dict]:
        """
        数据去重

        Args:
            data_list: 数据列表
            id_field: ID字段名

        Returns:
            去重后的数据列表
        """
        self.reset_seen_ids()
        result = []

        for item in data_list:
            item_id = item.get(id_field)
            if not item_id:
                continue

            if item_id in self.seen_ids:
                continue

            self.seen_ids.add(item_id)
            result.append(item)

        return result

    def clean_batch(self, data_list: List[Dict]) -> List[Dict]:
        """
        批量清洗数据

        Args:
            data_list: 原始数据列表

        Returns:
            清洗后的数据列表
        """
        cleaned = []

        for item in data_list:
            # 清洗内容
            if 'content' in item:
                item['content'] = self.clean_content(item['content'])

            # 检查有效性
            if self.is_valid_content(item.get('content', '')):
                cleaned.append(item)

        # 去重
        cleaned = self.deduplicate(cleaned)

        return cleaned

    def filter_by_keyword(self, data_list: List[Dict], keyword: str, content_field: str = 'content') -> List[Dict]:
        """
        按关键词过滤数据

        Args:
            data_list: 数据列表
            keyword: 关键词
            content_field: 内容字段名

        Returns:
            过滤后的数据列表
        """
        if not keyword:
            return data_list

        keyword = keyword.lower()
        filtered = []

        for item in data_list:
            content = item.get(content_field, '').lower()
            if keyword in content:
                filtered.append(item)

        return filtered

    def get_statistics(self, data_list: List[Dict]) -> Dict[str, Any]:
        """
        获取数据统计信息

        Args:
            data_list: 数据列表

        Returns:
            统计信息
        """
        if not data_list:
            return {
                'total': 0,
                'avg_length': 0,
                'min_length': 0,
                'max_length': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_reposts': 0,
            }

        lengths = [len(item.get('content', '')) for item in data_list]
        total_likes = sum(item.get('like_count', 0) for item in data_list)
        total_comments = sum(item.get('comment_count', 0) for item in data_list)
        total_reposts = sum(item.get('repost_count', 0) for item in data_list)

        return {
            'total': len(data_list),
            'avg_length': sum(lengths) / len(lengths) if lengths else 0,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_reposts': total_reposts,
        }
