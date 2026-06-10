# -*- coding: utf-8 -*-
"""
文本处理工具模块
提供中文分词、关键词提取等文本处理功能
"""

import re
from typing import List, Dict, Set, Tuple
from collections import Counter

import jieba
import jieba.analyse
import jieba.posseg as pseg

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ML_CONFIG


class TextProcessor:
    """文本处理类"""

    def __init__(self):
        """初始化文本处理器"""
        # 加载自定义词典（可选）
        # jieba.load_userdict('user_dict.txt')

        # 设置停用词
        self.stop_words = ML_CONFIG['stop_words']

        # 初始化TF-IDF关键词提取器
        self.topK = ML_CONFIG['max_keywords']

    def segment(self, text: str) -> List[str]:
        """
        中文分词

        Args:
            text: 输入文本

        Returns:
            分词列表
        """
        if not text:
            return []

        # 使用精确模式分词
        words = jieba.lcut(text, cut_all=False)

        # 过滤停用词和单字
        filtered = [
            w.strip() for w in words
            if w.strip() and
               w.strip() not in self.stop_words and
               len(w.strip()) > 1 and
               not w.strip().isdigit()
        ]

        return filtered

    def extract_keywords(self, text: str, topK: int = None, method: str = 'tfidf') -> List[Dict]:
        """
        提取关键词

        Args:
            text: 输入文本
            topK: 返回数量
            method: 提取方法 ('tfidf' 或 'textrank')

        Returns:
            关键词列表 [{'word': str, 'weight': float}]
        """
        if not text:
            return []

        if topK is None:
            topK = self.topK

        if method == 'textrank':
            keywords = jieba.analyse.textrank(text, topK=topK, withWeight=True)
        else:  # 默认使用TF-IDF
            keywords = jieba.analyse.extract_tags(text, topK=topK, withWeight=True)

        # 过滤停用词
        result = []
        for word, weight in keywords:
            word = word.strip()
            if word and word not in self.stop_words and len(word) > 1 and not word.isdigit():
                result.append({
                    'word': word,
                    'weight': round(float(weight), 4)
                })

        return result

    def extract_keywords_batch(self, texts: List[str], topK: int = None) -> List[Dict]:
        """
        批量提取关键词

        Args:
            texts: 文本列表
            topK: 每个文本返回数量

        Returns:
            合并后的关键词列表
        """
        if not texts:
            return []

        if topK is None:
            topK = self.topK

        # 合并所有文本
        combined_text = ' '.join(texts)

        # 一次性提取关键词
        return self.extract_keywords(combined_text, topK=topK * 2)

    def get_word_frequency(self, texts: List[str], topK: int = 50) -> List[Dict]:
        """
        获取词频统计

        Args:
            texts: 文本列表
            topK: 返回数量

        Returns:
            词频列表 [{'word': str, 'count': int}]
        """
        if not texts:
            return []

        # 分词
        all_words = []
        for text in texts:
            words = self.segment(text)
            all_words.extend(words)

        # 词频统计
        counter = Counter(all_words)

        # 取TOP K
        most_common = counter.most_common(topK)

        return [{'word': word, 'count': count} for word, count in most_common]

    def extract_ngrams(self, text: str, n: int = 2) -> List[str]:
        """
        提取N-gram

        Args:
            text: 输入文本
            n: N值（2为二元组，3为三元组）

        Returns:
            N-gram列表
        """
        words = self.segment(text)
        if len(words) < n:
            return []

        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ''.join(words[i:i+n])
            ngrams.append(ngram)

        return ngrams

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        提取命名实体（简单版）

        Args:
            text: 输入文本

        Returns:
            实体字典 {'nr': 人名, 'ns': 地名, 'nt': 机构名}
        """
        if not text:
            return {'nr': [], 'ns': [], 'nt': []}

        words = pseg.cut(text)

        entities = {
            'nr': [],  # 人名
            'ns': [],  # 地名
            'nt': [],  # 机构名
        }

        for word, flag in words:
            if flag == 'nr' and word not in entities['nr']:
                entities['nr'].append(word)
            elif flag == 'ns' and word not in entities['ns']:
                entities['ns'].append(word)
            elif flag == 'nt' and word not in entities['nt']:
                entities['nt'].append(word)

        return entities

    def get_text_stats(self, text: str) -> Dict:
        """
        获取文本统计信息

        Args:
            text: 输入文本

        Returns:
            统计信息
        """
        if not text:
            return {
                'char_count': 0,
                'word_count': 0,
                'chinese_char_count': 0,
            }

        char_count = len(text)
        chinese_char_count = len(re.findall(r'[\u4e00-\u9fa5]', text))
        words = self.segment(text)
        word_count = len(words)

        return {
            'char_count': char_count,
            'word_count': word_count,
            'chinese_char_count': chinese_char_count,
        }
