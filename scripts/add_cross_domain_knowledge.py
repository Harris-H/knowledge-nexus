"""
添加跨领域知识节点和关联关系。
演示 Knowledge Nexus 的核心能力：发现不同领域知识间的深层关联。
"""

import sqlite3
import uuid
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "knowledge_nexus.db")


def gen_id():
    return uuid.uuid4().hex[:12]


conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ── 创建 knowledge_nodes 表（如果不存在） ──
cur.execute("""
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    node_type TEXT NOT NULL,
    domain TEXT NOT NULL,
    description TEXT,
    summary TEXT,
    source_info TEXT,
    year INTEGER,
    tags TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
""")
cur.execute("CREATE INDEX IF NOT EXISTS ix_kn_name ON knowledge_nodes(name)")
cur.execute("CREATE INDEX IF NOT EXISTS ix_kn_type ON knowledge_nodes(node_type)")
cur.execute("CREATE INDEX IF NOT EXISTS ix_kn_domain ON knowledge_nodes(domain)")

now = datetime.utcnow().isoformat()

# ══════════════════════════════════════════════════════════════
#  知识节点定义
# ══════════════════════════════════════════════════════════════

NODES = [
    # ── 生物学 ──
    {
        "id": gen_id(),
        "name": "自然选择与进化",
        "node_type": "phenomenon",
        "domain": "biology",
        "description": "达尔文提出的进化论核心机制：种群中个体存在随机变异，"
        "适应环境的个体更可能存活和繁殖，有利变异逐代积累导致物种演化。"
        "包含变异、选择、遗传三大要素。",
        "summary": "适者生存——自然界的优化算法",
        "source_info": "Charles Darwin, 1859, 《物种起源》",
        "year": 1859,
        "tags": "进化,自然选择,适者生存,达尔文,变异,遗传",
    },
    {
        "id": gen_id(),
        "name": "蚁群觅食行为",
        "node_type": "phenomenon",
        "domain": "biology",
        "description": "蚂蚁通过释放信息素标记路径来引导同伴找到食物。"
        "较短路径上的信息素浓度更高（蚂蚁往返更快、释放更频繁），"
        "形成正反馈，最终全群收敛到最优路径。是分布式智能的自然范例。",
        "summary": "蚂蚁用信息素找到最短路径——分布式优化的自然原型",
        "source_info": "昆虫行为学经典观察",
        "year": None,
        "tags": "蚁群,信息素,分布式智能,集群行为,正反馈",
    },
    {
        "id": gen_id(),
        "name": "免疫系统应答",
        "node_type": "process",
        "domain": "biology",
        "description": "生物免疫系统通过抗体识别抗原、克隆选择和亲和力成熟来对抗病原体。"
        "关键机制：多样性生成（V(D)J 重组）、克隆选择（有效抗体增殖）、"
        "免疫记忆（二次应答更快更强）。",
        "summary": "抗体的克隆选择与记忆——生物体的自适应防御系统",
        "source_info": "Burnet 克隆选择理论, 1957",
        "year": 1957,
        "tags": "免疫,抗体,克隆选择,亲和力成熟,免疫记忆",
    },
    {
        "id": gen_id(),
        "name": "神经突触传导",
        "node_type": "process",
        "domain": "neuroscience",
        "description": "神经元通过突触传递信号：前突触释放神经递质，后突触接收后产生电位变化。"
        "突触可塑性（Hebbian learning: 一起放电的神经元连接增强）"
        "是学习和记忆的生物基础。",
        "summary": "神经元通过突触传递和加强信号——大脑学习的生物基础",
        "source_info": "Santiago Ramón y Cajal (神经元学说), Donald Hebb (1949)",
        "year": 1949,
        "tags": "神经元,突触,赫布学习,突触可塑性,神经递质",
    },
    {
        "id": gen_id(),
        "name": "基因表达与调控",
        "node_type": "process",
        "domain": "biology",
        "description": "DNA→mRNA→蛋白质的中心法则，以及转录因子、增强子、表观遗传等调控机制。"
        "基因组是生命的'源代码'，表达调控决定了不同细胞的功能分化。",
        "summary": "DNA是生命的源代码，基因调控决定程序如何运行",
        "source_info": "Crick 中心法则, 1958; Jacob & Monod 操纵子模型, 1961",
        "year": 1958,
        "tags": "基因,DNA,转录,翻译,表观遗传,中心法则",
    },
    # ── 物理学 ──
    {
        "id": gen_id(),
        "name": "金属退火过程",
        "node_type": "phenomenon",
        "domain": "physics",
        "description": "将金属加热到高温后缓慢冷却，原子获得足够能量跳出局部能量陷阱，"
        "逐步找到更低能量的晶体排列。温度越高原子越活跃，"
        "冷却越慢越能找到全局最优结构。",
        "summary": "高温给原子逃离局部陷阱的能量，缓慢冷却找到全局最优",
        "source_info": "冶金学经典工艺",
        "year": None,
        "tags": "退火,冶金,能量最小化,相变,结晶",
    },
    {
        "id": gen_id(),
        "name": "最小作用量原理",
        "node_type": "principle",
        "domain": "physics",
        "description": "物理系统的运动路径使作用量（拉格朗日量的时间积分）取极值。"
        "从经典力学到量子场论，几乎所有物理定律都可以从这一原理推导。"
        "自然界似乎总在'优化'某个目标函数。",
        "summary": "自然界选择使作用量极值的路径——万物皆优化",
        "source_info": "Pierre-Louis Maupertuis (1744), Euler, Lagrange, Hamilton",
        "year": 1744,
        "tags": "作用量,拉格朗日,变分法,优化,最优路径",
    },
    {
        "id": gen_id(),
        "name": "热力学第二定律（熵增）",
        "node_type": "law",
        "domain": "physics",
        "description": "孤立系统的熵不会减少，趋向最大无序状态。"
        "信息论中的熵与热力学熵有深刻联系（Shannon 1948）。"
        "机器学习中的交叉熵损失函数直接源于信息熵概念。",
        "summary": "万物趋向无序——从热力学到信息论的统一",
        "source_info": "Rudolf Clausius, 1850; Ludwig Boltzmann; Claude Shannon",
        "year": 1850,
        "tags": "熵,热力学,信息论,无序,概率",
    },
    {
        "id": gen_id(),
        "name": "反馈控制（负反馈）",
        "node_type": "principle",
        "domain": "engineering",
        "description": "通过将系统输出反馈到输入端，与期望值比较产生误差信号，"
        "驱动系统减小误差。PID 控制器是最经典的实现。"
        "深度学习的反向传播本质上也是一种反馈控制。",
        "summary": "测量误差→调整输入→减小误差——万能的控制策略",
        "source_info": "James Watt 蒸汽机调速器 (1788); Nyquist, Bode (20世纪)",
        "year": 1788,
        "tags": "反馈,PID,控制论,误差修正,自动控制",
    },
    # ── 数学 ──
    {
        "id": gen_id(),
        "name": "贝叶斯定理",
        "node_type": "theorem",
        "domain": "mathematics",
        "description": "P(A|B) = P(B|A)·P(A)/P(B)。允许我们根据新证据更新对假设的信念。"
        "是概率推理、机器学习（朴素贝叶斯、贝叶斯网络）、"
        "医学诊断、垃圾邮件过滤的数学基础。",
        "summary": "用证据更新信念——从先验到后验的推理法则",
        "source_info": "Thomas Bayes, 1763 (遗作); Pierre-Simon Laplace 推广",
        "year": 1763,
        "tags": "贝叶斯,概率,后验,先验,推理,统计",
    },
    {
        "id": gen_id(),
        "name": "梯度下降法",
        "node_type": "method",
        "domain": "mathematics",
        "description": "沿函数梯度的反方向迭代更新参数以最小化目标函数。"
        "变体：随机梯度下降(SGD)、Adam、RMSprop 等。"
        "是深度学习训练的核心引擎，也类似于水沿山坡向下流的自然现象。",
        "summary": "沿最陡方向下山——深度学习训练的核心引擎",
        "source_info": "Augustin-Louis Cauchy, 1847",
        "year": 1847,
        "tags": "梯度,优化,SGD,Adam,深度学习,凸优化",
    },
    {
        "id": gen_id(),
        "name": "图论与网络科学",
        "node_type": "concept",
        "domain": "mathematics",
        "description": "用节点和边描述实体及其关系。从欧拉的柯尼斯堡七桥问题到现代社交网络分析、"
        "知识图谱、图神经网络。六度分隔理论揭示了小世界网络的普遍性。",
        "summary": "万物皆可建模为图——从七桥问题到知识图谱",
        "source_info": "Leonhard Euler, 1736; Erdős–Rényi 随机图; Watts-Strogatz 小世界",
        "year": 1736,
        "tags": "图论,网络,小世界,度分布,图神经网络",
    },
    # ── 计算机科学（方法） ──
    {
        "id": gen_id(),
        "name": "遗传算法",
        "node_type": "method",
        "domain": "computer_science",
        "description": "模拟自然选择和遗传机制的优化算法：个体编码为染色体，"
        "通过选择、交叉、变异操作进化种群，适应度函数驱动演化方向。"
        "适合解决 NP 难问题的近似最优解。",
        "summary": "在计算机中重现进化——用自然选择求解优化问题",
        "source_info": "John Holland, 1975, 《Adaptation in Natural and Artificial Systems》",
        "year": 1975,
        "tags": "遗传算法,进化计算,选择,交叉,变异,优化",
    },
    {
        "id": gen_id(),
        "name": "蚁群优化算法",
        "node_type": "method",
        "domain": "computer_science",
        "description": "模拟蚂蚁觅食行为的元启发式优化算法。"
        "虚拟蚂蚁在图上行走并释放虚拟信息素，好路径获得更多信息素，"
        "信息素随时间蒸发防止过早收敛。经典应用：旅行商问题(TSP)。",
        "summary": "虚拟蚂蚁用数字信息素找最优路径——群体智能优化",
        "source_info": "Marco Dorigo, 1992, 博士论文",
        "year": 1992,
        "tags": "蚁群算法,信息素,TSP,群体智能,组合优化",
    },
    {
        "id": gen_id(),
        "name": "模拟退火算法",
        "node_type": "method",
        "domain": "computer_science",
        "description": "模拟金属退火过程的概率优化算法。以一定概率接受较差解"
        "（概率随'温度'降低而减小），避免陷入局部最优。"
        "温度调度策略决定了探索与利用的平衡。",
        "summary": "用数字温度跳出局部陷阱——物理退火的算法映射",
        "source_info": "Scott Kirkpatrick, C. Daniel Gelatt Jr., Mario P. Vecchi, 1983",
        "year": 1983,
        "tags": "模拟退火,Metropolis,温度调度,全局优化,随机搜索",
    },
    {
        "id": gen_id(),
        "name": "人工神经网络",
        "node_type": "method",
        "domain": "computer_science",
        "description": "模仿生物神经网络的计算模型。人工神经元接收加权输入，"
        "经激活函数产生输出。多层网络通过反向传播学习权重。"
        "从感知机(1958)到深度学习(2012+)，始终是AI的核心范式。",
        "summary": "用数学神经元模拟大脑——从感知机到深度学习的60年",
        "source_info": "McCulloch & Pitts (1943); Rosenblatt 感知机 (1958); Hinton et al. (2006+)",
        "year": 1943,
        "tags": "神经网络,感知机,反向传播,深度学习,激活函数",
    },
    {
        "id": gen_id(),
        "name": "人工免疫算法",
        "node_type": "method",
        "domain": "computer_science",
        "description": "受生物免疫系统启发的计算框架。核心机制：负选择（异常检测）、"
        "克隆选择（优化搜索）、免疫网络（多样性维护）。"
        "应用于网络安全入侵检测、模式识别和优化。",
        "summary": "用计算机模拟免疫应答——自适应异常检测和优化",
        "source_info": "Farmer, Packard & Perelson (1986); de Castro & Von Zuben (2002)",
        "year": 1986,
        "tags": "人工免疫,克隆选择,负选择,异常检测,网络安全",
    },
    {
        "id": gen_id(),
        "name": "注意力机制",
        "node_type": "method",
        "domain": "computer_science",
        "description": "让模型动态地'关注'输入中最相关的部分，而非平等对待所有信息。"
        "灵感来自人类视觉的选择性注意。从 Seq2Seq 注意力(2014)到 "
        "Transformer 的自注意力(2017)，彻底改变了 NLP 和 CV。",
        "summary": "让AI学会'看重点'——从人类注意力到Transformer",
        "source_info": "Bahdanau et al. (2014); Vaswani et al. 'Attention Is All You Need' (2017)",
        "year": 2014,
        "tags": "注意力,Transformer,自注意力,Seq2Seq,选择性关注",
    },
    {
        "id": gen_id(),
        "name": "信息熵与交叉熵",
        "node_type": "concept",
        "domain": "computer_science",
        "description": "Shannon 信息熵量化了随机变量的不确定性。交叉熵衡量两个概率分布的差异。"
        "在机器学习中，交叉熵损失函数是分类任务的标准损失。"
        "与热力学熵在数学结构上完全同构。",
        "summary": "信息的不确定性度量——从通信理论到深度学习损失函数",
        "source_info": "Claude Shannon, 1948, 'A Mathematical Theory of Communication'",
        "year": 1948,
        "tags": "信息熵,交叉熵,Shannon,损失函数,KL散度",
    },
    # ── 经济学/博弈论 ──
    {
        "id": gen_id(),
        "name": "纳什均衡",
        "node_type": "theorem",
        "domain": "economics",
        "description": "博弈论核心概念：所有玩家都不能通过单方面改变策略来提高收益的状态。"
        "GAN 的训练过程（生成器vs判别器）本质上就是寻找纳什均衡。"
        "也解释了市场竞争、军备竞赛等现象。",
        "summary": "无人能单方面获利的博弈稳态——GAN训练的数学本质",
        "source_info": "John Nash, 1950, 'Equilibrium Points in N-Person Games'",
        "year": 1950,
        "tags": "博弈论,纳什均衡,GAN,对抗,策略",
    },
]

