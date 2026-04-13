"""
补充各领域内部节点之间的关联关系
——让每个领域的知识节点形成内聚网络

覆盖领域：life_science, art, history, medicine, military_science,
cognitive_science, biology, physics, mathematics, psychology,
chemistry, ecology, sociology, engineering
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "../backend/knowledge_nexus.db"


def get_id():
    return uuid.uuid4().hex[:12]


now = datetime.utcnow().isoformat()

# 所有新增的领域内关系
# 格式：(source_name, target_name, relation_type, description)
relations_def = [
    # ===================== 生命科学 (life_science) =====================
    (
        "基因调控网络 (Gene Regulatory Network)",
        "表观遗传学 (Epigenetics)",
        "RELATED_TO",
        "基因调控网络的表达受表观遗传修饰调控——甲基化和组蛋白修饰改变基因调控网络的活性模式。",
    ),
    (
        "基因调控网络 (Gene Regulatory Network)",
        "细胞信号传导 (Cell Signaling)",
        "RELATED_TO",
        "外部信号通过信号传导通路激活转录因子，进而调控基因表达网络。信号传导是基因调控网络的上游输入。",
    ),
    (
        "细胞信号传导 (Cell Signaling)",
        "干细胞分化 (Stem Cell Differentiation)",
        "ENABLES",
        "干细胞分化由特定的信号分子(生长因子、形态发生素)驱动，信号传导决定分化方向。",
    ),
    (
        "表观遗传学 (Epigenetics)",
        "干细胞分化 (Stem Cell Differentiation)",
        "ENABLES",
        "分化过程中表观遗传修饰逐步锁定基因表达模式——甲基化积累使分化不可逆。",
    ),
    (
        "蛋白质折叠 (Protein Folding)",
        "细胞信号传导 (Cell Signaling)",
        "RELATED_TO",
        "蛋白质的3D结构决定其功能——受体和信号蛋白必须正确折叠才能参与信号传导。",
    ),
    (
        "趋化性 (Chemotaxis)",
        "细胞信号传导 (Cell Signaling)",
        "BUILDS_ON",
        "趋化性依赖细胞表面受体检测化学浓度梯度，通过胞内信号级联控制运动方向。",
    ),
    (
        "生物钟与昼夜节律 (Circadian Rhythm)",
        "基因调控网络 (Gene Regulatory Network)",
        "BUILDS_ON",
        "生物钟由转录-翻译反馈环路驱动(CLOCK/BMAL1/PER/CRY)，是基因调控网络的一种周期性振荡模式。",
    ),
    (
        "共生与协同进化 (Symbiosis and Co-evolution)",
        "趋化性 (Chemotaxis)",
        "RELATED_TO",
        "共生关系的建立常依赖化学信号识别——如根瘤菌通过趋化性找到豆科植物根部。",
    ),
    (
        "共生与协同进化 (Symbiosis and Co-evolution)",
        "基因调控网络 (Gene Regulatory Network)",
        "RELATED_TO",
        "长期共生导致基因调控网络的协同适应——线粒体基因组与核基因组的协调表达就是内共生进化的产物。",
    ),
    # ===================== 艺术 (art) =====================
    (
        "黄金比例 (Golden Ratio)",
        "和声学 (Harmony / Music Theory)",
        "RELATED_TO",
        "黄金比例不仅出现在视觉艺术中，也存在于音乐结构中——巴赫作品中黄金分割点常放置高潮段。数学和谐统一了视听美感。",
    ),
    (
        "黄金比例 (Golden Ratio)",
        "透视法 (Perspective / Projection)",
        "RELATED_TO",
        "文艺复兴画家在透视构图中广泛应用黄金比例确定消失点和画面分割——将数学和谐融入空间表达。",
    ),
    (
        "极简主义 (Minimalism)",
        "创造力与组合创新 (Combinatorial Creativity)",
        "RELATED_TO",
        "极简主义的约束反而激发创造力——在有限元素中寻找最大表达，约束成为创新的催化剂。",
    ),
    (
        "即兴创作 (Improvisation)",
        "和声学 (Harmony / Music Theory)",
        "BUILDS_ON",
        "即兴创作建立在深厚的和声学基础上——爵士乐手必须熟练掌握和弦进行和音阶，才能在规则框架内自由发挥。",
    ),
    (
        "即兴创作 (Improvisation)",
        "创造力与组合创新 (Combinatorial Creativity)",
        "RELATED_TO",
        "即兴创作是创造力的实时体现——在已有知识(和声、旋律模式)的基础上实时进行组合创新。",
    ),
    (
        "生成式艺术 (Generative Art)",
        "创造力与组合创新 (Combinatorial Creativity)",
        "BUILDS_ON",
        "生成式艺术用算法实现组合创新——通过程序化的规则组合产生新的视觉/听觉艺术作品。",
    ),
    (
        "透视法 (Perspective / Projection)",
        "黄金比例 (Golden Ratio)",
        "RELATED_TO",
        "文艺复兴大师将透视法和黄金比例结合，创造出令人信服的三维空间感和视觉和谐。",
    ),
    # ===================== 历史 (history) =====================
    (
        "历史周期律 (Dynastic Cycle)",
        "以史为鉴 (Learning from History)",
        "ENABLES",
        "历史周期律的存在使'以史为鉴'成为可能——如果历史是纯随机的就无法借鉴。正是因为有周期性模式，历史经验才有预测价值。",
    ),
    (
        "技术革命与范式转换 (Technological Revolutions)",
        "黑天鹅事件 (Black Swan Events)",
        "RELATED_TO",
        "重大技术革命往往是黑天鹅事件——事前很少有人预见到互联网、智能手机、ChatGPT会如此深刻地改变世界。",
    ),
    (
        "修昔底德陷阱 (Thucydides Trap)",
        "文明冲突论 (Clash of Civilizations)",
        "RELATED_TO",
        "修昔底德陷阱(权力转移冲突)与文明冲突论(文化差异冲突)是理解国际冲突的两个互补框架。",
    ),
    (
        "黑天鹅事件 (Black Swan Events)",
        "历史周期律 (Dynastic Cycle)",
        "RELATED_TO",
        "黑天鹅事件(战争、瘟疫、革命)常常是打破历史周期、触发新周期的关键转折点。",
    ),
    (
        "长尾效应 (The Long Tail)",
        "技术革命与范式转换 (Technological Revolutions)",
        "RELATED_TO",
        "互联网技术革命催生了长尾效应——数字化分发使小众内容的累积价值得以释放。",
    ),
    (
        "以史为鉴 (Learning from History)",
        "文明冲突论 (Clash of Civilizations)",
        "RELATED_TO",
        "以史为鉴的深层挑战：不同文明对同一历史事件有截然不同的解读——'鉴'出什么取决于文明视角。",
    ),
    # ===================== 医学 (medicine) =====================
    (
        "免疫记忆与疫苗 (Immunological Memory)",
        "耐药性与军备竞赛 (Antibiotic Resistance)",
        "RELATED_TO",
        "免疫记忆(适应性免疫)与耐药性(病原体进化)是同一场军备竞赛的两面——宿主和病原体互相驱动对方进化。",
    ),
    (
        "流行病学 SIR 模型 (Epidemiological Modeling)",
        "免疫记忆与疫苗 (Immunological Memory)",
        "RELATED_TO",
        "疫苗通过建立群体免疫记忆改变SIR模型参数——接种率提高→R₀有效降低→传播被遏制。",
    ),
    (
        "药物靶点与锁钥模型 (Drug Target / Lock-and-Key)",
        "耐药性与军备竞赛 (Antibiotic Resistance)",
        "RELATED_TO",
        "耐药性的分子机制：病原体通过突变改变靶点结构(锁变形了)，使药物(钥匙)无法结合。",
    ),
    (
        "安慰剂效应 (Placebo Effect)",
        "临床诊断推理 (Clinical Reasoning)",
        "RELATED_TO",
        "安慰剂效应是临床诊断推理中的干扰因素——患者症状改善可能来自安慰剂而非真实疗效，需要双盲对照排除。",
    ),
    (
        "循证医学 (Evidence-Based Medicine)",
        "流行病学 SIR 模型 (Epidemiological Modeling)",
        "RELATED_TO",
        "循证医学依赖流行病学方法提供证据——随机对照试验、队列研究、病例对照研究都是流行病学工具。",
    ),
    (
        "药物靶点与锁钥模型 (Drug Target / Lock-and-Key)",
        "临床诊断推理 (Clinical Reasoning)",
        "RELATED_TO",
        "准确的临床诊断确定疾病机制→找到正确靶点→选择对应药物。诊断推理是精准用药的前提。",
    ),
    # ===================== 军事学 (military_science) =====================
    (
        "战争迷雾 (Fog of War)",
        "知彼知己 (Know Your Enemy and Yourself)",
        "RELATED_TO",
        "战争迷雾是'知彼知己'的最大障碍——信息不完整、不确定、甚至被刻意误导，使'知'变得极其困难。",
    ),
    (
        "兵者诡道 (War is Deception)",
        "战争迷雾 (Fog of War)",
        "ENABLES",
        "诡道(欺骗)主动制造和加深战争迷雾——通过虚假信息增加对手的不确定性。",
    ),
    (
        "OODA 循环 (Observe-Orient-Decide-Act)",
        "知彼知己 (Know Your Enemy and Yourself)",
        "BUILDS_ON",
        "OODA循环的Observe和Orient阶段就是在实现'知彼知己'——快速获取和理解信息。",
    ),
    (
        "集中优势兵力 (Principle of Concentration)",
        "兰切斯特方程 (Lanchester's Laws)",
        "BUILDS_ON",
        "兰切斯特平方律为'集中优势兵力'提供了数学证明——集中兵力的战斗力优势是兵力比的平方。",
    ),
    (
        "博弈对抗与零和博弈 (Adversarial Game Theory)",
        "兵者诡道 (War is Deception)",
        "RELATED_TO",
        "欺骗是博弈中的核心策略——信号博弈(signaling game)研究如何通过发送虚假/真实信号获取优势。",
    ),
    (
        "博弈对抗与零和博弈 (Adversarial Game Theory)",
        "知彼知己 (Know Your Enemy and Yourself)",
        "RELATED_TO",
        "博弈论的核心就是理解对手(知彼)和评估自身策略(知己)——完全信息vs不完全信息博弈。",
    ),
    (
        "不战而屈人之兵 (Win Without Fighting)",
        "博弈对抗与零和博弈 (Adversarial Game Theory)",
        "RELATED_TO",
        "'不战而胜'在博弈论中对应威慑策略(deterrence)——通过可置信威胁使对手理性选择退让。",
    ),
    # ===================== 认知科学 (cognitive_science) =====================
    (
        "双系统理论 (Dual Process Theory)",
        "选择性注意 (Selective Attention)",
        "RELATED_TO",
        "系统1的快速响应依赖选择性注意的自动化过滤——只有通过注意力筛选的信息才进入认知处理。",
    ),
    (
        "双系统理论 (Dual Process Theory)",
        "认知负荷理论 (Cognitive Load Theory)",
        "RELATED_TO",
        "系统2推理消耗大量认知资源，受认知负荷限制。认知负荷过高时，人倾向于切换到系统1(直觉模式)。",
    ),
    (
        "元认知 (Metacognition)",
        "双系统理论 (Dual Process Theory)",
        "BUILDS_ON",
        "元认知是监控系统1和系统2的'执行系统'——知道何时该信任直觉(系统1)，何时需要深思(系统2)。",
    ),
    (
        "元认知 (Metacognition)",
        "迁移理论 (Transfer of Learning)",
        "RELATED_TO",
        "有效迁移需要元认知能力——意识到当前问题与过去经验的相似性，主动调用相关知识图式。",
    ),
    (
        "具身认知 (Embodied Cognition)",
        "选择性注意 (Selective Attention)",
        "RELATED_TO",
        "具身认知强调注意力不仅是大脑功能，还涉及身体朝向(头部转向、眼球运动)和环境中的行动可能性(affordances)。",
    ),
    # ===================== 生物学 (biology) =====================
    (
        "自然选择与进化",
        "基因表达与调控",
        "RELATED_TO",
        "自然选择作用于表型，而表型由基因表达调控决定。基因调控机制的变异是进化的重要原料。",
    ),
    (
        "自然选择与进化",
        "免疫系统应答",
        "RELATED_TO",
        "免疫系统的克隆选择是体细胞水平的'自然选择'——有效抗体被选择扩增，无效抗体被淘汰。",
    ),
    (
        "基因表达与调控",
        "免疫系统应答",
        "RELATED_TO",
        "免疫应答依赖精密的基因表达调控：V(D)J重组、类别转换、细胞因子调控等都是基因调控的具体实例。",
    ),
    (
        "蚁群觅食行为",
        "自然选择与进化",
        "RELATED_TO",
        "蚁群的觅食行为模式是长期自然选择塑造的结果——信息素通信策略使群体在进化中获得觅食优势。",
    ),
    # ===================== 物理学 (physics) =====================
    (
        "热力学第二定律（熵增）",
        "金属退火过程",
        "ENABLES",
        "退火利用热力学第二定律：加热使系统跨越能量势垒(熵增)，缓慢冷却使系统在更大的状态空间中找到低能态。",
    ),
    (
        "混沌理论（蝴蝶效应）",
        "最小作用量原理",
        "RELATED_TO",
        "看似矛盾实则互补：微观上系统遵循最小作用量原理，但宏观上非线性系统可展现混沌行为——确定性规则产生不可预测结果。",
    ),
    (
        "热力学第二定律（熵增）",
        "混沌理论（蝴蝶效应）",
        "RELATED_TO",
        "熵增描述系统走向无序的趋势，混沌理论描述确定性系统中的不可预测性——两者都说明复杂系统行为难以长期预测。",
    ),
    # ===================== 数学 (mathematics) =====================
    (
        "贝叶斯定理",
        "蒙特卡洛方法",
        "RELATED_TO",
        "MCMC(马尔可夫链蒙特卡洛)方法是贝叶斯推断的计算工具——当后验分布无法解析求解时，用随机采样近似。",
    ),
    (
        "图论与网络科学",
        "蒙特卡洛方法",
        "RELATED_TO",
        "蒙特卡洛方法用于分析复杂网络性质——如随机游走估计PageRank、随机采样估计网络统计量。",
    ),
    (
        "梯度下降法",
        "傅里叶变换",
        "RELATED_TO",
        "优化问题中傅里叶分析揭示损失函数的频率特征——低频分量先收敛、高频后收敛(频率偏差原理)，指导学习率选择。",
    ),
    (
        "贝叶斯定理",
        "梯度下降法",
        "RELATED_TO",
        "贝叶斯优化使用贝叶斯定理指导超参数搜索——比网格搜索更高效地找到梯度下降的最佳学习率等参数。",
    ),
    # ===================== 心理学 (psychology) =====================
    (
        "巴甫洛夫条件反射",
        "操作性条件反射（强化学习原型）",
        "RELATED_TO",
        "巴甫洛夫(经典)条件反射研究刺激-反应关联，操作性条件反射(斯金纳)研究行为-后果关联。两者共同构成行为主义学习理论的基础。",
    ),
    (
        "认知偏差与启发式",
        "遗忘曲线与间隔重复",
        "RELATED_TO",
        "可用性启发式(认知偏差)与遗忘曲线相关——容易回忆的信息(未遗忘的)被判断为更常见/更重要。",
    ),
    (
        "操作性条件反射（强化学习原型）",
        "认知偏差与启发式",
        "RELATED_TO",
        "强化学习建立的行为模式可能导致认知偏差——过去被奖励的选择会被过度偏好(确认偏差的行为学基础)。",
    ),
    # ===================== 化学 (chemistry) =====================
    (
        "催化作用",
        "分子自组装",
        "RELATED_TO",
        "催化和自组装都依赖分子间的特异性相互作用——催化是加速反应，自组装是形成有序结构，两者共享分子识别机制。",
    ),
    # ===================== 生态学 (ecology) =====================
    (
        "捕食者-猎物动力学（Lotka-Volterra）",
        "生态位分化与共存",
        "RELATED_TO",
        "捕食关系是塑造生态位分化的重要力量——捕食压力促使猎物种群在不同生态位中特化以减少竞争。",
    ),
    # ===================== 社会学 (sociology) =====================
    (
        "六度分隔与小世界网络",
        "马太效应（富者愈富）",
        "RELATED_TO",
        "小世界网络中hub节点(高连接度)因优先连接机制(马太效应)而不断增强——'连接越多越容易获得更多连接'。",
    ),
    # ===================== 工程学 (engineering) =====================
    (
        "反馈控制（负反馈）",
        "控制论（Cybernetics）",
        "BUILDS_ON",
        "控制论的核心就是反馈机制——维纳将负反馈控制理论推广为控制论，统一了工程、生物和社会系统的控制原理。",
    ),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 构建全库名称→ID映射
    node_name_to_id = {}
    cursor.execute("SELECT id, name FROM knowledge_nodes")
    for row in cursor.fetchall():
        node_name_to_id[row[1]] = row[0]

    inserted = 0
    skipped = 0
    failed = 0

    for src_name, tgt_name, rel_type, desc in relations_def:
        src_id = node_name_to_id.get(src_name)
        tgt_id = node_name_to_id.get(tgt_name)

        if not src_id or not tgt_id:
            failed += 1
            missing = []
            if not src_id:
                missing.append(f"源'{src_name}'")
            if not tgt_id:
                missing.append(f"目标'{tgt_name}'")
            print(f"  ❌ 找不到: {', '.join(missing)}")
            continue

        cursor.execute(
            """
            SELECT id FROM relations 
            WHERE source_id = ? AND target_id = ? AND relation_type = ?
        """,
            (src_id, tgt_id, rel_type),
        )
        if cursor.fetchone():
            skipped += 1
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
        inserted += 1
        print(f"  ✅ {src_name} --{rel_type}--> {tgt_name}")

    conn.commit()

    # 统计
    cursor.execute("SELECT COUNT(*) FROM knowledge_nodes")
    total_nodes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM relations")
    total_rels = cursor.fetchone()[0]

    # 领域内关系统计
    cursor.execute("""
        SELECT kn1.domain, COUNT(*) FROM relations r 
        JOIN knowledge_nodes kn1 ON r.source_id = kn1.id AND r.source_type = 'knowledge_node'
        JOIN knowledge_nodes kn2 ON r.target_id = kn2.id AND r.target_type = 'knowledge_node'
        WHERE kn1.domain = kn2.domain
        GROUP BY kn1.domain ORDER BY COUNT(*) DESC
    """)
    print(f"\n📊 新增 {inserted}, 跳过 {skipped}, 失败 {failed}")
    print(f"🎉 数据库: {total_nodes} 节点, {total_rels} 关系")
    print("\n📌 各领域内部关系数:")
    for r in cursor.fetchall():
        print(f"  {r[0]}: {r[1]}")

    conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🔗 补充各领域内部关联关系")
    print("=" * 60)
    main()
