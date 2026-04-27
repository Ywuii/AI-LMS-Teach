# test_stream_support.py
import os
import sys
import django

from rag_service.rag_kg_chain import build_rag_kg_chain

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from langchain.callbacks.base import BaseCallbackHandler
import time


class TestCallback(BaseCallbackHandler):
    """测试回调处理器"""

    def on_llm_new_token(self, token: str, **kwargs):
        print(f"[回调] 新token: {repr(token)}")

    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"[回调] LLM开始")

    def on_llm_end(self, response, **kwargs):
        print(f"[回调] LLM结束")


def test_chain_stream_support():
    """测试链的流式支持"""
    print("测试链的流式支持")
    print("=" * 60)

    # 创建回调
    callback = TestCallback()

    # 构建链
    print("1. 构建链...")
    chain = build_rag_kg_chain(callbacks=[callback])

    print(f"链类型: {type(chain)}")
    print(f"是否有 stream 方法: {hasattr(chain, 'stream')}")
    print(f"是否有 astream 方法: {hasattr(chain, 'astream')}")

    # 测试流式调用
    print("\n2. 测试简单流式调用...")

    # 先测试简单的输入
    test_input = {
        "question": "你好",
        "kg_context": "",
        "rag_context": "",
        "chat_history": []
    }

    config = {"configurable": {"session_id": "test_stream_123"}}

    try:
        print("开始 stream() 调用...")

        # 记录开始时间
        start_time = time.time()
        token_count = 0

        for i, chunk in enumerate(chain.stream(
                input=test_input,
                config=config
        )):
            elapsed = time.time() - start_time
            print(f"[{i}] 收到chunk: {repr(chunk)} (耗时: {elapsed:.2f}s)")
            token_count += 1

            if i >= 10:  # 限制数量
                print("... 限制显示前10个chunk")
                break

        print(f"\n总chunk数: {token_count}")
        print(f"总耗时: {time.time() - start_time:.2f}s")

        if token_count == 0:
            print("⚠️ 警告: 没有收到任何chunk!")
            print("可能的原因:")
            print("1. LLM没有流式输出")
            print("2. 链不支持.stream()方法")
            print("3. 输入数据有问题")

    except Exception as e:
        print(f"❌ stream() 调用异常: {e}")
        import traceback
        traceback.print_exc()

    # 测试 invoke 对比
    print("\n3. 测试 invoke() 对比...")
    try:
        start_time = time.time()
        result = chain.invoke(
            input=test_input,
            config=config
        )
        elapsed = time.time() - start_time
        print(f"invoke() 耗时: {elapsed:.2f}s")
        print(f"invoke() 结果长度: {len(result)}")
        print(f"invoke() 结果: {repr(result[:100])}...")
    except Exception as e:
        print(f"❌ invoke() 调用异常: {e}")

    print("\n" + "=" * 60)
    print("测试完成")


if __name__ == "__main__":
    test_chain_stream_support()