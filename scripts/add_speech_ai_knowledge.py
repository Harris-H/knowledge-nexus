"""
第四批知识节点：语音AI/语音大模型领域。
覆盖：语音识别(ASR)、语音合成(TTS)、语音自监督学习、语音大模型、音频生成等。
新增 ~12 个语音AI知识节点 + ~18 篇关键论文 + ~70 条关联关系。
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
#  语音AI 知识节点
# ══════════════════════════════════════════════════════════════

NODES = [
    {
        "name": "自动语音识别 (ASR)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将语音信号转换为文字的技术。发展路线：GMM-HMM(1980s)→DNN-HMM(2012)→"
        "端到端模型(CTC/Attention/Transducer)。"
        "经典系统：Kaldi(传统)、DeepSpeech(端到端)、Conformer(混合架构)、Whisper(大规模弱监督)。"
        "核心挑战：噪声鲁棒性、多语言、实时性、方言/口音。",
        "summary": "语音→文字：从HMM到Whisper的ASR演进之路",
        "source_info": "领域综述：Li Deng et al., 2013; Radford et al., 2022 (Whisper)",
        "year": 1982,
        "tags": "ASR,语音识别,端到端,CTC,Whisper,Conformer",
    },
    {
        "name": "语音合成 (TTS)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将文字转换为自然语音的技术。发展路线：拼接合成→参数合成→"
        "神经网络合成(WaveNet/Tacotron)→大模型合成(VALL-E/CosyVoice)。"
        "关键组件：文本前端(分词/韵律)→声学模型(文字→梅尔频谱)→声码器(频谱→波形)。"
        "前沿方向：零样本语音克隆、情感可控、多语言。",
        "summary": "文字→语音：从拼接合成到神经网络的TTS革命",
        "source_info": "里程碑：WaveNet(2016), Tacotron(2017), VALL-E(2023)",
        "year": 2016,
        "tags": "TTS,语音合成,声码器,WaveNet,Tacotron,VALL-E",
    },
    {
        "name": "语音自监督学习",
        "node_type": "method",
        "domain": "computer_science",
        "description": "从大量无标注语音数据中学习通用语音表示的方法。"
        "核心思路：对比学习(Wav2Vec 2.0)或掩码预测(HuBERT)来学习语音特征。"
        "类比NLP的BERT预训练——但语音数据是连续信号而非离散token，需要先量化。"
        "学到的表示可微调用于ASR、TTS、情感识别、说话人验证等下游任务。"
        "大幅降低了对标注数据的依赖——10分钟标注数据即可达到传统方法的效果。",
        "summary": "无标注语音数据学通用表示——语音界的BERT时刻",
        "source_info": "Wav2Vec 2.0 (Baevski et al., 2020), HuBERT (Hsu et al., 2021)",
        "year": 2020,
        "tags": "自监督,语音表示,Wav2Vec,HuBERT,预训练,对比学习",
    },
    {
        "name": "CTC (连接时序分类)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "解决输入序列和输出序列长度不对齐的训练方法。"
        "通过引入blank标签，在所有可能的对齐路径上求和计算损失。"
        "使端到端语音识别成为可能——不再需要手动帧级别对齐。"
        "被Wav2Vec 2.0、DeepSpeech等广泛使用。"
        "也用于手写识别、OCR等序列标注任务。",
        "summary": "解决序列不对齐问题——端到端语音识别的数学基础",
        "source_info": "Alex Graves et al., 2006, 'Connectionist Temporal Classification'",
        "year": 2006,
        "tags": "CTC,序列对齐,端到端,blank标签,Graves",
    },
    {
        "name": "声码器 (Vocoder)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将声学特征（梅尔频谱/声学token）转换为可播放音频波形的模块。"
        "传统：Griffin-Lim、WORLD声码器。"
        "神经网络：WaveNet(自回归,质量最高但慢)→WaveRNN→WaveGlow(流模型)→"
        "HiFi-GAN(GAN,快速高质量)→Vocos→BigVGAN。"
        "HiFi-GAN是目前最广泛使用的神经声码器——实时推理+高音质。",
        "summary": "频谱→波形：从Griffin-Lim到HiFi-GAN的声码器演进",
        "source_info": "WaveNet(2016), HiFi-GAN(Kong et al., 2020)",
        "year": 2016,
        "tags": "声码器,Vocoder,WaveNet,HiFi-GAN,波形生成,梅尔频谱",
    },
    {
        "name": "神经音频编解码 (Neural Audio Codec)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "将连续音频波形压缩为离散token序列，再从token恢复音频。"
        "关键创新：用VQ-VAE/残差向量量化(RVQ)将音频编码为多层离散码本。"
        "代表工作：SoundStream(Google)、EnCodec(Meta)、DAC。"
        "意义重大——让语音/音频可以像文本token一样被语言模型处理！"
        "是语音大模型(VALL-E、AudioLM)的基础组件。",
        "summary": "音频→离散token：让语言模型能'读写'声音的关键技术",
        "source_info": "Zeghidour et al., 2021 (SoundStream); Défossez et al., 2022 (EnCodec)",
        "year": 2021,
        "tags": "音频编解码,EnCodec,SoundStream,RVQ,向量量化,离散化",
    },
    {
        "name": "语音大模型 (Speech Foundation Model)",
        "node_type": "concept",
        "domain": "computer_science",
        "description": "将LLM的思路应用到语音领域：在海量语音数据上预训练大规模模型，获得通用语音理解/生成能力。"
        "两条路线：\n"
        "1. 语音→token→语言模型：AudioLM、VALL-E把语音token化后用LM建模\n"
        "2. 多模态LLM：将语音编码器接入LLM(如GPT-4o的语音模式)\n"
        "标志着语音AI从专用模型走向通用模型。",
        "summary": "LLM思路应用到语音——通用语音理解与生成的新范式",
        "source_info": "AudioLM(2022), VALL-E(2023), Whisper(2022), GPT-4o(2024)",
        "year": 2022,
        "tags": "语音大模型,Speech LLM,AudioLM,VALL-E,通用语音",
    },
    {
        "name": "零样本语音克隆 (Zero-shot Voice Cloning)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "仅用几秒钟的参考音频即可生成任意文本的该说话人语音，无需微调模型。"
        "核心技术：说话人嵌入(speaker embedding) + 条件生成。"
        "代表工作：VALL-E(3秒prompt)、GPT-SoVITS、CosyVoice、OpenVoice。"
        "引发严重伦理问题：语音诈骗、深度伪造。需要配套检测和水印技术。",
        "summary": "3秒音频克隆任意人声——能力与伦理的双刃剑",
        "source_info": "VALL-E (Wang et al., 2023); GPT-SoVITS (2024)",
        "year": 2023,
        "tags": "语音克隆,零样本,VALL-E,GPT-SoVITS,说话人嵌入,伦理",
    },
    {
        "name": "音频生成 (Audio Generation)",
        "node_type": "concept",
        "domain": "computer_science",
        "description": "AI生成各类音频内容：语音、音乐、环境音、音效等。"
        "技术路线：自回归(AudioLM)、扩散模型(AudioLDM)、流匹配(VoiceBox)。"
        "应用：文字转音乐(MusicLM/Suno)、文字转音效(AudioLDM)、"
        "语音合成(TTS)、语音转换(VC)。"
        "类比图像生成(DALL-E/Stable Diffusion)在音频领域的对应。",
        "summary": "AI生成语音/音乐/音效——音频领域的'DALL-E时刻'",
        "source_info": "AudioLM(2022), AudioLDM(2023), MusicLM(2023), Suno(2024)",
        "year": 2022,
        "tags": "音频生成,AudioLDM,MusicLM,Suno,文字转音频",
    },
    {
        "name": "Conformer (卷积+Transformer)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "结合CNN的局部特征提取和Transformer的全局注意力的混合架构。"
        "结构：Macaron-FFN + Multi-Head Self-Attention + Conv Module + Macaron-FFN。"
        "在语音识别上超越了纯Transformer和纯CNN架构。"
        "已成为工业级ASR系统的标准架构(Google、微软等)。"
        "思路类似CV中的卷积+注意力混合架构(如CoAtNet)。",
        "summary": "CNN局部特征+Transformer全局注意力——工业级ASR的标准架构",
        "source_info": "Gulati et al., 2020, 'Conformer: Convolution-augmented Transformer for Speech Recognition'",
        "year": 2020,
        "tags": "Conformer,混合架构,CNN,Transformer,ASR,局部+全局",
    },
    {
        "name": "说话人验证与声纹识别",
        "node_type": "method",
        "domain": "computer_science",
        "description": "通过语音判断说话人身份的技术。两种模式：验证(1:1比对)和识别(1:N检索)。"
        "从i-vector→d-vector→x-vector→ECAPA-TDNN→基于自监督的方法。"
        "核心：提取说话人嵌入向量(speaker embedding)→余弦相似度比较。"
        "应用：手机声纹解锁、声纹支付、会议记录说话人分离。",
        "summary": "从声音识别身份——说话人嵌入与声纹比对",
        "source_info": "VoxCeleb数据集(Nagrani et al., 2017); ECAPA-TDNN(Desplanques et al., 2020)",
        "year": 2017,
        "tags": "声纹识别,说话人验证,x-vector,ECAPA-TDNN,speaker embedding",
    },
    {
        "name": "语音情感识别 (SER)",
        "node_type": "method",
        "domain": "computer_science",
        "description": "从语音信号中识别说话人的情感状态（高兴、悲伤、愤怒、恐惧等）。"
        "特征：声学特征(基频F0、能量、语速、MFCC)+语义特征(ASR转文字后分析)。"
        "现代方法：预训练语音模型(Wav2Vec/HuBERT)微调用于情感分类。"
        "应用：智能客服(检测用户情绪)、心理健康监测、人机交互。"
        "跨学科：结合心理学情感理论(如维度模型:效价-唤醒度)。",
        "summary": "从声音识别情感——AI理解人类情绪的听觉通道",
        "source_info": "领域综述: Schuller et al., INTERSPEECH系列",
        "year": 2009,
        "tags": "情感识别,SER,情绪,语音特征,MFCC,效价唤醒",
    },
]

# ══════════════════════════════════════════════════════════════
#  语音AI 关键论文
# ══════════════════════════════════════════════════════════════

PAPERS = [
    {
        "title": "WaveNet: A Generative Model for Raw Audio",
        "key_contributions": "WaveNet",
        "summary": "用深度自回归网络直接生成原始音频波形——开创性的神经声码器",
        "abstract": "This paper introduces WaveNet, a deep neural network for generating raw audio waveforms. "
        "The model is fully probabilistic and autoregressive, with the predictive distribution for each audio sample "
        "conditioned on all previous ones. When applied to text-to-speech, it yields state-of-the-art performance. "
        "WaveNet produces more natural-sounding speech than the best existing parametric and concatenative systems.",
        "year": 2016,
        "citation_count": 7500,
        "venue": "arXiv / SSW 2016",
        "doi": None,
        "arxiv_id": "1609.03499",
        "fields_of_study": "speech synthesis,deep learning,generative model,vocoder,autoregressive",
    },
    {
        "title": "Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions",
        "key_contributions": "Tacotron 2",
        "summary": "序列到序列+WaveNet声码器的端到端TTS系统——接近人类语音质量",
        "abstract": "This paper describes Tacotron 2, a neural network architecture for speech synthesis directly from text. "
        "The system is composed of a recurrent sequence-to-sequence feature prediction network that maps "
        "character embeddings to mel-scale spectrograms, followed by a modified WaveNet model acting as a vocoder. "
        "Achieving a mean opinion score (MOS) of 4.53 comparable to a MOS of 4.58 for professionally recorded speech.",
        "year": 2018,
        "citation_count": 4200,
        "venue": "ICASSP 2018",
        "doi": None,
        "arxiv_id": "1712.05884",
        "fields_of_study": "text-to-speech,sequence-to-sequence,mel spectrogram,vocoder,neural TTS",
    },
    {
        "title": "wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations",
        "key_contributions": "Wav2Vec 2.0",
        "summary": "对比学习+量化的语音自监督框架——10分钟标注数据即可匹敌传统系统",
        "abstract": "We show for the first time that learning powerful representations from speech audio alone "
        "followed by fine-tuning on transcribed speech can outperform the best semi-supervised methods "
        "while being conceptually simpler. wav2vec 2.0 masks the speech input in the latent space "
        "and solves a contrastive task defined over a quantization of the latent representations.",
        "year": 2020,
        "citation_count": 4500,
        "venue": "NeurIPS 2020",
        "doi": None,
        "arxiv_id": "2006.11477",
        "fields_of_study": "self-supervised learning,speech recognition,contrastive learning,representation learning",
    },
    {
        "title": "HuBERT: Self-Supervised Speech Representation Learning by Masked Prediction of Hidden Units",
        "key_contributions": "HuBERT",
        "summary": "掩码预测离散聚类标签的语音自监督方法——ASR/TTS通用表示",
        "abstract": "Self-supervised approaches for speech representation learning are challenged by three unique problems: "
        "(1) there are multiple sound units in each input utterance, (2) there is no lexicon of input sound units, "
        "and (3) sound units have variable lengths. HuBERT utilizes an offline clustering step "
        "to provide aligned target labels for a BERT-like prediction loss.",
        "year": 2021,
        "citation_count": 1200,
        "venue": "IEEE/ACM TASLP 2021",
        "doi": None,
        "arxiv_id": "2106.07447",
        "fields_of_study": "self-supervised learning,speech representation,masked prediction,clustering",
    },
    {
        "title": "Robust Speech Recognition via Large-Scale Weak Supervision",
        "key_contributions": "Whisper",
        "summary": "68万小时弱监督数据训练的多语言ASR——噪声鲁棒+零样本泛化",
        "abstract": "We study the capabilities of speech processing systems trained simply to predict large amounts "
        "of transcripts of audio on the internet. When scaled to 680,000 hours of multilingual and multitask "
        "weak supervision, the resulting models generalize well to standard benchmarks and are often competitive "
        "with prior fully supervised results without the need for any fine-tuning.",
        "year": 2022,
        "citation_count": 2200,
        "venue": "ICML 2023",
        "doi": None,
        "arxiv_id": "2212.04356",
        "fields_of_study": "speech recognition,weak supervision,multilingual,robustness,large-scale training",
    },
    {
        "title": "Conformer: Convolution-augmented Transformer for Speech Recognition",
        "key_contributions": "Conformer",
        "summary": "卷积+Transformer混合架构——工业级ASR的标准配置",
        "abstract": "Recently Transformer and Convolution neural network based models have shown promising results "
        "in Automatic Speech Recognition. Transformer models are good at capturing content-based global interactions, "
        "while CNNs exploit local features effectively. We propose the Conformer model that combines "
        "convolution and self-attention in a novel way, achieving state-of-the-art accuracy on LibriSpeech.",
        "year": 2020,
        "citation_count": 2700,
        "venue": "INTERSPEECH 2020",
        "doi": None,
        "arxiv_id": "2005.08100",
        "fields_of_study": "speech recognition,transformer,convolution,hybrid architecture,ASR",
    },
    {
        "title": "AudioLM: a Language Modeling Approach to Audio Generation",
        "key_contributions": "AudioLM",
        "summary": "将音频token化后用语言模型自回归生成——语音大模型的开创性工作",
        "abstract": "We introduce AudioLM, a framework for high-quality audio generation with long-term consistency. "
        "AudioLM maps the input audio to a sequence of discrete tokens and casts audio generation as a language "
        "modeling task in this representation space. By training on large amounts of speech audio, "
        "AudioLM learns to generate natural and coherent continuations given short prompts.",
        "year": 2022,
        "citation_count": 400,
        "venue": "arXiv 2022",
        "doi": None,
        "arxiv_id": "2209.03143",
        "fields_of_study": "audio generation,language model,speech synthesis,discrete tokens,autoregressive",
    },
    {
        "title": "Neural Codec Language Models are Zero-Shot Text to Speech Synthesizers",
        "key_contributions": "VALL-E",
        "summary": "3秒音频prompt实现零样本语音克隆——语音合成的GPT时刻",
        "abstract": "We introduce a language modeling approach for text to speech synthesis (TTS). "
        "Specifically, we train a neural codec language model (called VALL-E) using discrete codes "
        "derived from an off-the-shelf neural audio codec model, and regard TTS as a conditional "
        "language modeling task rather than continuous signal regression as in previous work. "
        "VALL-E emerges in-context learning capabilities and can synthesize high-quality personalized "
        "speech with only a 3-second enrolled recording.",
        "year": 2023,
        "citation_count": 500,
        "venue": "arXiv 2023",
        "doi": None,
        "arxiv_id": "2301.02111",
        "fields_of_study": "text-to-speech,language model,zero-shot,voice cloning,neural codec",
    },
    {
        "title": "High Fidelity Neural Audio Compression",
        "key_contributions": "EnCodec",
        "summary": "Meta的神经音频编解码器——将音频压缩为离散token的基础设施",
        "abstract": "We introduce a state-of-the-art real-time, high-fidelity, audio codec leveraging neural networks. "
        "It consists in a streaming encoder-decoder architecture with quantized latent space trained in an "
        "end-to-end fashion. We simplify and speed-up the training by using a single multiscale spectrogram "
        "adversarial loss. We introduce a novel loss balancer mechanism to stabilize training.",
        "year": 2022,
        "citation_count": 350,
        "venue": "TMLR 2023",
        "doi": None,
        "arxiv_id": "2210.13438",
        "fields_of_study": "audio compression,neural codec,vector quantization,streaming,encoder-decoder",
    },
    {
        "title": "SoundStorm: Efficient Parallel Audio Generation",
        "key_contributions": "SoundStorm",
        "summary": "并行解码的高效音频生成——比自回归快100倍",
        "abstract": "We present SoundStorm, a model for efficient, non-autoregressive audio generation. "
        "SoundStorm receives as input the semantic tokens of AudioLM, and fills in the tokens of a "
        "neural audio codec in parallel. SoundStorm produces audio of the same quality and with higher "
        "consistency in voice and acoustic conditions compared to the autoregressive AudioLM, "
        "while being two orders of magnitude faster.",
        "year": 2023,
        "citation_count": 80,
        "venue": "arXiv 2023",
        "doi": None,
        "arxiv_id": "2305.09636",
        "fields_of_study": "audio generation,parallel decoding,neural codec,efficient inference,speech synthesis",
    },
    {
        "title": "Deep Speech 2: End-to-End Speech Recognition in English and Mandarin",
        "key_contributions": "DeepSpeech 2",
        "summary": "百度端到端ASR系统——英语和普通话的双语识别里程碑",
        "abstract": "We show that an end-to-end deep learning approach can be used to recognize either "
        "English or Mandarin Chinese speech. We use a model consisting of a deep recurrent neural "
        "network trained using CTC loss. The system achieves competitive accuracy on several benchmarks "
        "and is deployed in a production system.",
        "year": 2016,
        "citation_count": 3500,
        "venue": "ICML 2016",
        "doi": None,
        "arxiv_id": "1512.02595",
        "fields_of_study": "speech recognition,end-to-end,CTC,deep learning,bilingual",
    },
    {
        "title": "HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis",
        "key_contributions": "HiFi-GAN",
        "summary": "GAN实现实时高保真语音合成——目前最广泛使用的神经声码器",
        "abstract": "Several recent works on speech synthesis have employed generative adversarial networks (GANs) "
        "to produce raw waveforms. Although such methods improve the sampling efficiency, their sample quality "
        "has not yet reached that of autoregressive and flow-based generative models. "
        "We propose HiFi-GAN, which achieves both efficient and high-fidelity speech synthesis.",
        "year": 2020,
        "citation_count": 1800,
        "venue": "NeurIPS 2020",
        "doi": None,
        "arxiv_id": "2010.05646",
        "fields_of_study": "speech synthesis,GAN,vocoder,waveform generation,real-time",
    },
    {
        "title": "GPT-SoVITS: Few-Shot Voice Conversion and Text-to-Speech",
        "key_contributions": "GPT-SoVITS",
        "summary": "GPT+SoVITS结合的少样本语音克隆——开源社区最受欢迎的TTS工具",
        "abstract": "GPT-SoVITS combines GPT-style language modeling with SoVITS (Soft Voice Intelligent TTS) "
        "for high-quality few-shot voice cloning and text-to-speech synthesis. "
        "With just a few seconds of reference audio, it can generate natural speech in the target voice. "
        "The system supports Chinese, English, and Japanese, and has become one of the most popular "
        "open-source TTS tools with 40K+ GitHub stars.",
        "year": 2024,
        "citation_count": 100,
        "venue": "GitHub/Open Source",
        "doi": None,
        "arxiv_id": None,
        "fields_of_study": "voice cloning,text-to-speech,few-shot learning,GPT,open source",
    },
    {
        "title": "CosyVoice: A Scalable Multilingual Zero-shot Text-to-speech Synthesizer Based on Supervised Semantic Tokens",
        "key_contributions": "CosyVoice",
        "summary": "阿里巴巴的多语言零样本TTS——监督语义token+流匹配",
        "abstract": "We propose CosyVoice, a multilingual TTS model based on supervised semantic tokens. "
        "CosyVoice uses a flow-matching based speech generation model conditioned on text and semantic tokens. "
        "It supports zero-shot voice cloning with a 3-second prompt and can generate speech in Chinese, "
        "English, Japanese, Cantonese, and Korean with high naturalness and speaker similarity.",
        "year": 2024,
        "citation_count": 50,
        "venue": "arXiv 2024",
        "doi": None,
        "arxiv_id": "2407.05407",
        "fields_of_study": "text-to-speech,multilingual,zero-shot,flow matching,semantic tokens",
    },
    {
        "title": "ChatTTS: A Generative Speech Model for Daily Dialogue",
        "key_contributions": "ChatTTS",
        "summary": "面向日常对话的中文语音生成模型——自然韵律+笑声/停顿控制",
        "abstract": "ChatTTS is a text-to-speech model designed specifically for dialogue scenarios. "
        "It supports both Chinese and English, trained on over 100K hours of speech data. "
        "The model can generate natural, expressive speech with controllable prosody, "
        "including laughter, pauses, and interjections, making it ideal for conversational AI applications.",
        "year": 2024,
        "citation_count": 30,
        "venue": "GitHub/Open Source",
        "doi": None,
        "arxiv_id": None,
        "fields_of_study": "text-to-speech,dialogue,Chinese,prosody control,conversational AI",
    },
    {
        "title": "Fish Speech: A Novel Multilingual Text-to-Speech System",
        "key_contributions": "Fish Speech",
        "summary": "VITS2架构的开源多语言TTS——低延迟+高质量的工业级方案",
        "abstract": "Fish Speech is an open-source, multilingual text-to-speech system built on VITS2 architecture "
        "with improvements in prosody modeling and speaker adaptation. It supports Chinese, English, Japanese "
        "and more languages with low-latency inference suitable for real-time applications. "
        "Features include voice cloning, emotion control, and streaming generation.",
        "year": 2024,
        "citation_count": 20,
        "venue": "GitHub/Open Source",
        "doi": None,
        "arxiv_id": None,
        "fields_of_study": "text-to-speech,multilingual,VITS,streaming,open source",
    },
    {
        "title": "Voicebox: Text-Guided Multilingual Universal Speech Generation at Scale",
        "key_contributions": "Voicebox",
        "summary": "Meta的通用语音生成模型——流匹配+上下文学习的非自回归TTS",
        "abstract": "We present Voicebox, the most versatile text-guided generative model for speech at scale. "
        "Voicebox is a non-autoregressive flow-matching model trained to infill speech, given audio context "
        "and text. It can perform mono or cross-lingual zero-shot text-to-speech synthesis, "
        "noise removal, content editing, style conversion, and diverse sample generation.",
        "year": 2023,
        "citation_count": 200,
        "venue": "arXiv 2023 (Meta AI)",
        "doi": None,
        "arxiv_id": "2306.15687",
        "fields_of_study": "speech generation,flow matching,zero-shot TTS,speech editing,multilingual",
    },
    {
        "title": "AudioLDM: Text-to-Audio Generation with Latent Diffusion Models",
        "key_contributions": "AudioLDM",
        "summary": "潜在扩散模型用于文字生成音频——音频领域的Stable Diffusion",
        "abstract": "In this work, we propose AudioLDM, a text-to-audio generation framework that "
        "leverages the latent diffusion model (LDM) for audio generation. AudioLDM "
        "is built on AudioMAE representation, trained on AudioCaps with additional unlabeled data, "
        "and achieves state-of-the-art text-to-audio generation measured by objective and subjective metrics.",
        "year": 2023,
        "citation_count": 300,
        "venue": "ICML 2023",
        "doi": None,
        "arxiv_id": "2301.12503",
        "fields_of_study": "audio generation,latent diffusion,text-to-audio,contrastive learning",
    },
]

# ══════════════════════════════════════════════════════════════
#  插入知识节点
# ══════════════════════════════════════════════════════════════

node_ids = {}
inserted_kn = 0

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
    inserted_kn += 1
    print(f"  ✅ [{n['node_type']}] {n['name']}")

print(f"\n📌 插入 {inserted_kn} 个语音AI知识节点")

# ══════════════════════════════════════════════════════════════
#  插入论文
# ══════════════════════════════════════════════════════════════

papers = {}
for row in cur.execute("SELECT id, key_contributions, title FROM papers"):
    papers[row[1] or row[2]] = row[0]

inserted_p = 0
for p in PAPERS:
    key = p["key_contributions"] or p["title"]
    if key in papers:
        print(f"  ⏭ 论文已存在: {key}")
        continue
    pid = gen_id()
    cur.execute(
        "INSERT INTO papers (id, title, key_contributions, summary, abstract, year, "
        "citation_count, venue, doi, arxiv_id, fields_of_study, "
        "impact_score, influential_citation_count, ai_status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            pid,
            p["title"],
            p["key_contributions"],
            p["summary"],
            p["abstract"],
            p["year"],
            p["citation_count"],
            p["venue"],
            p["doi"],
            p["arxiv_id"],
            p["fields_of_study"],
            min(p["citation_count"] / 100, 100.0),
            0,
            "completed",
            now,
            now,
        ),
    )
    papers[key] = pid
    inserted_p += 1
    print(f"  📄 {key} ({p['year']}, {p['citation_count']}引)")

print(f"\n📌 插入 {inserted_p} 篇语音AI论文")

# ══════════════════════════════════════════════════════════════
#  关联关系
# ══════════════════════════════════════════════════════════════

N = node_ids
P = papers

existing_rels = set()
for row in cur.execute("SELECT source_id, target_id FROM relations"):
    existing_rels.add((row[0], row[1]))

RELATIONS = [
    # ═══════════════════════════════════════════════════════════
    #  Part 1: 语音AI知识节点内部关联
    # ═══════════════════════════════════════════════════════════
    (
        N.get("自动语音识别 (ASR)"),
        N.get("语音合成 (TTS)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "ASR和TTS是语音处理的两大核心任务——互为逆过程：语音→文字 vs 文字→语音",
    ),
    (
        N.get("CTC (连接时序分类)"),
        N.get("自动语音识别 (ASR)"),
        "ENABLES",
        "knowledge_node",
        "knowledge_node",
        "CTC解决了语音帧与文字的对齐问题，使端到端ASR成为可能",
    ),
    (
        N.get("声码器 (Vocoder)"),
        N.get("语音合成 (TTS)"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "声码器是TTS流水线的最后环节——将频谱特征转换为可播放的音频波形",
    ),
    (
        N.get("神经音频编解码 (Neural Audio Codec)"),
        N.get("语音大模型 (Speech Foundation Model)"),
        "ENABLES",
        "knowledge_node",
        "knowledge_node",
        "音频编解码器将语音离散化为token，是语音大模型能用LM方式建模语音的关键",
    ),
    (
        N.get("语音自监督学习"),
        N.get("自动语音识别 (ASR)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "自监督预训练大幅减少ASR对标注数据的依赖——10分钟标注即可达到传统效果",
    ),
    (
        N.get("语音自监督学习"),
        N.get("语音合成 (TTS)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "自监督语音表示也可用于TTS的说话人建模和韵律建模",
    ),
    (
        N.get("语音大模型 (Speech Foundation Model)"),
        N.get("自动语音识别 (ASR)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "语音大模型（如Whisper）在ASR任务上展现出惊人的零样本泛化能力",
    ),
    (
        N.get("语音大模型 (Speech Foundation Model)"),
        N.get("语音合成 (TTS)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "语音大模型（如VALL-E）将TTS重新定义为语言建模任务",
    ),
    (
        N.get("零样本语音克隆 (Zero-shot Voice Cloning)"),
        N.get("语音合成 (TTS)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "零样本语音克隆是TTS的前沿方向——无需微调即可复制任意人声",
    ),
    (
        N.get("零样本语音克隆 (Zero-shot Voice Cloning)"),
        N.get("神经音频编解码 (Neural Audio Codec)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "语音克隆模型通常基于神经编解码器的离散表示来建模说话人特征",
    ),
    (
        N.get("音频生成 (Audio Generation)"),
        N.get("语音合成 (TTS)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "TTS是音频生成的核心子任务，音频生成还包括音乐/音效生成",
    ),
    (
        N.get("Conformer (卷积+Transformer)"),
        N.get("自动语音识别 (ASR)"),
        "IMPROVES",
        "knowledge_node",
        "knowledge_node",
        "Conformer是工业级ASR系统的标准架构——CNN局部+Transformer全局",
    ),
    (
        N.get("说话人验证与声纹识别"),
        N.get("零样本语音克隆 (Zero-shot Voice Cloning)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "声纹识别提取的说话人嵌入是语音克隆中条件生成的关键输入",
    ),
    (
        N.get("语音情感识别 (SER)"),
        N.get("自动语音识别 (ASR)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "SER常与ASR结合：先识别文字内容，再结合声学特征判断情感",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 2: 论文↔知识节点关联
    # ═══════════════════════════════════════════════════════════
    (
        P.get("WaveNet"),
        N.get("声码器 (Vocoder)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "WaveNet开创了神经声码器时代——直接从特征生成原始音频波形",
    ),
    (
        P.get("WaveNet"),
        N.get("语音合成 (TTS)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "WaveNet是TTS领域里程碑式的工作，语音质量远超传统方法",
    ),
    (
        P.get("Tacotron 2"),
        N.get("语音合成 (TTS)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "Tacotron 2是端到端TTS的经典工作——接近人类语音质量的MOS 4.53",
    ),
    (
        P.get("Tacotron 2"),
        P.get("WaveNet"),
        "BUILDS_ON",
        "paper",
        "paper",
        "Tacotron 2使用WaveNet作为声码器生成最终波形",
    ),
    (
        P.get("Wav2Vec 2.0"),
        N.get("语音自监督学习"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "Wav2Vec 2.0是语音自监督学习的奠基性工作——对比学习+量化",
    ),
    (
        P.get("HuBERT"),
        N.get("语音自监督学习"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "HuBERT用掩码预测离散聚类标签，是Wav2Vec 2.0的重要改进",
    ),
    (
        P.get("HuBERT"),
        P.get("Wav2Vec 2.0"),
        "IMPROVES",
        "paper",
        "paper",
        "HuBERT改进了Wav2Vec 2.0的训练方式——用离线聚类代替在线量化",
    ),
    (
        P.get("Whisper"),
        N.get("自动语音识别 (ASR)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "Whisper在68万小时数据上训练，是ASR领域的里程碑大模型",
    ),
    (
        P.get("Whisper"),
        N.get("语音大模型 (Speech Foundation Model)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "Whisper展示了大规模弱监督训练在语音识别中的巨大潜力",
    ),
    (
        P.get("Conformer"),
        N.get("Conformer (卷积+Transformer)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "Conformer论文提出了这一CNN+Transformer混合架构",
    ),
    (
        P.get("AudioLM"),
        N.get("语音大模型 (Speech Foundation Model)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "AudioLM开创性地将语音建模为token序列→语言模型自回归生成",
    ),
    (
        P.get("AudioLM"),
        N.get("音频生成 (Audio Generation)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "AudioLM是音频生成领域的里程碑——不依赖文本即可生成连贯音频",
    ),
    (
        P.get("VALL-E"),
        N.get("零样本语音克隆 (Zero-shot Voice Cloning)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "VALL-E首次实现了3秒prompt的零样本语音克隆——TTS的GPT时刻",
    ),
    (
        P.get("VALL-E"),
        N.get("语音大模型 (Speech Foundation Model)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "VALL-E将TTS重定义为神经编解码语言模型——语音合成的新范式",
    ),
    (
        P.get("VALL-E"),
        P.get("EnCodec"),
        "BUILDS_ON",
        "paper",
        "paper",
        "VALL-E使用EnCodec的离散音频token作为建模目标",
    ),
    (
        P.get("VALL-E"),
        P.get("AudioLM"),
        "BUILDS_ON",
        "paper",
        "paper",
        "VALL-E借鉴AudioLM的语言建模思路，但增加了文本条件输入",
    ),
    (
        P.get("EnCodec"),
        N.get("神经音频编解码 (Neural Audio Codec)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "EnCodec是Meta的神经音频编解码器——VALL-E等语音大模型的基础",
    ),
    (
        P.get("SoundStorm"),
        P.get("AudioLM"),
        "IMPROVES",
        "paper",
        "paper",
        "SoundStorm用并行解码替代AudioLM的自回归，速度快100倍",
    ),
    (
        P.get("SoundStorm"),
        N.get("音频生成 (Audio Generation)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "SoundStorm实现了高效并行音频生成——解决自回归方法的速度瓶颈",
    ),
    (
        P.get("DeepSpeech 2"),
        N.get("自动语音识别 (ASR)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "百度DeepSpeech 2是端到端ASR的里程碑——英语+普通话双语",
    ),
    (
        P.get("DeepSpeech 2"),
        N.get("CTC (连接时序分类)"),
        "BUILDS_ON",
        "paper",
        "knowledge_node",
        "DeepSpeech 2使用CTC损失训练端到端ASR模型",
    ),
    (
        P.get("HiFi-GAN"),
        N.get("声码器 (Vocoder)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "HiFi-GAN是目前最广泛使用的神经声码器——实时+高保真",
    ),
    (
        P.get("GPT-SoVITS"),
        N.get("零样本语音克隆 (Zero-shot Voice Cloning)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "GPT-SoVITS是开源社区最受欢迎的语音克隆工具——40K+ Stars",
    ),
    (
        P.get("CosyVoice"),
        N.get("零样本语音克隆 (Zero-shot Voice Cloning)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "CosyVoice用监督语义token+流匹配实现多语言零样本TTS",
    ),
    (
        P.get("CosyVoice"),
        P.get("VALL-E"),
        "BUILDS_ON",
        "paper",
        "paper",
        "CosyVoice改进了VALL-E的思路——用监督语义token替代无监督离散化",
    ),
    (
        P.get("ChatTTS"),
        N.get("语音合成 (TTS)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "ChatTTS专注于对话场景的中文语音生成——可控韵律+笑声/停顿",
    ),
    (
        P.get("Fish Speech"),
        N.get("语音合成 (TTS)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "Fish Speech是基于VITS2的开源多语言TTS——低延迟工业级方案",
    ),
    (
        P.get("Voicebox"),
        N.get("音频生成 (Audio Generation)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "Voicebox用流匹配实现通用语音生成——支持克隆/编辑/降噪等多任务",
    ),
    (
        P.get("AudioLDM"),
        N.get("音频生成 (Audio Generation)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "AudioLDM将Stable Diffusion的潜在扩散思路应用到音频生成",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 3: 论文之间的关联
    # ═══════════════════════════════════════════════════════════
    (
        P.get("Whisper"),
        P.get("Wav2Vec 2.0"),
        "RELATED_TO",
        "paper",
        "paper",
        "两条不同路线的大规模ASR：Whisper=弱监督, Wav2Vec=自监督",
    ),
    (
        P.get("Whisper"),
        P.get("Conformer"),
        "BUILDS_ON",
        "paper",
        "paper",
        "Whisper的编码器使用了类似Conformer的架构设计",
    ),
    (
        P.get("GPT-SoVITS"),
        P.get("VALL-E"),
        "BUILDS_ON",
        "paper",
        "paper",
        "GPT-SoVITS借鉴VALL-E的语言模型思路，用GPT控制语音生成",
    ),
    (
        P.get("AudioLDM"),
        P.get("AudioLM"),
        "RELATED_TO",
        "paper",
        "paper",
        "两条音频生成路线：AudioLM=自回归token模型, AudioLDM=潜在扩散模型",
    ),
    (
        P.get("Voicebox"),
        P.get("VALL-E"),
        "RELATED_TO",
        "paper",
        "paper",
        "两条TTS路线：VALL-E=自回归语言模型, Voicebox=流匹配非自回归",
    ),
    (
        P.get("HiFi-GAN"),
        P.get("WaveNet"),
        "IMPROVES",
        "paper",
        "paper",
        "HiFi-GAN用GAN替代自回归——实时速度+接近WaveNet的质量",
    ),
    (
        P.get("HiFi-GAN"),
        P.get("Tacotron 2"),
        "RELATED_TO",
        "paper",
        "paper",
        "HiFi-GAN常替代Tacotron 2中的WaveNet声码器以提升推理速度",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 4: 与现有CS知识节点的跨域关联
    # ═══════════════════════════════════════════════════════════
    (
        N.get("Conformer (卷积+Transformer)"),
        N.get("Transformer 架构"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "Conformer在Transformer基础上融合了卷积模块，专为语音设计",
    ),
    (
        N.get("Conformer (卷积+Transformer)"),
        N.get("卷积神经网络 (CNN)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "Conformer结合CNN的局部特征提取能力处理语音的短时特征",
    ),
    (
        N.get("语音大模型 (Speech Foundation Model)"),
        N.get("大语言模型 (LLM)"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "语音大模型借鉴LLM的思路：大规模预训练→通用能力→下游适配",
    ),
    (
        N.get("语音大模型 (Speech Foundation Model)"),
        N.get("Scaling Law (规模定律)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "Whisper验证了Scaling Law在语音领域同样成立——更多数据=更强泛化",
    ),
    (
        N.get("神经音频编解码 (Neural Audio Codec)"),
        N.get("变分自编码器 (VAE)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "神经音频编解码器使用VQ-VAE/残差向量量化将音频压缩为离散token",
    ),
    (
        N.get("语音自监督学习"),
        N.get("自监督学习 (Self-Supervised Learning)"),
        "PART_OF",
        "knowledge_node",
        "knowledge_node",
        "语音自监督学习是自监督学习在语音领域的应用——从无标注语音学表示",
    ),
    (
        N.get("语音自监督学习"),
        N.get("对比学习 (Contrastive Learning)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "Wav2Vec 2.0使用对比学习作为语音自监督的核心目标",
    ),
    (
        N.get("语音自监督学习"),
        N.get("预训练-微调范式"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "语音自监督→预训练→微调 = NLP的BERT范式在语音领域的复现",
    ),
    (
        N.get("零样本语音克隆 (Zero-shot Voice Cloning)"),
        N.get("上下文学习 (In-Context Learning)"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "3秒音频prompt → 生成该人声音，类似LLM的few-shot in-context learning",
    ),
    (
        N.get("CTC (连接时序分类)"),
        N.get("循环神经网络 (RNN/LSTM)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "CTC最初与LSTM-RNN结合使用，实现端到端的序列到序列映射",
    ),
    (
        N.get("音频生成 (Audio Generation)"),
        N.get("扩散模型 (Diffusion Models)"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "AudioLDM等用扩散模型生成音频——图像扩散思路到音频的迁移",
    ),
    (
        N.get("音频生成 (Audio Generation)"),
        N.get("自回归生成模型"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "AudioLM用自回归方式逐token生成音频——语言模型思路的音频版",
    ),
    (
        P.get("HiFi-GAN"),
        N.get("生成对抗网络 (GAN)"),
        "BUILDS_ON",
        "paper",
        "knowledge_node",
        "HiFi-GAN将GAN应用于声码器——对抗训练生成高保真音频",
    ),
    (
        P.get("AudioLDM"),
        N.get("扩散模型 (Diffusion Models)"),
        "BUILDS_ON",
        "paper",
        "knowledge_node",
        "AudioLDM = 潜在扩散模型(Stable Diffusion思路) + 音频生成",
    ),
    (
        P.get("Wav2Vec 2.0"),
        N.get("对比学习 (Contrastive Learning)"),
        "BUILDS_ON",
        "paper",
        "knowledge_node",
        "Wav2Vec 2.0用对比学习目标训练语音表示——正例=同一帧量化后的码本",
    ),
    (
        P.get("VALL-E"),
        N.get("大语言模型 (LLM)"),
        "ANALOGOUS_TO",
        "paper",
        "knowledge_node",
        "VALL-E将TTS重定义为语言建模——编解码token上的自回归生成，类比GPT",
    ),
    (
        P.get("VALL-E"),
        N.get("上下文学习 (In-Context Learning)"),
        "RELATED_TO",
        "paper",
        "knowledge_node",
        "VALL-E展现了语音领域的in-context learning：3秒prompt → 克隆该人声音",
    ),
    # ═══════════════════════════════════════════════════════════
    #  Part 5: 跨领域关联
    # ═══════════════════════════════════════════════════════════
    (
        N.get("语音情感识别 (SER)"),
        N.get("巴甫洛夫条件反射"),
        "ANALOGOUS_TO",
        "knowledge_node",
        "knowledge_node",
        "情感信号是条件化的声学线索——语音中的情感特征(F0、语速)与情感状态的关联类似条件反射",
    )
    if N.get("巴甫洛夫条件反射")
    else None,
    (
        N.get("声码器 (Vocoder)"),
        N.get("傅里叶变换"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "声码器处理梅尔频谱(频域)→波形(时域)的变换，与傅里叶变换的时频变换密切相关",
    )
    if N.get("傅里叶变换")
    else None,
    (
        N.get("语音大模型 (Speech Foundation Model)"),
        N.get("涌现能力 (Emergent Abilities)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "Whisper/VALL-E展示了类似LLM的涌现能力——规模增大后出现零样本跨语言/跨说话人能力",
    ),
    (
        N.get("多模态学习 (Multimodal Learning)"),
        N.get("语音大模型 (Speech Foundation Model)"),
        "RELATED_TO",
        "knowledge_node",
        "knowledge_node",
        "GPT-4o将语音理解/生成集成到多模态LLM中——语音成为多模态的重要模态",
    ),
    (
        N.get("自动语音识别 (ASR)"),
        N.get("注意力机制"),
        "BUILDS_ON",
        "knowledge_node",
        "knowledge_node",
        "注意力机制在ASR中解决encoder-decoder的对齐问题——Listen, Attend and Spell",
    ),
]

# 过滤 None
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
speech_papers = c.execute(
    "SELECT COUNT(*) FROM papers WHERE fields_of_study LIKE '%speech%' OR fields_of_study LIKE '%audio%' OR fields_of_study LIKE '%TTS%' OR fields_of_study LIKE '%vocoder%'"
).fetchone()[0]
conn2.close()

print(f"\n{'=' * 50}")
print("📊 数据库全局统计:")
print(f"   知识节点: {kn_count} (CS: {cs_count})")
print(f"   论    文: {p_count} (语音AI: ~{speech_papers})")
print(f"   关    系: {r_count}")
print(f"   总节点数: {kn_count + p_count}")
print(f"{'=' * 50}")