# ── 插入知识节点 ──
node_ids = {}  # name -> id
inserted = 0
for n in NODES:
    # 检查是否已存在
    existing = cur.execute(
        "SELECT id FROM knowledge_nodes WHERE name = ?", (n["name"],)
    ).fetchone()
    if existing:
        node_ids[n["name"]] = existing[0]
        print(f"  ⏭ 已存在: {n['name']}")
        continue

    cur.execute(
        "INSERT INTO knowledge_nodes (id, name, node_type, domain, description, summary, "
        "source_info, year, tags, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            n["id"],
            n["name"],
            n["node_type"],
            n["domain"],
            n["description"],
            n["summary"],
            n["source_info"],
            n["year"],
            n["tags"],
            now,
            now,
        ),
    )
    node_ids[n["name"]] = n["id"]
    inserted += 1
    print(f"  ✅ [{n['node_type']}] {n['name']} ({n['domain']})")

print(f"\n📌 插入 {inserted} 个知识节点")

# ══════════════════════════════════════════════════════════════
#  跨领域关联关系
# ══════════════════════════════════════════════════════════════

# 查出论文 ID
papers = {}
for row in cur.execute("SELECT id, key_contributions, title FROM papers"):
    papers[row[1] or row[2]] = row[0]

# 便捷引用
N = node_ids  # knowledge nodes
P = papers  # papers

