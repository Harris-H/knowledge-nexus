"""为缺少核心工作名称和简介的论文补充数据"""
import sqlite3

DB_PATH = "backend/knowledge_nexus.db"

PAPER_METADATA = {
    "1d2abcbb837d": {
        "key_contributions": "CIFAR-10/100",
        "summary": "创建了计算机视觉最经典的基准数据集CIFAR-10和CIFAR-100，几乎所有图像识别研究都在此数据集上评测。",
    },
    "765eefafc309": {
        "key_contributions": "GAN",
        "summary": "提出生成对抗网络，用「生成器vs判别器」博弈的方式让AI学会生成逼真图像，开创了AI生成内容的新纪元。",
    },
    "45e050c397c0": {
        "key_contributions": "ViT",
        "summary": "将图像切成16×16的小块当作「单词」输入Transformer，证明纯Transformer也能做图像识别，颠覆了CNN的统治地位。",
    },
    "39b0539ae3c6": {
        "key_contributions": "GAN 综述",
        "summary": "全面综述生成对抗网络的原理、变体（DCGAN/WGAN/StyleGAN等）、训练技巧和应用场景。",
    },
    "25ee97751d2c": {
        "key_contributions": "Stable Diffusion / LDM",
        "summary": "在压缩的潜空间中做扩散生成，大幅降低计算成本，就是大名鼎鼎的Stable Diffusion背后的核心论文。",
    },
    "bb718fb979fa": {
        "key_contributions": "SRGAN",
        "summary": "首次用GAN做图像超分辨率，能将低分辨率图片放大4倍并生成逼真细节，开创了AI图像增强的新方向。",
    },
    "b41fb65a0379": {
        "key_contributions": "LAMMPS",
        "summary": "大规模原子/分子并行模拟器，物理/化学/材料科学领域最广泛使用的分子动力学模拟工具。",
    },
}

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

updated = 0
for pid, data in PAPER_METADATA.items():
    cur.execute(
        "UPDATE papers SET key_contributions = ?, summary = ? WHERE id = ?",
        (data["key_contributions"], data["summary"], pid),
    )
    if cur.rowcount > 0:
        print(f"  ✅ {data['key_contributions']}: {data['summary'][:50]}...")
        updated += 1
    else:
        print(f"  ⚠️ Paper {pid} not found")

conn.commit()
conn.close()
print(f"\nUpdated {updated}/{len(PAPER_METADATA)} papers")
