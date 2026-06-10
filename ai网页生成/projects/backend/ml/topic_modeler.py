# -*- coding: utf-8 -*-
"""
主题建模模块
使用 LDA (Latent Dirichlet Allocation) 进行主题建模
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict

import numpy as np

from .text_processor import TextProcessor

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TopicModeler:
    """LDA主题建模器"""

    def __init__(self, num_topics: int = 5):
        """
        初始化主题建模器

        Args:
            num_topics: 主题数量
        """
        self.num_topics = num_topics
        self.text_processor = TextProcessor()

        # 模型参数
        self.alpha = 0.1  # 文档-主题分布的先验
        self.beta = 0.01  # 主题-词分布的先验
        self.iterations = 100  # 迭代次数

        # 模型状态
        self.vocabulary: List[str] = []
        self.word_to_idx: Dict[str, int] = {}
        self.idx_to_word: Dict[int, str] = {}

        # 主题结果
        self.doc_topics: List[List[float]] = []  # 每篇文档的主题分布
        self.topic_words: List[List[Tuple[str, float]]] = []  # 每个主题的词分布

    def _build_vocabulary(self, texts: List[str]) -> None:
        """构建词汇表"""
        # 分词
        all_words = []
        for text in texts:
            words = self.text_processor.segment(text)
            all_words.extend(words)

        # 统计词频
        word_freq = defaultdict(int)
        for word in all_words:
            word_freq[word] += 1

        # 过滤低频词，保留TOP词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        min_freq = 2

        self.vocabulary = [word for word, freq in sorted_words if freq >= min_freq]

        # 限制词汇表大小
        max_vocab_size = 1000
        if len(self.vocabulary) > max_vocab_size:
            self.vocabulary = self.vocabulary[:max_vocab_size]

        # 构建映射
        self.word_to_idx = {word: idx for idx, word in enumerate(self.vocabulary)}
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}

    def _text_to_bow(self, text: str) -> List[Tuple[int, int]]:
        """
        将文本转换为词袋表示

        Returns:
            [(word_idx, count), ...]
        """
        words = self.text_processor.segment(text)
        word_counts = defaultdict(int)

        for word in words:
            if word in self.word_to_idx:
                word_counts[self.word_to_idx[word]] += 1

        return list(word_counts.items())

    def _initialize(self, texts: List[str]) -> Tuple[np.ndarray, np.ndarray, List[List[int]]]:
        """
        初始化LDA参数

        Returns:
            (doc_topic_counts, topic_word_counts, assignments)
        """
        D = len(texts)
        V = len(self.vocabulary)
        K = self.num_topics

        # 文档-主题计数矩阵 (D x K)
        doc_topic_counts = np.zeros((D, K))

        # 主题-词计数矩阵 (K x V)
        topic_word_counts = np.zeros((K, V))

        # 每个词的topic分配 (List of List)
        assignments = []

        # 初始化分配
        for d, text in enumerate(texts):
            bow = self._text_to_bow(text)
            doc_assignments = []

            for word_idx, count in bow:
                # 随机分配主题
                topic = np.random.randint(0, K)
                doc_assignments.append((word_idx, topic, count))

                # 更新计数
                doc_topic_counts[d, topic] += count
                topic_word_counts[topic, word_idx] += count

            assignments.append(doc_assignments)

        return doc_topic_counts, topic_word_counts, assignments

    def _gibbs_sample(self, doc_topic_counts: np.ndarray,
                    topic_word_counts: np.ndarray,
                    assignments: List[List[Tuple[int, int, int]]],
                    texts: List[str]) -> None:
        """
        Gibbs采样

        Args:
            doc_topic_counts: 文档-主题计数
            topic_word_counts: 主题-词计数
            assignments: 词-主题分配
            texts: 原始文本
        """
        D = len(texts)
        K = self.num_topics
        V = len(self.vocabulary)

        # 主题-词总数
        topic_totals = topic_word_counts.sum(axis=1)

        for d in range(D):
            bow = self._text_to_bow(texts[d])
            word_indices = [item[0] for item in bow]

            for i, word_idx in enumerate(word_indices):
                # 获取当前分配
                current_topic = assignments[d][i][1]

                # 更新计数（减去当前）
                doc_topic_counts[d, current_topic] -= 1
                topic_word_counts[current_topic, word_idx] -= 1
                topic_totals[current_topic] -= 1

                # 计算新主题的概率
                probs = np.zeros(K)
                for topic in range(K):
                    # P(topic|document) * P(word|topic)
                    prob_topic_doc = (doc_topic_counts[d, topic] + self.alpha) / (D * self.alpha + sum(doc_topic_counts[d]))
                    prob_word_topic = (topic_word_counts[topic, word_idx] + self.beta) / (V * self.beta + topic_totals[topic])
                    probs[topic] = prob_topic_doc * prob_word_topic

                # 归一化
                probs = probs / probs.sum()

                # 采样新主题
                new_topic = np.random.choice(K, p=probs)

                # 更新分配
                assignments[d][i] = (word_idx, new_topic, 1)

                # 更新计数
                doc_topic_counts[d, new_topic] += 1
                topic_word_counts[new_topic, word_idx] += 1
                topic_totals[new_topic] += 1

    def fit(self, texts: List[str]) -> None:
        """
        训练LDA模型

        Args:
            texts: 文本列表
        """
        if len(texts) < 5:
            print("文本数量太少，无法进行主题建模")
            return

        print(f"开始训练LDA模型，文本数: {len(texts)}, 主题数: {self.num_topics}")

        # 构建词汇表
        self._build_vocabulary(texts)
        print(f"词汇表大小: {len(self.vocabulary)}")

        # 初始化
        doc_topic_counts, topic_word_counts, assignments = self._initialize(texts)

        # Gibbs采样迭代
        for iteration in range(self.iterations):
            self._gibbs_sample(doc_topic_counts, topic_word_counts, assignments, texts)

            if (iteration + 1) % 20 == 0:
                print(f"迭代 {iteration + 1}/{self.iterations} 完成")

        # 计算最终的主题分布
        D = len(texts)
        K = self.num_topics

        # 文档-主题分布
        self.doc_topics = []
        for d in range(D):
            topic_dist = (doc_topic_counts[d] + self.alpha) / (sum(doc_topic_counts[d]) + K * self.alpha)
            self.doc_topics.append(topic_dist.tolist())

        # 主题-词分布
        self.topic_words = []
        for topic in range(K):
            # 获取该主题下概率最高的词
            word_probs = (topic_word_counts[topic] + self.beta) / (topic_word_counts[topic].sum() + len(self.vocabulary) * self.beta)

            # 排序并取TOP词
            top_indices = np.argsort(word_probs)[::-1][:20]
            words_probs = [(self.idx_to_word[idx], round(float(word_probs[idx]), 4)) for idx in top_indices]

            self.topic_words.append(words_probs)

        print("LDA模型训练完成")

    def get_document_topics(self, doc_idx: int) -> List[Dict]:
        """
        获取指定文档的主题分布

        Args:
            doc_idx: 文档索引

        Returns:
            主题分布列表
        """
        if not self.doc_topics or doc_idx >= len(self.doc_topics):
            return []

        dist = self.doc_topics[doc_idx]
        return [
            {'topic_id': i, 'probability': round(p, 4)}
            for i, p in enumerate(dist)
        ]

    def get_topic_words(self, topic_idx: int, top_n: int = 10) -> List[Dict]:
        """
        获取指定主题的关键词

        Args:
            topic_idx: 主题索引
            top_n: 返回词数

        Returns:
            关键词列表
        """
        if not self.topic_words or topic_idx >= len(self.topic_words):
            return []

        return [
            {'word': word, 'weight': weight}
            for word, weight in self.topic_words[topic_idx][:top_n]
        ]

    def get_all_topics(self) -> List[Dict]:
        """
        获取所有主题

        Returns:
            主题列表
        """
        if not self.topic_words:
            return []

        return [
            {
                'topic_id': i,
                'keywords': [
                    {'word': word, 'weight': weight}
                    for word, weight in words[:10]
                ]
            }
            for i, words in enumerate(self.topic_words)
        ]


# 简单主题提取（无需完整LDA训练）
class SimpleTopicExtractor:
    """简单主题提取器"""

    def __init__(self):
        """初始化"""
        self.text_processor = TextProcessor()

    def extract_simple_topics(self, texts: List[str], num_topics: int = 5) -> List[Dict]:
        """
        简单主题提取（基于聚类思想）

        Args:
            texts: 文本列表
            num_topics: 主题数量

        Returns:
            主题列表
        """
        if len(texts) < num_topics:
            num_topics = len(texts)

        # 合并所有文本进行关键词提取
        combined_text = ' '.join(texts)
        keywords = self.text_processor.extract_keywords(combined_text, topK=num_topics * 10)

        # 简单分组
        topics = []
        words_per_topic = max(5, len(keywords) // num_topics)

        for i in range(num_topics):
            start_idx = i * words_per_topic
            end_idx = min(start_idx + words_per_topic, len(keywords))

            if start_idx >= len(keywords):
                break

            topic_keywords = keywords[start_idx:end_idx]

            topics.append({
                'topic_id': i,
                'topic_name': f'主题{i+1}',
                'keywords': topic_keywords
            })

        return topics
