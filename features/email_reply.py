import streamlit as st
from utils.gemini_client import stream_generate

TONES = ["丁寧・フォーマル", "親しみやすい", "簡潔・ビジネス", "カジュアル"]
LANGUAGES = ["日本語", "English", "日本語と英語（両方）"]


def build_prompts(received_email, reply_points, tone, language):
    lang_instruction = {
        "日本語": "日本語で返信してください。",
        "English": "Please write the reply in English.",
        "日本語と英語（両方）": "日本語と英語の両方で返信を書いてください。日本語版の後に英語版を書いてください。",
    }[language]

    system = f"""あなたはメール返信の専門家です。ユーザーが提示する受信メールに対する適切な返信文を作成してください。

【返信の文体】{tone}
【言語】{lang_instruction}

返信メールの件名と本文を含めて出力してください。件名は「件名: 」で始めてください。
署名は「（署名）」と記載してください（実際の署名は含めないでください）。"""

    parts = ["【受信メール】", received_email]
    if reply_points.strip():
        parts += ["\n【返信に含めたい要点】", reply_points]
    user_content = "\n".join(parts)

    return system, user_content


def email_reply_page(model_name: str):
    st.title("📧 メール返信文生成")
    st.caption("受信メールを貼り付けるだけで、適切な返信文を自動生成します。")
    st.divider()

    col1, col2 = st.columns([3, 2])
    with col1:
        received_email = st.text_area(
            "受信メールの内容 ＊",
            height=200,
            max_chars=5000,
            placeholder="ここに受信したメールの文章を貼り付けてください...",
        )
        reply_points = st.text_area(
            "返信に含めたい要点（任意）",
            height=100,
            max_chars=1000,
            placeholder="例:\n- 参加可能です\n- 日程は来週月曜日を希望します\n- 資料を添付します",
        )
    with col2:
        tone = st.selectbox("返信の文体", TONES)
        language = st.selectbox("言語", LANGUAGES)
        temperature = st.slider(
            "創造性",
            min_value=0.0, max_value=1.0, value=0.4, step=0.1,
            help="低めにすると安定した定型文、高めにすると自然なバリエーションが出ます",
        )

    if st.button("📧 返信文を生成", type="primary", use_container_width=True):
        if not received_email.strip():
            st.error("❌ 受信メールの内容を入力してください")
            return
        system_instr, user_content = build_prompts(received_email, reply_points, tone, language)
        st.divider()
        st.markdown("### 📄 生成された返信文")
        result = st.write_stream(
            stream_generate(model_name, system_instr, user_content, temperature=temperature, max_output_tokens=2048)
        )
        if result and not str(result).startswith("\n\n⚠️"):
            st.divider()
            with st.expander("📋 テキストをコピー"):
                st.code(result, language=None)
