# -*- coding: utf-8 -*-
"""
数据相关API路由
提供数据查询功能
"""

from flask import Blueprint, request, jsonify

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db

# 创建蓝图
data_bp = Blueprint('data', __name__, url_prefix='/api/data')


@data_bp.route('/list', methods=['GET'])
def get_data_list():
    """
    获取数据列表

    GET /api/data/list?limit=100&offset=0
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        # 限制范围
        limit = min(limit, 1000)
        offset = max(offset, 0)

        # 获取数据
        data = db.get_all_weibo(limit=limit, offset=offset)
        total = db.get_weibo_count()

        # 处理keywords字段（JSON字符串转对象）
        import json
        for item in data:
            if item.get('keywords'):
                try:
                    item['keywords'] = json.loads(item['keywords'])
                except:
                    item['keywords'] = []

        return jsonify({
            'success': True,
            'data': data,
            'total': total,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        }), 500


@data_bp.route('/stats', methods=['GET'])
def get_data_stats():
    """
    获取数据统计

    GET /api/data/stats
    """
    try:
        total = db.get_weibo_count()

        # 情感分布
        sentiment_stats = db.get_sentiment_stats()

        # 计算总计
        total_engagement = 0
        total_likes = 0
        total_comments = 0
        total_reposts = 0

        all_data = db.get_all_weibo(limit=10000)
        for item in all_data:
            total_likes += item.get('like_count', 0)
            total_comments += item.get('comment_count', 0)
            total_reposts += item.get('repost_count', 0)

        total_engagement = total_likes + total_comments + total_reposts

        return jsonify({
            'success': True,
            'stats': {
                'total_weibos': total,
                'sentiment_distribution': sentiment_stats,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_reposts': total_reposts,
                'total_engagement': total_engagement
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计失败: {str(e)}'
        }), 500


@data_bp.route('/detail/<weibo_id>', methods=['GET'])
def get_data_detail(weibo_id):
    """
    获取单条数据详情

    GET /api/data/detail/<weibo_id>
    """
    try:
        # 这里简化为返回列表中匹配的数据
        all_data = db.get_all_weibo(limit=10000)

        for item in all_data:
            if item.get('weibo_id') == weibo_id:
                import json
                if item.get('keywords'):
                    try:
                        item['keywords'] = json.loads(item['keywords'])
                    except:
                        item['keywords'] = []

                return jsonify({
                    'success': True,
                    'data': item
                })

        return jsonify({
            'success': False,
            'message': '数据不存在'
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取详情失败: {str(e)}'
        }), 500


@data_bp.route('/clear', methods=['POST'])
def clear_data():
    """
    清空所有数据

    POST /api/data/clear
    """
    try:
        db.delete_all()

        return jsonify({
            'success': True,
            'message': '数据已清空'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'清空数据失败: {str(e)}'
        }), 500


@data_bp.route('/recent', methods=['GET'])
def get_recent_data():
    """
    获取最近数据

    GET /api/data/recent?days=7&limit=20
    """
    try:
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 20, type=int)

        # 获取趋势数据
        trend_data = db.get_trend_data(days=days)

        # 获取最近的数据
        all_data = db.get_all_weibo(limit=limit)

        import json
        recent_items = []
        for item in all_data[:limit]:
            if item.get('keywords'):
                try:
                    item['keywords'] = json.loads(item['keywords'])
                except:
                    item['keywords'] = []
            recent_items.append(item)

        return jsonify({
            'success': True,
            'trend': trend_data,
            'recent': recent_items
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取最近数据失败: {str(e)}'
        }), 500
