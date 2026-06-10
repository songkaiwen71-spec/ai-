# -*- coding: utf-8 -*-
"""
情感分析模块
使用 SnowNLP 进行中文文本情感分析
"""

from typing import List, Dict, Tuple
import random

from snownlp import SnowNLP

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ML_CONFIG


class SentimentAnalyzer:
    """情感分析器"""

    def __init__(self):
        """初始化情感分析器"""
        self.threshold = ML_CONFIG['snownl_p_threshold']

    def analyze(self, text: str) -> Dict:
        """
        分析单条文本的情感

        Args:
            text: 输入文本

        Returns:
            情感分析结果 {
                'score': float,  # 情感分数 0-1
                'label': str,    # 情感标签 'positive', 'negative', 'neutral'
                'confidence': float  # 置信度
            }
        """
        if not text or len(text.strip()) < 2:
            return {
                'score': 0.5,
                'label': 'neutral',
                'confidence': 0.0
            }

        try:
            # 使用SnowNLP分析
            s = SnowNLP(text)

            # 情感分数（0-1之间，1表示积极）
            score = s.sentiments

            # 根据阈值判断情感标签
            if score >= 0.6:
                label = 'positive'
            elif score <= 0.4:
                label = 'negative'
            else:
                label = 'neutral'

            # 置信度：距离阈值越远，置信度越高
            if label == 'neutral':
                confidence = 1 - abs(score - 0.5) * 2
            else:
                confidence = abs(score - 0.5) * 2

            return {
                'score': round(float(score), 4),
                'label': label,
                'confidence': round(float(confidence), 4)
            }

        except Exception as e:
            print(f"情感分析失败: {e}, text: {text[:50]}")
            return {
                'score': 0.5,
                'label': 'neutral',
                'confidence': 0.0
            }

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        批量分析文本情感

        Args:
            texts: 文本列表

        Returns:
            情感分析结果列表
        """
        results = []

        for text in texts:
            result = self.analyze(text)
            results.append(result)

        return results

    def get_distribution(self, texts: List[str]) -> Dict[str, int]:
        """
        获取情感分布统计

        Args:
            texts: 文本列表

        Returns:
            情感分布 {'positive': int, 'neutral': int, 'negative': int}
        """
        distribution = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }

        for text in texts:
            result = self.analyze(text)
            distribution[result['label']] += 1

        return distribution

    def get_distribution_percentage(self, texts: List[str]) -> Dict[str, float]:
        """
        获取情感分布百分比

        Args:
            texts: 文本列表

        Returns:
            情感分布百分比
        """
        total = len(texts)
        if total == 0:
            return {
                'positive': 0.0,
                'neutral': 0.0,
                'negative': 0.0
            }

        distribution = self.get_distribution(texts)

        return {
            'positive': round(distribution['positive'] / total * 100, 2),
            'neutral': round(distribution['neutral'] / total * 100, 2),
            'negative': round(distribution['negative'] / total * 100, 2)
        }

    def get_average_score(self, texts: List[str]) -> float:
        """
        获取平均情感分数

        Args:
            texts: 文本列表

        Returns:
            平均分数
        """
        if not texts:
            return 0.5

        total_score = 0.0
        count = 0

        for text in texts:
            result = self.analyze(text)
            total_score += result['score']
            count += 1

        return round(total_score / count, 4) if count > 0 else 0.5

    def get_sentiment_trend(self, data_list: List[Dict], time_field: str = 'publish_time') -> List[Dict]:
        """
        获取情感趋势数据

        Args:
            data_list: 数据列表，每条包含文本和时间
            time_field: 时间字段名

        Returns:
            按时间分组的情感趋势
        """
        from collections import defaultdict

        # 按日期分组
        trends = defaultdict(lambda: {'scores': [], 'count': 0})

        for item in data_list:
            text = item.get('content', '')
            time_str = item.get(time_field, '')

            if not text:
                continue

            # 提取日期
            if time_str:
                date = time_str.split(' ')[0] if ' ' in time_str else time_str[:10]
            else:
                date = 'unknown'

            # 分析情感
            result = self.analyze(text)
            trends[date]['scores'].append(result['score'])
            trends[date]['count'] += 1

        # 计算每日平均
        result = []
        for date in sorted(trends.keys()):
            scores = trends[date]['scores']
            avg_score = sum(scores) / len(scores) if scores else 0.5

            # 计算正负中性比例
            positive = sum(1 for s in scores if s >= 0.6)
            negative = sum(1 for s in scores if s <= 0.4)
            neutral = len(scores) - positive - negative

            result.append({
                'date': date,
                'avg_sentiment': round(avg_score, 4),
                'count': trends[date]['count'],
                'positive_ratio': round(positive / len(scores) * 100, 2) if scores else 0,
                'negative_ratio': round(negative / len(scores) * 100, 2) if scores else 0,
                'neutral_ratio': round(neutral / len(scores) * 100, 2) if scores else 0,
            })

        return result


# 辅助函数：生成模拟情感数据（用于演示）
def generate_demo_sentiment(texts: List[str]) -> List[Dict]:
    """
    生成演示用情感数据

    当没有真实分析能力时，生成模拟结果
    """
    import random

    results = []
    for text in texts:
        # 随机生成一个分数
        score = random.uniform(0.3, 0.8)

        if score >= 0.6:
            label = 'positive'
        elif score <= 0.4:
            label = 'negative'
        else:
            label = 'neutral'

        results.append({
            'score': round(score, 4),
            'label': label,
            'confidence': round(random.uniform(0.5, 0.9), 4)
        })

    return results
