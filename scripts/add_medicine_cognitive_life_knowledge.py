"""
添加医学、认知科学、生命科学知识节点
——生命系统与AI系统的深层类比

包含：
- 医学：免疫学、药物设计、流行病学、诊断推理
- 认知科学：认知架构、注意力理论、记忆系统、决策偏差
- 生命科学：细胞信号传导、基因调控网络、蛋白质折叠、进化博弈
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
    # ===================== 医学 (medicine) =====================
    {
        "name": "循证医学 (Evidence-Based Medicine)",
        "node_type": "method",
        "domain": "medicine",
        "description": "以系统性研究证据为基础做临床决策，而非仅依赖个人经验。核心流程：提出问题→检索证据→评价证据→结合临床情境→评估效果。是数据驱动决策在医学中的体现。",
        "summary": "用数据和证据而非经验驱动医学决策",
        "tags": "数据驱动,决策,证据,元分析",
        "year": 1992,
    },
    {
        "name": "免疫记忆与疫苗 (Immunological Memory)",
        "node_type": "phenomenon",
        "domain": "medicine",
        "description": "免疫系统初次接触病原体后产生记忆细胞(B/T记忆细胞)，再次遇到相同病原时可快速激活免疫反应。疫苗利用这一机制：用无害抗原'预训练'免疫系统。",
        "summary": "免疫系统的'预训练'——用历史经验加速未来响应",
        "tags": "免疫,记忆,预训练,疫苗",
        "year": 1796,
    },
    {
        "name": "药物靶点与锁钥模型 (Drug Target / Lock-and-Key)",
        "node_type": "concept",
        "domain": "medicine",
        "description": "药物分子(钥匙)精确结合靶点蛋白(锁)发挥作用。现代药物设计从海量分子库中筛选最佳'钥匙'——本质上是高维空间中的搜索优化问题。",
        "summary": "在巨大化学空间中搜索最优分子——组合优化问题",
        "tags": "药物设计,搜索,优化,蛋白质",
        "year": 1894,
    },
    {
        "name": "流行病学 SIR 模型 (Epidemiological Modeling)",
        "node_type": "method",
        "domain": "medicine",
        "description": "用微分方程描述传染病传播：易感(S)→感染(I)→恢复(R)。R₀(基本再生数)决定是否爆发。同样的扩散模型适用于信息传播、病毒营销、谣言扩散。",
        "summary": "传播动力学的数学模型——适用于疾病和信息",
        "tags": "流行病,微分方程,传播,网络",
        "year": 1927,
    },
    {
        "name": "临床诊断推理 (Clinical Reasoning)",
        "node_type": "method",
        "domain": "medicine",
        "description": "医生的诊断过程：症状→生成假设→验证/排除→最终诊断。使用模式识别(pattern recognition)和假设演绎推理(hypothetico-deductive)。本质上是在不完全信息下的贝叶斯推理。",
        "summary": "在不完全信息下的假说生成与验证——贝叶斯推理的临床实践",
        "tags": "诊断,推理,贝叶斯,模式识别",
        "year": 1970,
    },
    {
        "name": "耐药性与军备竞赛 (Antibiotic Resistance)",
        "node_type": "phenomenon",
        "domain": "medicine",
        "description": "细菌通过突变和自然选择发展出抗生素耐药性，人类不断开发新药应对——形成进化'军备竞赛'(Red Queen hypothesis)。对抗训练中的攻防迭代是同一模式。",
        "summary": "病原体与药物的进化军备竞赛——永恒的对抗博弈",
        "tags": "进化,对抗,红皇后,自然选择",
        "year": 1945,
    },
    {
        "name": "安慰剂效应 (Placebo Effect)",
        "node_type": "phenomenon",
        "domain": "medicine",
        "description": "无药理活性的'假药'也能产生真实疗效——仅因为患者'相信'它有效。揭示了信念/期望对物理结果的强大影响。在AI领域，用户对系统的信任度也会影响人机交互效果。",
        "summary": "信念和期望能产生真实的物理效果",
        "tags": "心理,信念,期望,主观性",
        "year": 1955,
    },

    # ===================== 认知科学 (cognitive_science) =====================
    {
        "name": "工作记忆 (Working Memory)",
        "node_type": "concept",
        "domain": "cognitive_science",
        "description": "认知系统的'内存'——短时存储和操纵信息的有限容量系统(约7±2个项目)。Baddeley模型包含中央执行系统、语音环路和视觉空间画板。是注意力和推理的认知基础。",
        "summary": "认知系统的有限容量'RAM'——信息暂存与操纵",
        "tags": "记忆,容量限制,注意力,认知架构",
        "year": 1974,
    },
    {
        "name": "认知负荷理论 (Cognitive Load Theory)",
        "node_type": "concept",
        "domain": "cognitive_science",
        "description": "Sweller提出：人的认知资源有限，学习效率取决于认知负荷管理。内在负荷(知识复杂度)+外在负荷(呈现方式)+关联负荷(深层加工)。UI设计和信息架构的认知基础。",
        "summary": "认知资源有限——信息呈现方式决定学习效率",
        "tags": "学习,资源管理,UI设计,信息架构",
        "year": 1988,
    },
    {
        "name": "双系统理论 (Dual Process Theory)",
        "node_type": "concept",
        "domain": "cognitive_science",
        "description": "Kahneman的思考快与慢：系统1(快速、直觉、自动)和系统2(慢速、理性、费力)。日常决策大多由系统1驱动，系统2负责复杂推理。LLM的token生成类似系统1，CoT类似系统2。",
        "summary": "快思考(直觉)与慢思考(推理)的双系统认知架构",
        "tags": "Kahneman,直觉,推理,决策",
        "year": 2011,
    },
    {
        "name": "具身认知 (Embodied Cognition)",
        "node_type": "concept",
        "domain": "cognitive_science",
        "description": "认知不仅在大脑中发生，还依赖身体和环境的交互。'思维是身体化的'——手势影响思考，姿态影响情绪。对具身AI(embodied AI)和机器人认知有深刻启示。",
        "summary": "认知依赖身体-环境交互，而非纯粹的符号计算",
        "tags": "身体,环境,交互,机器人",
        "year": 1991,
    },
    {
        "name": "选择性注意 (Selective Attention)",
        "node_type": "phenomenon",
        "domain": "cognitive_science",
        "description": "大脑在信息过载时选择性处理最相关的信息——鸡尾酒会效应(在嘈杂中听到自己名字)。Broadbent过滤器模型→Treisman衰减模型。是计算注意力机制的生物学原型。",
        "summary": "大脑从海量信息中选择性聚焦——生物注意力机制",
        "tags": "注意力,过滤,聚焦,信息选择",
        "year": 1958,
    },
    {
        "name": "图式理论 (Schema Theory)",
        "node_type": "concept",
        "domain": "cognitive_science",
        "description": "Piaget和Bartlett提出：人用'图式'(心理模板)组织和理解新信息。新信息要么被同化(融入已有图式)，要么导致图式顺应(修改图式)。与预训练模型的知识更新机制相似。",
        "summary": "用心理模板组织知识——认知的'预训练模型'",
        "tags": "知识表示,模板,同化,顺应",
        "year": 1932,
    },
    {
        "name": "元认知 (Metacognition)",
        "node_type": "concept",
        "domain": "cognitive_science",
        "description": "'思考关于思考'——对自己认知过程的监控和调节。知道自己知道什么、不知道什么。是自我反思、学习策略调整和错误纠正的基础。与AI的自评估和反思机制(Reflexion)相通。",
        "summary": "对自身认知过程的监控——'知道自己不知道'",
        "tags": "反思,自我监控,学习策略,AI反思",
        "year": 1979,
    },
    {
        "name": "迁移理论 (Transfer of Learning)",
        "node_type": "concept",
        "domain": "cognitive_science",
        "description": "在一个情境中学到的知识/技能应用到新情境的能力。近迁移(相似情境)比远迁移(跨域)容易。学习的目标不是记忆特定知识，而是获得可迁移的认知结构。",
        "summary": "知识从一个领域应用到另一个领域的认知能力",
        "tags": "迁移,泛化,学习,跨域",
        "year": 1901,
    },

    # ===================== 生命科学 (life_science) =====================
    {
        "name": "细胞信号传导 (Cell Signaling)",
        "node_type": "phenomenon",
        "domain": "life_science",
        "description": "细胞通过化学信号(配体-受体)接收、处理和响应外部信息。信号级联放大：一个信号分子→激活数千个下游分子。与计算机的消息传递、事件驱动架构高度相似。",
        "summary": "细胞的'消息传递系统'——接收、处理、响应信号",
        "tags": "信号,级联,通信,反馈",
        "year": 1970,
    },
    {
        "name": "基因调控网络 (Gene Regulatory Network)",
        "node_type": "concept",
        "domain": "life_science",
        "description": "基因通过转录因子相互调控表达——形成复杂的调控网络。增强子、抑制子、正负反馈环路构成了生命的'程序'。本质上是一个生物学的有向图/知识图谱。",
        "summary": "生命的'代码'——基因相互调控的网络拓扑",
        "tags": "基因,网络,调控,反馈环路",
        "year": 1961,
    },
    {
        "name": "蛋白质折叠 (Protein Folding)",
        "node_type": "phenomenon",
        "domain": "life_science",
        "description": "蛋白质从一维氨基酸序列自发折叠成特定三维结构，结构决定功能。Levinthal悖论：随机搜索需要天文数字时间，但蛋白质在毫秒内完成——说明存在高效的折叠路径。AlphaFold解决了50年来的生物学难题。",
        "summary": "序列→结构→功能：生命中最精妙的自组织过程",
        "tags": "结构预测,AlphaFold,自组织,搜索",
        "year": 1961,
    },
    {
        "name": "表观遗传学 (Epigenetics)",
        "node_type": "concept",
        "domain": "life_science",
        "description": "不改变DNA序列但影响基因表达的可遗传修饰(甲基化、组蛋白修饰等)。'硬件相同但软件不同'——同一基因组可产生不同的表型。环境可通过表观遗传影响后代。",
        "summary": "基因表达的'软件层'——不改代码改配置",
        "tags": "基因表达,环境,可塑性,配置",
        "year": 1942,
    },
    {
        "name": "共生与协同进化 (Symbiosis and Co-evolution)",
        "node_type": "phenomenon",
        "domain": "life_science",
        "description": "不同物种相互依存、共同进化。从线粒体(内共生起源)到肠道菌群-宿主关系。互利共生产生1+1>2的效果，与多Agent协作、联邦学习的理念相通。",
        "summary": "不同物种互利共存、共同进化——1+1>2",
        "tags": "共生,协作,互利,多agent",
        "year": 1879,
    },
    {
        "name": "趋化性 (Chemotaxis)",
        "node_type": "phenomenon",
        "domain": "life_science",
        "description": "细胞或微生物沿化学浓度梯度移动——向高浓度营养物质移动或远离有害物质。大肠杆菌的趋化性是一种原始但高效的梯度追踪算法，是梯度下降的生物学原型。",
        "summary": "沿化学梯度寻找最优位置——生物版梯度下降",
        "tags": "梯度,搜索,优化,细菌",
        "year": 1884,
    },
    {
        "name": "干细胞分化 (Stem Cell Differentiation)",
        "node_type": "phenomenon",
        "domain": "life_science",
        "description": "干细胞具有分化为多种细胞类型的潜能。分化过程中逐步'特化'——从全能到多能到单能。这是一个信息逐步确定的过程，类似于模型从通用到专用的微调。",
        "summary": "从通用潜能到特定功能——生物系统的'微调'过程",
        "tags": "分化,特化,潜能,微调",
        "year": 1961,
    },
    {
        "name": "生物钟与昼夜节律 (Circadian Rhythm)",
        "node_type": "phenomenon",
        "domain": "life_science",
        "description": "几乎所有生物都有约24小时的内在节律时钟，调控睡眠、代谢、免疫等。由转录-翻译反馈环路驱动。是生物系统中最精确的周期性调控机制。",
        "summary": "生命内置的24小时周期调度器",
        "tags": "节律,周期,调度,反馈环路",
        "year": 1729,
    },
]

# ============================================================
# 2. 跨领域关系
# ============================================================
relations_def = [
    # === 医学 ↔ 计算机/AI ===
    ("免疫记忆与疫苗 (Immunological Memory)", "预训练-微调范式", "ANALOGOUS_TO",
     "疫苗'预训练'免疫系统——用无害抗原让免疫系统学习识别病原的模式，之后遇到真实病原时可快速'微调'响应。这与LLM预训练→微调范式完全同构。"),
    
    ("免疫记忆与疫苗 (Immunological Memory)", "免疫系统应答", "BUILDS_ON",
     "免疫记忆是免疫系统应答的高级机制——在首次免疫应答基础上产生记忆细胞。"),
    
    ("药物靶点与锁钥模型 (Drug Target / Lock-and-Key)", "蛋白质折叠 (Protein Folding)", "RELATED_TO",
     "药物设计需要知道靶点蛋白的3D结构(锁的形状)才能设计匹配的分子(钥匙)。蛋白质折叠预测直接赋能药物设计。"),
    
    ("流行病学 SIR 模型 (Epidemiological Modeling)", "图论与网络科学", "BUILDS_ON",
     "流行病传播发生在社会网络上。将SIR模型与网络拓扑结合，可以更准确预测传播路径。网络科学提供了流行病学的结构基础。"),
    
    ("流行病学 SIR 模型 (Epidemiological Modeling)", "六度分隔与小世界网络", "RELATED_TO",
     "小世界网络特性加速疫病传播——少数'超级传播者'(hub节点)通过短路径连接远距离个体，使传染病能在人群中快速扩散。"),
    
    ("临床诊断推理 (Clinical Reasoning)", "贝叶斯定理", "BUILDS_ON",
     "临床诊断是贝叶斯推理的实践：先验概率(疾病发病率) + 检测结果(似然) → 后验概率(患病概率)。医生不断用新证据更新诊断概率。"),
    
    ("临床诊断推理 (Clinical Reasoning)", "思维链推理 (Chain of Thought)", "ANALOGOUS_TO",
     "医生的诊断推理是一种思维链：症状→可能诊断→检查→排除→确诊。CoT让LLM模拟这种逐步推理过程，在医疗AI中尤为重要。"),
    
    ("循证医学 (Evidence-Based Medicine)", "检索增强生成 (RAG)", "ANALOGOUS_TO",
     "循证医学核心流程：面对问题→检索最佳证据→结合临床判断→做出决策。RAG同样：面对问题→检索相关知识→结合模型推理→生成答案。两者都强调'基于证据而非记忆'。"),
    
    ("耐药性与军备竞赛 (Antibiotic Resistance)", "生成对抗网络 (GAN)", "ANALOGOUS_TO",
     "耐药性是进化的军备竞赛：细菌不断进化抗药性，人类不断开发新药。GAN的对抗训练同构：生成器不断改进以骗过判别器，判别器不断提升以识别假样本。"),
    
    ("耐药性与军备竞赛 (Antibiotic Resistance)", "自然选择与进化", "BUILDS_ON",
     "耐药性是自然选择的经典案例：抗生素施加选择压力，有耐药突变的细菌存活并繁殖。"),
    
    ("安慰剂效应 (Placebo Effect)", "RLHF (人类反馈强化学习)", "RELATED_TO",
     "安慰剂效应揭示：人的'反馈'受主观期望强烈影响。RLHF依赖人类反馈，但人类反馈本身可能存在'安慰剂式'偏差——对某些模型风格的偏好可能与实际质量无关。"),
    
    # === 认知科学 ↔ 计算机/AI ===
    ("工作记忆 (Working Memory)", "Transformer 架构", "ANALOGOUS_TO",
     "工作记忆容量有限(~7项)。Transformer的context window就是AI的'工作记忆'——有限的上下文长度决定了模型能同时处理的信息量。超长上下文研究就是在扩展AI的'工作记忆'。"),
    
    ("选择性注意 (Selective Attention)", "注意力机制", "INSPIRES",
     "计算注意力机制直接受认知科学启发：大脑选择性关注最相关的信息，Attention机制同样让模型为不同输入分配不同权重，聚焦最重要的部分。"),
    
    ("双系统理论 (Dual Process Theory)", "思维链推理 (Chain of Thought)", "ANALOGOUS_TO",
     "系统1(快速直觉)→系统2(慢速推理)。LLM的直接输出类似系统1(快但可能错)，CoT强制模型进入'系统2模式'——逐步推理虽慢但更准确。"),
    
    ("双系统理论 (Dual Process Theory)", "大语言模型 (LLM)", "ANALOGOUS_TO",
     "LLM兼具两种模式：简单问题直接输出(系统1)，复杂问题需要CoT/多步推理(系统2)。这种双系统特征是LLM认知能力的核心结构。"),
    
    ("具身认知 (Embodied Cognition)", "多模态学习 (Multimodal Learning)", "ANALOGOUS_TO",
     "具身认知认为理解需要感知-运动经验，不能仅靠符号。多模态AI同样：仅有文本不够，还需要图像、声音、视频等多种'感知通道'才能更深地理解世界。"),
    
    ("具身认知 (Embodied Cognition)", "AI Agent (智能体)", "INSPIRES",
     "具身认知强调认知依赖身体-环境交互。具身AI Agent不仅思考还要在环境中行动——通过感知-行动循环(而非纯符号推理)获得理解。"),
    
    ("图式理论 (Schema Theory)", "预训练-微调范式", "ANALOGOUS_TO",
     "图式是认知的'预训练模型'——已有的知识框架。新信息被同化(融入已有图式)≈微调不改变权重；图式顺应(修改图式)≈微调更新参数。学习就是不断更新内部图式。"),
    
    ("元认知 (Metacognition)", "思维链推理 (Chain of Thought)", "RELATED_TO",
     "元认知是'思考关于思考'。CoT让模型显式展示思考过程，是一种元认知的外化——让AI'意识到'自己在如何推理，从而能监控和修正推理过程。"),
    
    ("元认知 (Metacognition)", "RLHF (人类反馈强化学习)", "RELATED_TO",
     "元认知包含自我评估和自我调节。RLHF训练模型学会评估自己输出的质量并调整——是一种'训练元认知'的技术手段。"),
    
    ("迁移理论 (Transfer of Learning)", "迁移学习", "INSPIRES",
     "认知科学的迁移理论直接启发了机器学习中的迁移学习：将一个任务/领域学到的知识应用到新任务/领域。近迁移↔领域内迁移，远迁移↔跨域迁移。"),
    
    ("认知负荷理论 (Cognitive Load Theory)", "量化与模型压缩", "ANALOGOUS_TO",
     "认知负荷理论关注如何在有限认知资源下优化信息处理。模型压缩同样关注如何在有限计算资源下保持模型能力——减少'认知负荷'同时保持'理解能力'。"),
    
    # === 生命科学 ↔ 计算机/AI ===
    ("细胞信号传导 (Cell Signaling)", "人工神经网络", "ANALOGOUS_TO",
     "细胞通过信号级联传递和放大信息。人工神经网络同样通过层层传递和变换信号——每一层接收输入、处理、传递给下一层。生物信号传导是神经网络的分子层面原型。"),
    
    ("基因调控网络 (Gene Regulatory Network)", "知识图谱 (Knowledge Graph)", "ANALOGOUS_TO",
     "基因调控网络是生物学的'知识图谱'——基因(节点)通过调控关系(边)相互连接，形成复杂的有向图。理解基因网络就是在做生物学的图谱分析。"),
    
    ("基因调控网络 (Gene Regulatory Network)", "图神经网络 (GNN)", "RELATED_TO",
     "基因调控网络的分析和预测是GNN的重要应用场景。GNN能捕获基因间的复杂调控关系，预测基因表达模式。"),
    
    ("蛋白质折叠 (Protein Folding)", "深度学习", "RELATED_TO",
     "AlphaFold2用深度学习解决了蛋白质折叠问题——50年来最重要的生物学突破之一。证明了AI能在传统科学难题上取得革命性突破。"),
    
    ("蛋白质折叠 (Protein Folding)", "自注意力机制 (Self-Attention)", "RELATED_TO",
     "AlphaFold2的核心创新之一是将Self-Attention应用于氨基酸序列，建模远距离残基间的相互作用。Attention机制完美适配蛋白质中的长距离依赖关系。"),
    
    ("表观遗传学 (Epigenetics)", "预训练-微调范式", "ANALOGOUS_TO",
     "表观遗传 = '不改DNA序列但改变基因表达'。微调 = '不改大部分预训练权重但改变模型行为'。两者都是在不修改底层'代码'的情况下，通过上层'配置'改变系统行为。"),
    
    ("表观遗传学 (Epigenetics)", "提示工程 (Prompt Engineering)", "ANALOGOUS_TO",
     "表观遗传通过甲基化等修饰影响基因表达而不改变DNA。Prompt Engineering通过改变输入文本影响LLM输出而不改变模型权重——两者都是不改'硬件'改'环境指令'。"),
    
    ("共生与协同进化 (Symbiosis and Co-evolution)", "联邦学习 (Federated Learning)", "ANALOGOUS_TO",
     "共生中不同物种各自保留独立性但共享利益。联邦学习中不同机构保留数据主权但共享模型知识——两者都是'独立而协作'的互利模式。"),
    
    ("共生与协同进化 (Symbiosis and Co-evolution)", "多Agent系统 (Multi-Agent)", "ANALOGOUS_TO",
     "共生关系中不同物种各有特长、互补协作。多Agent系统同样：不同Agent各有专长，通过协作完成单个Agent无法完成的任务。"),
    
    ("趋化性 (Chemotaxis)", "梯度下降法", "ANALOGOUS_TO",
     "趋化性是生物版的梯度下降：细菌沿化学浓度梯度移动，向'更优'方向迁移。梯度下降沿损失函数梯度方向更新参数——两者都是'顺着梯度走'的优化策略。"),
    
    ("趋化性 (Chemotaxis)", "梯度下降与优化器", "ANALOGOUS_TO",
     "细菌趋化性使用'随机游走+偏向'策略(run-and-tumble)：随机探索但偏向浓度增加方向。SGD(随机梯度下降)同样：随机采样但期望方向指向最优。"),
    
    ("干细胞分化 (Stem Cell Differentiation)", "预训练-微调范式", "ANALOGOUS_TO",
     "干细胞从全能到特化。预训练模型从通用到专用。两者都经历：广泛潜能→接收特定'信号'(领域数据/微调)→特化为特定功能(组织细胞/领域模型)。"),
    
    ("生物钟与昼夜节律 (Circadian Rhythm)", "批量归一化 (Batch Normalization)", "ANALOGOUS_TO",
     "生物钟通过反馈环路维持稳定的24小时节律，防止代谢过程偏离正常范围。BatchNorm同样通过归一化维持激活值在稳定范围内，防止训练过程中的数值漂移。"),
    
    # === 领域间关系 ===
    ("临床诊断推理 (Clinical Reasoning)", "循证医学 (Evidence-Based Medicine)", "BUILDS_ON",
     "循证医学为临床诊断推理提供了系统性的证据检索和评估框架——从经验驱动走向数据驱动。"),
    
    ("工作记忆 (Working Memory)", "选择性注意 (Selective Attention)", "RELATED_TO",
     "工作记忆和选择性注意紧密关联：注意力决定什么信息进入工作记忆，工作记忆容量限制决定注意力需要高度选择性。"),
    
    ("认知负荷理论 (Cognitive Load Theory)", "工作记忆 (Working Memory)", "BUILDS_ON",
     "认知负荷理论直接建立在工作记忆容量有限的基础上——正因为工作记忆有限，才需要管理认知负荷。"),
    
    ("图式理论 (Schema Theory)", "迁移理论 (Transfer of Learning)", "ENABLES",
     "迁移学习的认知基础是图式：抽象的知识图式可以跨情境应用，具体知识难以迁移。图式越抽象，迁移越容易。"),
    
    ("选择性注意 (Selective Attention)", "巴甫洛夫条件反射", "RELATED_TO",
     "注意力可以被条件化——经过训练，特定刺激会自动吸引注意力。巴甫洛夫条件反射建立了刺激-反应的自动化联结，注意力也可以被类似地'条件化'。"),
    
    ("具身认知 (Embodied Cognition)", "现象学 (Phenomenology)", "BUILDS_ON",
     "具身认知哲学根源于现象学——梅洛-庞蒂的身体现象学强调知觉的身体性，为具身认知提供了哲学基础。"),
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
    print(f"📌 所有领域({len(domains)}): {', '.join(sorted(domains))}")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🏥🧠🧬 添加医学·认知科学·生命科学知识节点")
    print("=" * 60)
    main()
