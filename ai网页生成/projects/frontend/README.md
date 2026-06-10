# 前端说明

## 技术栈

- Vue 3 - 渐进式JavaScript框架
- Vite - 新一代前端构建工具
- ECharts 5 - 数据可视化图表库
- axios - HTTP客户端

## 开发命令

```bash
# 安装依赖
npm install

# 开发模式启动
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 目录结构

```
src/
├── api/                # API接口封装
├── assets/             # 静态资源
│   └── main.css        # 全局样式
├── components/         # Vue组件
│   ├── DataStats.vue   # 数据统计卡片
│   ├── WordCloud.vue   # 词云组件
│   ├── SentimentPie.vue # 情感饼图
│   ├── TrendLine.vue   # 趋势折线图
│   ├── HotWordsBar.vue # 热词柱状图
│   └── GeoMap.vue      # 地理分布图
├── router/             # 路由配置
├── views/              # 页面
│   ├── Dashboard.vue   # 数据大屏
│   └── CrawlControl.vue # 爬虫控制
├── App.vue             # 根组件
└── main.js             # 入口文件
```

## 组件说明

### DataStats.vue
数据统计卡片组件，用于展示关键指标。

### WordCloud.vue
词云组件，使用 echarts-wordcloud 插件实现。

### SentimentPie.vue
情感分布饼图，展示积极、中性、消极的比例。

### TrendLine.vue
舆情热度趋势折线图，展示随时间变化的趋势。

### HotWordsBar.vue
热词统计横向柱状图，展示高频关键词。

### GeoMap.vue
中国地图组件，展示用户地域分布。

## 样式规范

全局样式使用 CSS 变量实现主题一致性：

```css
:root {
  --primary-color: #4fc3f7;
  --bg-dark: #0a0e27;
  --bg-card: rgba(25, 35, 75, 0.8);
}
```
