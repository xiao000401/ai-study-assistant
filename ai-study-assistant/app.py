"""
AI学习助手-gradio聊天界面
"""
#导入工具箱
import gradio as gr
from backend.llm import ask_ai_with_history

SYSTEM_PROMPT="""
AI学习助手 - Gradio 聊天界面
"""
import gradio as gr
from backend.llm import ask_ai_with_history

# 系统提示词：定义 AI 的角色和行为
SYSTEM_PROMPT = """你是一位耐心、专业的学习助手，名叫"思伴"（StudyPal）。
你的核心原则：
1. 用通俗易懂的语言讲解知识点，像老师给学生讲题一样
2. 如果问题超出你的知识范围，坦诚说"不知道"，不要编造
3. 鼓励学生思考，适当提问引导
4. 回答要结构清晰，可以用列表或分段
5. 涉及数学或代码时，注意格式规范
"""


def chat(message, history):
    """
    处理用户消息并返回AI回复
    
    参数:
        message: 用户当前输入的消息（字符串）
        history: 历史对话记录（列表，Gradio自动维护）
                格式: [[user_msg, ai_msg], [user_msg, ai_msg], ...]
    
    返回:
        AI 的回复内容（字符串）
    """
    print(f"当前对话轮数：{len(history)}")
    
    messages = []
    
    for item in history:
        # 直接用索引，更安全
        if isinstance(item, dict):
            role = item.get('role', '')
            content = item.get('content', [])
            
            # 提取文本内容
            text_content = ""
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and 'text' in c:
                        text_content += c['text']
                    elif isinstance(c, str):
                        text_content += c
            elif isinstance(content, str):
                text_content = content
            
            if role == 'user' and text_content:
                messages.append({"role": "user", "content": text_content})
            elif role == 'assistant' and text_content:
                messages.append({"role": "assistant", "content": text_content})

        
        elif isinstance(item,(list,tuple)) and len(item)>=2:
            user_msg = item[0] if item[0] else""
            ai_msg = item[1] if item[1] else""
            if user_msg :    
                messages.append({"role": "user", "content": user_msg})
            if ai_msg :
                messages.append({"role": "assistant", "content": ai_msg})
        else:
            print(f"跳过未知格式：{item}")
            continue
    
    if message and message.strip():
        messages.append({"role": "user", "content": message})
    print(f"发送给AI的消息数：{len(message)}")


    # 4. 调用 AI（传入系统提示词）
    try:
        reply = ask_ai_with_history(messages, system_prompt=SYSTEM_PROMPT)
        print (f"AI 回复成功，长度: {len(reply)} 字符")
        return reply
    except Exception as e:
        print(f"AI 调用失败: {e}")
        return f"出错了：{str(e)}"


# 创建聊天界面
demo = gr.ChatInterface(
    fn=chat,
    title="📚 AI 学习助手 - 思伴",
    description="我是你的私人AI助教，可以陪你聊天、解答问题、讲解知识点。",
    examples=[  # 推荐问题，方便测试
        "你能帮我讲解一下什么是递归吗？",
        "我想学 Python，从哪里开始？",
        "解释一下什么是大语言模型（LLM）"
    ],
    cache_examples=False,  # 示例不缓存，避免浪费 API
)

# 启动服务
if __name__ == "__main__":
    demo.launch(share=True)  # share=True 生成公网链接，方便展示

