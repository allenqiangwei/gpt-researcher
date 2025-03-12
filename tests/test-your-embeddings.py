from gpt_researcher.config.config import Config
from gpt_researcher.memory.embeddings import Memory
import asyncio
import os
from dotenv import load_dotenv

# 先加载.env文件
load_dotenv()

# 然后手动设置环境变量
os.environ["EMBEDDING"] = "custom:text-embedding-nomic-embed-text-v1.5"
os.environ["OPENAI_BASE_URL"] = "http://192.168.7.198:1234/v1"

async def main():
    cfg = Config()
    
    print("当前嵌入配置信息:")
    print(f"EMBEDDING 环境变量: {os.getenv('EMBEDDING', '未设置')}")
    print(f"OPENAI_BASE_URL 环境变量: {os.getenv('OPENAI_BASE_URL', '未设置')}")
    
    try:
        # 检查并打印当前配置
        print(f"cfg.embedding: {getattr(cfg, 'embedding', '未设置')}")
        print(f"cfg.embedding_provider: {getattr(cfg, 'embedding_provider', '未设置')}")
        print(f"cfg.embedding_model: {getattr(cfg, 'embedding_model', '未设置')}")
        
        if not cfg.embedding_provider or not cfg.embedding_model:
            raise ValueError("请在.env文件中设置EMBEDDING环境变量，格式为'provider:model'")
            
        print(f"\n使用以下配置进行测试:")
        print(f"嵌入提供者: {cfg.embedding_provider}")
        print(f"嵌入模型: {cfg.embedding_model}")
        
        # 创建Memory实例
        embedding_kwargs = {}  # 可以根据需要添加额外的参数
        
        memory = Memory(
            embedding_provider=cfg.embedding_provider,
            model=cfg.embedding_model,
            **embedding_kwargs
        )
        
        # 获取embeddings对象
        embeddings = memory.get_embeddings()
        
        # 测试文本
        test_text = "这是一个测试句子，用于验证嵌入功能是否正常工作。"
        embedding_vector = embeddings.embed_query(test_text)
        
        # 打印结果
        print(f"\n测试成功！")
        print(f"使用提供者: {cfg.embedding_provider}")
        print(f"使用模型: {cfg.embedding_model}")
        print(f"嵌入向量长度: {len(embedding_vector)}")
        print(f"向量前几个值: {embedding_vector[:5]}")
        
    except ValueError as ve:
        print(f"配置错误: {ve}")
    except Exception as e:
        print(f"测试嵌入时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())