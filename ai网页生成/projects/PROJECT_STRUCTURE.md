# 大数据舆情可视化分析系统 - 项目结构

```
weibo-sentiment-analysis/
├── README.md                     # 项目说明文档
├── LICENSE                       # 开源协议
├── docs/                         # 项目文档
│   ├── PROJECT_STRUCTURE.md      # 项目结构详解
│   ├── API_DOCUMENTATION.md     # API接口文档
│   └── DATABASE_SCHEMA.md       # 数据库设计文档
│
├── backend/                     # 后端目录
│   ├── requirements.txt          # Python依赖
│   ├── run.py                    # 后端启动入口
│   ├── config.py                 # 配置文件
│   │
│   ├── app.py                    # Flask应用主文件
│   │
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   └── database.py           # 数据库初始化和操作
│   │
│   ├── crawler/                  # 爬虫模块
│   │   ├── __init__.py
│   │   ├── weibo_crawler.py     # 微博爬虫核心
│   │   └── data_cleaner.py      # 数据清洗模块
│   │
│   ├── ml/                       # 机器学习模块
│   │   ├── __init__.py
│   │   ├── sentiment_analyzer.py # 情感分析模块
│   │   ├── topic_modeler.py      # 主题建模模块
│   │   └── text_processor.py     # 文本处理工具
│   │
│   └── routes/                   # API路由
│       ├── __init__.py
│       ├── crawl.py              # 爬虫相关接口
│       ├── data.py               # 数据接口
│       └── analytics.py          # 分析接口
│
├── frontend/                     # 前端目录
│   ├── package.json              # npm依赖
│   ├── vite.config.js            # Vite配置
│   ├── index.html                # HTML入口
│   ├── README.md                 # 前端说明
│   │
│   ├── public/                   # 静态资源
│   │   └── favicon.ico
│   │
│   └── src/                      # 源代码
│       ├── main.js               # Vue入口
│       ├── App.vue               # 根组件
│       ├── api/                  # API调用
│       │   └── index.js          # API封装
│       │
│       ├── views/                # 页面
│       │   ├── Dashboard.vue     # 数据大屏主页
│       │   └── CrawlControl.vue  # 爬虫控制页
│       │
│       └── components/           # 组件
│           ├── WordCloud.vue     # 词云组件
│           ├── SentimentPie.vue  # 情感饼图
│           ├── TrendLine.vue     # 趋势折线图
│           ├── HotWordsBar.vue    # 热词柱状图
│           ├── GeoMap.vue        # 地理分布图
│           └── DataStats.vue      # 数据统计卡片
│
└── data/                         # 数据目录
    └── weibo.db                  # SQLite数据库文件（运行时生成）
```

## 技术栈

### 后端
- Python 3.8+
- Flask 2.x - Web框架
- SQLite - 数据库
- requests - HTTP请求
- jieba - 中文分词
- snownlp - 情感分析
- wordcloud - 词云生成

### 前端
- Vue 3 - 框架
- Vite - 构建工具
- ECharts 5 - 可视化图表
- echarts-wordcloud - 词云插件
- axios - HTTP客户端

## 功能模块

### 1. 爬虫模块 (crawler/)
实现微博数据爬取，支持：
- 按关键词搜索微博
- 爬取微博正文、发布时间、点赞/评论/转发数
- 用户信息提取
- 自动翻页
- 请求频率控制

### 2. 机器学习模块 (ml/)
实现数据分析处理：
- 中文分词（jieba）
- 情感分析（SnowNLP）
- 关键词提取
- TF-IDF统计
- LDA主题建模（可选）

### 3. 数据模型 (models/)
数据库设计与操作：
- SQLite数据库初始化
- CRUD操作封装
- 数据去重逻辑

### 4. API接口 (routes/)
RESTful API接口：
- `/api/crawl` - 触发爬虫
- `/api/data` - 获取原始数据
- `/api/sentiment` - 情感统计
- `/api/wordcloud` - 词云数据
- `/api/trend` - 时间趋势
- `/api/hotwords` - 热词统计
- `/api/geo` - 地理分布

### 5. 前端可视化 (frontend/src/)
Vue3组件实现数据可视化：
- 数据大屏首页
- 词云图（echarts-wordcloud）
- 情感分布饼图
- 舆情热度折线图
- 热词柱状图
- 地理分布地图
- 数据统计卡片

## 数据库设计

### weibo_data 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| weibo_id | TEXT | 微博唯一ID |
| content | TEXT | 微博内容 |
| username | TEXT | 用户名 |
| user_id | TEXT | 用户ID |
| publish_time | DATETIME | 发布时间 |
| like_count | INTEGER | 点赞数 |
| comment_count | INTEGER | 评论数 |
| repost_count | INTEGER | 转发数 |
| sentiment_score | REAL | 情感分数 |
| sentiment_label | TEXT | 情感标签 |
| keywords | TEXT | 关键词(JSON) |
| created_at | DATETIME | 入库时间 |

## 快速开始

详见 README.md
