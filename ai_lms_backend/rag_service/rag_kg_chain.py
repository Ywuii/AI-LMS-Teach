from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_ollama import OllamaLLM
from typing import Any, Dict, List
from chat.chat_history import DjangoChatMessageHistory
from .triple_extractor_spacy import TripleExtractorSpacy
import asyncio

_session_configs = {}
_summary_llm = None
def get_summary_llm() -> OllamaLLM:
    global _summary_llm
    if _summary_llm is None:
        _summary_llm = OllamaLLM(
            model="clidx/Qwen3-1.7B-Q8_0:think",
            temperature=0.3,
            streaming=False
        )
    return _summary_llm

def build_rag_kg_chain(callbacks: List[BaseCallbackHandler] = None):
    """构建融合RAG和KG(知识图谱)的问答链"""

    # 初始化支持流式的LLM
    llm = OllamaLLM(
        model="clidx/Qwen3-1.7B-Q8_0:think",
        streaming=True,  # 启用流式
        callbacks=callbacks or []  # 传递回调
    )

    # 定义prompt模板
    template = """
    # 角色与任务
    你是一个精炼的信息提取和问答专家。你的任务是从提供的材料中**精确提取**与用户问题直接相关的信息，然后用最简洁、准确的方式回答问题。
    用户问题：{question}
    # 处理流程
    为了回答用户问题，你必须按照以下两步流程执行：
    
    ## 第一步：信息提取与筛选
    请从以下两个来源中，**只提取**与用户问题直接相关的信息：
    
    1. 从【知识图谱】中提取相关概念：
    {kg_context}
    
    2. 从【文档】中提取相关段落：
    {rag_context}
    
    **提取要求**：不要复制整个段落，只提取与问题**核心**相关的关键词、定义、属性或要点。
    
    ## 第二步：组织答案
    基于**第一步提取的信息**，用你自己的话组织答案。
    
    # 答案要求
    1. **直接回答问题**：第一句话就直接给出问题的答案
    2. **融合信息**：自然地结合从两个来源提取的信息
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        # ("human", "用户问题：{question}")
    ])
    #构建chain
    rag_kg_chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    conversational_chain = RunnableWithMessageHistory(
        runnable=rag_kg_chain,
        get_session_history=get_session_history,
        input_messages_key="question",  # 用户问题的key
        history_messages_key="chat_history",
    )

    return conversational_chain

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_session_history(session_id: str, **kwargs) -> DjangoChatMessageHistory:
    print(f"get_session_history 被调用: session_id={session_id}, kwargs={kwargs}")
    config = _session_configs.get(session_id, {})
    history = DjangoChatMessageHistory(session_id=session_id, **config)
    all_messages = history.messages
    print(f"消息记录 {all_messages}")
    # 3. 如果消息数量不多，直接返回
    if len(all_messages) <= 10:  # 阈值可以调整
        print(f"消息数量 {len(all_messages)} ≤ 10，不使用摘要")
        return history

    # 4. 分割消息
    # 保留最后2条完整消息，前面的进行摘要
    last_two_messages = all_messages[-3:]  # 保留最后两条
    messages_to_summarize = all_messages[:-3]  # 需要摘要的部分

    print(f"原始消息数量: {len(all_messages)}")
    print(f"需要摘要的消息: {len(messages_to_summarize)} 条")
    print(f"保留完整消息: {len(last_two_messages)} 条")

    # 5. 生成摘要
    summary = generate_summary(messages_to_summarize)

    # 6. 清空历史并重新构建
    history.clear()

    # 添加摘要消息
    from langchain_core.messages import SystemMessage
    summary_msg = SystemMessage(content=f"【对话历史摘要】\n{summary}")
    history.add_message(summary_msg)

    # 添加保留的完整消息
    for msg in last_two_messages:
        history.add_message(msg)

    print(f"摘要后消息数量: {len(history.messages)}")
    return history

def ask_question(rag_kg_chain, retriever, kg, tes, config, question):
    print(f"\n问题：{question}")
    try:
        # 从config中提取session_id
        session_id = config.get("configurable", {}).get("session_id")
        if not session_id:
            raise ValueError("config中必须包含session_id")

        # 打印session_id用于调试
        print(f"会话ID: {session_id}")

        # 初始化中文NLP模型用于实体识别

        entities_in_question = tes.named_entity_recognition(question)
        print("识别问题中的实体：", entities_in_question)

        # 查询知识图谱获取相关上下文
        kg_context = ""
        if entities_in_question:
            kg_relations = []
            for ent in entities_in_question:
                relations = kg.query_relations(ent)
                if relations:
                    kg_relations.append(f"{ent} 的相关关系有：{', '.join(relations)}")
            kg_context = "\n".join(kg_relations)
        print("【知识图谱上下文】\n", kg_context[:500] + "..." if len(kg_context) > 500 else kg_context)

        # 使用RAG检索文档相关段落
        rag_docs = retriever.invoke(
            question,
        )
        rag_context = format_docs_with_limit(rag_docs)
        print("【RAG上下文】\n", rag_context[:500] + "..." if len(rag_context) > 500 else rag_context)

        # 构建输入数据
        # 注意：这里只需要传递question、kg_context、rag_context
        # chat_history会自动从session中获取
        input_data = {
            "question": question,
            "kg_context": kg_context,
            "rag_context": rag_context
        }

        # 调用带消息历史的chain
        # RunnableWithMessageHistory会自动：
        # 1. 从session_id获取历史消息
        # 2. 将历史消息注入到prompt的chat_history变量
        # 3. 处理新的question
        # 4. 将新的对话对保存到历史
        response = rag_kg_chain.invoke(
            input=input_data,
            config=config
        )

        return response

    except Exception as e:
        import traceback
        print(f"处理问题时发生错误：{e}")
        print(traceback.format_exc())
        return f"抱歉，处理问题时发生错误：{str(e)}"


def generate_summary(messages, max_summary_length=200):
    """生成对话摘要"""
    if not messages:
        return "无历史对话。"

    llm = get_summary_llm()
    # 构建摘要提示
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的对话摘要生成器。请将以下对话历史压缩为简洁的摘要，保留关键信息。
            要求：
            1. 提取对话的核心主题和关键信息
            2. 保持对话的连贯性
            3. 用第三人称客观描述
            4. 摘要长度不超过{max_length}字
            5. 格式：用户问了什么，AI回答了什么
        
        对话历史："""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "请基于以上对话生成简洁摘要。")
    ])

    # 创建摘要链
    summary_chain = summary_prompt | llm

    try:
        # 生成摘要
        summary = summary_chain.invoke({
            "chat_history": messages,
            "max_length": max_summary_length
        })

        print(f"生成的摘要: {summary}")
        return summary.content if hasattr(summary, 'content') else str(summary)

    except Exception as e:
        print(f"生成摘要时出错: {e}")
        # 返回简单的摘要
        human_count = sum(1 for msg in messages if isinstance(msg, HumanMessage))
        ai_count = sum(1 for msg in messages if isinstance(msg, AIMessage))
        return f"历史对话摘要：包含{human_count}条用户消息和{ai_count}条AI回复。"


