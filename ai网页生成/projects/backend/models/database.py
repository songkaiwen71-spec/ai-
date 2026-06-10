# -*- coding: utf-8 -*-
"""
数据库模型 - SQLite数据库初始化与操作
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH


class Database:
    """数据库操作类"""

    def __init__(self, db_path: str = None):
        """初始化数据库连接"""
        self.db_path = db_path or DATABASE_PATH
        # 确保data目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """初始化数据库，创建表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 创建微博数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weibo_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weibo_id TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    username TEXT,
                    user_id TEXT,
                    publish_time DATETIME,
                    like_count INTEGER DEFAULT 0,
                    comment_count INTEGER DEFAULT 0,
                    repost_count INTEGER DEFAULT 0,
                    sentiment_score REAL DEFAULT 0.5,
                    sentiment_label TEXT DEFAULT 'neutral',
                    keywords TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建爬取记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawl_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME,
                    status TEXT DEFAULT 'running',
                    total_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    error_message TEXT
                )
            ''')

            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_weibo_publish_time
                ON weibo_data(publish_time)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_weibo_sentiment
                ON weibo_data(sentiment_label)
            ''')

    def insert_weibo(self, data: Dict[str, Any]) -> bool:
        """插入单条微博数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO weibo_data
                    (weibo_id, content, username, user_id, publish_time,
                     like_count, comment_count, repost_count, sentiment_score,
                     sentiment_label, keywords, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get('weibo_id'),
                    data.get('content'),
                    data.get('username'),
                    data.get('user_id'),
                    data.get('publish_time'),
                    data.get('like_count', 0),
                    data.get('comment_count', 0),
                    data.get('repost_count', 0),
                    data.get('sentiment_score', 0.5),
                    data.get('sentiment_label', 'neutral'),
                    json.dumps(data.get('keywords', []), ensure_ascii=False),
                    datetime.now()
                ))
                return True
            except Exception as e:
                print(f"插入数据失败: {e}")
                return False

    def insert_weibo_batch(self, data_list: List[Dict[str, Any]]) -> int:
        """批量插入微博数据"""
        count = 0
        for data in data_list:
            if self.insert_weibo(data):
                count += 1
        return count

    def get_all_weibo(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """获取所有微博数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM weibo_data
                ORDER BY publish_time DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_weibo_count(self) -> int:
        """获取微博总数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM weibo_data')
            return cursor.fetchone()[0]

    def get_sentiment_stats(self) -> Dict[str, int]:
        """获取情感统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sentiment_label, COUNT(*) as count
                FROM weibo_data
                GROUP BY sentiment_label
            ''')
            rows = cursor.fetchall()
            return {row['sentiment_label']: row['count'] for row in rows}

    def get_trend_data(self, days: int = 7) -> List[Dict]:
        """获取时间趋势数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT
                    DATE(publish_time) as date,
                    COUNT(*) as count,
                    AVG(sentiment_score) as avg_sentiment,
                    SUM(like_count) as total_likes,
                    SUM(comment_count) as total_comments,
                    SUM(repost_count) as total_reposts
                FROM weibo_data
                WHERE publish_time >= DATE('now', '-' || ? || ' days')
                GROUP BY DATE(publish_time)
                ORDER BY date
            ''', (days,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_hot_words(self, limit: int = 50) -> List[Dict]:
        """获取热词统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT keywords FROM weibo_data
                WHERE keywords IS NOT NULL AND keywords != '[]'
            ''')
            rows = cursor.fetchall()

            # 合并所有关键词
            word_count = {}
            for row in rows:
                try:
                    keywords = json.loads(row['keywords'])
                    for kw in keywords:
                        word_count[kw['word']] = word_count.get(kw['word'], 0) + kw['weight']
                except:
                    continue

            # 排序并返回
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            return [{'word': w, 'count': int(c)} for w, c in sorted_words[:limit]]

    def get_geo_distribution(self) -> List[Dict]:
        """获取地理分布数据（模拟数据，实际微博通常不带地理位置）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT
                    user_id,
                    username,
                    like_count + comment_count + repost_count as engagement
                FROM weibo_data
                WHERE user_id IS NOT NULL
                ORDER BY engagement DESC
                LIMIT 100
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_all(self) -> bool:
        """清空所有数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM weibo_data')
            return True

    def create_crawl_record(self, keyword: str) -> int:
        """创建爬取记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO crawl_records (keyword, status)
                VALUES (?, 'running')
            ''', (keyword,))
            return cursor.lastrowid

    def update_crawl_record(self, record_id: int, status: str,
                           total: int = 0, success: int = 0, error: str = None):
        """更新爬取记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE crawl_records
                SET status = ?, total_count = ?, success_count = ?,
                    error_message = ?, end_time = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, total, success, error, record_id))

    def get_crawl_records(self, limit: int = 10) -> List[Dict]:
        """获取爬取记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM crawl_records
                ORDER BY start_time DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


# 创建全局数据库实例
db = Database()
