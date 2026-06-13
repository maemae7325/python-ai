import streamlit as st
from utils.gemini_client import stream_generate
from utils.validators import contains_injection

TARGET_STYLES = {
    "ですます調（丁寧体）": "「です」「ます」を使う丁寧な文体に変換してください。",
    "だ・である調（常体）": "「だ」「である」を使う論述的な文体に変換してください。",
    "敬語（ビジネスメール風）": "取引先に送るビジネスメールのような格式のある敬語表現に変換してください。",
    "カジュアル（友達感覚）": "友達に話しかけるような気軽でくだけた文体に変換してください。",
    "ビジネス文書": "社内文書・報告書として適切な、簡潔で明確なビジネス文体に変換してください。",
    "学術・論文調": "論文や学術レポートとして適切な、客観的で厳密な文体に変換してください。",
    "ポップ・エンタメ調": "読んで楽しい、テンポの良いエンタメ的な文体に変換してください。",
    "子供向け（分かりやすく）": "小学生でも理解できる、やさしい言葉と文体に変換してください。",
}


def build_prompts(text, target_style):
    system = f"""あなたは文章スタイルの変換専門家です。ユーザーが提示する文章を指定された文体に変換してください。

【変換先の文体】
{TARGET_STYLES[target_style]}

内容や意味は変えずに、文体・表現のみを変換してください。変換後の文章のみを出力してください（説明は不要です）。"""

    user_content = f"【変換する文章】\n{text}"

    return system, user_content


def style_converter_page(model_name: str):
    st.title("🔄 文体変換")
    st.caption("文章を貼り付けて変換先のスタイルを選ぶだけで、自動的に文体を変換します。")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📝 変換前の文章**")
        text = st.text_area(
            "変換前",
            height=300,
            max_chars=10000,
            placeholder="ここに変換したい文章を貼り付けてください...",
            label_visibility="collapsed",
        )

    with col2:
        st.markdown("**✨ 変換後（ここに結果が表示されます）**")
        result_placeholder = st.empty()

    target_style = st.selectbox(
        "変換先の文体",
        list(TARGET_STYLES.keys()),
        help="変換後の文体スタイルを選択してください",
    )
    temperature = 0.4

    # スタイルの説明を表示
    st.info(f"💡 **{target_style}**: {TARGET_STYLES[target_style]}")

    if st.button("🔄 文体を変換", type="primary", use_container_width=True):
        if not text.strip():
            st.error("❌ 変換したい文章を入力してください")
            return
        if contains_injection(text):
            st.error("❌ 入力に不正なパターンが検出されました。内容を確認してください。")
            return

        system_instr, user_content = build_prompts(text, target_style)
        st.divider()
        st.markdown("### ✨ 変換結果")
        result = st.write_stream(
            stream_generate(model_name, system_instr, user_content, temperature=temperature, max_output_tokens=4096)
        )
        if result and not str(result).startswith("\n\n⚠️"):
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**変換前**")
                st.text_area("before", value=text, height=200, disabled=True, label_visibility="collapsed")
            with col_b:
                st.markdown("**変換後**")
                st.text_area("after", value=str(result), height=200, label_visibility="collapsed")
            with st.expander("📋 テキストをコピー"):
                st.code(result, language=None)