def ask_question_stream(rag_kg_chain, retriever, kg, tes, config, question):
    """流式询问问题"""
    print(f"\n[流式] 问题：{question}")

    try:
        # 从config中提取session_id
        session_id = config.get("configurable", {}).get("session_id")
        if not session_id:
            raise ValueError("config中必须包含session_id")

        print(f"[流式] 会话ID: {session_id}")

        # 初始化中文NLP模型用于实体识别
        entities_in_question = tes.named_entity_recognition(question)
        print("[流式] 识别问题中的实体：", entities_in_question)

        # 查询知识图谱获取相关上下文
        kg_context = ""
        if entities_in_question:
            kg_relations = []
            for ent in entities_in_question:
                relations = kg.query_relations(ent)
                if relations:
                    kg_relations.append(f"{ent} 的相关关系有：{', '.join(relations)}")
            kg_context = "\n".join(kg_relations)
        print("[流式] 【知识图谱上下文】\n", kg_context[:200] + "..." if len(kg_context) > 200 else kg_context)

        # 使用RAG检索文档相关段落
        rag_docs = retriever.invoke(question)
        rag_context = format_docs(rag_docs)
        print("[流式] 【RAG上下文】\n", rag_context[:200] + "..." if len(rag_context) > 200 else rag_context)

        # 构建输入数据
        input_data = {
            "question": question,
            "kg_context": kg_context,
            "rag_context": rag_context
        }

        # 流式调用chain
        for chunk in rag_kg_chain.stream(
                input=input_data,
                config=config
        ):
            yield chunk

    except Exception as e:
        import traceback
        error_msg = f"[流式] 处理问题时发生错误：{e}"
        print(error_msg)
        print(traceback.format_exc())
        yield f"抱歉，处理问题时发生错误：{str(e)}"


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def format_docs_with_limit(docs, max_length_per_doc=200, max_total_length=500):
    """格式化文档，限制长度"""
    formatted = []
    total_length = 0

    for i, doc in enumerate(docs):
        # 获取文档内容
        content = doc.page_content

        # 截断单个文档
        if len(content) > max_length_per_doc:
            # 智能截断：尽量在句子结束处截断
            truncated = content[:max_length_per_doc]
            # 找最后一个句号
            last_period = truncated.rfind('。')
            if last_period > max_length_per_doc * 0.7:  # 如果截断位置在句子中间
                content = truncated[:last_period + 1] + "..."
            else:
                content = truncated + "..."

        # 检查总长度
        if total_length + len(content) > max_total_length:
            # 如果超过总长度限制，添加提示并停止
            formatted.append(f"[文档{i + 1}]: {content[:max_total_length - total_length]}...")
            formatted.append(f"\n[已截断，只显示前{len(formatted)}个最相关文档]")
            break

        formatted.append(f"[文档{i + 1}]: {content}")
        total_length += len(content)

    return "\n\n".join(formatted)