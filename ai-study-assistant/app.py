"""
AI学习助手-gradio聊天界面+错题本
"""
#导入工具箱
import gradio as gr
from backend.llm import ask_ai_with_history
from backend.database import (
    add_mistake, 
    get_all_mistakes, 
    mark_as_mastered, 
    delete_mistake,
    get_dashboard_stats,
    get_mistake_by_id
)



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

def add_mistake_from_ui(question, my_answer, correct_answer, knowledge_point):
    """添加错题（带AI评讲）"""
    if not question or not question.strip():
        return " 题目不能为空！", "", "", "", "", get_mistake_table()
    
    # 调用 AI 评讲
    try:
        prompt = f"""你是一位耐心的老师。学生做了一道题，请用鼓励的语气给出反馈：
1. 判断对错
2. 如果错，指出错误原因
3. 给出正确答案
4. 总结这道题考察的知识点

题目：{question}
学生的答案：{my_answer if my_answer else "（未作答）"}
正确答案：{correct_answer if correct_answer else "（未提供）"}
"""
        ai_feedback = ask_ai_with_history(
            [{"role": "user", "content": prompt}],
            system_prompt="你是一位耐心的老师，用鼓励的语气给学生讲评。"
        )
    except Exception as e:
        ai_feedback = f"AI 评讲失败：{str(e)}"
    
    # 保存到数据库
    mistake_id = add_mistake(
        question=question,
        my_answer=my_answer,
        correct_answer=correct_answer,
        ai_feedback=ai_feedback,
        knowledge_point=knowledge_point
    )
    
    return (
        f" 错题已保存！编号: {mistake_id}\n AI 评讲：\n{ai_feedback}",
        "",  # 清空题目
        "",  # 清空我的答案
        "",  # 清空正确答案
        "",  # 清空知识点
        get_mistake_table()  # 刷新表格
    )


def get_mistake_table():
    """获取错题列表（表格数据）"""
    mistakes = get_all_mistakes()
    if not mistakes:
        return [["暂无错题，快去录入吧！", "", "", "", ""]]
    
    table_data = []
    for m in mistakes:
        status = "已掌握" if m['is_mastered'] else "学习中"
        table_data.append([
            m['id'],
            m['question'][:40] + ("..." if len(m['question']) > 40 else ""),
            m['knowledge_point'] or "未分类",
            status,
            m['created_at'][:10] if m['created_at'] else ""
        ])
    return table_data


def view_mistake_detail(mistake_id):
    """查看错题详情"""
    if not mistake_id:
        return "请输入错题编号"
    try:
        m = get_mistake_by_id(int(mistake_id))
        if not m:
            return "未找到该错题"
        
        return f"""
**题目**：{m['question']}

**我的答案**：{m['my_answer'] or "（未填写）"}

**正确答案**：{m['correct_answer'] or "（未填写）"}

**AI 评讲**：{m['ai_feedback'] or "（暂无评讲）"}

**知识点**：{m['knowledge_point'] or "未分类"}

**状态**：{"已掌握" if m['is_mastered'] else "学习中"}

**录入时间**：{m['created_at']}
"""
    except Exception as e:
        return f"出错：{str(e)}"


def mark_mastered_from_ui(mistake_id):
    """标记为已掌握"""
    if not mistake_id:
        return "请输入错题编号", get_mistake_table()
    try:
        success = mark_as_mastered(int(mistake_id))
        if success:
            return f"错题 {mistake_id} 已删除！", get_mistake_table()
        else:
            return f"未找到编号为 {mistake_id} 的错题", get_mistake_table()
    except Exception as e:
        return f"操作失败：{str(e)}", get_mistake_table()


def delete_mistake_from_ui(mistake_id):
    """删除错题"""
    if not mistake_id:
        return "❌ 请输入错题编号", get_mistake_table()
    try:
        success = delete_mistake(int(mistake_id))
        if success:
            return f"错题 {mistake_id} 已删除！", get_mistake_table()
        else:
            return f"未找到编号为 {mistake_id} 的错题", get_mistake_table()
    except Exception as e:
        return f"操作失败：{str(e)}", get_mistake_table()


def refresh_table():
    """刷新表格"""
    return get_mistake_table()


    