existing_rels = set()
for row in cur.execute("SELECT source_id, target_id FROM relations"):
    existing_rels.add((row[0], row[1]))

RELATIONS = [
    # ═══ 生物→计算机：进化论→遗传算法 ═══
    (
        N["自然选择与进化"],
        N["遗传算法"],
        "INSPIRES",
        "knowledge_node",
        "knowledge_node",
        "遗传算法直接模拟自然选择：个体=解，适应度=目标函数，交叉变异=搜索算子",
    ),
    # ═══ 生物→计算机：蚁群→蚁群算法 ═══
    (
        N["蚁群觅食行为"],
        N["蚁群优化算法"],
        "INSPIRES",
        "knowledge_node",
        "knowledge_node",
        "蚁群算法将真实蚂蚁的信息素机制数字化：路径=解空间，信息素=经验累积",
    ),
    # ═══ 物理→计算机：退火→模拟退火 ═══
    (
        N["金属退火过程"],
        N["模拟退火算法"],
        "INSPIRES",
        "knowledge_node",
        "knowledge_node",
        "模拟退火算法映射金属退火过程：温度→搜索温度，能量→目标函数，慢冷→概率递减",
    ),
    # ═══ 神经科学→计算机：神经元→人工神经网络 ═══
    (
        N["神经突触传导"],
        N["人工神经网络"],
        "INSPIRES",
        "knowledge_node",
        "knowledge_node",
        "人工神经网络直接模拟突触传导：权重=突触强度，激活函数=神经元放电阈值，反向传播≈赫布学习",
    ),
    # ═══ 生物→计算机：免疫→人工免疫 ═══
    (
        N["免疫系统应答"],
        N["人工免疫算法"],
        "INSPIRES",
        "knowledge_node",
        "knowledge_node",
        "人工免疫算法映射免疫应答：抗体=检测器，克隆选择=优化，负选择=异常检测",
    ),
    # ═══ 物理→数学→计算机：最优路径 ═══
    (
        N["最小作用量原理"],
        N["梯度下降法"],
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "自然选择最优路径（最小作用量）↔ 算法寻找最优解（梯度下降），都在某种'景观'上寻找极值",
    ),
    # ═══ 物理→计算机：熵 ═══
    (
        N["热力学第二定律（熵增）"],
        N["信息熵与交叉熵"],
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "热力学熵与信息熵在数学上同构：S = -k∑p·ln(p)，从物理无序到信息不确定性的统一",
    ),
    # ═══ 工程→计算机：反馈控制→反向传播 ═══
    (
        N["反馈控制（负反馈）"],
        N["人工神经网络"],
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "反向传播本质是反馈控制：误差信号从输出传回，调整权重以减小误差",
    ),
    # ═══ 博弈论→GAN ═══
    (
        N["纳什均衡"],
        P.get("GAN", ""),
        "ANALOGOUS_TO",
        "knowledge_node",
        "paper",
        "GAN 训练就是寻找生成器与判别器的纳什均衡：双方都不能单方面改善时达到稳态",
    ),
    # ═══ 数学→论文：贝叶斯→多个ML论文 ═══
    (
        N["贝叶斯定理"],
        N["人工神经网络"],
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "贝叶斯推理是神经网络概率解释的基础，贝叶斯神经网络量化预测不确定性",
    ),
    # ═══ 数学→论文：梯度下降→深度学习框架 ═══
    (
        N["梯度下降法"],
        P.get("PyTorch", ""),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "PyTorch 的 autograd 引擎自动计算梯度，是梯度下降法的工程化实现",
    ),
    # ═══ 神经网络→深度学习论文 ═══
    (
        N["人工神经网络"],
        P.get("ViT", ""),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "ViT 是人工神经网络的前沿变体，用 Transformer 架构处理视觉任务",
    ),
    (
        N["人工神经网络"],
        P.get("AlphaFold", ""),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "AlphaFold 使用深度神经网络从序列预测蛋白质3D结构，是AI赋能科学的典范",
    ),
    # ═══ 注意力→论文 ═══
    (
        N["注意力机制"],
        P.get("Swin Transformer", ""),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "Swin Transformer 是注意力机制在计算机视觉中的高效实现",
    ),
    (
        N["注意力机制"],
        P.get("SE-Net", ""),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "SE-Net 的通道注意力是注意力机制在CNN中的早期应用",
    ),
    # ═══ 生物：基因→计算机 ═══
    (
        N["基因表达与调控"],
        N["遗传算法"],
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "基因编码→蛋白质表达 ↔ 染色体编码→适应度评估，都是编码-解码-选择的过程",
    ),
    # ═══ 图论→知识图谱项目本身 ═══
    (
        N["图论与网络科学"],
        P.get("DGCNN", ""),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "DGCNN 是图论在深度学习中的应用，用图卷积处理点云数据",
    ),
    # ═══ 物理→科学计算论文 ═══
    (
        N["最小作用量原理"],
        P.get("PINNs", ""),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "PINNs 用神经网络求解由最小作用量原理推导出的微分方程",
    ),
    # ═══ 跨知识节点：进化+博弈 ═══
    (
        N["自然选择与进化"],
        N["纳什均衡"],
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "进化博弈论：自然选择可以用博弈论描述，进化稳定策略(ESS)是纳什均衡的生物学对应",
    ),
    # ═══ 知识节点间：退火+熵 ═══
    (
        N["金属退火过程"],
        N["热力学第二定律（熵增）"],
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "退火过程中系统从高熵无序态缓慢趋向低熵有序态，是熵减的典型案例（需要外部能量输入）",
    ),
    # ═══ 人类注意力→计算机注意力 ═══
    (
        N["神经突触传导"],
        N["注意力机制"],
        "INSPIRES",
        "knowledge_node",
        "knowledge_node",
        "计算机注意力机制灵感源于人类大脑的选择性注意：神经元对重要刺激增强响应",
    ),
]

# ── 插入关系 ──
rel_added = 0
for src, tgt, rtype, stype, ttype, desc in RELATIONS:
    if not src or not tgt:
        print(f"  ⚠ 跳过（ID 缺失）: {desc[:40]}")
        continue
    if (src, tgt) in existing_rels:
        print(f"  ⏭ 已存在: {desc[:40]}")
        continue

    cur.execute(
        "INSERT INTO relations (id, source_id, source_type, target_id, target_type, "
        "relation_type, description, confidence, ai_generated, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 1.0, 0, 'confirmed', ?)",
        (gen_id(), src, stype, tgt, ttype, rtype, desc, now),
    )
    existing_rels.add((src, tgt))
    rel_added += 1
    print(f"  ✅ {rtype}: {desc[:50]}")

conn.commit()

# ── 统计 ──
total_nodes = cur.execute("SELECT COUNT(*) FROM knowledge_nodes").fetchone()[0]
total_rels = cur.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
total_papers = cur.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
print(f"\n{'=' * 50}")
print(f"📊 知识节点: {total_nodes} | 论文: {total_papers} | 关系: {total_rels}")
print(f"📌 本次新增: {inserted} 个节点, {rel_added} 条关系")
conn.close()
