"""将语音AI相关节点和论文的domain统一为 speech_ai"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "knowledge_nexus.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. 更新知识节点
speech_kn_names = [
    "自动语音识别 (ASR)", "语音合成 (TTS)", "语音自监督学习",
    "CTC (连接时序分类)", "声码器 (Vocoder)", "神经音频编解码 (Neural Audio Codec)",
    "语音大模型 (Speech Foundation Model)", "零样本语音克隆 (Zero-shot Voice Cloning)",
    "音频生成 (Audio Generation)", "Conformer (卷积+Transformer)",
    "说话人验证与声纹识别", "语音情感识别 (SER)",
]
for name in speech_kn_names:
    cur.execute("UPDATE knowledge_nodes SET domain = 'speech_ai' WHERE name = ?", (name,))
print(f"✅ 更新 {len(speech_kn_names)} 个知识节点 domain → speech_ai")

# 2. 更新论文 fields_of_study 第一项为 speech_ai
speech_paper_keys = [
    "WaveNet", "Tacotron 2", "Wav2Vec 2.0", "HuBERT", "Whisper", "Conformer",
    "AudioLM", "VALL-E", "EnCodec", "SoundStorm", "DeepSpeech 2", "HiFi-GAN",
    "GPT-SoVITS", "CosyVoice", "ChatTTS", "Fish Speech", "Voicebox", "AudioLDM",
]
updated = 0
for key in speech_paper_keys:
    row = cur.execute("SELECT id, fields_of_study FROM papers WHERE key_contributions = ?", (key,)).fetchone()
    if row:
        new_fos = "speech_ai," + (row[1] or "")
        cur.execute("UPDATE papers SET fields_of_study = ? WHERE id = ?", (new_fos, row[0]))
        updated += 1
print(f"✅ 更新 {updated} 篇论文 fields_of_study 前缀 → speech_ai")

conn.commit()
conn.close()
print("Done!")
