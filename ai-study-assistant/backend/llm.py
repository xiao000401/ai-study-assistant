#API配置
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
    """发送问题给AI，返回回答"""
    response =client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role":"user","content":question}
        ],
    )
    return response.choices[0].message.content

def ask_ai_with_history(messages,system_prompt=None):
    """
    支持多轮对话的AI调用
    messages:完整的对话历史列表
    system_prompt:系统提示词，用于设定"""
    if system_prompt:
        full_messages=[
            {"role":"system","content":system_prompt}
        ]+messages
    else:
        full_messages=messages


    response=client.chat.completions.create(
        model="glm-4-flash",
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
    )
    return response.choices[0].message.content
#入口测试
if __name__=='__main__':
    question="你好，请用一句话介绍自己。"
    print(f"你问：{question}")
    print(f"AI答:{ask_ai(question)}")

#测试多轮
print("\n---测试多轮对话---")
messages=[
    {"role":"user","content":"我叫小明"},
    {"role": "assistant", "content": "你好小明！很高兴认识你。"},
    {"role": "user", "content": "我叫什么名字？"},
]
reply=ask_ai_with_history(messages)
print(f"AI答：{reply}")
    
