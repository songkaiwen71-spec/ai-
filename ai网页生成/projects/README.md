# 大数据舆情可视化分析系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Vue](https://img.shields.io/badge/Vue-3.4-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**基于微博数据源的舆情分析与可视化系统**

</div>

## 项目简介

这是一个完整的大数据舆情可视化分析系统，实现了：

- 📊 **数据爬取**：从微博平台爬取指定话题的博文数据
- 🤖 **机器学习**：使用 SnowNLP 进行中文情感分析
- 📈 **可视化大屏**：Vue3 + ECharts 实现多种数据可视化图表
- 🔧 **后端服务**：Python Flask 提供 RESTful API

## 功能特性

### 核心功能
- 🔍 微博数据爬取（支持关键词搜索）
- 😊 情感分析（积极/中性/消极）
- 📊 词云图展示关键词
- 📈 舆情热度趋势分析
- 🔥 热词统计柱状图
- 🗺️ 用户地域分布地图
- 📝 最新微博列表

### 技术栈
| 模块 | 技术 |
|------|------|
| 后端 | Python 3.8+, Flask 2.x |
| 前端 | Vue 3, Vite, ECharts 5 |
| 数据库 | SQLite |
| 爬虫 | requests, BeautifulSoup |
| NLP | jieba, SnowNLP |

## 项目结构

```
weibo-sentiment-analysis/
├── backend/                    # 后端目录
│   ├── app.py                  # Flask应用
│   ├── run.py                  # 启动入口
│   ├── config.py               # 配置文件
│   ├── requirements.txt         # Python依赖
│   ├── crawler/                 # 爬虫模块
│   ├── ml/                      # 机器学习模块
│   ├── models/                  # 数据模型
│   └── routes/                  # API路由
├── frontend/                   # 前端目录
│   ├── package.json             # npm依赖
│   ├── vite.config.js           # Vite配置
│   ├── src/
│   │   ├── api/                 # API调用
│   │   ├── components/           # 可视化组件
│   │   ├── views/                # 页面
│   │   └── assets/               # 样式
│   └── public/                  # 静态资源
├── data/                       # 数据目录
└── docs/                       # 文档目录
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 pnpm

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/weibo-sentiment-analysis.git
cd weibo-sentiment-analysis
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
# 或使用 pnpm
pnpm install
```

### 4. 启动后端服务

```bash
cd backend
python run.py
```

后端服务将运行在 http://localhost:5000

### 5. 启动前端服务（开发模式）

```bash
cd frontend
npm run dev
```

前端服务将运行在 http://localhost:5000

### 6. 使用演示数据

如果不方便爬取真实微博数据，可以在爬虫控制页面点击「生成演示数据」按钮，系统将自动生成模拟数据进行演示。

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/crawl/start` | POST | 开始爬取 |
| `/api/crawl/demo` | POST | 生成演示数据 |
| `/api/data/list` | GET | 获取数据列表 |
| `/api/dashboard` | GET | 获取仪表盘数据 |
| `/api/sentiment` | GET | 情感统计 |
| `/api/wordcloud` | GET | 词云数据 |
| `/api/trend` | GET | 趋势数据 |
| `/api/hotwords` | GET | 热词统计 |
| `/api/geo` | GET | 地理分布 |

## 功能截图

### 数据大屏
- 顶部统计卡片（数据总量、今日新增、互动数据）
- 词云图（关键词可视化）
- 情感分布饼图
- 舆情热度趋势折线图
- 热词统计柱状图
- 地理分布地图
- 最新微博列表

### 爬虫控制
- 关键词设置
- 爬取页数配置
- 实时日志输出
- 数据统计展示
- 历史记录查询

## 开发说明

### 分工建议

**后端开发（一人）**
- 爬虫模块开发
- 机器学习模块开发
- API接口开发
- 数据库设计

**前端开发（一人）**
- Vue组件开发
- ECharts可视化
- 页面布局设计
- 用户交互体验

### 扩展建议

1. **增加更多数据源**：可扩展支持抖音、知乎等平台
2. **增强机器学习**：添加LDA主题建模、实体识别等
3. **实时监控**：添加WebSocket支持实时数据推送
4. **用户系统**：添加登录注册功能
5. **数据导出**：支持导出Excel、PDF报告

## 注意事项

1. **爬虫合规**：请遵守目标网站的robots.txt和使用条款
2. **数据安全**：不要将敏感信息硬编码在代码中
3. **请求频率**：合理设置爬虫间隔，避免对服务器造成压力
4. **演示模式**：如遇爬虫失败，可使用演示数据功能

## 常见问题

### Q: 爬虫失败怎么办？
A: 微博有反爬机制，可以尝试：
1. 使用演示数据模式
2. 降低请求频率
3. 添加代理IP

### Q: 情感分析准确吗？
A: SnowNLP是基于机器学习的情感分析库，对中文文本的准确率约为70-80%，可作为教学演示使用。

### Q: 如何部署到服务器？
A: 
1. 前端执行 `npm run build` 构建静态文件
2. 后端使用 gunicorn 或 uwsgi 部署
3. 配置 Nginx 反向代理

## 开源协议

本项目采用 MIT 开源协议，欢迎贡献代码和提出问题！

## 致谢

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [ECharts](https://echarts.apache.org/) - 数据可视化图表库
- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架
- [jieba](https://github.com/fxsjy/jieba) - 中文分词库
- [SnowNLP](https://github.com/isnowfy/snownlp) - 中文情感分析库

---

<div align="center">

**如果这个项目对你有帮助，请给个 Star ⭐**

</div>
