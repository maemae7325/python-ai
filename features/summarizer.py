import streamlit as st
from utils.gemini_client import stream_generate
from utils.validators import contains_injection

LENGTHS = {
    "超短め（1〜2文）": "1〜2文で",
    "短め（3〜5文）": "3〜5文で",
    "普通（5〜8文）": "5〜8文で",
    "詳細（重要点を全て含める）": "重要なポイントを漏らさず詳細に",
}

STYLES = {
    "文章形式": "読みやすい文章形式（段落）で",
    "箇条書き": "箇条書き（・）で",
    "見出し＋箇条書き": "見出しと箇条書きを組み合わせたMarkdown形式で",
}


def build_prompts(text, length, style, extra_instruction):
    system = f"""以下のテキストを要約してください。

【要約の長さ】{LENGTHS[length]}まとめてください
【出力スタイル】{STYLES[style]}出力してください

元のテキストの重要なポイントを正確に捉え、分かりやすく簡潔にまとめてください。"""

    parts = []
    if extra_instruction.strip():
        parts.append(f"【追加指示】{extra_instruction}\n")
    parts += ["【要約するテキスト】", text]
    user_content = "\n".join(parts)

    return system, user_content


def summarizer_page(model_name: str):
    st.title("📋 文章要約")
    st.caption("長い文章を貼り付けるだけで、要点をコンパクトにまとめます。")
    st.divider()

    text = st.text_area(
        "要約したい文章 ＊",
        height=250,
        max_chars=10000,
        placeholder="ここに要約したい文章を貼り付けてください...\n\n記事、論文、レポート、ニュース記事など何でもOKです。",
    )

    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("要約の長さ", list(LENGTHS.keys()), index=1)
    with col2:
        style = st.selectbox("出力スタイル", list(STYLES.keys()))
    temperature = 0.3

    extra_instruction = st.text_input(
        "追加の指示（任意）",
        placeholder="例: 技術的な用語は分かりやすく言い換えてください",
        max_chars=200,
    )

    if st.button("📋 要約する", type="primary", use_container_width=True):
        if not text.strip():
            st.error("❌ 要約したい文章を入力してください")
            return
        if contains_injection(text, extra_instruction):
            st.error("❌ 入力に不正なパターンが検出されました。内容を確認してください。")
            return
        if len(text) < 50:
            st.warning("⚠️ 文章が短すぎる可能性があります。より長い文章で試してください。")

        system_instr, user_content = build_prompts(text, length, style, extra_instruction)
        st.divider()

        col_orig, col_summary = st.columns(2)
        with col_orig:
            st.markdown("**📄 元の文章**")
            st.markdown(f"`{len(text)}文字`")
        with col_summary:
            st.markdown("**✨ 要約結果**")

        st.divider()
        st.markdown("### ✨ 要約結果")
        result = st.write_stream(
            stream_generate(model_name, system_instr, user_content, temperature=temperature, max_output_tokens=2048)
        )
        if result and not str(result).startswith("\n\n⚠️"):
            st.caption(f"元の文章: {len(text)}文字 → 要約: {len(str(result))}文字")
            st.divider()
            with st.expander("📋 テキストをコピー"):
                st.code(result, language=None)
