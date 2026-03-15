"""为已有论文添加 fields_of_study 字段"""
import sqlite3

DB_PATH = "backend/knowledge_nexus.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 添加列（如果不存在）
try:
    cur.execute("ALTER TABLE papers ADD COLUMN fields_of_study VARCHAR(500)")
    print("Added fields_of_study column")
except sqlite3.OperationalError:
    print("Column already exists")

# 根据论文标题/内容推断领域
FIELD_MAP = {
    "AlphaFold": "Biology, Computer Science, Structural Biology",
    "SWISS-MODEL": "Biology, Structural Biology, Bioinformatics",
    "Swin Transformer": "Computer Science, Computer Vision",
    "NumPy": "Computer Science, Mathematics, Scientific Computing",
    "Tidyverse": "Computer Science, Statistics, Data Science",
    "PyTorch": "Computer Science, Machine Learning",
    "PINNs": "Computer Science, Physics, Applied Mathematics",
    "SE-Net": "Computer Science, Computer Vision",
    "MoCo": "Computer Science, Computer Vision, Representation Learning",
    "Sentence-BERT": "Computer Science, Natural Language Processing",
    "EfficientDet": "Computer Science, Computer Vision, Object Detection",
    "deep learning": "Computer Science, Machine Learning",
    "DGCNN": "Computer Science, Computer Vision, 3D Understanding",
    "ConvNeXt": "Computer Science, Computer Vision",
    "NAT": "Computer Science, Machine Learning, AutoML",
    "对比学习": "Computer Science, Representation Learning",
    "数据增强": "Computer Science, Computer Vision, Machine Learning",
    "language model": "Computer Science, Natural Language Processing, AI",
    "ChatGPT": "Computer Science, Natural Language Processing, AI",
    "LLM": "Computer Science, Natural Language Processing, AI",
    "Hallucination": "Computer Science, Natural Language Processing, AI",
}

cur.execute("SELECT id, title, key_contributions FROM papers")
papers = cur.fetchall()

updated = 0
for pid, title, key_contrib in papers:
    fields = None
    # 尝试通过 key_contributions 匹配
    for keyword, field_value in FIELD_MAP.items():
        if (key_contrib and keyword.lower() in key_contrib.lower()) or \
           (title and keyword.lower() in title.lower()):
            fields = field_value
            break

    if not fields:
        fields = "Computer Science"  # 默认

    cur.execute("UPDATE papers SET fields_of_study = ? WHERE id = ?", (fields, pid))
    print(f"  {key_contrib or title[:40]}: {fields}")
    updated += 1

conn.commit()
conn.close()
print(f"\nUpdated {updated}/{len(papers)} papers")
