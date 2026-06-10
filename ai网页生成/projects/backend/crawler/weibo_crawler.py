# -*- coding: utf-8 -*-
"""
微博爬虫模块
使用 requests 爬取微博搜索结果
"""

import re
import json
import time
import random
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CRAWLER_CONFIG


class WeiboCrawler:
    """微博爬虫类"""

    def __init__(self):
        """初始化爬虫"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(CRAWLER_CONFIG['user_agents']),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://weibo.com/',
        })
        self.timeout = CRAWLER_CONFIG['timeout']
        self.max_pages = CRAWLER_CONFIG['max_pages']
        self.delay = CRAWLER_CONFIG['delay']

    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(CRAWLER_CONFIG['user_agents'])

    def _parse_timestamp(self, time_str: str) -> Optional[str]:
        """解析时间字符串"""
        if not time_str:
            return None

        now = datetime.now()

        # 匹配各种时间格式
        patterns = [
            (r'刚刚', lambda: now),
            (r'(\d+)秒前', lambda m: now.replace(second=now.second - int(m.group(1)))),
            (r'(\d+)分钟前', lambda m: now.replace(minute=now.minute - int(m.group(1)))),
            (r'(\d+)小时前', lambda m: now.replace(hour=now.hour - int(m.group(1)))),
            (r'今天(\d+):(\d+)', lambda m: now.replace(hour=int(m.group(1)), minute=int(m.group(2)))),
            (r'昨天(\d+):(\d+)', lambda m: (now.replace(hour=int(m.group(1)), minute=int(m.group(2)))
                                          .replace(day=now.day - 1))),
            (r'(\d+)-(\d+)', lambda m: datetime(now.year, int(m.group(1)), int(m.group(2)))),
            (r'(\d{4})-(\d{2})-(\d{2})', lambda m: datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
            # 标准格式: Tue Apr 18 10:30:00 +0800 2024
            (r'^\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} \+\d{4} \d{4}$',
             lambda m: datetime.strptime(time_str, '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d %H:%M:%S')),
        ]

        for pattern, handler in patterns:
            match = re.search(pattern, time_str)
            if match:
                try:
                    dt = handler(match)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    continue

        return now.strftime('%Y-%m-%d %H:%M:%S')

    def _clean_content(self, content: str) -> str:
        """清理微博内容"""
        if not content:
            return ''

        # 移除表情图片标签
        content = re.sub(r'\[.*?\]', '', content)
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content)
        # 移除特殊字符
        content = content.strip()

        return content

    def _parse_weibo_card(self, card: Dict) -> Optional[Dict]:
        """解析单条微博卡片"""
        try:
            # 获取微博内容
            mblog = card.get('mblog', {})
            if not mblog:
                return None

            # 获取文本内容
            text = mblog.get('text', '')
            if not text:
                # 尝试从原始HTML解析
                text = mblog.get('raw_text', '')

            # 清理HTML标签
            soup = BeautifulSoup(text, 'html.parser')
            text = soup.get_text()

            # 获取用户信息
            user = mblog.get('user', {})
            username = user.get('screen_name', '未知用户')
            user_id = str(user.get('id', ''))

            # 获取互动数据（顶层字段）
            like_count = mblog.get('attitudes_count', 0)
            comment_count = mblog.get('comments_count', 0)
            repost_count = mblog.get('reposts_count', 0)

            # 获取时间
            created_at = mblog.get('created_at', '')
            publish_time = self._parse_timestamp(created_at)

            # 获取微博ID
            weibo_id = str(mblog.get('id', ''))

            if not text or not weibo_id:
                return None

            return {
                'weibo_id': weibo_id,
                'content': self._clean_content(text),
                'username': username,
                'user_id': user_id,
                'publish_time': publish_time,
                'like_count': like_count,
                'comment_count': comment_count,
                'repost_count': repost_count,
            }

        except Exception as e:
            print(f"解析微博卡片失败: {e}")
            return None

    def crawl_by_keyword(self, keyword: str, pages: int = None) -> List[Dict]:
        """
        按关键词爬取微博

        Args:
            keyword: 搜索关键词
            pages: 爬取页数，默认使用配置值

        Returns:
            微博数据列表
        """
        if pages is None:
            pages = self.max_pages

        results = []
        encoded_keyword = quote(keyword)

        print(f"开始爬取关键词: {keyword}, 页数: {pages}")

        for page in range(1, pages + 1):
            try:
                # 微博移动端搜索API
                url = f'https://m.weibo.cn/api/container/getIndex'

                params = {
                    'type': 'all',
                    'queryVal': keyword,
                    'luicode': '10000011',
                    'lfid': '100103type=1&q=' + keyword,
                    'title': keyword,
                    'containerid': f'100103type=1&q={encoded_keyword}',
                    'page': page,
                    'page_type': 'searchall'
                }

                self.session.headers['User-Agent'] = self._get_random_user_agent()

                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    print(f"请求失败，状态码: {response.status_code}")
                    continue

                data = response.json()

                # 检查返回数据
                if data.get('ok') != 1:
                    print(f"API返回错误: {data.get('msg', '未知错误')}")
                    break

                cards = data.get('data', {}).get('cards', [])

                if not cards:
                    print(f"第{page}页没有数据")
                    break

                for card in cards:
                    # 处理微博卡片 (card_type=9) 和转发微博 (card_type=11)
                    card_type = card.get('card_type')
                    if card_type in (9, 11):
                        weibo_data = self._parse_weibo_card(card)
                        if weibo_data:
                            results.append(weibo_data)

                print(f"第{page}页完成，已获取 {len(results)} 条数据")

                # 请求间隔
                time.sleep(self.delay + random.uniform(0, 1))

            except requests.exceptions.Timeout:
                print(f"第{page}页请求超时")
                continue
            except requests.exceptions.RequestException as e:
                print(f"第{page}页请求异常: {e}")
                continue
            except json.JSONDecodeError:
                print(f"第{page}页JSON解析失败")
                continue
            except Exception as e:
                print(f"第{page}页处理异常: {e}")
                continue

        print(f"爬取完成，总计获取 {len(results)} 条数据")
        return results

    def crawl_hot_search(self, pages: int = 5) -> List[Dict]:
        """
        爬取微博热搜榜

        Args:
            pages: 爬取页数

        Returns:
            微博数据列表
        """
        results = []

        try:
            # 热搜榜API (正确containerid)
            url = 'https://m.weibo.cn/api/container/getIndex'
            params = {
                'containerid': '106003type=1',
                'page_type': 'search_square'
            }

            self.session.headers['User-Agent'] = self._get_random_user_agent()

            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                # 热搜数据在 data.cards[0].card_group 中
                cards = data.get('data', {}).get('cards', [])
                if cards and 'card_group' in cards[0]:
                    group_list = cards[0]['card_group']
                else:
                    # 降级: 尝试直接取 cards
                    group_list = cards

                for item in group_list:
                    word = item.get('word') or item.get('title_sub', '')
                    if word:
                        # 模拟微博数据
                        results.append({
                            'weibo_id': f'hot_{item.get("id", random.randint(10000, 99999))}',
                            'content': f'热搜话题: {word}',
                            'username': '微博热搜',
                            'user_id': 'hot_search',
                            'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'like_count': item.get('num', item.get('raw_hot', 0)),
                            'comment_count': 0,
                            'repost_count': item.get('num', item.get('raw_hot', 0)),
                        })

        except Exception as e:
            print(f"爬取热搜榜失败: {e}")

        return results


# 演示数据生成器（用于没有真实微博数据时）
class DemoDataGenerator:
    """演示数据生成器"""

    @staticmethod
    def generate_sample_data(keyword: str, count: int = 100) -> List[Dict]:
        """
        生成示例微博数据

        Args:
            keyword: 关键词
            count: 生成数量

        Returns:
            微博数据列表
        """
        import random
        from datetime import timedelta

        # 预定义的话题评论模板分情感倾向
        # 积极情感模板 (约40%)
        positive_templates = [
            f"我觉得{keyword}这个问题值得关注，大家怎么看？",
            f"今天看到关于{keyword}的新闻，感觉很有意思",
            f"我觉得{keyword}未来发展空间很大",
            f"最近{keyword}成为了热点，朋友圈都在讨论",
            f"希望{keyword}能够得到更多人的重视",
            f"支持{keyword}，加油！",
            f"{keyword}的技术突破令人振奋，未来可期！",
            f"强烈推荐大家关注{keyword}，很有价值的内容",
            f"终于等到{keyword}的好消息了，太棒了！",
            f"{keyword}真是太厉害了，颠覆了我的认知",
            f"关于{keyword}的进展，比预期的要好很多",
            f"体验了一下{keyword}相关产品，效果惊艳",
            f"{keyword}让生活变得更美好了，点赞！",
            f"国家大力支持{keyword}，前景广阔",
            f"{keyword}的解决方案非常实用，已经推荐给朋友了",
        ]
        # 中性情感模板 (约30%)
        neutral_templates = [
            f"关于{keyword}，我有一些看法，不知道对不对",
            f"有没有人也在关注{keyword}这个话题？",
            f"对于{keyword}，专家们怎么看呢？",
            f"作为一个普通人，我对{keyword}的感受是这样的",
            f"从不同角度看{keyword}，会有不同的发现",
            f"关于{keyword}，我想说...",
            f"客观来说，{keyword}还是有提升空间的",
            f"今天在群里聊到{keyword}，大家的观点不太一样",
            f"{keyword}这个话题最近热度挺高",
            f"查了一下{keyword}的相关资料，内容很丰富",
            f"来聊聊{keyword}，说说你的看法",
            f"{keyword}到底是不是风口？理性分析一下",
        ]
        # 消极情感模板 (约30%)
        negative_templates = [
            f"{keyword}这件事确实让人印象深刻",
            f"不得不承认，{keyword}做得不错",
            f"关于{keyword}，存在的问题也不容忽视",
            f"我对{keyword}的发展方向有些担忧",
            f"{keyword}目前的方案还有不少bug需要修复",
            f"说实话，{keyword}的实际效果和宣传差距不小",
            f"吐槽一下{keyword}，用户体验有待提升",
            f"{keyword}的问题越来越多，却没有得到足够重视",
            f"对{keyword}的未来持谨慎态度，还需要观察",
            f"{keyword}到底行不行？最近负面消息有点多",
            f"用了几天{keyword}，感觉还是不够成熟",
            f"朋友说{keyword}不太好用，我试了一下确实如此",
        ]

        # 按比例分配模板
        template_pool = []
        template_pool.extend(positive_templates)    # 15条积极
        template_pool.extend(neutral_templates)     # 12条中性
        template_pool.extend(negative_templates)    # 12条消极

        usernames = [
            '小明同学', '科技爱好者', '吃瓜群众', '热心网友',
            '数据分析师', '产品经理', '程序员老王', '财经达人',
            '娱乐八卦', '体育迷', '教育工作者', '医疗从业者',
            '法律顾问', '房产中介', '汽车达人', '旅游爱好者',
            '美食家', '音乐发烧友', '电影观众', '读书爱好者',
            '投资达人', '创业青年', '大学教授', '科研工作者',
            '市场总监', '运营主管', '设计狮', '前端开发'
        ]

        results = []
        base_time = datetime.now()

        for i in range(count):
            # 随机生成时间（过去14天内）
            days_ago = random.randint(0, 14)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            publish_time = base_time - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

            # 随机选择模板
            template = random.choice(template_pool)

            # 互动数据：采用幂律分布模拟真实社交数据
            # 大部分帖子互动少，少部分帖子互动多
            rank = random.random()
            if rank < 0.5:        # 50%: 低互动
                like_count = random.randint(0, 50)
            elif rank < 0.8:      # 30%: 中等互动
                like_count = random.randint(50, 500)
            elif rank < 0.95:     # 15%: 较高互动
                like_count = random.randint(500, 2000)
            else:                 # 5%: 高互动
                like_count = random.randint(2000, 10000)

            comment_count = random.randint(0, max(1, like_count // random.choice([8, 10, 15])))
            repost_count = random.randint(0, max(1, like_count // random.choice([15, 20, 30])))

            results.append({
                'weibo_id': f'demo_{keyword}_{i}_{random.randint(10000, 99999)}',
                'content': template,
                'username': random.choice(usernames),
                'user_id': f'user_{random.randint(1000000, 9999999)}',
                'publish_time': publish_time.strftime('%Y-%m-%d %H:%M:%S'),
                'like_count': like_count,
                'comment_count': comment_count,
                'repost_count': repost_count,
            })

        return results
