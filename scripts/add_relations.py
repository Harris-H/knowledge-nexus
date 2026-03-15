"""
为现有论文添加学术关联关系。
基于论文之间的技术继承、方法类比、竞争对比等关系建立知识图谱边。
"""
import sqlite3
import uuid
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "knowledge_nexus.db")

def gen_id():
    return uuid.uuid4().hex[:12]

# ── 先查出所有论文的 id，按 key_contributions 索引 ──
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

papers = {}
for row in cur.execute("SELECT id, key_contributions, title FROM papers"):
    key = row[1] or row[2]
    papers[key] = row[0]

# 打印方便调试
for k, v in papers.items():
    print(f"  {v} = {k}")

# ── 便捷引用 ──
ALPHAFOLD      = papers["AlphaFold"]
ALPHAFOLD3     = papers["AlphaFold 3"]
SWIN           = papers["Swin Transformer"]
CIFAR          = papers["CIFAR-10/100"]
GAN            = papers["GAN"]
VIT            = papers["ViT"]
NUMPY          = papers["NumPy"]
TIDYVERSE      = papers["Tidyverse"]
PYTORCH        = papers["PyTorch"]
PINNS          = papers["PINNs"]
SWISS_MODEL    = papers["SWISS-MODEL"]
GAN_SURVEY     = papers["GAN 综述"]
SENET          = papers["SE-Net"]
STABLE_DIFF    = papers["Stable Diffusion / LDM"]
SRGAN          = papers["SRGAN"]
DATA_AUG       = papers["数据增强综述"]
MOCO           = papers["MoCo"]
LAMMPS         = papers["LAMMPS"]
SENTENCE_BERT  = papers["Sentence-BERT"]
EFFICIENTDET   = papers["EfficientDet"]
DL_SURVEY      = papers["深度学习综述"]
DGCNN          = papers["DGCNN"]
CONVNEXT       = papers["ConvNeXt"]
NAT            = papers["NAT"]
CONTRASTIVE    = papers["对比学习嵌入"]

# ── 检查已有关系，避免重复 ──
existing = set()
for row in cur.execute("SELECT source_id, target_id FROM relations"):
    existing.add((row[0], row[1]))