# 创建聊天界面
with gr.Blocks(title="AI 学习助手 - 思伴") as demo:
    gr.Markdown("# AI 学习助手 - 思伴")
    gr.Markdown("你的私人 AI 助教，陪你聊天、刷题、记错题！")
    
    with gr.Tabs():
        # ===== Tab 1: 聊天 =====
        with gr.TabItem("聊天"):
            gr.ChatInterface(
                fn=chat,
                title=None,
                description="我是你的私人AI助教，可以陪你聊天、解答问题、讲解知识点。",
                examples=[
                    "你能帮我讲解一下什么是递归吗？",
                    "我想学 Python，从哪里开始？",
                    "解释一下什么是大语言模型（LLM）"
                ],
                cache_examples=False,
            )
        
        # ===== Tab 2: 错题本 =====
        with gr.TabItem("错题本"):
            gr.Markdown("### 录入错题")
            
            # 录入区域
            with gr.Row():
                with gr.Column(scale=2):
                    question_input = gr.Textbox(
                        label=" 题目",
                        placeholder="输入题目内容...",
                        lines=3
                    )
                    with gr.Row():
                        my_answer_input = gr.Textbox(
                            label="我的答案 ",
                            placeholder="输入你的答案...",
                            lines=2,
                            scale=1
                        )
                        correct_answer_input = gr.Textbox(
                            label="正确答案",
                            placeholder="输入正确答案...",
                            lines=2,
                            scale=1
                        )
                    knowledge_input = gr.Textbox(
                        label=" 知识点",
                        placeholder="例如：排序算法、数据结构、Python基础...",
                    )
                    submit_btn = gr.Button("保存错题", variant="primary")
                
                with gr.Column(scale=1):
                    add_result = gr.Textbox(
                        label="保存结果",
                        lines=10,
                        interactive=False
                    )
            
            gr.Markdown("---")
            gr.Markdown("### 我的错题列表")
            
            # 错题列表
            mistake_table = gr.Dataframe(
                headers=["编号", "题目", "知识点", "状态", "日期"],
                value=get_mistake_table(),
                interactive=False,
                wrap=True,
            )
            
            # 操作区
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("**查看详情**")
                    view_id_input = gr.Number(label="输入编号", precision=0)
                    view_btn = gr.Button("查看详情", variant="secondary")
                    view_result = gr.Markdown("")
                
                with gr.Column(scale=1):
                    gr.Markdown("** 标记已掌握**")
                    master_id_input = gr.Number(label="输入编号", precision=0)
                    master_btn = gr.Button("标记已掌握", variant="primary")
                    master_result = gr.Textbox(label="操作结果", interactive=False)
                
                with gr.Column(scale=1):
                    gr.Markdown("**删除错题**")
                    delete_id_input = gr.Number(label="输入编号", precision=0)
                    delete_btn = gr.Button("删除", variant="stop")
                    delete_result = gr.Textbox(label="操作结果", interactive=False)
            
            # 刷新按钮
            with gr.Row():
                refresh_btn = gr.Button("刷新列表", variant="secondary")
            
            # ---------- 绑定事件 ----------
            submit_btn.click(
                add_mistake_from_ui,
                inputs=[question_input, my_answer_input, correct_answer_input, knowledge_input],
                outputs=[add_result, question_input, my_answer_input, correct_answer_input, knowledge_input, mistake_table]
            )
            
            view_btn.click(
                view_mistake_detail,
                inputs=[view_id_input],
                outputs=[view_result]
            )
            
            master_btn.click(
                mark_mastered_from_ui,
                inputs=[master_id_input],
                outputs=[master_result, mistake_table]
            )
            
            delete_btn.click(
                delete_mistake_from_ui,
                inputs=[delete_id_input],
                outputs=[delete_result, mistake_table]
            )
            
            refresh_btn.click(
                refresh_table,
                inputs=[],
                outputs=[mistake_table]
            )
        
        # ===== Tab 3: 学习看板 =====
        with gr.TabItem("学习看板"):
            gr.Markdown("### 学习数据统计")
            
            # 获取统计数据
            stats = get_dashboard_stats()
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown(f"""
                    ###  概览
                    -  总错题：**{stats['total']}** 道
                    -  已掌握：**{stats['mastered']}** 道
                    -  学习中：**{stats['not_mastered']}** 道
                    -  掌握率：**{stats['mastery_rate']}**
                    """)
            
            if stats['knowledge_points']:
                gr.Markdown("###  各知识点错题分布")
                kp_text = ""
                for kp in stats['knowledge_points']:
                    bar = "" * min(kp['count'], 20)
                    kp_text += f"- {kp['name']}：{kp['count']} 道 {bar}\n"
                gr.Markdown(kp_text)
            else:
                gr.Markdown(" 暂无错题数据，快去录入吧！")
            
            gr.Markdown("---")
            gr.Markdown(" *更多统计功能（趋势图、学习日历等）将在 v1.1 更新*")
# 启动服务
if __name__ == "__main__":
    demo.launch(share=True)  # share=True 生成公网链接，方便展示

