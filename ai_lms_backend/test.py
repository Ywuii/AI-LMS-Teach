# test_rag_service.py
import sys
import os

# 添加RAG服务模块路径（根据你的实际结构调整）
sys.path.append('/path/to/your/rag_service')  # 修改为你的实际路径


def test_rag_query():
    """直接测试RAG服务的query方法"""
    try:
        # 导入RAGService
        from rag_service.rag_service import RAGService

        print("正在初始化RAG服务...")

        # 创建RAG服务实例
        rag_service = RAGService()

        # 初始化服务
        rag_service.initialize()

        print("RAG服务初始化完成！")
        print("=" * 50)

        # 测试查询
        test_question = "什么是C语言？"
        print(f"测试问题: {test_question}")
        print("-" * 50)

        # 执行查询
        result = rag_service.query(test_question)

        # 打印结果
        print(f"查询结果: {result}")
        print("-" * 50)

        if result.get('success'):
            print("✅ 查询成功！")
            print(f"答案: {result.get('answer', '')}")

            # 如果有其他信息也打印出来
            for key, value in result.items():
                if key not in ['success', 'answer'] and value:
                    print(f"{key}: {value}")
        else:
            print("❌ 查询失败！")
            print(f"错误信息: {result.get('error', '未知错误')}")
            print(f"详细结果: {result}")

        return result

    except ImportError as e:
        print(f"❌ 导入RAGService失败: {e}")
        print("请检查:")
        print("1. 是否正确设置了sys.path")
        print("2. rag_service模块是否在指定路径")
        print(f"当前sys.path: {sys.path}")

    except AttributeError as e:
        print(f"❌ 方法调用错误: {e}")
        print("请确保RAGService有query和initialize方法")

    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


# 使用示例
if __name__ == "__main__":
    # 如果RAGService在项目根目录
    # 可以这样添加路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # 假设test文件在项目子目录
    sys.path.insert(0, project_root)

    # 运行测试
    test_rag_query()