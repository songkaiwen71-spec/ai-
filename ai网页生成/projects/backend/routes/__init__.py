# -*- coding: utf-8 -*-
"""
API路由模块初始化
"""

from .crawl import crawl_bp
from .data import data_bp
from .analytics import analytics_bp

__all__ = [
    'crawl_bp',
    'data_bp',
    'analytics_bp',
]
