"""
添加更多跨领域知识节点和关联关系（第二批）。
覆盖：心理学、化学、生态学、哲学、社会学、信息论、控制论等。
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
now = datetime.utcnow().isoformat()

# ══════════════════════════════════════════════════════════════
#  第二批知识节点
# ══════════════════════════════════════════════════════════════

NODES = [
    # ── 心理学 / 认知科学 ──
    {
        "name": "巴甫洛夫条件反射",
        "node_type": "phenomenon",
        "domain": "psychology",
        "description": "经典条件反射：将无关刺激（铃声）与本能刺激（食物）反复配对后，"
        "无关刺激单独就能引起反应（分泌唾液）。"
        "是强化学习中「状态-奖励关联」的生物原型。",
        "summary": "铃声→唾液：环境信号与奖励的关联学习",
        "source_info": "Ivan Pavlov, 1897",
        "year": 1897,
        "tags": "条件反射,巴甫洛夫,学习,强化,关联",
    },
    {
        "name": "操作性条件反射（强化学习原型）",
        "node_type": "phenomenon",
        "domain": "psychology",
        "description": "斯金纳的操作性条件反射：行为后果决定行为频率。"
        "正强化（奖励增加行为）、负强化（去除惩罚增加行为）、"
        "惩罚（减少行为）。"
        "直接对应计算机强化学习的奖励/惩罚信号机制。",
        "summary": "行为→奖惩→行为调整：强化学习的心理学基础",
        "source_info": "B.F. Skinner, 1938, 《The Behavior of Organisms》",
        "year": 1938,
        "tags": "强化学习,斯金纳,操作性条件反射,奖励,惩罚",
    },
    {
        "name": "认知偏差与启发式",
        "node_type": "phenomenon",
        "domain": "psychology",
        "description": "人类决策中的系统性偏差：可用性启发式（容易想到的事被高估概率）、"
        "锚定效应、确认偏差等。Kahneman的双系统理论：快思考(System 1)易犯偏差，"
        "慢思考(System 2)更理性但耗能。",
        "summary": "人脑的'近似算法'——快但有偏差的决策捷径",
        "source_info": "Daniel Kahneman & Amos Tversky, 1974; 《Thinking, Fast and Slow》",
        "year": 1974,
        "tags": "认知偏差,启发式,Kahneman,双系统,决策",
    },
    {
        "name": "遗忘曲线与间隔重复",
        "node_type": "phenomenon",
        "domain": "psychology",
        "description": "艾宾浩斯发现记忆遗忘遵循指数衰减曲线。"
        "间隔重复（Spaced Repetition）利用遗忘曲线规律，"
        "在即将遗忘时复习以巩固记忆。"
        "类比：神经网络的权重衰减（weight decay）和学习率调度。",
        "summary": "记忆指数衰减——间隔重复延缓遗忘",
        "source_info": "Hermann Ebbinghaus, 1885",
        "year": 1885,
        "tags": "遗忘曲线,间隔重复,记忆,艾宾浩斯,学习",
    },
    # ── 化学 ──
    {
        "name": "催化作用",
        "node_type": "phenomenon",
        "domain": "chemistry",
        "description": "催化剂降低反应活化能，加速化学反应但不被消耗。"
        "类比：注意力机制是信息处理的'催化剂'，降低模型提取关键信息的'能量门槛'。"
        "也类比于算法中的预处理步骤降低复杂度。",
        "summary": "降低反应门槛的加速器——不消耗自身却改变过程",
        "source_info": "Jöns Jacob Berzelius 提出催化概念, 1835",
        "year": 1835,
        "tags": "催化,活化能,加速,酶,反应速率",
    },
    {
        "name": "分子自组装",
        "node_type": "phenomenon",
        "domain": "chemistry",
        "description": "分子在特定条件下自发组织成有序结构（如脂质双分子层、DNA双螺旋）。"
        "不需要外部指令，仅靠局部相互作用产生全局秩序。"
        "类比：涌现行为、自组织临界性、分布式系统中的共识。",
        "summary": "无需指令，局部作用产生全局秩序——自下而上的组织",
        "source_info": "George Whitesides 等, 自组装化学综述",
        "year": None,
        "tags": "自组装,涌现,自组织,有序,分子",
    },
    # ── 生态学 ──
    {
        "name": "捕食者-猎物动力学（Lotka-Volterra）",
        "node_type": "phenomenon",
        "domain": "ecology",
        "description": "捕食者和猎物种群数量呈周期性振荡：猎物增多→捕食者增多→猎物减少→捕食者减少→循环。"
        "Lotka-Volterra方程描述这种动态平衡。"
        "类比：GAN的训练震荡、供需市场周期。",
        "summary": "猎物-捕食者的周期博弈——自然界的动态平衡",
        "source_info": "Alfred Lotka (1925); Vito Volterra (1926)",
        "year": 1925,
        "tags": "捕食者,猎物,振荡,动态平衡,种群",
    },
    {
        "name": "生态位分化与共存",
        "node_type": "principle",
        "domain": "ecology",
        "description": "竞争排斥原则：两个物种不能占据完全相同的生态位。"
        "物种通过分化（食物/栖息地/时间）实现共存。"
        "类比：多模型集成（ensemble）中各模型的多样性、"
        "多智能体系统中的角色分化。",
        "summary": "竞争迫使差异化——多样性是共存的基础",
        "source_info": "G.F. Gause 竞争排斥原则, 1934; G.E. Hutchinson 生态位理论",
        "year": 1934,
        "tags": "生态位,竞争排斥,分化,共存,多样性",
    },
    # ── 哲学 / 方法论 ──
    {
        "name": "奥卡姆剃刀",
        "node_type": "principle",
        "domain": "philosophy",
        "description": "如无必要，勿增实体。在多个等效解释中选择最简单的。"
        "直接对应机器学习中的正则化（L1/L2）、模型选择中的信息准则（AIC/BIC）、"
        "最小描述长度原则（MDL）。",
        "summary": "简约为上——简单模型优于复杂模型",
        "source_info": "William of Ockham, ~1320",
        "year": 1320,
        "tags": "奥卡姆,简约,正则化,模型选择,MDL",
    },
    {
        "name": "涌现与还原论",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "涌现：整体表现出部分所不具有的新性质（意识源于神经元、生命源于化学反应）。"
        "还原论：复杂现象可以用组成部分的性质解释。"
        "深度学习中特征层次的涌现是典型案例。",
        "summary": "整体大于部分之和——简单规则产生复杂行为",
        "source_info": "P.W. Anderson, 'More Is Different', 1972",
        "year": 1972,
        "tags": "涌现,还原论,复杂性,层次,自组织",
    },
    {
        "name": "类比推理",
        "node_type": "method",
        "domain": "philosophy",
        "description": "通过两个领域之间的结构相似性进行知识迁移。"
        "是人类创造力的核心机制：卢瑟福类比太阳系提出原子模型，"
        "达尔文类比人工选择提出自然选择。"
        "也是本项目（Knowledge Nexus）的核心方法论。",
        "summary": "发现不同事物的深层相似——创造力的源泉",
        "source_info": "Dedre Gentner, Structure-Mapping Theory, 1983",
        "year": 1983,
        "tags": "类比,迁移,结构映射,创造力,知识迁移",
    },
    # ── 社会学 / 复杂系统 ──
    {
        "name": "六度分隔与小世界网络",
        "node_type": "phenomenon",
        "domain": "sociology",
        "description": "任意两个陌生人之间平均只隔六个人。"
        "Watts-Strogatz小世界网络模型：少量随机长程连接使网络直径急剧缩小。"
        "解释了社交网络、神经网络、互联网的高效性。",
        "summary": "六步之内连接全世界——网络拓扑的普遍规律",
        "source_info": "Stanley Milgram 实验 (1967); Watts & Strogatz (1998)",
        "year": 1967,
        "tags": "六度分隔,小世界,社交网络,图论,连通性",
    },
    {
        "name": "马太效应（富者愈富）",
        "node_type": "phenomenon",
        "domain": "sociology",
        "description": "优势会自我强化：引用多的论文更容易被引用，粉丝多的账号获得更多曝光。"
        "对应网络科学中的优先连接（Barabási-Albert模型）和幂律分布。"
        "也类似于强化学习中高奖励路径的正反馈。",
        "summary": "富者愈富——优势自我放大的普遍规律",
        "source_info": "Robert Merton, 1968; Barabási-Albert 无标度网络, 1999",
        "year": 1968,
        "tags": "马太效应,幂律,优先连接,正反馈,无标度",
    },
    # ── 信息论 / 控制论 ──
    {
        "name": "信息瓶颈理论",
        "node_type": "theorem",
        "domain": "computer_science",
        "description": "Tishby提出：最优表示应该在保留关于目标信息的同时最大限度压缩输入信息。"
        "深度学习被解释为逐层执行信息瓶颈：浅层保留多信息，深层只保留与任务相关的。",
        "summary": "保留有用信息，丢弃冗余——最优表示的信息论基础",
        "source_info": "Naftali Tishby, 1999; 'Deep Learning and the Information Bottleneck Principle', 2015",
        "year": 1999,
        "tags": "信息瓶颈,Tishby,压缩,表示学习,互信息",
    },
    {
        "name": "控制论（Cybernetics）",
        "node_type": "concept",
        "domain": "engineering",
        "description": "维纳创立的跨学科理论：研究动物和机器中的控制和通信。"
        "核心思想：反馈、自我调节、信息处理在生物和机器中遵循相同原理。"
        "是人工智能、自动控制、认知科学的共同源头。",
        "summary": "生物与机器遵循相同的控制原理——AI的哲学起源",
        "source_info": "Norbert Wiener, 1948, 《Cybernetics》",
        "year": 1948,
        "tags": "控制论,维纳,反馈,信息,自我调节,AI起源",
    },
    # ── 物理 / 数学 补充 ──
    {
        "name": "混沌理论（蝴蝶效应）",
        "node_type": "phenomenon",
        "domain": "physics",
        "description": "确定性系统对初始条件极度敏感——微小扰动可导致截然不同的结果。"
        "蝴蝶效应：巴西的蝴蝶扇动翅膀可能引发德克萨斯的龙卷风。"
        "类比：神经网络训练中随机种子导致不同收敛结果、超参数敏感性。",
        "summary": "微小差异导致巨大分歧——确定性中的不可预测",
        "source_info": "Edward Lorenz, 1963; 'Deterministic Nonperiodic Flow'",
        "year": 1963,
        "tags": "混沌,蝴蝶效应,敏感依赖,洛伦兹,非线性",
    },
    {
        "name": "傅里叶变换",
        "node_type": "method",
        "domain": "mathematics",
        "description": "任何周期信号都可以分解为不同频率正弦波的叠加。"
        "应用无处不在：信号处理、图像压缩(JPEG)、语音识别、"
        "CNN中的频域分析、量子力学中的动量表示。",
        "summary": "将复杂信号分解为简单频率——信号处理的基石",
        "source_info": "Joseph Fourier, 1822, 《Théorie analytique de la chaleur》",
        "year": 1822,
        "tags": "傅里叶,频域,信号处理,FFT,频谱",
    },
    {
        "name": "蒙特卡洛方法",
        "node_type": "method",
        "domain": "mathematics",
        "description": "用随机抽样解决确定性数学问题。"
        "应用：积分估计、强化学习中的策略评估（蒙特卡洛树搜索→AlphaGo）、"
        "贝叶斯推理（MCMC）、物理模拟。",
        "summary": "用随机性解决确定性问题——从赌场到AlphaGo",
        "source_info": "Stanislaw Ulam & John von Neumann, 1946 (曼哈顿计划)",
        "year": 1946,
        "tags": "蒙特卡洛,随机抽样,MCMC,AlphaGo,模拟",
    },
    # ── 计算机补充 ──
    {
        "name": "强化学习",
        "node_type": "method",
        "domain": "computer_science",
        "description": "智能体通过与环境交互、获得奖励/惩罚来学习最优策略。"
        "核心概念：状态、动作、奖励、策略、价值函数。"
        "从 Q-learning 到 Deep RL (DQN, PPO, SAC)，是 AlphaGo 和 ChatGPT(RLHF) 的关键技术。",
        "summary": "试错中学习最优策略——从棋类到大模型对齐",
        "source_info": "Richard Sutton & Andrew Barto, 1998; DeepMind DQN (2013)",
        "year": 1998,
        "tags": "强化学习,RL,Q-learning,PPO,AlphaGo,RLHF",
    },
    {
        "name": "迁移学习",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将一个任务/领域学到的知识迁移到另一个任务/领域。"
        "预训练+微调范式（ImageNet预训练→下游任务、GPT预训练→RLHF）。"
        "类比人类：学会骑自行车有助于学骑摩托车。"
        "是本项目核心理念'一通百通'的计算机实现。",
        "summary": "知识跨任务复用——预训练+微调的范式",
        "source_info": "Pan & Yang, 'A Survey on Transfer Learning', 2010",
        "year": 2010,
        "tags": "迁移学习,预训练,微调,知识复用,domain adaptation",
    },
]

# ── 插入知识节点 ──
node_ids = {}
inserted = 0

# 先加载已有节点
for row in cur.execute("SELECT id, name FROM knowledge_nodes"):
    node_ids[row[1]] = row[0]

for n in NODES:
    if n["name"] in node_ids:
        print(f"  ⏭ 已存在: {n['name']}")
        continue

    nid = gen_id()
    cur.execute(
        "INSERT INTO knowledge_nodes (id, name, node_type, domain, description, summary, "
        "source_info, year, tags, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            nid,
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
    node_ids[n["name"]] = nid
    inserted += 1
    print(f"  ✅ [{n['node_type']}] {n['name']} ({n['domain']})")

print(f"\n📌 插入 {inserted} 个知识节点")

# ══════════════════════════════════════════════════════════════
#  跨领域关联关系（第二批）
# ══════════════════════════════════════════════════════════════

# 加载论文 ID
papers = {}
for row in cur.execute("SELECT id, key_contributions, title FROM papers"):
    papers[row[1] or row[2]] = row[0]

N = node_ids
P = papers

existing_rels = set()
for row in cur.execute("SELECT source_id, target_id FROM relations"):
    existing_rels.add((row[0], row[1]))

RELATIONS = [
    # ═══ 心理学 → 计算机 ═══
    (
        N.get("操作性条件反射（强化学习原型）"),
        N.get("强化学习"),
        "INSPIRES",
        "knowledge_node",
        "knowledge_node",
        "强化学习直接借鉴操作性条件反射：奖励→增加行为(正强化)，惩罚→减少行为",
    ),
    (
        N.get("巴甫洛夫条件反射"),
        N.get("强化学习"),
        "INSPIRES",
        "knowledge_node",
        "knowledge_node",
        "条件反射中的状态-奖励关联是强化学习中价值函数的心理学基础",
    ),
    (
        N.get("认知偏差与启发式"),
        N.get("蒙特卡洛方法"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "人类启发式=快速近似推理 ↔ 蒙特卡洛=随机近似计算，都用简化策略处理复杂问题",
    ),
    (
        N.get("遗忘曲线与间隔重复"),
        N.get("人工神经网络"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "记忆衰减↔权重衰减(weight decay)，间隔重复↔学习率调度(learning rate schedule)",
    ),
    # ═══ 化学 → 计算机 ═══
    (
        N.get("催化作用"),
        N.get("注意力机制"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "催化剂降低反应能垒 ↔ 注意力机制降低信息提取难度，都是'效率放大器'",
    ),
    (
        N.get("分子自组装"),
        N.get("涌现与还原论"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "分子自组装是涌现现象的化学实例：局部分子相互作用→全局有序结构",
    ),
    # ═══ 生态学 → 计算机 ═══
    (
        N.get("捕食者-猎物动力学（Lotka-Volterra）"),
        N.get("纳什均衡"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "捕食者-猎物振荡 ↔ GAN 生成器-判别器博弈，都是两方对抗的动态平衡",
    ),
    (
        N.get("捕食者-猎物动力学（Lotka-Volterra）"),
        P.get("GAN"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "paper",
        "GAN训练中G/D的交替优化类似捕食者-猎物周期振荡",
    ),
    (
        N.get("生态位分化与共存"),
        N.get("迁移学习"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "物种生态位分化 ↔ 多模型ensemble的多样性/迁移学习的域差异",
    ),
    # ═══ 哲学 → 计算机 ═══
    (
        N.get("奥卡姆剃刀"),
        N.get("贝叶斯定理"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "奥卡姆剃刀的概率版本：贝叶斯模型选择中简单模型有更高的先验概率",
    ),
    (
        N.get("奥卡姆剃刀"),
        N.get("信息瓶颈理论"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "信息瓶颈压缩表示=奥卡姆剃刀的信息论实现：保留必要信息，丢弃冗余",
    ),
    (
        N.get("涌现与还原论"),
        N.get("人工神经网络"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "深度学习中的特征层次是涌现的典型案例：像素→边缘→纹理→物体",
    ),
    (
        N.get("类比推理"),
        N.get("迁移学习"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "人类类比推理 ↔ 机器迁移学习，都是通过结构相似性进行知识迁移",
    ),
    # ═══ 社会学 → 计算机 ═══
    (
        N.get("六度分隔与小世界网络"),
        N.get("图论与网络科学"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "六度分隔是图论小世界性质的社会学实证：高聚类+短路径",
    ),
    (
        N.get("马太效应（富者愈富）"),
        N.get("蚁群觅食行为"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "都是正反馈机制：信息素越多→更多蚂蚁→更多信息素 ↔ 优势越大→更多资源→更大优势",
    ),
    (
        N.get("六度分隔与小世界网络"),
        P.get("DGCNN"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "图神经网络在小世界拓扑图上的信息传播受六度分隔启发",
    ),
    # ═══ 物理/数学补充 ═══
    (
        N.get("混沌理论（蝴蝶效应）"),
        N.get("人工神经网络"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "神经网络训练对初始化/超参数敏感，类似混沌系统对初始条件的敏感依赖",
    ),
    (
        N.get("傅里叶变换"),
        N.get("注意力机制"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "傅里叶变换将信号分解到频域 ↔ 注意力机制将信息分解到不同重要性级别",
    ),
    (
        N.get("蒙特卡洛方法"),
        N.get("强化学习"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "蒙特卡洛树搜索(MCTS)是AlphaGo的核心算法，蒙特卡洛策略评估是RL基础方法",
    ),
    (
        N.get("蒙特卡洛方法"),
        P.get("AlphaFold"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "AlphaFold的蛋白质结构搜索结合了蒙特卡洛采样思想",
    ),
    # ═══ 控制论跨域 ═══
    (
        N.get("控制论（Cybernetics）"),
        N.get("反馈控制（负反馈）"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "控制论是反馈控制的理论基础，维纳将反馈概念统一到生物和机器",
    ),
    (
        N.get("控制论（Cybernetics）"),
        N.get("人工神经网络"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "控制论是人工智能的三大起源之一（另两个：符号主义、连接主义）",
    ),
    (
        N.get("控制论（Cybernetics）"),
        N.get("强化学习"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "强化学习中的目标-反馈-调整循环是控制论核心思想的直接体现",
    ),
    # ═══ 信息瓶颈跨域 ═══
    (
        N.get("信息瓶颈理论"),
        N.get("信息熵与交叉熵"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "信息瓶颈理论建立在互信息（信息熵的推广）之上",
    ),
    # ═══ 迁移学习 → 论文 ═══
    (
        N.get("迁移学习"),
        P.get("ViT"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "ViT 在大规模数据预训练→下游任务微调是迁移学习的典型应用",
    ),
    (
        N.get("迁移学习"),
        P.get("Swin Transformer"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "Swin Transformer 的 ImageNet 预训练模型广泛用于检测/分割的迁移学习",
    ),
    # ═══ 强化学习 → 论文 ═══
    (
        N.get("强化学习"),
        P.get("AlphaFold"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "AlphaFold 2 结合了强化学习思想进行蛋白质结构搜索",
    ),
    # ═══ 混沌 → 退火 ═══
    (
        N.get("混沌理论（蝴蝶效应）"),
        N.get("模拟退火算法"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "模拟退火的高温阶段具有混沌特征（随机跳转），低温时趋于确定性收敛",
    ),
]

# ── 插入关系 ──
rel_added = 0
for item in RELATIONS:
    src, tgt, rtype, stype, ttype, desc = item
    if not src or not tgt:
        print(f"  ⚠ 跳过（ID缺失）: {desc[:40]}")
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

# 按领域统计
print(f"\n{'=' * 50}")
print(f"📊 知识节点: {total_nodes} | 论文: {total_papers} | 关系: {total_rels}")
print(f"📌 本次新增: {inserted} 个节点, {rel_added} 条关系")
print("\n按领域分布:")
for row in cur.execute(
    "SELECT domain, COUNT(*) FROM knowledge_nodes GROUP BY domain ORDER BY COUNT(*) DESC"
):
    print(f"  {row[0]}: {row[1]}")
conn.close()
