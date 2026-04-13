"""
第三批知识节点：大规模补充计算机科学领域。
覆盖：深度学习基础 → Transformer → LLM → Agent → MCP → 生成模型 → 对比学习 → RLHF 等。
新增 ~35 个 CS 知识节点 + ~80 条关联关系。
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
#  第三批知识节点 —— 计算机科学/AI 技术栈
# ══════════════════════════════════════════════════════════════

NODES = [
    # ═══════════ 深度学习基础 ═══════════
    {
        "name": "深度学习",
        "node_type": "method",
        "domain": "computer_science",
        "description": "多层非线性变换的表示学习框架。通过反向传播+梯度下降训练多层神经网络，"
        "自动从原始数据中提取层次化特征表示。"
        "2006年Hinton提出深度信念网络引爆深度学习革命，后来CNN/RNN/Transformer等架构百花齐放。",
        "summary": "多层神经网络自动学习数据的层次化表示",
        "source_info": "Geoffrey Hinton et al., 2006, 'A Fast Learning Algorithm for Deep Belief Nets'",
        "year": 2006,
        "tags": "深度学习,deep learning,表示学习,Hinton,多层网络",
    },
    {
        "name": "反向传播算法",
        "node_type": "method",
        "domain": "computer_science",
        "description": "通过链式法则高效计算损失函数对每一层参数的梯度，是训练多层神经网络的核心算法。"
        "1986年Rumelhart、Hinton和Williams发表经典论文使其广泛应用。"
        "本质是自动微分的一种特例（反向模式），计算图上从输出到输入反向传播误差。",
        "summary": "链式法则 + 误差反向传播——训练神经网络的引擎",
        "source_info": "Rumelhart, Hinton, Williams, 1986, 'Learning representations by back-propagating errors'",
        "year": 1986,
        "tags": "反向传播,backpropagation,链式法则,梯度,自动微分",
    },
    {
        "name": "卷积神经网络 (CNN)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "利用卷积核提取局部空间特征的神经网络架构，具有参数共享和平移不变性。"
        "灵感来源于生物视觉系统中的简单细胞和复杂细胞。"
        "LeNet(1998)→AlexNet(2012)→VGG→ResNet，是计算机视觉的基石架构。",
        "summary": "局部卷积+池化+层叠——计算机视觉的基石架构",
        "source_info": "Yann LeCun et al., 1998, 'Gradient-Based Learning Applied to Document Recognition'",
        "year": 1998,
        "tags": "CNN,卷积,视觉,特征提取,ResNet,AlexNet",
    },
    {
        "name": "循环神经网络 (RNN/LSTM)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "处理序列数据的神经网络，通过隐藏状态实现对历史信息的记忆。"
        "基础RNN存在梯度消失/爆炸问题，LSTM(1997)通过门控机制解决长程依赖。"
        "GRU(2014)是简化版本。在Transformer出现前，是NLP和语音领域的主流架构。",
        "summary": "门控记忆单元处理序列——Transformer之前的NLP之王",
        "source_info": "Hochreiter & Schmidhuber, 1997, 'Long Short-Term Memory'",
        "year": 1997,
        "tags": "RNN,LSTM,GRU,序列,时序,梯度消失,门控",
    },
    {
        "name": "梯度下降与优化器",
        "node_type": "method",
        "domain": "computer_science",
        "description": "沿损失函数梯度的反方向更新参数以最小化损失。"
        "SGD→Momentum→AdaGrad→RMSProp→Adam，优化器的演进史就是深度学习的训练史。"
        "Adam(2014)结合一阶矩和二阶矩估计，是目前最广泛使用的优化器。"
        "类比物理学中球沿势能面下滚。",
        "summary": "沿梯度反方向更新参数——从SGD到Adam的优化器家族",
        "source_info": "Kingma & Ba, 2014, 'Adam: A Method for Stochastic Optimization'",
        "year": 2014,
        "tags": "梯度下降,SGD,Adam,优化器,学习率,momentum",
    },
    {
        "name": "批量归一化 (Batch Normalization)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "在每一层对输入进行归一化（零均值、单位方差），解决内部协变量偏移问题。"
        "使训练更稳定，允许使用更大的学习率，加速收敛。"
        "类比实验科学中的标准化/归一化操作。后续衍生出LayerNorm、GroupNorm等变体。",
        "summary": "层间归一化——让深度网络训练稳定且快速",
        "source_info": "Ioffe & Szegedy, 2015, 'Batch Normalization: Accelerating Deep Network Training'",
        "year": 2015,
        "tags": "BatchNorm,归一化,LayerNorm,训练稳定,协变量偏移",
    },
    {
        "name": "Dropout 正则化",
        "node_type": "method",
        "domain": "computer_science",
        "description": "训练时随机'丢弃'一部分神经元（置零），防止过拟合。"
        "直觉上迫使网络学习更鲁棒的特征，不过度依赖某几个神经元。"
        "生物学类比：大脑神经元有随机失活现象。"
        "数学上等价于训练指数级的子网络集成(ensemble)。",
        "summary": "随机丢弃神经元——简单有效的正则化技术",
        "source_info": "Srivastava et al., 2014, 'Dropout: A Simple Way to Prevent Neural Networks from Overfitting'",
        "year": 2014,
        "tags": "Dropout,正则化,过拟合,ensemble,随机失活",
    },
    {
        "name": "残差连接 (ResNet)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "通过跳跃连接(skip connection)让网络学习残差映射F(x)=H(x)-x而非直接映射H(x)。"
        "解决了深层网络的退化问题，使训练上百甚至上千层网络成为可能。"
        "152层ResNet在2015年ImageNet上超越人类表现。"
        "残差思想影响了Transformer(残差连接+LayerNorm)、DenseNet、UNet等所有现代架构。",
        "summary": "跳跃连接学习残差——突破深度网络退化瓶颈",
        "source_info": "Kaiming He et al., 2015, 'Deep Residual Learning for Image Recognition'",
        "year": 2015,
        "tags": "ResNet,残差连接,skip connection,深层网络,退化问题",
    },
    # ═══════════ Transformer 与 NLP 革命 ═══════════
    {
        "name": "Transformer 架构",
        "node_type": "method",
        "domain": "computer_science",
        "description": "基于自注意力机制的序列建模架构，完全抛弃了RNN的递归结构。"
        "核心组件：多头自注意力 + 前馈网络 + 残差连接 + LayerNorm + 位置编码。"
        "并行计算能力远超RNN，成为NLP→CV→多模态→科学计算的统一架构。"
        "BERT(编码器)、GPT(解码器)、T5(编解码器)分别用了Transformer的不同部分。",
        "summary": "自注意力驱动的并行序列建模——AI大一统架构",
        "source_info": "Vaswani et al., 2017, 'Attention Is All You Need'",
        "year": 2017,
        "tags": "Transformer,自注意力,多头注意力,位置编码,并行计算",
    },
    {
        "name": "自注意力机制 (Self-Attention)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "序列中每个位置与所有其他位置计算注意力权重(Q·K^T/√d)，实现全局信息交互。"
        "核心公式：Attention(Q,K,V) = softmax(QK^T/√d_k)V。"
        "多头注意力让模型同时关注不同子空间的信息。"
        "是Transformer的核心，也是注意力机制从'辅助增强'到'核心架构'的转折点。",
        "summary": "Q·K·V全局信息交互——Transformer的核心引擎",
        "source_info": "Vaswani et al., 2017 (Transformer论文的核心贡献)",
        "year": 2017,
        "tags": "自注意力,QKV,多头注意力,全局依赖,softmax",
    },
    {
        "name": "词嵌入 (Word Embedding)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将离散的词语映射到连续向量空间，使语义相似的词在向量空间中距离接近。"
        "Word2Vec(2013): CBOW和Skip-gram两种方法，'king-man+woman≈queen'。"
        "GloVe(2014): 基于共现矩阵的全局统计方法。"
        "后发展为上下文相关的动态嵌入(ELMo→BERT→GPT)。",
        "summary": "词→向量：语义空间中king-man+woman≈queen",
        "source_info": "Mikolov et al., 2013, 'Efficient Estimation of Word Representations in Vector Space'",
        "year": 2013,
        "tags": "Word2Vec,词嵌入,GloVe,语义空间,分布式表示",
    },
    {
        "name": "位置编码 (Positional Encoding)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "Transformer中自注意力是位置无关的(permutation invariant)，需要额外注入位置信息。"
        "原始方案：正弦/余弦函数编码。后续发展：可学习位置编码、ALiBi、RoPE(旋转位置编码)。"
        "RoPE通过旋转矩阵将相对位置信息编码到注意力计算中，被LLaMA等主流模型采用。",
        "summary": "为Transformer注入序列位置信息——从正弦到RoPE",
        "source_info": "Vaswani et al., 2017; Su et al., 2021 (RoPE)",
        "year": 2017,
        "tags": "位置编码,RoPE,正弦编码,ALiBi,旋转位置编码",
    },
    # ═══════════ 大语言模型 (LLM) 生态 ═══════════
    {
        "name": "大语言模型 (LLM)",
        "node_type": "concept",
        "domain": "computer_science",
        "description": "基于Transformer架构、在海量文本上预训练的超大规模语言模型。"
        "GPT-3(175B)→ChatGPT→GPT-4→Claude→Gemini→DeepSeek→Qwen。"
        "核心能力：语言理解与生成、推理、代码编写、工具使用。"
        "Scaling Law表明：模型参数、数据量、计算量三者的幂律关系决定模型能力。"
        "标志着AI从专用走向通用(AGI方向)。",
        "summary": "超大规模Transformer语言模型——通用人工智能的里程碑",
        "source_info": "Brown et al., 2020, 'Language Models are Few-Shot Learners' (GPT-3)",
        "year": 2020,
        "tags": "LLM,GPT,ChatGPT,大模型,Scaling Law,通用AI",
    },
    {
        "name": "预训练-微调范式",
        "node_type": "method",
        "domain": "computer_science",
        "description": "先在大规模无标注数据上预训练通用表示，再在小规模标注数据上微调以适应特定任务。"
        "BERT开创了NLP预训练时代(MLM+NSP)，GPT系列用自回归预训练。"
        "后续发展：Prompt Tuning、LoRA(低秩适配)、P-Tuning等参数高效微调方法。"
        "是迁移学习在深度学习时代的最重要实践。",
        "summary": "大规模预训练 + 小数据微调——深度学习的标准范式",
        "source_info": "Devlin et al., 2018, 'BERT'; Hu et al., 2021, 'LoRA'",
        "year": 2018,
        "tags": "预训练,微调,BERT,LoRA,Prompt Tuning,参数高效",
    },
    {
        "name": "Scaling Law (规模定律)",
        "node_type": "principle",
        "domain": "computer_science",
        "description": "模型性能与模型参数量N、数据集大小D、计算量C之间存在平滑的幂律关系。"
        "Kaplan et al.(2020)发现的经验规律，Chinchilla(2022)进一步给出最优N-D配比。"
        "指导了GPT-4/Claude/Gemini等大模型的训练策略。"
        "本质上反映了统计学习理论中的偏差-方差权衡在大规模场景下的表现。",
        "summary": "参数×数据×算力的幂律关系——大模型军备竞赛的理论基础",
        "source_info": "Kaplan et al., 2020, 'Scaling Laws for Neural Language Models'",
        "year": 2020,
        "tags": "Scaling Law,幂律,Chinchilla,算力,参数量,数据量",
    },
    {
        "name": "涌现能力 (Emergent Abilities)",
        "node_type": "phenomenon",
        "domain": "computer_science",
        "description": "大语言模型在规模突破某个阈值后突然展现出小模型没有的能力，如：思维链推理、"
        "少样本学习、代码生成、多步数学推理等。"
        "Wei et al.(2022)首次系统研究。与物理学中的相变和复杂系统的涌现高度类比。"
        "也引发争论：是否真正的涌现，还是评估指标的阶跃效应？",
        "summary": "模型规模突破阈值后突然获得新能力——AI的'相变'",
        "source_info": "Wei et al., 2022, 'Emergent Abilities of Large Language Models'",
        "year": 2022,
        "tags": "涌现,相变,规模效应,突变,少样本学习,推理能力",
    },
    {
        "name": "上下文学习 (In-Context Learning)",
        "node_type": "phenomenon",
        "domain": "computer_science",
        "description": "LLM无需更新权重，仅通过在prompt中提供几个示例就能学会新任务。"
        "GPT-3展示的核心能力，颠覆了传统'必须微调'的范式。"
        "机制研究：可能是隐式梯度下降(Akyürek et al.)或隐式贝叶斯推理(Xie et al.)。"
        "是Prompt Engineering的理论基础。",
        "summary": "不改权重，几个示例就能学新任务——LLM最神奇的能力",
        "source_info": "Brown et al., 2020 (GPT-3首次展示); 后续机制研究2022-2023",
        "year": 2020,
        "tags": "ICL,上下文学习,少样本,prompt,隐式学习,GPT-3",
    },
    {
        "name": "RLHF (人类反馈强化学习)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "通过人类偏好反馈训练奖励模型，再用强化学习(PPO)优化LLM使其输出符合人类意图。"
        "三步流程：SFT(监督微调)→RM(奖励模型训练)→PPO(强化学习优化)。"
        "是ChatGPT成功的关键技术，实现了AI对齐(alignment)的工程化路径。"
        "后续发展：DPO(Direct Preference Optimization)简化了这一流程。",
        "summary": "人类偏好→奖励模型→PPO优化——ChatGPT对齐的秘密武器",
        "source_info": "Ouyang et al., 2022, 'Training language models to follow instructions with human feedback'",
        "year": 2022,
        "tags": "RLHF,对齐,alignment,PPO,DPO,人类反馈,ChatGPT",
    },
    {
        "name": "思维链推理 (Chain of Thought)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "在prompt中提供逐步推理的示例，引导LLM展开中间推理步骤而非直接给出答案。"
        "显著提升了数学推理、逻辑推理、常识推理的准确率。"
        "后续发展：Zero-shot CoT('Let's think step by step')、"
        "Tree of Thought、Graph of Thought、Self-Consistency。"
        "类比人类的系统2思维(慢思考)。",
        "summary": "'一步步想'——让LLM展开推理过程的提示技术",
        "source_info": "Wei et al., 2022, 'Chain-of-Thought Prompting Elicits Reasoning in LLMs'",
        "year": 2022,
        "tags": "CoT,思维链,推理,提示工程,Tree of Thought,step by step",
    },
    {
        "name": "提示工程 (Prompt Engineering)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "设计和优化输入提示(prompt)以引导LLM产生期望输出的技术与方法论。"
        "包括：Few-shot、Zero-shot、CoT、Role-playing、Self-Ask、ReAct等策略。"
        "System prompt定义角色与约束，User prompt提供任务与上下文。"
        "是LLM时代的'新编程'——用自然语言编程。",
        "summary": "用自然语言'编程'LLM——提示设计的方法论",
        "source_info": "实践驱动的方法论，2021-2023年逐步形成体系",
        "year": 2021,
        "tags": "提示工程,prompt,Few-shot,Zero-shot,角色扮演,系统提示",
    },
    {
        "name": "检索增强生成 (RAG)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将外部知识库检索与LLM生成结合：先检索相关文档片段，再作为上下文注入prompt。"
        "解决LLM的知识截止、幻觉(hallucination)、领域知识不足等问题。"
        "技术栈：文档分块→向量嵌入→向量数据库(Faiss/Milvus/Chroma)→语义检索→LLM生成。"
        "是企业级LLM应用的标准架构。",
        "summary": "检索外部知识+LLM生成——解决幻觉的实用方案",
        "source_info": "Lewis et al., 2020, 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks'",
        "year": 2020,
        "tags": "RAG,检索增强,向量数据库,幻觉,知识库,Embedding",
    },
    {
        "name": "混合专家模型 (MoE)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将模型参数分为多个'专家'子网络，每次推理只激活少量相关专家(稀疏激活)。"
        "在保持推理效率的同时大幅增加模型总参数量。"
        "Mistral 8x7B、GPT-4(传言)、DeepSeek-V2/V3都采用MoE架构。"
        "类比人脑：不同脑区专门处理不同任务，按需激活。",
        "summary": "稀疏激活的专家集合——用少量计算撬动大量参数",
        "source_info": "Shazeer et al., 2017; Fedus et al., 2022, 'Switch Transformers'",
        "year": 2017,
        "tags": "MoE,混合专家,稀疏激活,Mixtral,Switch Transformer",
    },
    # ═══════════ AI Agent 与工具使用 ═══════════
    {
        "name": "AI Agent (智能体)",
        "node_type": "concept",
        "domain": "computer_science",
        "description": "以LLM为'大脑'的自主智能体，具备感知环境、规划任务、使用工具、执行动作的能力。"
        "核心循环：感知(Perception)→规划(Planning)→行动(Action)→反馈(Feedback)。"
        "代表项目：AutoGPT(2023)、MetaGPT、BabyAGI、OpenAI Assistants。"
        "从'对话AI'到'行动AI'的范式跃迁。",
        "summary": "LLM驱动的自主智能体——从对话到行动的范式跃迁",
        "source_info": "Significant Gravitas, 2023 (AutoGPT); 学术综述: Wang et al., 2023",
        "year": 2023,
        "tags": "Agent,智能体,自主,AutoGPT,规划,工具使用,行动",
    },
    {
        "name": "MCP (Model Context Protocol)",
        "node_type": "concept",
        "domain": "computer_science",
        "description": "Anthropic于2024年提出的开放协议，标准化LLM与外部数据源和工具的连接方式。"
        "采用Client-Server架构：LLM应用(Client)通过标准协议连接各种MCP Server(工具)。"
        "类比USB协议：统一接口标准，即插即用。"
        "定义了Resources(数据)、Tools(功能)、Prompts(模板)三种原语。"
        "目标是解决Agent生态的碎片化问题。",
        "summary": "LLM连接工具的USB协议——标准化AI与外部世界的交互",
        "source_info": "Anthropic, 2024, Model Context Protocol specification",
        "year": 2024,
        "tags": "MCP,协议,工具连接,Anthropic,标准化,Client-Server",
    },
    {
        "name": "Function Calling (函数调用)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "LLM根据用户意图自主决定调用哪个外部函数/API，并生成正确的参数。"
        "OpenAI在2023年GPT-3.5/4中首次引入，现已成为所有主流LLM的标准能力。"
        "流程：定义工具schema→LLM选择工具→生成参数JSON→执行→返回结果→LLM整合回复。"
        "是AI Agent实现工具使用的基础能力。",
        "summary": "LLM自主选择并调用外部API——Agent工具使用的基础",
        "source_info": "OpenAI, 2023, Function Calling in GPT-3.5/4",
        "year": 2023,
        "tags": "Function Calling,函数调用,工具使用,API,JSON Schema",
    },
    {
        "name": "多Agent系统 (Multi-Agent)",
        "node_type": "concept",
        "domain": "computer_science",
        "description": "多个AI Agent协作完成复杂任务，每个Agent有不同角色和专长。"
        "模式：辩论(Debate)、分工(Division)、层级(Hierarchy)、市场(Marketplace)。"
        "代表项目：MetaGPT(软件公司模拟)、ChatDev、CrewAI、AutoGen。"
        "类比人类组织：每个Agent如同团队成员，通过沟通协议协作。"
        "涌现出单Agent不具备的集体智慧。",
        "summary": "多个AI Agent分工协作——数字世界的团队协作",
        "source_info": "Hong et al., 2023, 'MetaGPT'; Microsoft, 2023, 'AutoGen'",
        "year": 2023,
        "tags": "多Agent,Multi-Agent,MetaGPT,AutoGen,协作,分工",
    },
    {
        "name": "ReAct 框架",
        "node_type": "method",
        "domain": "computer_science",
        "description": "Reasoning + Acting：LLM交替进行推理(Thought)和行动(Action)的框架。"
        "循环：Thought(分析当前状态)→Action(调用工具/搜索)→Observation(获取结果)→Thought→..."
        "将CoT(推理能力)与工具使用(行动能力)结合。"
        "是绝大多数Agent框架(LangChain、LlamaIndex)的底层模式。",
        "summary": "推理+行动交替循环——Agent框架的底层模式",
        "source_info": "Yao et al., 2022, 'ReAct: Synergizing Reasoning and Acting in LLMs'",
        "year": 2022,
        "tags": "ReAct,推理,行动,Agent,LangChain,Thought-Action",
    },
    {
        "name": "知识图谱 (Knowledge Graph)",
        "node_type": "concept",
        "domain": "computer_science",
        "description": "以图结构(节点+边)表示和组织知识的技术。节点表示实体，边表示关系。"
        "Google(2012)首次提出'知识图谱'概念。"
        "构建方法：实体抽取→关系抽取→知识融合→图存储(Neo4j/Neptune)。"
        "应用：搜索引擎、推荐系统、问答系统、RAG增强。"
        "与LLM结合(KG+LLM)是前沿方向：LLM构建KG、KG增强LLM推理。",
        "summary": "实体+关系的图结构知识组织——正是本项目的核心理念",
        "source_info": "Google, 2012, 'Introducing the Knowledge Graph'",
        "year": 2012,
        "tags": "知识图谱,KG,实体,关系,Neo4j,知识推理",
    },
    # ═══════════ 生成模型 ═══════════
    {
        "name": "生成对抗网络 (GAN)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "由生成器G和判别器D组成的对抗训练框架。"
        "G生成假数据欺骗D，D判别真假数据，两者在博弈中共同提升。"
        "理论基础：纳什均衡——G和D达到平衡时G生成的数据分布等于真实分布。"
        "变体繁多：DCGAN、StyleGAN(人脸生成)、Pix2Pix、CycleGAN(风格迁移)等。",
        "summary": "生成器vs判别器的对抗博弈——开创性的生成模型",
        "source_info": "Goodfellow et al., 2014, 'Generative Adversarial Nets'",
        "year": 2014,
        "tags": "GAN,生成对抗,生成器,判别器,对抗训练,纳什均衡",
    },
    {
        "name": "变分自编码器 (VAE)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "结合变分推断和自编码器的生成模型。将数据编码到连续潜在空间(latent space)，"
        "再从潜在空间采样解码生成新数据。"
        "与GAN互补：VAE生成结果更模糊但训练更稳定，有明确的概率解释(ELBO)。"
        "是Stable Diffusion中VAE组件的理论基础。",
        "summary": "编码→潜在空间→解码——有概率解释的生成模型",
        "source_info": "Kingma & Welling, 2013, 'Auto-Encoding Variational Bayes'",
        "year": 2013,
        "tags": "VAE,变分推断,潜在空间,ELBO,自编码器,生成",
    },
    {
        "name": "扩散模型 (Diffusion Models)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "正向过程：逐步给数据添加高斯噪声直到变成纯噪声。"
        "反向过程：学习去噪，从纯噪声逐步恢复为干净数据。"
        "质量超越GAN，且训练更稳定(无模式崩溃)。"
        "Stable Diffusion、DALL-E 2/3、Midjourney、Sora都基于扩散模型。"
        "物理类比：非平衡热力学中的扩散过程。",
        "summary": "加噪→去噪——从热力学扩散到AI图像生成的跨越",
        "source_info": "Ho et al., 2020, 'Denoising Diffusion Probabilistic Models' (DDPM)",
        "year": 2020,
        "tags": "扩散模型,DDPM,Stable Diffusion,去噪,Sora,图像生成",
    },
    {
        "name": "自回归生成模型",
        "node_type": "method",
        "domain": "computer_science",
        "description": "逐个token生成序列：每一步基于已生成的所有token预测下一个token的概率分布。"
        "P(x) = P(x1)·P(x2|x1)·P(x3|x1,x2)·...即链式法则分解联合概率。"
        "GPT系列的核心生成方式。也被引入图像生成(ImageGPT、VQVAE+自回归)。"
        "解码策略：贪心、Beam Search、Top-k、Top-p(nucleus)采样、温度控制。",
        "summary": "逐token预测下一个——GPT的核心生成方式",
        "source_info": "Radford et al., 2018, 'Improving Language Understanding by Generative Pre-Training' (GPT-1)",
        "year": 2018,
        "tags": "自回归,next token prediction,GPT,采样,Beam Search",
    },
    # ═══════════ 学习范式 ═══════════
    {
        "name": "对比学习 (Contrastive Learning)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "通过拉近正样本对(正例)、推远负样本对(负例)来学习数据表示。"
        "代表工作：SimCLR(2020)、MoCo、CLIP(图文对比)、DINO。"
        "CLIP将图像和文本映射到同一嵌入空间，实现零样本图像分类。"
        "是自监督学习的核心方法之一，无需人工标注即可学习强大表示。",
        "summary": "正例拉近、负例推远——无标注数据的表示学习利器",
        "source_info": "Chen et al., 2020, 'A Simple Framework for Contrastive Learning (SimCLR)'",
        "year": 2020,
        "tags": "对比学习,SimCLR,MoCo,CLIP,自监督,表示学习",
    },
    {
        "name": "自监督学习 (Self-Supervised Learning)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "从数据本身构造监督信号(pretext task)来学习表示，无需人工标注。"
        "NLP：掩码语言模型(BERT的MLM)、下一句预测。"
        "CV：对比学习(SimCLR)、掩码图像建模(MAE)。"
        "是预训练-微调范式的基础——预训练阶段本质上就是自监督学习。"
        "LeCun称之为'AI的暗物质'——可以利用海量无标注数据。",
        "summary": "从数据自身构造监督信号——利用海量无标注数据的密钥",
        "source_info": "LeCun & Misra, 2021; He et al., 2022, 'Masked Autoencoders (MAE)'",
        "year": 2019,
        "tags": "自监督,SSL,MAE,MLM,pretext task,无标注",
    },
    {
        "name": "知识蒸馏 (Knowledge Distillation)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将大模型(teacher)的知识迁移到小模型(student)中。"
        "Student不仅学hard label，还学teacher的soft output(概率分布)。"
        "软标签包含类间关系信息(如'猫'和'虎'的概率都高→它们相似)。"
        "应用场景：模型压缩、部署优化、知识传递。"
        "类比教育：老师教学生时不只给答案，还传授思考方式。",
        "summary": "大模型教小模型——知识压缩与传承",
        "source_info": "Hinton et al., 2015, 'Distilling the Knowledge in a Neural Network'",
        "year": 2015,
        "tags": "知识蒸馏,teacher,student,模型压缩,软标签,部署",
    },
    {
        "name": "联邦学习 (Federated Learning)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "多方协作训练模型但不共享原始数据——'数据不动模型动'。"
        "每个参与方本地训练→上传梯度/参数→服务器聚合→下发全局模型。"
        "解决数据隐私(GDPR)、数据孤岛问题。"
        "Google在2017年用于Gboard键盘的下一词预测。"
        "挑战：Non-IID数据、通信效率、对抗攻击。",
        "summary": "数据不动模型动——保护隐私的分布式训练",
        "source_info": "McMahan et al., 2017, 'Communication-Efficient Learning of Deep Networks'",
        "year": 2017,
        "tags": "联邦学习,隐私保护,分布式,数据孤岛,GDPR,聚合",
    },
    {
        "name": "多模态学习 (Multimodal Learning)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "融合多种模态(文本、图像、音频、视频、3D等)数据进行学习和推理。"
        "里程碑：CLIP(图文对齐)→DALL-E(文生图)→GPT-4V(图文理解)→Sora(文生视频)。"
        "核心挑战：不同模态的对齐(alignment)与融合(fusion)。"
        "人脑天然是多模态的——视觉+听觉+触觉+语言的统一认知。",
        "summary": "图文音视频的统一理解与生成——走向人类般的多感官AI",
        "source_info": "Radford et al., 2021, 'Learning Transferable Visual Models (CLIP)'; OpenAI, 2024, Sora",
        "year": 2021,
        "tags": "多模态,CLIP,GPT-4V,Sora,文生图,模态对齐",
    },
    {
        "name": "图神经网络 (GNN)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "在图结构数据上进行深度学习的方法，通过消息传递(message passing)聚合邻居信息。"
        "GCN(2017)→GAT(注意力图网络)→GraphSAGE(归纳学习)→GIN。"
        "应用：社交网络分析、分子性质预测(药物发现)、推荐系统、知识图谱推理。"
        "与知识图谱天然结合：GNN在KG上做链接预测、实体分类。",
        "summary": "图结构上的深度学习——消息传递与邻居聚合",
        "source_info": "Kipf & Welling, 2017, 'Semi-Supervised Classification with GCN'",
        "year": 2017,
        "tags": "GNN,图神经网络,GCN,GAT,消息传递,图学习",
    },
    {
        "name": "量化与模型压缩",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将模型参数从高精度(FP32/FP16)量化到低精度(INT8/INT4甚至1-bit)以减少存储和计算。"
        "GPTQ、AWQ、GGUF(llama.cpp)使得大模型能在消费级硬件上运行。"
        "其他压缩技术：剪枝(pruning)、低秩分解、稀疏化。"
        "与知识蒸馏互补：蒸馏压缩知识，量化压缩数值精度。",
        "summary": "FP32→INT4——让大模型在手机上运行的关键技术",
        "source_info": "Frantar et al., 2022, 'GPTQ'; Lin et al., 2023, 'AWQ'",
        "year": 2022,
        "tags": "量化,INT4,GPTQ,AWQ,模型压缩,剪枝,gguf",
    },
]

# ══════════════════════════════════════════════════════════════
#  插入知识节点
# ══════════════════════════════════════════════════════════════

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
    print(f"  ✅ [{n['node_type']}] {n['name']}")

print(f"\n📌 插入 {inserted} 个 CS 知识节点")

# ══════════════════════════════════════════════════════════════
#  关联关系
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
    # ═══════════════════════════════════════════════════════════
    #  Part 1: 深度学习基础内部关联
    # ═══════════════════════════════════════════════════════════
    (
        N.get("反向传播算法"),
        N.get("人工神经网络"),
        "ENABLES",
        "knowledge_node",
        "knowledge_node",
        "反向传播是训练多层神经网络的核心算法，使深度学习成为可能",
    ),
    (
        N.get("梯度下降与优化器"),
        N.get("反向传播算法"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "反向传播计算梯度，梯度下降利用梯度更新参数——二者缺一不可",
    ),
    (
        N.get("深度学习"),
        N.get("人工神经网络"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "深度学习是多层神经网络的现代化实践，本质上是'深层'的神经网络",
    ),
    (
        N.get("深度学习"),
        N.get("反向传播算法"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "反向传播是深度学习训练的基础引擎",
    ),
    (
        N.get("卷积神经网络 (CNN)"),
        N.get("深度学习"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "CNN是深度学习中处理视觉数据的核心架构",
    ),
    (
        N.get("循环神经网络 (RNN/LSTM)"),
        N.get("深度学习"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "RNN/LSTM是深度学习中处理序列数据的经典架构",
    ),
    (
        N.get("批量归一化 (Batch Normalization)"),
        N.get("深度学习"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "BN使深度网络训练更稳定、更快收敛",
    ),
    (
        N.get("Dropout 正则化"),
        N.get("深度学习"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "Dropout通过随机丢弃防止深度网络过拟合",
    ),
    (
        N.get("残差连接 (ResNet)"),
        N.get("深度学习"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "残差连接突破了深层网络的退化瓶颈，使超深网络成为可能",
    ),
    (
        N.get("残差连接 (ResNet)"),
        N.get("卷积神经网络 (CNN)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "ResNet是CNN架构的革命性改进，从数十层扩展到数百层",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 2: Transformer 与 NLP 革命
    # ═══════════════════════════════════════════════════════════
    (
        N.get("Transformer 架构"),
        N.get("注意力机制"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "Transformer将注意力从辅助机制升级为核心架构——'Attention Is All You Need'",
    ),
    (
        N.get("自注意力机制 (Self-Attention)"),
        N.get("注意力机制"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "自注意力是注意力机制的自回指版本，序列内部互相关注",
    ),
    (
        N.get("Transformer 架构"),
        N.get("自注意力机制 (Self-Attention)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "多头自注意力是Transformer的核心组件",
    ),
    (
        N.get("Transformer 架构"),
        N.get("残差连接 (ResNet)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "Transformer每个子层都使用残差连接+LayerNorm",
    ),
    (
        N.get("Transformer 架构"),
        N.get("位置编码 (Positional Encoding)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "位置编码弥补了自注意力的位置无关性",
    ),
    (
        N.get("Transformer 架构"),
        N.get("循环神经网络 (RNN/LSTM)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "Transformer用并行注意力取代了RNN的递归结构，训练效率大幅提升",
    ),
    (
        N.get("词嵌入 (Word Embedding)"),
        N.get("Transformer 架构"),
        "ENABLES",
        "knowledge_node",
        "knowledge_node",
        "词嵌入将离散token映射为连续向量，是Transformer输入的基础",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 3: LLM 生态系统
    # ═══════════════════════════════════════════════════════════
    (
        N.get("大语言模型 (LLM)"),
        N.get("Transformer 架构"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "LLM基于Transformer架构(通常是decoder-only)构建",
    ),
    (
        N.get("大语言模型 (LLM)"),
        N.get("预训练-微调范式"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "LLM的训练流程：大规模预训练→指令微调→RLHF对齐",
    ),
    (
        N.get("大语言模型 (LLM)"),
        N.get("自回归生成模型"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "GPT系列LLM本质上是自回归语言模型——逐token预测下一个",
    ),
    (
        N.get("大语言模型 (LLM)"),
        N.get("Scaling Law (规模定律)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "Scaling Law指导了LLM的训练策略——更大模型+更多数据=更强能力",
    ),
    (
        N.get("涌现能力 (Emergent Abilities)"),
        N.get("大语言模型 (LLM)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "涌现能力是LLM规模增长后的惊人副产物",
    ),
    (
        N.get("上下文学习 (In-Context Learning)"),
        N.get("大语言模型 (LLM)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "ICL是GPT-3展示的核心涌现能力——不改权重就能学新任务",
    ),
    (
        N.get("预训练-微调范式"),
        N.get("迁移学习"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "预训练-微调是迁移学习在深度学习时代最成功的实践",
    ),
    (
        N.get("RLHF (人类反馈强化学习)"),
        N.get("强化学习"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "RLHF将RL应用于LLM对齐：用人类偏好训练奖励模型+PPO优化",
    ),
    (
        N.get("RLHF (人类反馈强化学习)"),
        N.get("大语言模型 (LLM)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "RLHF是ChatGPT对齐的关键技术——让LLM更有帮助、更安全",
    ),
    (
        N.get("思维链推理 (Chain of Thought)"),
        N.get("大语言模型 (LLM)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "CoT提示让LLM展开推理过程，大幅提升数学和逻辑推理能力",
    ),
    (
        N.get("思维链推理 (Chain of Thought)"),
        N.get("提示工程 (Prompt Engineering)"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "CoT是提示工程中最重要的技术之一",
    ),
    (
        N.get("提示工程 (Prompt Engineering)"),
        N.get("上下文学习 (In-Context Learning)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "提示工程的理论基础是ICL——通过精心设计prompt引导模型行为",
    ),
    (
        N.get("检索增强生成 (RAG)"),
        N.get("大语言模型 (LLM)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "RAG通过检索外部知识解决LLM的幻觉和知识过时问题",
    ),
    (
        N.get("检索增强生成 (RAG)"),
        N.get("知识图谱 (Knowledge Graph)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "RAG+KG：知识图谱是RAG的高质量知识来源，结构化数据比文本检索更精确",
    ),
    (
        N.get("混合专家模型 (MoE)"),
        N.get("大语言模型 (LLM)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "MoE让LLM在保持推理效率的同时大幅增加参数量",
    ),
    (
        N.get("混合专家模型 (MoE)"),
        N.get("Transformer 架构"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "MoE替换Transformer中的FFN层，每层由多个专家子网络组成",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 4: AI Agent 与工具使用
    # ═══════════════════════════════════════════════════════════
    (
        N.get("AI Agent (智能体)"),
        N.get("大语言模型 (LLM)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "LLM是AI Agent的'大脑'——提供理解、推理和决策能力",
    ),
    (
        N.get("AI Agent (智能体)"),
        N.get("Function Calling (函数调用)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "Function Calling是Agent使用工具的基础能力",
    ),
    (
        N.get("AI Agent (智能体)"),
        N.get("ReAct 框架"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "ReAct的推理+行动循环是Agent框架的底层模式",
    ),
    (
        N.get("MCP (Model Context Protocol)"),
        N.get("AI Agent (智能体)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "MCP标准化了Agent与工具的连接方式——Agent生态的'USB协议'",
    ),
    (
        N.get("MCP (Model Context Protocol)"),
        N.get("Function Calling (函数调用)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "MCP在Function Calling基础上提供了标准化的Client-Server协议",
    ),
    (
        N.get("多Agent系统 (Multi-Agent)"),
        N.get("AI Agent (智能体)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "多Agent系统由多个Agent协作组成，涌现集体智慧",
    ),
    (
        N.get("ReAct 框架"),
        N.get("思维链推理 (Chain of Thought)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "ReAct = CoT(推理能力) + 工具使用(行动能力)的结合",
    ),
    (
        N.get("Function Calling (函数调用)"),
        N.get("大语言模型 (LLM)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "Function Calling是LLM从'纯文本'到'能调用API'的关键能力跃迁",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 5: 生成模型家族
    # ═══════════════════════════════════════════════════════════
    (
        N.get("生成对抗网络 (GAN)"),
        N.get("深度学习"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "GAN是深度学习中的经典生成模型框架",
    ),
    (
        N.get("变分自编码器 (VAE)"),
        N.get("深度学习"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "VAE是深度学习中的概率生成模型",
    ),
    (
        N.get("扩散模型 (Diffusion Models)"),
        N.get("深度学习"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "扩散模型是深度学习中最新的生成模型范式",
    ),
    (
        N.get("扩散模型 (Diffusion Models)"),
        N.get("变分自编码器 (VAE)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "扩散模型的数学推导与VAE有深层联系，DDPM可以看作特殊的层级VAE",
    ),
    (
        N.get("扩散模型 (Diffusion Models)"),
        N.get("生成对抗网络 (GAN)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "扩散模型在图像生成质量上超越了GAN，且训练更稳定",
    ),
    (
        N.get("自回归生成模型"),
        N.get("大语言模型 (LLM)"),
        "ENABLES",
        "knowledge_node",
        "knowledge_node",
        "自回归生成是LLM的核心生成方式——逐token预测下一个",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 6: 学习范式与方法
    # ═══════════════════════════════════════════════════════════
    (
        N.get("自监督学习 (Self-Supervised Learning)"),
        N.get("预训练-微调范式"),
        "ENABLES",
        "knowledge_node",
        "knowledge_node",
        "预训练阶段本质上就是自监督学习——从海量无标注数据学习表示",
    ),
    (
        N.get("对比学习 (Contrastive Learning)"),
        N.get("自监督学习 (Self-Supervised Learning)"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "对比学习是自监督学习的核心方法之一",
    ),
    (
        N.get("对比学习 (Contrastive Learning)"),
        N.get("多模态学习 (Multimodal Learning)"),
        "ENABLES",
        "knowledge_node",
        "knowledge_node",
        "CLIP用对比学习将图像和文本对齐到同一空间，开创多模态新范式",
    ),
    (
        N.get("知识蒸馏 (Knowledge Distillation)"),
        N.get("量化与模型压缩"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "蒸馏压缩知识结构，量化压缩数值精度——两种互补的模型压缩方案",
    ),
    (
        N.get("知识蒸馏 (Knowledge Distillation)"),
        N.get("迁移学习"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "蒸馏是一种特殊的迁移学习：从大模型(teacher)到小模型(student)迁移知识",
    ),
    (
        N.get("多模态学习 (Multimodal Learning)"),
        N.get("大语言模型 (LLM)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "GPT-4V、Gemini等多模态大模型在LLM基础上扩展视觉/音频理解能力",
    ),
    (
        N.get("图神经网络 (GNN)"),
        N.get("知识图谱 (Knowledge Graph)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "GNN在知识图谱上做链接预测、实体分类——图结构的天然搭档",
    ),
    (
        N.get("图神经网络 (GNN)"),
        N.get("深度学习"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "GNN是深度学习在图结构数据上的扩展",
    ),
    (
        N.get("联邦学习 (Federated Learning)"),
        N.get("深度学习"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "联邦学习解决深度学习训练中的数据隐私问题——数据不动模型动",
    ),
    (
        N.get("量化与模型压缩"),
        N.get("大语言模型 (LLM)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "GPTQ/AWQ等量化技术让大语言模型能在消费级硬件上运行",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 7: 与已有论文的关联
    # ═══════════════════════════════════════════════════════════
    (
        N.get("Transformer 架构"),
        P.get("Attention Is All You Need"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "Transformer架构的奠基论文",
    ),
    (
        N.get("Transformer 架构"),
        P.get("ViT"),
        "ENABLES",
        "knowledge_node",
        "paper",
        "ViT将Transformer从NLP迁移到计算机视觉",
    ),
    (
        N.get("Transformer 架构"),
        P.get("Swin Transformer"),
        "ENABLES",
        "knowledge_node",
        "paper",
        "Swin Transformer用层级化窗口注意力改进了ViT",
    ),
    (
        N.get("自注意力机制 (Self-Attention)"),
        P.get("Attention Is All You Need"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "该论文首次将自注意力作为核心架构（而非辅助增强）",
    ),
    (
        N.get("预训练-微调范式"),
        P.get("BERT"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "BERT开创了NLP预训练-微调范式",
    ),
    (
        N.get("自监督学习 (Self-Supervised Learning)"),
        P.get("BERT"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "BERT的MLM和NSP都是自监督学习任务",
    ),
    (
        N.get("自监督学习 (Self-Supervised Learning)"),
        P.get("MAE"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "MAE将掩码自监督学习从NLP扩展到计算机视觉",
    ),
    (
        N.get("对比学习 (Contrastive Learning)"),
        P.get("SimCLR"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "SimCLR是对比学习的标志性工作——简单框架，强大效果",
    ),
    (
        N.get("扩散模型 (Diffusion Models)"),
        P.get("Stable Diffusion"),
        "ENABLES",
        "knowledge_node",
        "paper",
        "Stable Diffusion = 扩散模型 + VAE + CLIP 的工程化集大成",
    ),
    (
        N.get("变分自编码器 (VAE)"),
        P.get("Stable Diffusion"),
        "ENABLES",
        "knowledge_node",
        "paper",
        "Stable Diffusion使用VAE将图像压缩到潜在空间再做扩散",
    ),
    (
        N.get("生成对抗网络 (GAN)"),
        P.get("GAN"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "GAN知识节点对应的原始论文",
    ),
    (
        N.get("生成对抗网络 (GAN)"),
        P.get("DCGAN"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "DCGAN引入卷积结构稳定GAN训练，是GAN实用化的关键一步",
    ),
    (
        N.get("生成对抗网络 (GAN)"),
        P.get("SRGAN"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "SRGAN将GAN应用于超分辨率——GAN的经典应用场景",
    ),
    (
        N.get("残差连接 (ResNet)"),
        P.get("ResNet"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "残差连接知识节点对应的原始论文",
    ),
    (
        N.get("卷积神经网络 (CNN)"),
        P.get("CIFAR-10"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "CIFAR-10是CNN性能评估的经典基准数据集",
    ),
    (
        N.get("深度学习"),
        P.get("PyTorch"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "PyTorch是最主流的深度学习框架",
    ),
    (
        N.get("图神经网络 (GNN)"),
        P.get("DGCNN"),
        "RELATED_TO",
        "knowledge_node",
        "paper",
        "DGCNN是在点云上应用图卷积的代表工作",
    ),
    (
        N.get("RLHF (人类反馈强化学习)"),
        P.get("AlphaFold"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "paper",
        "AlphaFold的迭代结构预测过程融合了RL思想，RLHF在蛋白质设计中也有潜力",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 8: 与其他领域知识的跨域关联
    # ═══════════════════════════════════════════════════════════
    (
        N.get("涌现能力 (Emergent Abilities)"),
        N.get("涌现与还原论"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "LLM的涌现能力与哲学/复杂系统中的涌现概念高度对应——整体大于部分之和",
    ),
    (
        N.get("Scaling Law (规模定律)"),
        N.get("幂律分布"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "Scaling Law本质是幂律关系L∝N^α，与物理/经济中的幂律分布同源",
    )
    if N.get("幂律分布")
    else None,
    (
        N.get("联邦学习 (Federated Learning)"),
        N.get("六度分隔与小世界网络"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "联邦学习的去中心化拓扑与小世界网络的信息传播模式有结构相似性",
    )
    if N.get("六度分隔与小世界网络")
    else None,
    (
        N.get("多Agent系统 (Multi-Agent)"),
        N.get("捕食者-猎物动力学（Lotka-Volterra）"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "多Agent的竞争与合作动力学类似生态系统中的种群互动模式",
    )
    if N.get("捕食者-猎物动力学（Lotka-Volterra）")
    else None,
    (
        N.get("多Agent系统 (Multi-Agent)"),
        N.get("蚁群觅食行为"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "蚂蚁社会的分工协作+信息素通讯 ↔ 多Agent的角色分配+消息传递",
    )
    if N.get("蚁群觅食行为")
    else None,
    (
        N.get("知识蒸馏 (Knowledge Distillation)"),
        N.get("遗忘曲线与间隔重复"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "师生模型的知识传递 ↔ 教学心理学中的知识传授与记忆巩固",
    )
    if N.get("遗忘曲线与间隔重复")
    else None,
    (
        N.get("Dropout 正则化"),
        N.get("免疫系统自适应防御"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "Dropout随机失活增强鲁棒性 ↔ 免疫系统通过多样化抗体增强防御",
    )
    if N.get("免疫系统自适应防御")
    else None,
    (
        N.get("扩散模型 (Diffusion Models)"),
        N.get("热力学第二定律（熵增原理）"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "正向扩散=熵增(数据→噪声)，反向去噪=局部熵减(噪声→数据)——热力学的AI映射",
    )
    if N.get("热力学第二定律（熵增原理）")
    else None,
    (
        N.get("梯度下降与优化器"),
        N.get("最小作用量原理"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "梯度下降沿最陡路径下降 ↔ 最小作用量原理：自然选择能量最低路径",
    )
    if N.get("最小作用量原理")
    else None,
    (
        N.get("AI Agent (智能体)"),
        N.get("控制论（Cybernetics）"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "Agent的感知-规划-行动-反馈循环是控制论核心思想的现代AI实现",
    )
    if N.get("控制论（Cybernetics）")
    else None,
    (
        N.get("生成对抗网络 (GAN)"),
        N.get("纳什均衡"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "GAN训练的目标点是纳什均衡：生成器和判别器都无法单方面改进",
    )
    if N.get("纳什均衡")
    else None,
    (
        N.get("对比学习 (Contrastive Learning)"),
        N.get("信息熵与交叉熵"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "对比学习的InfoNCE损失基于互信息最大化，与信息熵理论紧密关联",
    ),
    (
        N.get("知识图谱 (Knowledge Graph)"),
        N.get("图论与网络科学"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "知识图谱是图论在知识表示领域的应用——节点=实体，边=关系",
    )
    if N.get("图论与网络科学")
    else None,
    (
        N.get("自回归生成模型"),
        N.get("贝叶斯定理"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "自回归模型的链式条件概率分解P(x)=∏P(xi|x<i)根植于概率论/贝叶斯思想",
    )
    if N.get("贝叶斯定理")
    else None,
    (
        N.get("词嵌入 (Word Embedding)"),
        N.get("傅里叶变换"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "傅里叶将信号映射到频域 ↔ Word2Vec将词映射到语义空间——都是'表示变换'",
    )
    if N.get("傅里叶变换")
    else None,
    (
        N.get("批量归一化 (Batch Normalization)"),
        N.get("反馈控制（负反馈）"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "BN将层输入归一化到标准分布 ↔ 负反馈将系统输出稳定在目标值附近",
    )
    if N.get("反馈控制（负反馈）")
    else None,
]

# 过滤掉 None（来自条件表达式中不存在的节点）
RELATIONS = [r for r in RELATIONS if r is not None]

# ── 插入关系 ──
added = 0
skipped = 0

for rel in RELATIONS:
    src_id, tgt_id, rtype, stype, ttype, desc = rel
    if src_id is None or tgt_id is None:
        skipped += 1
        continue
    if (src_id, tgt_id) in existing_rels:
        skipped += 1
        continue

    rid = gen_id()
    cur.execute(
        "INSERT INTO relations (id, source_id, target_id, relation_type, "
        "source_type, target_type, description, confidence, ai_generated, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rid, src_id, tgt_id, rtype, stype, ttype, desc, 1.0, False, "confirmed", now),
    )
    existing_rels.add((src_id, tgt_id))
    added += 1
    print(f"  🔗 {rtype}: ...→... | {desc[:50]}")

print(f"\n📌 新增 {added} 条关系 (跳过 {skipped} 条)")

conn.commit()
conn.close()

# ── 统计 ──
conn2 = sqlite3.connect(DB_PATH)
c = conn2.cursor()
kn_count = c.execute("SELECT COUNT(*) FROM knowledge_nodes").fetchone()[0]
p_count = c.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
r_count = c.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
cs_count = c.execute(
    "SELECT COUNT(*) FROM knowledge_nodes WHERE domain='computer_science'"
).fetchone()[0]
d_count = c.execute("SELECT COUNT(DISTINCT domain) FROM knowledge_nodes").fetchone()[0]
conn2.close()

print(f"\n{'=' * 50}")
print("📊 数据库全局统计:")
print(f"   知识节点: {kn_count} (其中CS: {cs_count})")
print(f"   论    文: {p_count}")
print(f"   关    系: {r_count}")
print(f"   领    域: {d_count}")
print(f"   总节点数: {kn_count + p_count}")
print(f"{'=' * 50}")
