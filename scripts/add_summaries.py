"""为论文添加一句话简介"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import async_session, engine
from app.models.models import Paper
from sqlalchemy import select, text

SUMMARIES = {
    "AlphaFold": "用深度学习预测蛋白质3D结构，精度接近实验方法，被誉为AI解决了50年生物学难题。",
    "AlphaFold 3": "AlphaFold的升级版，不仅预测蛋白质，还能预测蛋白质与DNA/RNA/小分子的复合物结构。",
    "SWISS-MODEL": "经典的蛋白质同源建模工具，通过已知结构作为模板来预测未知蛋白质的3D结构。",
    "Swin Transformer": "将Transformer引入计算机视觉的里程碑工作，用滑动窗口机制高效处理图像。",
    "SE-Net": "提出通道注意力机制，让神经网络自动学习哪些特征通道更重要，提升图像识别精度。",
    "NumPy": "Python科学计算的基石库，提供高效的多维数组运算，几乎所有数据科学工具都依赖它。",
    "Tidyverse": "R语言的数据科学工具全家桶，包含ggplot2、dplyr等，让数据处理和可视化变得优雅简洁。",
    "PyTorch": "Facebook开源的深度学习框架，以动态计算图著称，是学术研究最主流的深度学习工具。",
    "PINNs": "用神经网络求解物理方程（如流体力学、热传导），让AI遵守物理定律。",
    "MoCo": "无监督视觉表征学习方法，通过对比学习让模型在没有标注数据时也能学到好的图像特征。",
    "Sentence-BERT": "将BERT改造为能高效计算句子相似度的模型，大幅提升语义搜索和文本匹配速度。",
    "数据增强综述": "系统综述了图像数据增强技术（翻转、裁剪、颜色变换等），以及如何用增强提升模型性能。",
    "EfficientDet": "高效目标检测模型，通过双向特征金字塔和复合缩放策略，在速度和精度间取得最优平衡。",
    "深度学习综述": "全面综述深度学习核心概念、CNN架构演进、面临的挑战和未来发展方向。",
    "DGCNN": "在点云数据上用图卷积进行3D物体识别，动态构建近邻图来捕获局部几何特征。",
    "ConvNeXt": "纯卷积网络的逆袭——用现代训练技巧改造传统CNN，性能媲美甚至超越Vision Transformer。",
    "NAT": "提出神经架构迁移方法，将已有网络结构的知识迁移到新任务上，减少架构搜索开销。",
    "对比学习嵌入": "深入分析对比学习中嵌入向量的几何性质，揭示了对比学习为什么有效的理论基础。",
}


async def main():
    # Add column if not exists
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE papers ADD COLUMN summary VARCHAR(500)"))
            print("Added summary column")
        except Exception as e:
            print(f"Column check: {e}")

    async with async_session() as db:
        result = await db.execute(select(Paper).order_by(Paper.citation_count.desc()))
        papers = result.scalars().all()
        updated = 0
        for p in papers:
            name = p.key_contributions
            if name and name in SUMMARIES:
                p.summary = SUMMARIES[name]
                updated += 1
                print(f"  {name}: {SUMMARIES[name][:50]}...")
        await db.commit()
        print(f"\nUpdated {updated}/{len(papers)} papers")


asyncio.run(main())
