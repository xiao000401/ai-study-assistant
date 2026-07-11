# AI 学习助手 (StudyPal)

> 一个能陪你刷题、讲解知识点、查笔记、记录错题的私人 AI 助教

## 技术栈
- Python 3.10+
- Gradio（聊天界面）
- ChromaDB（向量数据库）
- 智谱 GLM-4（大语言模型）

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 运行
python app.py