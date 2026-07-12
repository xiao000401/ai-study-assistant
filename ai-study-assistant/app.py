"""
AI学习助手-gradio聊天界面
"""
#导入工具箱
import gradio as gr
from backend.llm import ask_ai
#定义聊天处理函数
def chat(messages,history):
    """
    处理用户消息并返回AI回复
    messages:用户当前输入的消息（字符串）
    history:历史对话记录(列表,gradio自动维护)
    """
    reply=ask_ai(messages)

    return reply

#创建聊天界面（UI）
demo=gr.ChatInterface(
    fn=chat,
    title="AI学习助手",
    description="我是你的私人AI助教,可以陪你聊天、解答问题。",
)
#启动服务
if __name__=="__main__":
    demo.launch(share=True)