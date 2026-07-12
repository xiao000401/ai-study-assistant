#导入工具箱
import os
from zhipuai import ZhipuAI
from dotenv import load_dotenv
#加载配置
load_dotenv()

API_KEY=os.getenv("ZHIPU_API_KEY")
#防御性检测
if not API_KEY:
    raise ValueError("请在.env文件中配置ZHIPU_API_KEY")
#创建客户端
client=ZhipuAI(api_key=API_KEY)
#定义核心函数
def ask_ai(question):
    """发送问题给AI,返回回答"""
    response =client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role":"user","content":question}
        ],  
    )
    return response.choices[0].message.content
#入口测试
if __name__=='__main__':
    question="你好，请用一句话介绍自己。"
    print(f"你问：{question}")
    print(f"AI答:{ask_ai(question)}")