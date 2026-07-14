"""
数据库操作 - 极简版（只有错题，没有复杂的统计表）
"""
import sqlite3
import os

DB_PATH = "./data/study.db"

# 确保 data 目录存在
os.makedirs("./data", exist_ok=True)


def init_database():
    """初始化数据库（只运行一次）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS mistakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            my_answer TEXT,
            correct_answer TEXT,
            ai_feedback TEXT,
            knowledge_point TEXT,
            is_mastered INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ 数据库已创建！")


def add_mistake(question, my_answer="", correct_answer="", ai_feedback="", knowledge_point=""):
    """添加一道错题"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO mistakes (question, my_answer, correct_answer, ai_feedback, knowledge_point)
        VALUES (?, ?, ?, ?, ?)
    ''', (question, my_answer, correct_answer, ai_feedback, knowledge_point))
    mistake_id = c.lastrowid
    conn.commit()
    conn.close()
    print(f"✅ 错题已保存，编号: {mistake_id}")
    return mistake_id


def get_all_mistakes():
    """获取所有错题"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM mistakes ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_mistake_by_id(mistake_id):
    """根据ID获取单条错题"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM mistakes WHERE id = ?", (mistake_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_mistake(mistake_id, question=None, my_answer=None, correct_answer=None, 
                   ai_feedback=None, knowledge_point=None, is_mastered=None):
    """更新错题信息"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    updates = []
    params = []
    
    if question is not None:
        updates.append("question = ?")
        params.append(question)
    if my_answer is not None:
        updates.append("my_answer = ?")
        params.append(my_answer)
    if correct_answer is not None:
        updates.append("correct_answer = ?")
        params.append(correct_answer)
    if ai_feedback is not None:
        updates.append("ai_feedback = ?")
        params.append(ai_feedback)
    if knowledge_point is not None:
        updates.append("knowledge_point = ?")
        params.append(knowledge_point)
    if is_mastered is not None:
        updates.append("is_mastered = ?")
        params.append(1 if is_mastered else 0)
    
    if not updates:
        conn.close()
        return False
    
    params.append(mistake_id)
    sql = f"UPDATE mistakes SET {', '.join(updates)} WHERE id = ?"
    c.execute(sql, params)
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0


def mark_as_mastered(mistake_id):
    """标记错题为已掌握"""
    return update_mistake(mistake_id, is_mastered=True)


def delete_mistake(mistake_id):
    """删除错题"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM mistakes WHERE id = ?", (mistake_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0


def get_dashboard_stats():
    """获取统计信息"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM mistakes")
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM mistakes WHERE is_mastered = 1")
    mastered = c.fetchone()[0]
    
    # 获取所有知识点（用于统计）
    c.execute("SELECT knowledge_point, COUNT(*) as count FROM mistakes GROUP BY knowledge_point")
    knowledge_points = c.fetchall()
    
    conn.close()
    
    return {
        "total": total,
        "mastered": mastered,
        "not_mastered": total - mastered,
        "mastery_rate": f"{round(mastered/total*100, 1)}%" if total > 0 else "0%",
        "knowledge_points": [{"name": kp[0], "count": kp[1]} for kp in knowledge_points if kp[0]]
    }


# ========== 测试入口 ==========
if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    print("\n" + "=" * 50)
    print("🧪 测试数据库操作")
    print("=" * 50)
    
    # 添加测试数据
    print("\n📝 添加错题...")
    add_mistake(
        question="快速排序的平均时间复杂度是多少？",
        my_answer="O(n)",
        correct_answer="O(n log n)",
        ai_feedback="快速排序平均时间复杂度是 O(n log n)，你的回答不对哦。",
        knowledge_point="排序算法"
    )
    
    add_mistake(
        question="红黑树是什么？",
        my_answer="一种排序算法",
        correct_answer="红黑树是一种自平衡的二叉搜索树",
        ai_feedback="红黑树是数据结构，不是排序算法。",
        knowledge_point="数据结构"
    )
    
    add_mistake(
        question="Python 中 append() 和 extend() 的区别？",
        my_answer="append 和 extend 都是添加元素",
        correct_answer="append 添加单个元素，extend 添加列表中的多个元素",
        ai_feedback="你没有说出核心区别。",
        knowledge_point="Python基础"
    )
    
    # 查询所有错题
    print("\n📋 所有错题:")
    mistakes = get_all_mistakes()
    for m in mistakes:
        print(f"  [{m['id']}] {m['question'][:30]}... | 知识点: {m['knowledge_point']}")
    
    # 统计数据
    print("\n📊 统计:")
    stats = get_dashboard_stats()
    print(f"  总错题: {stats['total']}")
    print(f"  已掌握: {stats['mastered']}")
    print(f"  掌握率: {stats['mastery_rate']}")
    
    print("\n📚 各知识点错题数:")
    for kp in stats['knowledge_points']:
        print(f"  {kp['name']}: {kp['count']} 道")
    
    print("\n✅ 测试完成！")