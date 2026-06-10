# -*- coding: utf-8 -*-
"""
配置文件 - 后端应用配置
包含数据库配置、爬虫配置、机器学习配置等
"""

import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库配置
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'weibo.db')

# 爬虫配置
CRAWLER_CONFIG = {
    'max_pages': 10,              # 最大爬取页数
    'timeout': 30,                # 请求超时时间（秒）
    'retry_times': 3,             # 重试次数
    'delay': 2,                   # 请求间隔（秒）
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]
}

# 机器学习配置
ML_CONFIG = {
    'snownl_p_threshold': 0.5,    # SnowNLP情感分析阈值
    'max_keywords': 50,           # 最大关键词数量
    'wordcloud_width': 800,       # 词云宽度
    'wordcloud_height': 600,      # 词云高度
    'stop_words': set([
        '的', '了', '是', '在', '我', '有', '和', '就', '不', '人',
        '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
        '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他',
        '她', '它', '们', '这个', '那个', '什么', '怎么', '为什么', '如何',
        '啊', '呢', '吧', '吗', '呀', '哦', '嗯', '哈哈', '嘿嘿', '唉',
        '可以', '可能', '应该', '就是', '还是', '但是', '因为', '所以',
        '如果', '虽然', '然后', '而且', '或者', '以及', '关于', '对于',
        '转发', '微博', '评论', '视频', '图片', '全文', '展开', '收起',
        '点击', '链接', '网页', '来源', '分钟', '小时', '今天', '昨天',
        '现在', '已经', '正在', '刚刚', '终于', '居然', '竟然', '当然'
    ])
}

# API配置
API_CONFIG = {
    'cors_enabled': True,         # 允许跨域
    'cors_origins': '*',          # 跨域来源
    'json_sort': False,           # JSON不排序
    'max_content_length': 16 * 1024 * 1024  # 最大16MB
}

# Flask配置
FLASK_CONFIG = {
    'SECRET_KEY': 'weibo-sentiment-analysis-secret-key-2024',
    'DEBUG': True,
    'JSON_AS_ASCII': False  # JSON中文不转义
}
