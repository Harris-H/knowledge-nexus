"""
添加哲学、道家及人文学科知识节点
——文理交叉，产生新思考

包含：
- 中国哲学：道家、儒家、易经、阴阳五行
- 西方哲学：辩证法、现象学、存在主义、实用主义、系统论
- 人文-理工跨域关联
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "../backend/knowledge_nexus.db"


def get_id():
    return uuid.uuid4().hex[:12]


now = datetime.utcnow().isoformat()

# ============================================================
# 1. 知识节点 — 哲学与人文
# ============================================================
nodes = [
    # ---- 道家哲学 ----
    {
        "name": "道 (Tao / The Way)",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "道家核心概念。道是宇宙万物的本源与运行法则，'道生一，一生二，二生三，三生万物'。道不可名状，是超越语言的终极实在。",
        "summary": "万物本源，宇宙运行的根本法则",
        "tags": "道家,老子,本体论,宇宙论",
        "year": -500,
    },
    {
        "name": "无为 (Wu Wei / Non-Action)",
        "node_type": "principle",
        "domain": "philosophy",
        "description": "道家核心原则：不妄为、不强为，顺应自然规律而行。非不作为，而是不违背事物本性的行为方式。'无为而无不为'——通过不干预实现最大效果。",
        "summary": "顺应自然，不强行干预却能达到最优效果",
        "tags": "道家,老子,行为哲学,自组织",
        "year": -500,
    },
    {
        "name": "阴阳 (Yin-Yang)",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "中国古代辩证思想：万事万物都包含对立统一的两面——阴与阳。二者相互依存、相互转化、动态平衡。'孤阴不生，独阳不长'。",
        "summary": "对立统一、动态平衡的辩证哲学",
        "tags": "道家,辩证法,二元论,平衡",
        "year": -700,
    },
    {
        "name": "道法自然 (Tao Follows Nature)",
        "node_type": "principle",
        "domain": "philosophy",
        "description": "道家思想：'人法地，地法天，天法道，道法自然'。最高法则是遵循自然。自然界的运行规律是一切方法论的源泉。",
        "summary": "从自然中学习法则，仿生思想的哲学根基",
        "tags": "道家,仿生,自然法则,方法论",
        "year": -500,
    },
    {
        "name": "物极必反 (Reversal at the Extreme)",
        "node_type": "principle",
        "domain": "philosophy",
        "description": "道家辩证观：事物发展到极端必然走向反面。'反者道之动'——运动和变化是道的根本特征，事物在对立面之间循环往复。",
        "summary": "极端状态必然反转，系统自我调节的哲学表达",
        "tags": "道家,辩证法,非线性,相变",
        "year": -500,
    },
    # ---- 儒家哲学 ----
    {
        "name": "格物致知 (Investigation of Things)",
        "node_type": "method",
        "domain": "philosophy",
        "description": "儒家认识论方法：通过研究事物的原理来获得知识。'致知在格物，物格而后知至'。这是中国最早的系统性经验主义认识方法。",
        "summary": "通过实践探究事物本质来获取知识",
        "tags": "儒家,认识论,经验主义,科学方法",
        "year": -400,
    },
    {
        "name": "中庸之道 (The Doctrine of the Mean)",
        "node_type": "principle",
        "domain": "philosophy",
        "description": "儒家核心原则：不偏不倚，执两用中。'中也者，天下之大本也；和也者，天下之达道也'。追求平衡与和谐的最优状态。",
        "summary": "在极端之间寻找最优平衡点",
        "tags": "儒家,平衡,优化,和谐",
        "year": -400,
    },
    # ---- 易经 ----
    {
        "name": "易经八卦 (I Ching / Book of Changes)",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "中国最古老的哲学经典。以阴(- -)阳(—)两种基本符号组合成八卦、六十四卦，描述宇宙万物的变化规律。二进制编码的最早原型，莱布尼茨从中获得二进制灵感。",
        "summary": "用二元符号编码万物变化，二进制的哲学源头",
        "tags": "易经,二进制,编码,变化,莱布尼茨",
        "year": -1000,
    },
    # ---- 西方哲学 ----
    {
        "name": "辩证法 (Dialectics)",
        "node_type": "method",
        "domain": "philosophy",
        "description": "黑格尔辩证法：正题→反题→合题的螺旋上升过程。通过矛盾的对立统一推动认识和事物发展。马克思将其发展为唯物辩证法。",
        "summary": "正反合的思维方法，通过矛盾推动发展",
        "tags": "黑格尔,马克思,矛盾,螺旋发展",
        "year": 1807,
    },
    {
        "name": "现象学 (Phenomenology)",
        "node_type": "method",
        "domain": "philosophy",
        "description": "胡塞尔创立的哲学方法：回到事物本身，悬置先入之见，直接描述意识经验的结构。强调第一人称视角和意向性（意识总是关于某物的意识）。",
        "summary": "回到事物本身，直接研究意识体验的结构",
        "tags": "胡塞尔,意识,体验,主观性,AI意识",
        "year": 1900,
    },
    {
        "name": "存在主义 (Existentialism)",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "萨特、海德格尔等人的哲学：'存在先于本质'——人先存在于世界，再通过自由选择创造自己的本质。强调个体自由、选择与责任。",
        "summary": "存在先于本质，人通过选择定义自我",
        "tags": "萨特,海德格尔,自由意志,选择,AI伦理",
        "year": 1943,
    },
    {
        "name": "实用主义 (Pragmatism)",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "美国哲学流派（皮尔士、詹姆斯、杜威）：知识的价值在于其实际效果。'真理就是在实践中有效的东西'。关注理论的可操作性和效果验证。",
        "summary": "以实际效果检验理论价值",
        "tags": "皮尔士,詹姆斯,杜威,实践,验证",
        "year": 1878,
    },
    {
        "name": "系统论 (Systems Theory)",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "贝塔朗菲创立：整体大于部分之和。系统具有涌现性、层级性、开放性。不能通过分析孤立部件来理解系统，必须研究部件间的相互作用和组织方式。",
        "summary": "整体大于部分之和，关注系统的涌现性和组织方式",
        "tags": "贝塔朗菲,复杂性,涌现,整体论",
        "year": 1968,
    },
    {
        "name": "解构主义 (Deconstruction)",
        "node_type": "method",
        "domain": "philosophy",
        "description": "德里达提出的哲学方法：拆解文本中隐含的二元对立（如中心/边缘、在场/缺席），揭示意义的不确定性和多层性。挑战固定分类和确定性知识。",
        "summary": "拆解二元对立，揭示隐含假设和意义的多层性",
        "tags": "德里达,后现代,文本,不确定性",
        "year": 1967,
    },
    {
        "name": "认识论 (Epistemology)",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "研究知识本质的哲学分支：什么是知识？如何获得知识？知识的边界在哪里？经验主义vs理性主义之争是其核心议题。从笛卡尔的'我思故我在'到贝叶斯认识论。",
        "summary": "研究知识的本质、来源和边界",
        "tags": "知识论,认知,经验主义,理性主义",
        "year": -400,
    },
    {
        "name": "功利主义 (Utilitarianism)",
        "node_type": "principle",
        "domain": "philosophy",
        "description": "边沁和密尔提出的伦理原则：行为的对错取决于其产生的效用（幸福/痛苦）总量。'最大多数人的最大幸福'。与AI对齐问题和奖励函数设计密切相关。",
        "summary": "以效用最大化为目标的决策原则",
        "tags": "边沁,密尔,伦理,效用,AI对齐",
        "year": 1789,
    },
    # ---- 美学/艺术哲学 ----
    {
        "name": "留白 (Negative Space / Ma)",
        "node_type": "principle",
        "domain": "philosophy",
        "description": "东方美学原则：不填满的空间同样传达意义。中国画'计白当黑'，日本'間'(Ma)。空白不是缺失，而是有意义的组成部分。与信息论中的稀疏编码、正则化思想相通。",
        "summary": "空白即信息，少即是多的设计哲学",
        "tags": "美学,东方,信息论,稀疏性,设计",
        "year": -300,
    },
    # ---- 语言哲学 ----
    {
        "name": "维特根斯坦语言游戏 (Language Games)",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "维特根斯坦后期哲学：语言的意义在于其使用方式，而非对应外部实在。不同的'语言游戏'有不同的规则。'语言的边界就是世界的边界'。对NLP和语言模型有深刻启示。",
        "summary": "语言的意义在于使用，不同场景有不同规则",
        "tags": "维特根斯坦,语言哲学,NLP,意义,上下文",
        "year": 1953,
    },
    # ---- 伦理学/决策 ----
    {
        "name": "电车难题 (Trolley Problem)",
        "node_type": "concept",
        "domain": "philosophy",
        "description": "经典伦理思想实验：一辆失控电车将撞死5人，你是否应该扳道岔让它改道撞死1人？揭示功利主义与义务论的根本冲突，是自动驾驶AI伦理的核心议题。",
        "summary": "AI伦理的核心困境——如何在冲突价值间做选择",
        "tags": "伦理学,AI伦理,自动驾驶,决策,思想实验",
        "year": 1967,
    },
]

# ============================================================
# 2. 跨领域关系 — 哲学 ↔ 理工科
# ============================================================
# 关系定义时使用节点名称，之后匹配为 ID
relations_def = [
    # === 道家 ↔ 计算机 ===
    (
        "无为 (Wu Wei / Non-Action)",
        "强化学习",
        "ANALOGOUS_TO",
        "无为的'不干预、让系统自行找到最优路径'与强化学习中agent通过自主探索学习策略高度相似。探索-利用权衡(exploration-exploitation)就是'无为而无不为'的数学形式。",
    ),
    (
        "无为 (Wu Wei / Non-Action)",
        "自监督学习 (Self-Supervised Learning)",
        "ANALOGOUS_TO",
        "无为强调不人为施加标签/指导，让系统自己从数据中学习规律——这正是自监督学习的核心理念：不依赖人工标注，从数据自身结构中提取知识。",
    ),
    (
        "阴阳 (Yin-Yang)",
        "生成对抗网络 (GAN)",
        "ANALOGOUS_TO",
        "阴阳的对立统一、相互制约、动态平衡，精确对应GAN中生成器与判别器的对抗训练：双方互相博弈推动共同进化，达到纳什均衡。",
    ),
    (
        "阴阳 (Yin-Yang)",
        "对比学习 (Contrastive Learning)",
        "ANALOGOUS_TO",
        "阴阳思想——通过区分对立面来认识事物。对比学习同样通过区分正样本对和负样本对来学习特征表示，本质上都是'通过对比认识世界'。",
    ),
    (
        "道法自然 (Tao Follows Nature)",
        "遗传算法",
        "INSPIRES",
        "'道法自然'是仿生计算的哲学根基——从自然界的进化机制中学习优化策略，遗传算法直接模仿自然选择和遗传变异。",
    ),
    (
        "道法自然 (Tao Follows Nature)",
        "蚁群优化算法",
        "INSPIRES",
        "道法自然——从蚂蚁群体的觅食行为中提取优化算法，体现了'天地有大美而不言'中蕴含的算法智慧。",
    ),
    (
        "物极必反 (Reversal at the Extreme)",
        "梯度下降与优化器",
        "ANALOGOUS_TO",
        "物极必反与优化中的overshooting（步长过大导致震荡）、学习率衰减策略相似：当更新过于激进时需要反向调节，AdaGrad/Adam等自适应优化器就是这种'自我纠正'的体现。",
    ),
    (
        "物极必反 (Reversal at the Extreme)",
        "Dropout 正则化",
        "ANALOGOUS_TO",
        "物极必反的智慧：模型过于'强大'（过拟合）反而性能下降。Dropout通过随机'削弱'网络来增强泛化能力，完美诠释了'弱者道之用'。",
    ),
    (
        "易经八卦 (I Ching / Book of Changes)",
        "信息熵与交叉熵",
        "INSPIRES",
        "易经用阴(--)阳(—)二进制编码描述万物变化，莱布尼茨从中获得二进制灵感。二进制→香农信息论→信息熵，这是从易经到现代信息科学的直接传承线。",
    ),
    (
        "道 (Tao / The Way)",
        "深度学习",
        "ANALOGOUS_TO",
        "道'不可道'——无法用显式规则描述，但确实存在且运行着万物。深度学习的神经网络同样学到了无法用显式规则表达的'隐式知识'(implicit knowledge)，权重中蕴含的模式人类无法直接解读。",
    ),
    # === 儒家 ↔ 计算机 ===
    (
        "格物致知 (Investigation of Things)",
        "预训练-微调范式",
        "ANALOGOUS_TO",
        "格物致知——先广泛研究事物(预训练/通识学习)，再专精某一领域(微调)。这与现代LLM的预训练-微调范式完全吻合：先在海量数据上学习通用知识，再针对特定任务精调。",
    ),
    (
        "中庸之道 (The Doctrine of the Mean)",
        "批量归一化 (Batch Normalization)",
        "ANALOGOUS_TO",
        "中庸追求'不偏不倚'的平衡状态。Batch Normalization将激活值归一化到均值为0、方差为1的平衡分布，防止极端值，使训练稳定——这是技术层面的'中庸之道'。",
    ),
    (
        "中庸之道 (The Doctrine of the Mean)",
        "RLHF (人类反馈强化学习)",
        "ANALOGOUS_TO",
        "中庸在多种价值/需求之间寻找平衡。RLHF同样试图在helpfulness、harmlessness、honesty之间找到平衡点，用人类反馈校准模型的输出，避免走向任何极端。",
    ),
    # === 西方哲学 ↔ 计算机 ===
    (
        "辩证法 (Dialectics)",
        "生成对抗网络 (GAN)",
        "ANALOGOUS_TO",
        "辩证法的正题→反题→合题与GAN训练过程同构：生成器(正题)产出，判别器(反题)否定，对抗训练的均衡(合题)产出更好的生成能力。",
    ),
    (
        "辩证法 (Dialectics)",
        "思维链推理 (Chain of Thought)",
        "ANALOGOUS_TO",
        "辩证法的步进式推理——从正题出发，经过反驳与综合，逐步深化认识。CoT同样将复杂问题分解为逐步推理的链条，通过中间步骤达成更准确的结论。",
    ),
    (
        "现象学 (Phenomenology)",
        "多模态学习 (Multimodal Learning)",
        "ANALOGOUS_TO",
        "现象学强调回到直接体验——人的认知是视觉、听觉、触觉等多感官的整合。多模态学习正是让AI整合文本、图像、音频等多种'感知通道'，模拟人的全方位体验式认知。",
    ),
    (
        "存在主义 (Existentialism)",
        "AI Agent (智能体)",
        "ANALOGOUS_TO",
        "'存在先于本质'——Agent也是先被'抛入'环境(exist)，再通过与环境交互、做出选择来定义自己的'能力'(essence)。Agent的自主决策能力呼应了存在主义对自由选择的强调。",
    ),
    (
        "实用主义 (Pragmatism)",
        "提示工程 (Prompt Engineering)",
        "ANALOGOUS_TO",
        "实用主义的'有效即真理'与Prompt Engineering高度契合——不追求理论完美的提示，而是反复试验找到实际效果最好的Prompt。评估标准是输出质量而非理论优雅。",
    ),
    (
        "系统论 (Systems Theory)",
        "涌现能力 (Emergent Abilities)",
        "ANALOGOUS_TO",
        "系统论的核心命题'整体大于部分之和'精确预言了LLM的涌现能力——当模型规模超过阈值，出现了单个神经元或小规模模型无法解释的全新能力。",
    ),
    (
        "系统论 (Systems Theory)",
        "多Agent系统 (Multi-Agent)",
        "ANALOGOUS_TO",
        "系统论关注组件间的交互产生的涌现行为。多Agent系统中，多个Agent的协作/竞争产生了单个Agent不具备的集体智能，正是系统论的直接体现。",
    ),
    (
        "解构主义 (Deconstruction)",
        "注意力机制",
        "ANALOGOUS_TO",
        "解构主义拆解文本的固定层级结构，揭示每个元素在不同上下文中的多重意义。Attention机制同样打破了固定的序列处理顺序，让每个token根据上下文动态获取不同权重的信息。",
    ),
    (
        "认识论 (Epistemology)",
        "检索增强生成 (RAG)",
        "ANALOGOUS_TO",
        "认识论探讨知识的来源和可靠性。RAG体现了一种认识论立场：承认模型内部知识可能过时/错误，因此通过检索外部可靠知识源来增强，这是'经验主义+理性主义'的混合认识论。",
    ),
    (
        "功利主义 (Utilitarianism)",
        "RLHF (人类反馈强化学习)",
        "ANALOGOUS_TO",
        "功利主义的'最大化效用总和'直接对应RLHF中reward model的设计：用奖励信号量化人类对输出的满意度，训练模型最大化这个'效用函数'。AI对齐问题本质上是功利主义的计算化。",
    ),
    (
        "电车难题 (Trolley Problem)",
        "RLHF (人类反馈强化学习)",
        "RELATED_TO",
        "电车难题揭示的价值冲突是AI对齐的核心挑战：当不同人类价值观冲突时，AI应如何决策？RLHF试图通过人类反馈解决这个问题，但电车难题提醒我们这并非总能达成一致。",
    ),
    (
        "维特根斯坦语言游戏 (Language Games)",
        "大语言模型 (LLM)",
        "ANALOGOUS_TO",
        "维特根斯坦认为语言意义来源于使用(language game)，而非对应外部实在。LLM正是通过学习海量语言使用样本(语言游戏的统计)来理解语义，它不'知道'世界，但'掌握'了语言游戏的规则。",
    ),
    (
        "维特根斯坦语言游戏 (Language Games)",
        "上下文学习 (In-Context Learning)",
        "ANALOGOUS_TO",
        "语言游戏理论：意义由使用上下文决定。In-Context Learning同样依赖上下文(few-shot examples)来确定当前任务的'规则'——给不同上下文就玩不同的'语言游戏'。",
    ),
    (
        "留白 (Negative Space / Ma)",
        "Dropout 正则化",
        "ANALOGOUS_TO",
        "留白的'空白即力量'——刻意的缺失反而增强整体效果。Dropout随机'留白'(置零部分神经元)反而提升模型泛化能力，空白成为正则化的手段。",
    ),
    (
        "留白 (Negative Space / Ma)",
        "量化与模型压缩",
        "ANALOGOUS_TO",
        "留白艺术——用更少表达更多。模型量化/压缩通过减少参数精度和数量，在保持核心能力的同时大幅缩小模型体积，'少即是多'的工程实践。",
    ),
    # === 道家 ↔ 其他自然科学 ===
    (
        "阴阳 (Yin-Yang)",
        "热力学第二定律（熵增）",
        "ANALOGOUS_TO",
        "阴阳的动态平衡与热力学中的有序(低熵)→无序(高熵)过程相呼应。阴阳在封闭系统中趋向混合(熵增)，但在开放系统中可维持有序结构(耗散结构)。",
    ),
    (
        "物极必反 (Reversal at the Extreme)",
        "混沌理论（蝴蝶效应）",
        "ANALOGOUS_TO",
        "物极必反描述系统在极端点的突变行为，混沌理论同样研究系统在临界点附近的分岔和相变——两者都关注'临界状态的质变'。",
    ),
    (
        "道 (Tao / The Way)",
        "涌现与还原论",
        "ANALOGOUS_TO",
        "道是不可还原的整体性存在，'道生万物'但道本身不是万物的简单叠加。这与涌现论的核心观点一致：复杂系统的整体行为不能还原为部件的简单组合。",
    ),
    # === 西方哲学之间的关系 ===
    (
        "辩证法 (Dialectics)",
        "阴阳 (Yin-Yang)",
        "ANALOGOUS_TO",
        "黑格尔辩证法的对立统一与中国阴阳思想高度相似——都强调矛盾双方相互依存、相互转化、在对抗中发展。但阴阳更强调循环平衡，辩证法更强调螺旋上升。",
    ),
    (
        "系统论 (Systems Theory)",
        "涌现与还原论",
        "BUILDS_ON",
        "系统论直接建立在涌现概念之上：'整体大于部分之和'就是涌现性的核心表述。系统论是对涌现现象的方法论框架化。",
    ),
    (
        "认识论 (Epistemology)",
        "贝叶斯定理",
        "RELATED_TO",
        "贝叶斯定理为认识论提供了数学形式：先验信念 + 新证据 → 后验信念。贝叶斯认识论是将哲学认识论精确化的重要尝试。",
    ),
    (
        "功利主义 (Utilitarianism)",
        "纳什均衡",
        "RELATED_TO",
        "功利主义追求效用最大化，博弈论中的纳什均衡是多方各自追求效用最大化时的均衡状态。从个体功利到集体均衡，博弈论是功利主义的多人扩展。",
    ),
    # === 哲学内部关系 ===
    (
        "道 (Tao / The Way)",
        "无为 (Wu Wei / Non-Action)",
        "ENABLES",
        "道是本体论，无为是方法论。理解了道的运行法则，自然引出无为的行事方式——顺道而行即是无为。",
    ),
    (
        "道 (Tao / The Way)",
        "阴阳 (Yin-Yang)",
        "ENABLES",
        "道的运行展现为阴阳的交互：'一阴一阳之谓道'。阴阳是道的动态表现形式。",
    ),
    (
        "道 (Tao / The Way)",
        "道法自然 (Tao Follows Nature)",
        "ENABLES",
        "'道法自然'是理解道的关键命题——道的最高法则就是自然本身。",
    ),
    (
        "道 (Tao / The Way)",
        "物极必反 (Reversal at the Extreme)",
        "ENABLES",
        "'反者道之动'——物极必反是道的运动规律的体现。",
    ),
    (
        "阴阳 (Yin-Yang)",
        "中庸之道 (The Doctrine of the Mean)",
        "RELATED_TO",
        "阴阳平衡思想与中庸的'执两用中'相通：两者都追求对立面之间的最优平衡状态。",
    ),
    (
        "格物致知 (Investigation of Things)",
        "认识论 (Epistemology)",
        "RELATED_TO",
        "格物致知是中国式认识论——通过实践研究事物来获取知识，与西方经验主义认识论相呼应。",
    ),
    (
        "实用主义 (Pragmatism)",
        "格物致知 (Investigation of Things)",
        "ANALOGOUS_TO",
        "实用主义的'有效即真理'与格物致知的'实践出真知'高度相似——都强调知识的实践性和效果验证。",
    ),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 插入知识节点
    node_name_to_id = {}
    inserted_nodes = 0
    skipped_nodes = 0

    for node in nodes:
        # 检查是否已存在
        cursor.execute("SELECT id FROM knowledge_nodes WHERE name = ?", (node["name"],))
        existing = cursor.fetchone()
        if existing:
            node_name_to_id[node["name"]] = existing[0]
            skipped_nodes += 1
            print(f"  ⏩ 已存在: {node['name']}")
            continue

        nid = get_id()
        node_name_to_id[node["name"]] = nid
        cursor.execute(
            """
            INSERT INTO knowledge_nodes 
            (id, name, node_type, domain, description, summary, source_info, year, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                nid,
                node["name"],
                node["node_type"],
                node["domain"],
                node["description"],
                node["summary"],
                None,
                node.get("year"),
                node.get("tags"),
                now,
                now,
            ),
        )
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

        # 检查是否已存在
        cursor.execute(
            """
            SELECT id FROM relations 
            WHERE source_id = ? AND target_id = ? AND relation_type = ?
        """,
            (src_id, tgt_id, rel_type),
        )
        if cursor.fetchone():
            skipped_rels += 1
            print(f"  ⏩ 关系已存在: {src_name} --{rel_type}--> {tgt_name}")
            continue

        rid = get_id()
        cursor.execute(
            """
            INSERT INTO relations 
            (id, source_id, target_id, relation_type, source_type, target_type, 
             description, confidence, ai_generated, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                rid,
                src_id,
                tgt_id,
                rel_type,
                "knowledge_node",
                "knowledge_node",
                desc,
                1.0,
                False,
                "confirmed",
                now,
            ),
        )
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
    print("🏛️  添加哲学与人文知识节点 — 文理交叉")
    print("=" * 60)
    main()
