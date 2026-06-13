import streamlit as st
from utils.gemini_client import stream_generate
from utils.validators import contains_injection

TONES = {
    "親しみやすい": "読者に親近感を与える、温かみのある文体",
    "フォーマル": "丁寧で格式のある文体",
    "プロフェッショナル": "専門的で信頼感のある文体",
    "カジュアル": "気軽に読める、くだけた文体",
    "教育的": "分かりやすく学べる、解説重視の文体",
}

LENGTHS = {
    "短め（約500文字）": "500文字程度",
    "普通（約1000文字）": "1000文字程度",
    "長め（約2000文字）": "2000文字程度",
}


def build_prompts(topic, keywords, target, tone, length):
    system = f"""あなたはプロのブログライターです。ユーザーが指定したトピックをもとに、読みやすく魅力的なブログ記事を日本語で書いてください。

【文体】{tone}（{TONES[tone]}）
【文字数目安】{LENGTHS[length]}

以下の構成でMarkdown形式で出力してください:
# （魅力的なタイトル）

（読者を引き込む導入文）

## （見出し1）
（内容）

## （見出し2）
（内容）

（適切な数の見出しで構成してください）

## まとめ
（内容）

具体的な情報・例・数字を含め、読者に実際の価値を提供する内容にしてください。"""

    parts = [f"【記事のトピック】{topic}"]
    if keywords.strip():
        parts.append(f"【キーワード】{keywords}")
    if target.strip():
        parts.append(f"【ターゲット読者】{target}")
    user_content = "\n".join(parts)

    return system, user_content


def blog_writer_page(model_name: str):
    st.title("📝 ブログ記事生成")
    st.caption("トピックを入力するだけで、読みやすいブログ記事を自動生成します。")
    st.divider()

    col1, col2 = st.columns([3, 2])
    with col1:
        topic = st.text_input(
            "記事のトピック ＊",
            placeholder="例: 初心者向けPythonプログラミング入門",
            max_chars=200,
        )
        keywords = st.text_input(
            "キーワード（任意）",
            placeholder="例: Python, プログラミング, 初心者, 独学",
            max_chars=200,
        )
        target = st.text_input(
            "ターゲット読者（任意）",
            placeholder="例: プログラミング未経験の20〜30代社会人",
            max_chars=200,
        )
    with col2:
        tone = st.selectbox("文体", list(TONES.keys()))
        length = st.selectbox("記事の長さ", list(LENGTHS.keys()), index=1)

    temperature = 0.7
    if st.button("📝 記事を生成", type="primary", use_container_width=True):
        if not topic.strip():
            st.error("❌ 記事のトピックを入力してください")
            return
        if contains_injection(topic, keywords, target):
            st.error("❌ 入力に不正なパターンが検出されました。内容を確認してください。")
            return
        system_instr, user_content = build_prompts(topic, keywords, target, tone, length)
        st.divider()
        st.markdown("### 📄 生成結果")
        result = st.write_stream(
            stream_generate(model_name, system_instr, user_content, temperature=temperature, max_output_tokens=4096)
        )
        if result and not str(result).startswith("\n\n⚠️"):
            st.divider()
            with st.expander("📋 テキストをコピー"):
                st.code(result, language=None)
