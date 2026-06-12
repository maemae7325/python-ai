import streamlit as st
from utils.gemini_client import stream_generate

LEVELS = {
    "軽微な修正": "誤字脱字・表記ゆれ・句読点の修正のみ行い、文章の流れは極力変えないでください。",
    "標準的な改善": "誤字脱字の修正に加え、読みにくい箇所や不自然な表現を自然に改善してください。",
    "徹底的なリライト": "内容を保ちながら、全体的に読みやすく魅力的な文章にリライトしてください。",
}


def build_prompts(text, level, show_changes, target_audience):
    changes_instruction = ""
    if show_changes:
        changes_instruction = """
修正後の文章の後に、以下の形式で修正内容を説明してください:

---
## 修正・改善した点
- （修正点1）
- （修正点2）
..."""

    system = f"""あなたはプロの校正者・編集者です。ユーザーが提示する文章を校正・改善してください。

【修正レベル】{level}
{LEVELS[level]}

まず改善後の文章を出力してください。{changes_instruction}"""

    parts = []
    if target_audience.strip():
        parts.append(f"【想定読者】{target_audience}\n")
    parts += ["【校正する文章】", text]
    user_content = "\n".join(parts)

    return system, user_content


def proofreader_page(model_name: str):
    st.title("✏️ 文章校正・改善")
    st.caption("文章を貼り付けるだけで、誤字脱字の修正から全体的なリライトまで対応します。")
    st.divider()

    col1, col2 = st.columns([3, 2])
    with col1:
        text = st.text_area(
            "校正・改善したい文章 ＊",
            height=250,
            max_chars=10000,
            placeholder="ここに校正・改善したい文章を貼り付けてください...",
        )
    with col2:
        level = st.selectbox(
            "修正レベル",
            list(LEVELS.keys()),
            index=1,
            help="\n".join([f"**{k}**: {v}" for k, v in LEVELS.items()]),
        )
        target_audience = st.text_input(
            "想定読者（任意）",
            placeholder="例: ビジネスパーソン, 高校生, 専門家",
            max_chars=200,
        )
        show_changes = st.checkbox("修正箇所の説明を表示する", value=True)
        temperature = st.slider(
            "改善の積極度",
            min_value=0.0, max_value=1.0, value=0.4, step=0.1,
            help="高めにすると大胆な改善提案が増えます",
        )

    if st.button("✏️ 校正・改善する", type="primary", use_container_width=True):
        if not text.strip():
            st.error("❌ 校正・改善したい文章を入力してください")
            return

        system_instr, user_content = build_prompts(text, level, show_changes, target_audience)
        st.divider()

        col_before, col_after = st.columns(2)
        with col_before:
            st.markdown("**📝 修正前**")
            st.text_area("", value=text, height=200, disabled=True, label_visibility="collapsed")
        with col_after:
            st.markdown("**✨ 修正後**")

        st.divider()
        st.markdown("### ✨ 校正・改善結果")
        result = st.write_stream(
            stream_generate(model_name, system_instr, user_content, temperature=temperature, max_output_tokens=4096)
        )
        if result and not str(result).startswith("\n\n⚠️"):
            st.divider()
            with st.expander("📋 テキストをコピー"):
                st.code(result, language=None)
