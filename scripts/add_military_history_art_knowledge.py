"""
添加军事学、历史学、艺术领域知识节点
——跨领域启发：兵法与算法、历史规律与模型、艺术与AI创造

包含：
- 军事学：孙子兵法核心思想、博弈战略、战争迷雾
- 历史学：历史周期律、文明演化、技术革命
- 艺术：创造力理论、音乐和声学、黄金比例、生成式艺术
- 跨域关联
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "../backend/knowledge_nexus.db"

def get_id():
    return uuid.uuid4().hex[:12]

now = datetime.utcnow().isoformat()

# ============================================================
# 1. 知识节点
# ============================================================
nodes = [
    # ===================== 军事学 (military_science) =====================
    {
        "name": "孙子兵法 (The Art of War)",
        "node_type": "concept",
        "domain": "military_science",
        "description": "中国古代最伟大的军事著作（约公元前500年）。核心思想：'知彼知己，百战不殆'、'不战而屈人之兵'、'兵者，诡道也'。是战略思维、博弈论和对抗决策的经典源泉。",
        "summary": "古代战略思维的集大成之作，跨域影响深远",
        "tags": "战略,博弈,决策,孙武",
        "year": -500,
    },
    {
        "name": "知彼知己 (Know Your Enemy and Yourself)",
        "node_type": "principle",
        "domain": "military_science",
        "description": "'知彼知己，百战不殆；不知彼而知己，一胜一负；不知彼不知己，每战必殆。'——信息是决策的基础，完整信息下可做最优决策。",
        "summary": "信息优势决定决策质量",
        "tags": "信息,决策,博弈,情报",
        "year": -500,
    },
    {
        "name": "兵者诡道 (War is Deception)",
        "node_type": "principle",
        "domain": "military_science",
        "description": "'能而示之不能，用而示之不用，近而示之远，远而示之近。'——通过误导对手的信息来获取优势。欺骗与反欺骗是对抗博弈的核心。",
        "summary": "通过信息操纵获取对抗优势",
        "tags": "对抗,博弈,信息不对称,迷惑",
        "year": -500,
    },
    {
        "name": "不战而屈人之兵 (Win Without Fighting)",
        "node_type": "principle",
        "domain": "military_science",
        "description": "'百战百胜，非善之善者也；不战而屈人之兵，善之善者也。'——最高战略不是直接对抗，而是通过态势塑造使对手放弃抵抗。",
        "summary": "最优策略是使对抗不必发生",
        "tags": "战略,博弈,威慑,最优策略",
        "year": -500,
    },
    {
        "name": "战争迷雾 (Fog of War)",
        "node_type": "concept",
        "domain": "military_science",
        "description": "克劳塞维茨在《战争论》中提出：战争中信息不完整、不确定、甚至矛盾，决策者必须在'迷雾'中做出判断。这是不完全信息博弈和POMDP的现实原型。",
        "summary": "不完全信息下的决策——真实世界的不确定性",
        "tags": "克劳塞维茨,不确定性,信息不完全,决策",
        "year": 1832,
    },
    {
        "name": "OODA 循环 (Observe-Orient-Decide-Act)",
        "node_type": "method",
        "domain": "military_science",
        "description": "博伊德提出的军事决策循环：观察(Observe)→判断(Orient)→决策(Decide)→行动(Act)。比对手更快完成OODA循环就能获得主动权。是敏捷开发和实时AI系统的思想源头。",
        "summary": "快速决策循环——速度决定胜负",
        "tags": "决策循环,敏捷,实时系统,博伊德",
        "year": 1976,
    },
    {
        "name": "兰切斯特方程 (Lanchester's Laws)",
        "node_type": "theorem",
        "domain": "military_science",
        "description": "用数学方程描述战斗中兵力消耗：线性律(一对一)和平方律(集中火力)。平方律揭示：集中兵力的优势是兵力比的平方——这解释了为什么集中优势兵力是基本战术原则。",
        "summary": "战斗力随兵力集中度平方增长",
        "tags": "数学建模,微分方程,兵力,战术",
        "year": 1916,
    },
    {
        "name": "博弈对抗与零和博弈 (Adversarial Game Theory)",
        "node_type": "concept",
        "domain": "military_science",
        "description": "军事对抗本质上是零和博弈——一方的得利等于另一方的损失。极小化极大策略(minimax)、混合策略纳什均衡等博弈论工具直接源于军事对抗分析。",
        "summary": "对抗场景中的最优策略选择",
        "tags": "零和博弈,minimax,纳什均衡,对抗",
        "year": 1944,
    },
    {
        "name": "集中优势兵力 (Principle of Concentration)",
        "node_type": "principle",
        "domain": "military_science",
        "description": "拿破仑核心战术原则：在决定性时间和地点集中最大兵力。分散的力量容易被各个击破，集中才能形成压倒性优势。与计算中的资源调度和负载集中策略相通。",
        "summary": "在关键点集中资源以获取决定性优势",
        "tags": "拿破仑,战术,资源分配,专注",
        "year": 1805,
    },

    # ===================== 历史学 (history) =====================
    {
        "name": "历史周期律 (Dynastic Cycle)",
        "node_type": "phenomenon",
        "domain": "history",
        "description": "中国历史中反复出现的王朝兴衰周期：建立→繁荣→腐败→衰亡→新朝建立。黄炎培与毛泽东的'窑洞对'讨论如何跳出这个周期。类似于系统的生命周期和技术债务累积。",
        "summary": "王朝兴衰的循环模式——系统的生命周期",
        "tags": "周期,兴衰,制度,系统退化",
        "year": -200,
    },
    {
        "name": "技术革命与范式转换 (Technological Revolutions)",
        "node_type": "phenomenon",
        "domain": "history",
        "description": "人类历史的重大转折：农业革命→工业革命→信息革命→AI革命。每次技术革命都重塑生产方式、社会结构和思维模式。库恩的范式转换理论：新范式取代旧范式。",
        "summary": "技术飞跃驱动文明跃迁",
        "tags": "革命,范式,库恩,技术变革",
        "year": 1962,
    },
    {
        "name": "修昔底德陷阱 (Thucydides Trap)",
        "node_type": "concept",
        "domain": "history",
        "description": "新兴大国崛起必然威胁现有霸权，往往导致冲突（源自雅典vs斯巴达）。艾利森研究发现过去500年16次权力转移中12次导致战争。是博弈论中'承诺问题'的历史体现。",
        "summary": "权力转移中的结构性冲突倾向",
        "tags": "国际关系,博弈,冲突,权力转移",
        "year": -431,
    },
    {
        "name": "黑天鹅事件 (Black Swan Events)",
        "node_type": "concept",
        "domain": "history",
        "description": "塔勒布提出：极小概率但影响极大的事件主导着历史进程（如世界大战、互联网发明、COVID）。传统概率模型低估了这类事件。与厚尾分布和鲁棒性设计密切相关。",
        "summary": "低概率高影响事件主导历史走向",
        "tags": "塔勒布,不确定性,风险,厚尾分布",
        "year": 2007,
    },
    {
        "name": "以史为鉴 (Learning from History)",
        "node_type": "principle",
        "domain": "history",
        "description": "'以铜为鉴，可以正衣冠；以史为鉴，可以知兴替。'——历史经验是决策的重要参考。但黑格尔说'人类从历史中学到的唯一教训就是人类没有从历史中学到任何教训'。",
        "summary": "从历史模式中提取知识指导决策",
        "tags": "经验学习,模式识别,决策,知识迁移",
        "year": -400,
    },
    {
        "name": "文明冲突论 (Clash of Civilizations)",
        "node_type": "concept",
        "domain": "history",
        "description": "亨廷顿1996年提出：冷战后世界冲突的主要源泉不再是意识形态或经济，而是文明之间的文化差异。不同文明有不同的世界观、价值观和问题解决方式。",
        "summary": "文化/价值观差异是深层冲突的根源",
        "tags": "亨廷顿,文明,文化,冲突",
        "year": 1996,
    },
    {
        "name": "长尾效应 (The Long Tail)",
        "node_type": "phenomenon",
        "domain": "history",
        "description": "克里斯·安德森观察：互联网时代，冷门商品的累计销量可以超过热门商品。少数头部+大量长尾的分布模式广泛存在于语言(齐普夫定律)、社交网络、知识分布等领域。",
        "summary": "大量小众的累计影响可超过少数大众",
        "tags": "幂律,分布,互联网,齐普夫",
        "year": 2004,
    },

    # ===================== 艺术 (art) =====================
    {
        "name": "黄金比例 (Golden Ratio)",
        "node_type": "concept",
        "domain": "art",
        "description": "φ ≈ 1.618，从古希腊帕特农神庙到达·芬奇《维特鲁威人》，被认为是最和谐的比例。出现在斐波那契数列、自然界的螺旋（向日葵、贝壳）和现代设计中。数学之美与艺术之美的交汇。",
        "summary": "自然与艺术中反复出现的和谐比例",
        "tags": "斐波那契,和谐,设计,数学之美",
        "year": -300,
    },
    {
        "name": "和声学 (Harmony / Music Theory)",
        "node_type": "concept",
        "domain": "art",
        "description": "音乐中音程和弦的规律：协和与不协和、张力与解决、调性与变调。毕达哥拉斯发现音程对应简单整数比(2:1八度, 3:2五度)。音乐结构与数学、物理波动理论深度关联。",
        "summary": "音乐中的数学规律——频率比与和谐感",
        "tags": "音乐,数学,波动,毕达哥拉斯",
        "year": -500,
    },
    {
        "name": "创造力与组合创新 (Combinatorial Creativity)",
        "node_type": "concept",
        "domain": "art",
        "description": "Arthur Koestler提出'双联想'理论：创造力是将两个原本不相关的思维框架碰撞产生新想法。乔布斯说'创造力就是把事物联系起来'。这与知识图谱的跨域关联发现理念完全一致。",
        "summary": "创造力的本质是跨领域的知识组合与碰撞",
        "tags": "创造力,联想,创新,跨域",
        "year": 1964,
    },
    {
        "name": "生成式艺术 (Generative Art)",
        "node_type": "concept",
        "domain": "art",
        "description": "使用算法、规则或AI系统自主生成艺术作品。从1960年代的计算机艺术先驱，到今天的DALL-E、Midjourney、Stable Diffusion。核心问题：AI能否真正'创造'？还是仅在重组已有模式？",
        "summary": "算法与AI驱动的艺术创作——创造力的新形态",
        "tags": "AI艺术,扩散模型,创造力,算法",
        "year": 1965,
    },
    {
        "name": "极简主义 (Minimalism)",
        "node_type": "principle",
        "domain": "art",
        "description": "20世纪艺术运动：用最少的元素传达最大的表现力。'Less is more'(密斯·凡德罗)。从建筑到设计到音乐，极简主义追求去除一切非本质的元素，与奥卡姆剃刀和模型简约性相通。",
        "summary": "去除冗余，以最少元素达到最大表达",
        "tags": "设计,简约,奥卡姆剃刀,本质",
        "year": 1960,
    },
    {
        "name": "透视法 (Perspective / Projection)",
        "node_type": "method",
        "domain": "art",
        "description": "文艺复兴时期发展的绘画技法：将三维场景投影到二维平面。布鲁内莱斯基和阿尔贝蒂建立了数学化的透视理论。这是计算机图形学中投影变换、3D渲染的直接历史源头。",
        "summary": "将高维信息映射到低维空间的艺术方法",
        "tags": "投影,降维,文艺复兴,计算机图形学",
        "year": 1435,
    },
    {
        "name": "即兴创作 (Improvisation)",
        "node_type": "method",
        "domain": "art",
        "description": "在没有预设剧本的情况下实时创作（爵士乐、即兴戏剧）。需要深厚的基本功(已有知识)作为即兴发挥的基础。与LLM的自回归生成类似——基于已有上下文实时生成下一个token。",
        "summary": "基于深厚积累的实时创造——无剧本的生成过程",
        "tags": "爵士乐,实时生成,自回归,创造力",
        "year": 1900,
    },
]

# ============================================================
# 2. 跨领域关系
# ============================================================
relations_def = [
    # === 军事 ↔ 计算机/AI ===
    ("知彼知己 (Know Your Enemy and Yourself)", "强化学习", "ANALOGOUS_TO",
     "'知彼'需要环境建模(world model)，'知己'需要策略评估(policy evaluation)。完全'知彼知己'对应完全信息博弈中的最优策略。强化学习就是在不断'知彼知己'的过程中学习。"),
    
    ("兵者诡道 (War is Deception)", "生成对抗网络 (GAN)", "ANALOGOUS_TO",
     "兵者诡道——通过欺骗获取优势。GAN中生成器试图'欺骗'判别器，制造以假乱真的数据。对抗训练本质上就是'诡道'的数学化——攻防双方在欺骗与识别中共同进化。"),
    
    ("兵者诡道 (War is Deception)", "对比学习 (Contrastive Learning)", "RELATED_TO",
     "对抗中需要识别真假信息。对比学习训练模型区分'真样本'和'假样本'，正是反欺骗能力的技术体现——让模型学会在噪声和干扰中辨别真伪。"),
    
    ("战争迷雾 (Fog of War)", "检索增强生成 (RAG)", "ANALOGOUS_TO",
     "战争迷雾——决策者面对不完整信息。RAG承认LLM内部知识不完整，通过主动检索外部信息来'拨开迷雾'，获取做出更好决策所需的信息。"),
    
    ("OODA 循环 (Observe-Orient-Decide-Act)", "ReAct 框架", "ANALOGOUS_TO",
     "OODA(观察→判断→决策→行动)与ReAct(Reasoning→Acting→Observing)高度同构：都是感知-思考-行动的闭环决策循环。ReAct就是AI Agent版本的OODA循环。"),
    
    ("OODA 循环 (Observe-Orient-Decide-Act)", "AI Agent (智能体)", "INSPIRES",
     "OODA循环是Agent架构的思想源头：Agent的感知(Observe)→推理(Orient/Decide)→工具调用(Act)→观察结果(Observe)循环正是OODA在AI中的实现。"),
    
    ("不战而屈人之兵 (Win Without Fighting)", "知识蒸馏 (Knowledge Distillation)", "ANALOGOUS_TO",
     "'不战而胜'——用最小代价达到目标。知识蒸馏让小模型直接'继承'大模型的能力，不需要重新训练(不战)就获得了强大性能(屈人之兵)。"),
    
    ("集中优势兵力 (Principle of Concentration)", "混合专家模型 (MoE)", "ANALOGOUS_TO",
     "集中优势兵力在关键战场。MoE的核心思想类似：不是所有专家同时工作，而是根据输入(战场)激活最相关的专家(精锐部队)，将计算资源集中在最需要的地方。"),
    
    ("博弈对抗与零和博弈 (Adversarial Game Theory)", "纳什均衡", "BUILDS_ON",
     "军事对抗博弈直接建立在纳什均衡理论上：在零和博弈中，纳什均衡就是minimax策略，双方都选择使自己最坏情况最好的策略。"),
    
    ("博弈对抗与零和博弈 (Adversarial Game Theory)", "RLHF (人类反馈强化学习)", "RELATED_TO",
     "对抗博弈思维在RLHF中体现为：用red-teaming(红队对抗)测试模型的安全边界，在攻击与防御的博弈中提升模型鲁棒性。"),
    
    ("兰切斯特方程 (Lanchester's Laws)", "Scaling Law (规模定律)", "ANALOGOUS_TO",
     "兰切斯特平方律：战斗力∝兵力²。LLM的Scaling Law：模型能力按参数量的幂律增长。两者都揭示了'规模效应'的数学本质——量变引发质变的精确描述。"),
    
    # === 军事内部关系 ===
    ("孙子兵法 (The Art of War)", "知彼知己 (Know Your Enemy and Yourself)", "ENABLES",
     "'知彼知己'是孙子兵法的核心命题之一。"),
    
    ("孙子兵法 (The Art of War)", "兵者诡道 (War is Deception)", "ENABLES",
     "'兵者，诡道也'出自《孙子兵法·始计篇》。"),
    
    ("孙子兵法 (The Art of War)", "不战而屈人之兵 (Win Without Fighting)", "ENABLES",
     "'不战而屈人之兵，善之善者也'出自《孙子兵法·谋攻篇》。"),
    
    # === 历史 ↔ 计算机/AI ===
    ("历史周期律 (Dynastic Cycle)", "梯度下降与优化器", "ANALOGOUS_TO",
     "历史周期律的兴→衰→新生循环类似优化过程中的学习率调度：warm-up(兴起)→训练(繁荣)→学习率衰减(衰落)→重新warm-up(新周期)。Cosine annealing就是一种'周期律'。"),
    
    ("技术革命与范式转换 (Technological Revolutions)", "Scaling Law (规模定律)", "RELATED_TO",
     "每次技术革命都是一个范式转换——从蒸汽机到电力到计算机。LLM的涌现能力也是一种范式转换：当规模突破阈值，系统能力发生质变，类似技术革命的突变点。"),
    
    ("技术革命与范式转换 (Technological Revolutions)", "大语言模型 (LLM)", "RELATED_TO",
     "LLM/AI被广泛认为是下一次技术革命的核心：正如蒸汽机定义了工业革命，LLM可能定义AI革命。"),
    
    ("黑天鹅事件 (Black Swan Events)", "混沌理论（蝴蝶效应）", "ANALOGOUS_TO",
     "黑天鹅(低概率高影响)与蝴蝶效应(微小扰动导致巨大变化)都描述系统的极端敏感性。两者都挑战了线性预测和正态分布假设。"),
    
    ("黑天鹅事件 (Black Swan Events)", "涌现能力 (Emergent Abilities)", "ANALOGOUS_TO",
     "黑天鹅事件出人意料地改变历史走向。LLM的涌现能力同样是'黑天鹅式'的——没有人预测到某个规模的模型会突然获得推理、代码编写等能力。"),
    
    ("以史为鉴 (Learning from History)", "预训练-微调范式", "ANALOGOUS_TO",
     "'以史为鉴'——从海量历史经验中学习模式以指导未来决策。预训练就是模型的'读史'过程：在海量文本中学习人类知识的模式，微调则是将这些经验应用于具体场景。"),
    
    ("以史为鉴 (Learning from History)", "迁移学习", "ANALOGOUS_TO",
     "以史为鉴的核心是知识迁移：从一个时代/场景学到的经验应用到新的时代/场景。这正是迁移学习的本质——将源域的知识迁移到目标域。"),
    
    ("长尾效应 (The Long Tail)", "注意力机制", "RELATED_TO",
     "长尾分布中大量低频元素的重要性。Attention机制允许模型关注到输入中的'长尾'信息——那些不在位置前端但语义重要的token。"),
    
    # === 修昔底德陷阱 ↔ 博弈 ===
    ("修昔底德陷阱 (Thucydides Trap)", "博弈对抗与零和博弈 (Adversarial Game Theory)", "RELATED_TO",
     "修昔底德陷阱本质上是博弈论中的'承诺问题'——新兴大国的崛起承诺不可置信，导致现有霸权选择先发制人。"),
    
    # === 艺术 ↔ 计算机/AI ===
    ("生成式艺术 (Generative Art)", "扩散模型 (Diffusion Models)", "BUILDS_ON",
     "扩散模型(DALL-E, Stable Diffusion, Midjourney)是当前生成式艺术最强大的技术基础。从随机噪声中'去噪'出艺术作品，AI成为了艺术创作的新工具。"),
    
    ("生成式艺术 (Generative Art)", "生成对抗网络 (GAN)", "BUILDS_ON",
     "GAN开启了AI艺术的新纪元——StyleGAN等模型能生成逼真的人脸、艺术作品，模糊了'创作'与'生成'的边界。"),
    
    ("创造力与组合创新 (Combinatorial Creativity)", "知识图谱 (Knowledge Graph)", "ANALOGOUS_TO",
     "创造力 = 跨域联想。知识图谱将不同领域的知识节点连接起来，为发现'意想不到的关联'提供结构化基础——Knowledge Nexus项目本身就是组合创新理论的实践。"),
    
    ("创造力与组合创新 (Combinatorial Creativity)", "检索增强生成 (RAG)", "RELATED_TO",
     "组合创新需要广泛的知识检索和碰撞。RAG通过检索多源知识再生成新内容，提供了一种'机械化的组合创新'——从不同来源检索知识片段，由AI重新组合。"),
    
    ("极简主义 (Minimalism)", "奥卡姆剃刀", "ANALOGOUS_TO",
     "极简主义(Less is more)与奥卡姆剃刀(如无必要，勿增实体)是同一理念在不同领域的表达：在艺术中去除冗余元素，在科学中去除冗余假设，追求最简约的解释/表达。"),
    
    ("极简主义 (Minimalism)", "量化与模型压缩", "ANALOGOUS_TO",
     "极简主义去除一切非本质元素。模型压缩/剪枝也是去除模型中'非本质'的参数，在保持核心能力的前提下追求最小化。"),
    
    ("透视法 (Perspective / Projection)", "卷积神经网络 (CNN)", "ANALOGOUS_TO",
     "透视法将3D世界映射到2D平面——这是一种投影/降维。CNN同样通过卷积和池化将高维图像特征逐层降维提取，文艺复兴的投影思想在计算机视觉中得到了技术延续。"),
    
    ("透视法 (Perspective / Projection)", "变分自编码器 (VAE)", "ANALOGOUS_TO",
     "透视法是高维到低维的有损投影。VAE将数据编码到低维潜在空间再解码重建——编码过程就是一种学到的'透视法'，找到数据最本质的低维表示。"),
    
    ("即兴创作 (Improvisation)", "自回归生成模型", "ANALOGOUS_TO",
     "即兴创作基于已有旋律/和声实时生成下一个音符。自回归模型同样基于已生成的上下文逐步预测下一个token——两者都是'基于已有、创造未来'的序列生成过程。"),
    
    ("即兴创作 (Improvisation)", "上下文学习 (In-Context Learning)", "ANALOGOUS_TO",
     "爵士乐手根据当前演奏的上下文(调性、节奏、其他乐手的演奏)即兴发挥。LLM的In-Context Learning同样根据给定的上下文(examples)实时调整输出策略，无需重新训练。"),
    
    ("和声学 (Harmony / Music Theory)", "傅里叶变换", "RELATED_TO",
     "和声学的数学基础是频率分析。傅里叶变换将复杂声音分解为单一频率的叠加——和弦就是特定频率组合的傅里叶合成。音乐之美有精确的数学描述。"),
    
    ("黄金比例 (Golden Ratio)", "梯度下降法", "RELATED_TO",
     "黄金比例(φ=1.618)出现在斐波那契数列中，而黄金分割搜索法是一维优化中的经典方法——利用φ的数学性质在搜索区间中高效定位最优点。"),
    
    # === 艺术 ↔ 哲学 ===
    ("极简主义 (Minimalism)", "留白 (Negative Space / Ma)", "ANALOGOUS_TO",
     "极简主义的'Less is more'与东方留白美学'计白当黑'高度相通——两者都认为空白/缺失不是不足而是力量，以最少元素传达最大意义。"),
    
    ("创造力与组合创新 (Combinatorial Creativity)", "类比推理", "BUILDS_ON",
     "组合创新的核心能力就是类比推理——从一个领域的模式看到另一个领域的相似结构。类比推理是创造力的认知基础。"),
    
    # === 军事 ↔ 哲学 ===
    ("孙子兵法 (The Art of War)", "道 (Tao / The Way)", "RELATED_TO",
     "孙子兵法深受道家思想影响：'道者，令民与上同意也'——以道治军。兵法中'以柔克刚'、'以静制动'等策略直接源于道家哲学。"),
    
    ("不战而屈人之兵 (Win Without Fighting)", "无为 (Wu Wei / Non-Action)", "ANALOGOUS_TO",
     "'不战而屈人之兵'是军事领域的'无为'——通过不直接交战(无为)达到最大战略目标(无不为)。两者都强调最高层次的效能不需要暴力/强制手段。"),
    
    # === 历史 ↔ 哲学 ===
    ("历史周期律 (Dynastic Cycle)", "物极必反 (Reversal at the Extreme)", "ANALOGOUS_TO",
     "历史周期律是物极必反在宏观历史中的体现：繁荣到极点必然走向衰落，衰落到极点必然孕育新生。"),
    
    ("技术革命与范式转换 (Technological Revolutions)", "辩证法 (Dialectics)", "ANALOGOUS_TO",
     "每次技术革命都是辩证法的体现：旧范式(正题)→危机与挑战(反题)→新技术范式(合题)。螺旋式上升，每一次革命都在更高层次重建。"),
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 插入知识节点
    node_name_to_id = {}
    inserted_nodes = 0
    skipped_nodes = 0
    
    for node in nodes:
        cursor.execute("SELECT id FROM knowledge_nodes WHERE name = ?", (node["name"],))
        existing = cursor.fetchone()
        if existing:
            node_name_to_id[node["name"]] = existing[0]
            skipped_nodes += 1
            print(f"  ⏩ 已存在: {node['name']}")
            continue
        
        nid = get_id()
        node_name_to_id[node["name"]] = nid
        cursor.execute("""
            INSERT INTO knowledge_nodes 
            (id, name, node_type, domain, description, summary, source_info, year, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nid, node["name"], node["node_type"], node["domain"],
            node["description"], node["summary"], None, node.get("year"),
            node.get("tags"), now, now
        ))
        inserted_nodes += 1
        print(f"  ✅ 新增节点: {node['name']} [{node['node_type']}|{node['domain']}]")
    
    print(f"\n📊 节点: 新增 {inserted_nodes}, 跳过 {skipped_nodes}")
    
    # 2. 构建全库名称→ID映射
    cursor.execute("SELECT id, name FROM knowledge_nodes")
    for row in cursor.fetchall():
        node_name_to_id[row[1]] = row[0]
    
    # 3. 插入关系
    inserted_rels = 0
    skipped_rels = 0
    failed_rels = 0
    
    for src_name, tgt_name, rel_type, desc in relations_def:
        src_id = node_name_to_id.get(src_name)
        tgt_id = node_name_to_id.get(tgt_name)
        
        if not src_id or not tgt_id:
            failed_rels += 1
            missing = []
            if not src_id:
                missing.append(f"源'{src_name}'")
            if not tgt_id:
                missing.append(f"目标'{tgt_name}'")
            print(f"  ❌ 找不到节点: {', '.join(missing)}")
            continue
        
        cursor.execute("""
            SELECT id FROM relations 
            WHERE source_id = ? AND target_id = ? AND relation_type = ?
        """, (src_id, tgt_id, rel_type))
        if cursor.fetchone():
            skipped_rels += 1
            print(f"  ⏩ 关系已存在: {src_name} --{rel_type}--> {tgt_name}")
            continue
        
        rid = get_id()
        cursor.execute("""
            INSERT INTO relations 
            (id, source_id, target_id, relation_type, source_type, target_type, 
             description, confidence, ai_generated, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rid, src_id, tgt_id, rel_type,
            "knowledge_node", "knowledge_node",
            desc, 1.0, False, "confirmed", now
        ))
        inserted_rels += 1
        print(f"  ✅ {src_name} --{rel_type}--> {tgt_name}")
    
    conn.commit()
    
    # 统计
    cursor.execute("SELECT COUNT(*) FROM knowledge_nodes")
    total_nodes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM relations")
    total_rels = cursor.fetchone()[0]
    cursor.execute("SELECT DISTINCT domain FROM knowledge_nodes")
    domains = [r[0] for r in cursor.fetchall()]
    
    print(f"\n📊 关系: 新增 {inserted_rels}, 跳过 {skipped_rels}, 失败 {failed_rels}")
    print(f"\n🎉 数据库总计: {total_nodes} 节点, {total_rels} 关系")
    print(f"📌 所有领域: {', '.join(sorted(domains))}")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("⚔️  添加军事学·历史·艺术知识节点 — 跨文理域")
    print("=" * 60)
    main()
