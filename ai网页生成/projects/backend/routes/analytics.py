# -*- coding: utf-8 -*-
"""
分析相关API路由
提供各种分析接口
"""

from flask import Blueprint, request, jsonify
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db
from ml import SentimentAnalyzer, TextProcessor

# 创建蓝图
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api')


@analytics_bp.route('/sentiment', methods=['GET'])
def get_sentiment_stats():
    """
    获取情感统计

    GET /api/sentiment
    """
    try:
        # 获取所有数据
        all_data = db.get_all_weibo(limit=10000)

        if not all_data:
            return jsonify({
                'success': True,
                'data': {
                    'distribution': {
                        'positive': 0,
                        'neutral': 0,
                        'negative': 0
                    },
                    'percentage': {
                        'positive': 0,
                        'neutral': 0,
                        'negative': 0
                    },
                    'average_score': 0,
                    'total': 0
                }
            })

        # 统计情感分布
        distribution = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }

        total_score = 0

        for item in all_data:
            label = item.get('sentiment_label', 'neutral')
            if label in distribution:
                distribution[label] += 1
            total_score += item.get('sentiment_score', 0.5)

        total = len(all_data)
        average_score = total_score / total if total > 0 else 0.5

        # 计算百分比
        percentage = {
            'positive': round(distribution['positive'] / total * 100, 2) if total > 0 else 0,
            'neutral': round(distribution['neutral'] / total * 100, 2) if total > 0 else 0,
            'negative': round(distribution['negative'] / total * 100, 2) if total > 0 else 0,
        }

        return jsonify({
            'success': True,
            'data': {
                'distribution': distribution,
                'percentage': percentage,
                'average_score': round(average_score, 4),
                'total': total
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取情感统计失败: {str(e)}'
        }), 500


@analytics_bp.route('/wordcloud', methods=['GET'])
def get_wordcloud_data():
    """
    获取词云数据

    GET /api/wordcloud?limit=100
    """
    try:
        limit = request.args.get('limit', 100, type=int)

        # 获取热词
        hot_words = db.get_hot_words(limit=limit)

        # 转换为词云格式
        wordcloud_data = [
            {'name': item['word'], 'value': item['count']}
            for item in hot_words
        ]

        return jsonify({
            'success': True,
            'data': wordcloud_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取词云数据失败: {str(e)}'
        }), 500


@analytics_bp.route('/trend', methods=['GET'])
def get_trend_data():
    """
    获取趋势数据

    GET /api/trend?days=7
    """
    try:
        days = request.args.get('days', 7, type=int)

        # 获取趋势数据
        trend_data = db.get_trend_data(days=days)

        return jsonify({
            'success': True,
            'data': trend_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取趋势数据失败: {str(e)}'
        }), 500


@analytics_bp.route('/hotwords', methods=['GET'])
def get_hotwords():
    """
    获取热词统计

    GET /api/hotwords?limit=50
    """
    try:
        limit = request.args.get('limit', 50, type=int)

        # 获取热词
        hot_words = db.get_hot_words(limit=limit)

        return jsonify({
            'success': True,
            'data': hot_words
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取热词失败: {str(e)}'
        }), 500


@analytics_bp.route('/geo', methods=['GET'])
def get_geo_distribution():
    """
    获取地理分布数据

    GET /api/geo
    """
    try:
        # 获取用户分布数据
        geo_data = db.get_geo_distribution()

        # 模拟省份分布（基于用户ID随机分布）
        import random
        provinces = [
            {'name': '北京', 'value': 0},
            {'name': '上海', 'value': 0},
            {'name': '广东', 'value': 0},
            {'name': '浙江', 'value': 0},
            {'name': '江苏', 'value': 0},
            {'name': '四川', 'value': 0},
            {'name': '湖北', 'value': 0},
            {'name': '河南', 'value': 0},
            {'name': '山东', 'value': 0},
            {'name': '福建', 'value': 0},
            {'name': '湖南', 'value': 0},
            {'name': '陕西', 'value': 0},
            {'name': '辽宁', 'value': 0},
            {'name': '重庆', 'value': 0},
            {'name': '天津', 'value': 0},
            {'name': '安徽', 'value': 0},
            {'name': '江西', 'value': 0},
            {'name': '河北', 'value': 0},
            {'name': '山西', 'value': 0},
            {'name': '云南', 'value': 0},
        ]

        total = len(geo_data)
        if total > 0:
            # 根据用户数量分配省份
            for i, item in enumerate(geo_data[:len(provinces)]):
                provinces[i]['value'] = item.get('engagement', 0) + random.randint(10, 100)

        # 排序
        provinces = sorted(provinces, key=lambda x: x['value'], reverse=True)

        return jsonify({
            'success': True,
            'data': provinces
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取地理分布失败: {str(e)}'
        }), 500


@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    获取仪表盘综合数据

    GET /api/dashboard
    """
    try:
        # 获取所有数据
        all_data = db.get_all_weibo(limit=10000)
        total = len(all_data)

        # 1. 情感分布
        sentiment_distribution = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }
        total_sentiment_score = 0

        for item in all_data:
            label = item.get('sentiment_label', 'neutral')
            if label in sentiment_distribution:
                sentiment_distribution[label] += 1
            total_sentiment_score += item.get('sentiment_score', 0.5)

        avg_sentiment = total_sentiment_score / total if total > 0 else 0.5

        sentiment_percentage = {
            'positive': round(sentiment_distribution['positive'] / total * 100, 2) if total > 0 else 0,
            'neutral': round(sentiment_distribution['neutral'] / total * 100, 2) if total > 0 else 0,
            'negative': round(sentiment_distribution['negative'] / total * 100, 2) if total > 0 else 0,
        }

        # 2. 互动统计
        total_likes = sum(item.get('like_count', 0) for item in all_data)
        total_comments = sum(item.get('comment_count', 0) for item in all_data)
        total_reposts = sum(item.get('repost_count', 0) for item in all_data)

        # 3. 热词
        hot_words = db.get_hot_words(limit=30)

        # 4. 趋势数据
        trend_data = db.get_trend_data(days=7)

        # 5. 地理分布
        geo_data = db.get_geo_distribution()

        # 模拟省份分布
        import random
        provinces = [
            {'name': '北京', 'value': 0},
            {'name': '上海', 'value': 0},
            {'name': '广东', 'value': 0},
            {'name': '浙江', 'value': 0},
            {'name': '江苏', 'value': 0},
            {'name': '四川', 'value': 0},
            {'name': '湖北', 'value': 0},
            {'name': '河南', 'value': 0},
            {'name': '山东', 'value': 0},
            {'name': '福建', 'value': 0},
            {'name': '湖南', 'value': 0},
            {'name': '陕西', 'value': 0},
            {'name': '辽宁', 'value': 0},
            {'name': '重庆', 'value': 0},
            {'name': '天津', 'value': 0},
        ]

        for i in range(min(len(geo_data), len(provinces))):
            provinces[i]['value'] = geo_data[i].get('engagement', 0) + random.randint(10, 100)

        provinces = sorted(provinces, key=lambda x: x['value'], reverse=True)

        # 6. 最近微博
        recent_weibos = all_data[:10]
        for item in recent_weibos:
            if item.get('keywords'):
                try:
                    item['keywords'] = json.loads(item['keywords'])
                except:
                    item['keywords'] = []

        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'total': total,
                    'avg_sentiment': round(avg_sentiment, 4),
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'total_reposts': total_reposts,
                },
                'sentiment': {
                    'distribution': sentiment_distribution,
                    'percentage': sentiment_percentage,
                },
                'hotwords': hot_words,
                'trend': trend_data,
                'geo': provinces,
                'recent': recent_weibos
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取仪表盘数据失败: {str(e)}'
        }), 500


@analytics_bp.route('/realtime', methods=['GET'])
def get_realtime_stats():
    """
    获取实时统计（模拟）

    GET /api/realtime
    """
    try:
        import random
        from datetime import datetime

        # 模拟实时数据变化
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        all_data = db.get_all_weibo(limit=10000)
        total = len(all_data)

        return jsonify({
            'success': True,
            'data': {
                'time': current_time,
                'total': total,
                'new_today': random.randint(0, 50),
                'active_users': random.randint(10, min(100, total)),
                'engagement_rate': round(random.uniform(2, 15), 2),
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取实时统计失败: {str(e)}'
        }), 500
