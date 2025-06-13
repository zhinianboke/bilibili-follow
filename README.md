# B站自动涨粉工具

这是一个帮助你自动涨粉的B站工具。
原理：找到B站所有会互关或者互粉的UP主，先关注他们，然后等待他们回关

## 功能特点

- 网页界面操作，使用简单
- 支持批量关注UP主
- 实时显示关注进度
- 自动处理关注间隔，避免触发风控
- 详细的操作日志
- 支持随时暂停任务
- 支持Docker部署

## 使用说明

### 方法一：直接运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python app.py
```

### 方法二：使用Docker（推荐）

1. 使用 docker-compose 运行（推荐）：
```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

2. 或者使用 Docker 直接运行：
```bash
# 构建镜像
docker build -t bilibili-follow .

# 运行容器
docker run -d -p 5000:5000 \
  -v ${PWD}/logs:/app/logs \
  --name bilibili-follow \
  bilibili-follow
```

3. 打开浏览器访问：`http://localhost:5000`

## 准备工作

1. 确保目录中有以`merged_unique`开头的txt文件，包含要关注的UP主URL
2. 获取你的B站Cookie（需要登录状态）

## 使用步骤

1. 将B站Cookie粘贴到文本框
2. 点击"开始关注"按钮
3. 等待程序自动执行
4. 可以随时点击"停止任务"按钮暂停

## 注意事项

- Cookie中必须包含登录信息，否则无法进行关注操作
- 程序会自动处理关注间隔，每次关注之间会有8-20秒的随机延迟
- 每关注10个用户后会自动休息60-120秒，进一步避免触发风控
- 建议不要一次性关注太多UP主，以免触发B站的风控机制
- 如果遇到频繁失败，建议暂停一段时间后再继续

## 文件说明

- `app.py`: Web应用主程序
- `merged_unique_urls*.txt`: 所有会互粉的up主
- `follow_authors.py`: 关注功能核心代码
- `templates/index.html`: 网页前端界面
- `requirements.txt`: 项目依赖
- `Dockerfile`: Docker镜像构建文件
- `docker-compose.yml`: Docker容器编排配置
