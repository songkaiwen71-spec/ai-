# -*- coding: utf-8 -*-
"""
爬虫相关API路由
提供数据爬取功能
"""

from flask import Blueprint, request, jsonify
from threading import Thread
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler import WeiboCrawler, DemoDataGenerator, DataCleaner
from ml import SentimentAnalyzer, TextProcessor
from models import db

# 创建蓝图
crawl_bp = Blueprint('crawl', __name__, url_prefix='/api/crawl')


def process_weibo_data(weibo_list):
    """
    处理微博数据：情感分析、关键词提取

    Args:
        weibo_list: 微博列表

    Returns:
        处理后的微博列表
    """
    sentiment_analyzer = SentimentAnalyzer()
    text_processor = TextProcessor()

    processed = []
    for weibo in weibo_list:
        content = weibo.get('content', '')

        if not content:
            continue

        # 情感分析
        sentiment_result = sentiment_analyzer.analyze(content)
        weibo['sentiment_score'] = sentiment_result['score']
        weibo['sentiment_label'] = sentiment_result['label']

        # 关键词提取
        keywords = text_processor.extract_keywords(content, topK=10)
        weibo['keywords'] = keywords

        processed.append(weibo)

    return processed


@crawl_bp.route('/start', methods=['POST'])
def start_crawl():
    """
    开始爬取数据

    POST /api/crawl/start
    {
        "keyword": "关键词",
        "pages": 5,
        "use_demo": false  // 是否使用演示数据
    }
    """
    try:
        data = request.get_json() or {}
        keyword = data.get('keyword', '人工智能')
        pages = data.get('pages', 5)
        use_demo = data.get('use_demo', False)

        # 创建爬取记录
        record_id = db.create_crawl_record(keyword)

        result = {
            'success': True,
            'message': '爬取任务已启动',
            'record_id': record_id,
            'keyword': keyword,
            'pages': pages,
        }

        # 如果使用演示数据
        if use_demo:
            # 生成演示数据
            demo_data = DemoDataGenerator.generate_sample_data(keyword, count=pages * 10)

            # 清洗数据
            cleaner = DataCleaner()
            cleaned_data = cleaner.clean_batch(demo_data)

            # 处理数据（情感分析、关键词）
            processed_data = process_weibo_data(cleaned_data)

            # 保存到数据库
            saved_count = db.insert_weibo_batch(processed_data)

            # 更新记录
            db.update_crawl_record(record_id, 'completed',
                                 total=len(demo_data),
                                 success=saved_count)

            result['message'] = f'演示数据生成完成'
            result['total'] = len(demo_data)
            result['saved'] = saved_count

        else:
            # 实际爬取
            try:
                crawler = WeiboCrawler()
                weibo_data = crawler.crawl_by_keyword(keyword, pages)

                # 清洗数据
                cleaner = DataCleaner()
                cleaned_data = cleaner.clean_batch(weibo_data)

                # 处理数据
                processed_data = process_weibo_data(cleaned_data)

                # 保存到数据库
                saved_count = db.insert_weibo_batch(processed_data)

                # 更新记录
                db.update_crawl_record(record_id, 'completed',
                                     total=len(weibo_data),
                                     success=saved_count)

                result['message'] = f'爬取完成'
                result['total'] = len(weibo_data)
                result['saved'] = saved_count

            except Exception as e:
                db.update_crawl_record(record_id, 'failed', error=str(e))
                result['success'] = False
                result['message'] = f'爬取失败: {str(e)}'

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'启动爬取失败: {str(e)}'
        }), 500


@crawl_bp.route('/demo', methods=['POST'])
def generate_demo():
    """
    生成演示数据

    POST /api/crawl/demo
    {
        "keyword": "关键词",
        "count": 100
    }
    """
    try:
        data = request.get_json() or {}
        keyword = data.get('keyword', '人工智能')
        count = data.get('count', 100)

        # 生成演示数据
        demo_data = DemoDataGenerator.generate_sample_data(keyword, count)

        # 清洗数据
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean_batch(demo_data)

        # 处理数据
        processed_data = process_weibo_data(cleaned_data)

        # 保存到数据库
        saved_count = db.insert_weibo_batch(processed_data)

        # 获取统计
        stats = cleaner.get_statistics(cleaned_data)

        return jsonify({
            'success': True,
            'message': '演示数据生成完成',
            'total': len(demo_data),
            'saved': saved_count,
            'statistics': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成演示数据失败: {str(e)}'
        }), 500


@crawl_bp.route('/status', methods=['GET'])
def get_crawl_status():
    """
    获取爬取状态

    GET /api/crawl/status
    """
    try:
        records = db.get_crawl_records(limit=10)

        return jsonify({
            'success': True,
            'records': records
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取状态失败: {str(e)}'
        }), 500


@crawl_bp.route('/hot', methods=['POST'])
def crawl_hot_search():
    """
    爬取热搜榜

    POST /api/crawl/hot
    """
    try:
        data = request.get_json() or {}
        pages = data.get('pages', 5)

        # 爬取热搜
        crawler = WeiboCrawler()
        hot_data = crawler.crawl_hot_search(pages)

        # 清洗和处理
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean_batch(hot_data)
        processed_data = process_weibo_data(cleaned_data)

        # 保存
        saved_count = db.insert_weibo_batch(processed_data)

        return jsonify({
            'success': True,
            'message': '热搜数据获取完成',
            'total': len(hot_data),
            'saved': saved_count,
            'data': hot_data[:10]  # 返回前10条
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'爬取热搜失败: {str(e)}'
        }), 500
