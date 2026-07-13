#API配置
#导入工具箱
import os
import time
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
    """发送问题给AI，返回回答(单轮对话)"""
    response =client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role":"user","content":question}
        ],
    )
    return response.choices[0].message.content

def ask_ai_with_history(messages,system_prompt=None,max_tokens=2048,max_retries=3):
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

    if len(full_messages)>30:
        full_messages=[full_messages[0]]+full_messages[-30:]
        print(f"截断历史，保留{len(full_messages)}条消息")

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=full_messages,
                temperature=0.7,
                max_tokens=max_tokens,
                timeout=60.0,  # 增加超时时间
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ 第 {attempt + 1} 次尝试失败: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                raise e    
#入口测试
if __name__=='__main__':
    print("=" * 50)
    print("🔍 测试 AI 连接...")
    print("=" * 50)

    
    
    
    try:
         question = "你好，请用一句话介绍自己。"
         print(f"你问：{question}")
         reply = ask_ai(question)
         print(f"AI答：{reply}")
         print("\n 连接成功！")
    except Exception as e:
         print(f"\n 连接失败：{e}")

    