# ── 定义新关系 ──
# 格式: (source_id, target_id, relation_type, description)
NEW_RELATIONS = [
    # === GAN 家族 ===
    (GAN_SURVEY, GAN, "REVIEWS",
     "全面综述 GAN 的原理、变体和应用，GAN 是该综述的核心主题"),
    (SRGAN, GAN, "BUILDS_ON",
     "SRGAN 将 GAN 的对抗训练框架应用于图像超分辨率任务"),
    (STABLE_DIFF, GAN, "RELATED_TO",
     "扩散模型是 GAN 之后的新一代生成范式，两者常被对比"),
    (GAN_SURVEY, SRGAN, "RELATED_TO",
     "综述覆盖了 SRGAN 等条件 GAN 在图像恢复中的应用"),
    (GAN_SURVEY, STABLE_DIFF, "RELATED_TO",
     "综述讨论了从 GAN 到扩散模型的生成式 AI 演进"),
    (SRGAN, STABLE_DIFF, "RELATED_TO",
     "都是图像生成/增强领域的里程碑，SRGAN 用 GAN，SD 用扩散"),

    # === Vision Transformer 家族 ===
    (SWIN, VIT, "IMPROVES",
     "Swin 引入层级结构和移位窗口注意力，解决了 ViT 在密集预测上的不足"),
    (CONVNEXT, VIT, "COMPETES_WITH",
     "ConvNeXt 用纯卷积架构对标 ViT，证明 CNN 仍有竞争力"),
    (NAT, VIT, "IMPROVES",
     "NAT 用邻域注意力替代全局注意力，降低 ViT 的计算复杂度"),
    (NAT, SWIN, "RELATED_TO",
     "都使用局部注意力机制，NAT 用邻域窗口，Swin 用移位窗口"),

    # === 注意力机制演化 ===
    (VIT, SENET, "BUILDS_ON",
     "ViT 的自注意力机制是 SE-Net 通道注意力思想的自然延伸"),
    (NAT, SENET, "BUILDS_ON",
     "邻域注意力继承了 SE-Net 局部特征增强的思路"),

    # === CIFAR 基准数据集 ===
    (GAN, CIFAR, "RELATED_TO",
     "GAN 论文使用 CIFAR-10 评估生成图像质量"),
    (VIT, CIFAR, "RELATED_TO",
     "ViT 在 CIFAR-10/100 上验证了 Transformer 用于图像分类的有效性"),
    (SENET, CIFAR, "RELATED_TO",
     "SE-Net 在 CIFAR 上验证了通道注意力的效果"),
    (CONVNEXT, CIFAR, "RELATED_TO",
     "ConvNeXt 在 CIFAR 等经典基准上与 Transformer 对比"),

    # === 跨域：科学计算 ===
    (PINNS, LAMMPS, "ANALOGOUS_TO",
     "PINNs 用神经网络求解物理方程 ↔ LAMMPS 用经典力学模拟，殊途同归"),
    (ALPHAFOLD, PINNS, "ANALOGOUS_TO",
     "都是深度学习赋能科学计算的代表：蛋白质结构预测 ↔ 物理方程求解"),
    (LAMMPS, SWISS_MODEL, "RELATED_TO",
     "都是计算生物/化学领域的核心工具：分子动力学 ↔ 蛋白质同源建模"),

    # === 深度学习框架 & 工具 ===
    (VIT, PYTORCH, "RELATED_TO",
     "ViT 的主要开源实现基于 PyTorch (timm 库)"),
    (GAN, PYTORCH, "RELATED_TO",
     "GAN 及其变体广泛使用 PyTorch 实现和训练"),
    (NUMPY, TIDYVERSE, "ANALOGOUS_TO",
     "Python 的数值计算基石 ↔ R 的数据科学基石，不同生态的同类角色"),

    # === 深度学习综述覆盖 ===
    (DL_SURVEY, VIT, "RELATED_TO",
     "综述覆盖了 Vision Transformer 等前沿视觉架构"),
    (DL_SURVEY, GAN, "RELATED_TO",
     "综述覆盖了 GAN 等生成模型的原理和发展"),
    (DL_SURVEY, MOCO, "RELATED_TO",
     "综述覆盖了自监督对比学习等无监督学习范式"),

    # === 自监督学习 & 表示学习 ===
    (MOCO, VIT, "RELATED_TO",
     "MoCo v3 将对比学习扩展到 ViT 架构，推动自监督视觉 Transformer"),
    (DATA_AUG, SRGAN, "RELATED_TO",
     "SRGAN 的超分辨率可作为数据增强手段提升下游任务性能"),
    (DATA_AUG, GAN, "RELATED_TO",
     "GAN 生成的合成数据是重要的数据增强策略之一"),

    # === 跨模态/跨领域类比 ===
    (SENTENCE_BERT, VIT, "ANALOGOUS_TO",
     "NLP 的句子嵌入 ↔ CV 的图像 patch 嵌入，都将输入编码为向量表示"),
    (DGCNN, PINNS, "ANALOGOUS_TO",
     "图神经网络处理几何结构 ↔ PINNs 处理物理场，都将深度学习用于结构化数据"),
]

# ── 插入新关系 ──
added = 0
skipped = 0
for src, tgt, rtype, desc in NEW_RELATIONS:
    if (src, tgt) in existing:
        print(f"  ⏭ 已存在: {src} -> {tgt}")
        skipped += 1
        continue
    cur.execute(
        "INSERT INTO relations (id, source_id, source_type, target_id, target_type, "
        "relation_type, description, confidence, ai_generated, status, created_at) "
        "VALUES (?, ?, 'paper', ?, 'paper', ?, ?, 1.0, 0, 'confirmed', ?)",
        (gen_id(), src, tgt, rtype, desc, datetime.utcnow().isoformat())
    )
    existing.add((src, tgt))
    added += 1
    print(f"  ✅ {rtype}: {desc[:50]}")

conn.commit()

# ── 统计 ──
total = cur.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
print(f"\n新增 {added} 条关系，跳过 {skipped} 条重复")
print(f"数据库现有 {total} 条关系")
conn.close()
