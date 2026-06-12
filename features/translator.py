import streamlit as st
from utils.gemini_client import stream_generate

LANGUAGES = [
    "英語（English）",
    "日本語",
    "中国語（簡体字）",
    "中国語（繁体字）",
    "韓国語（한국어）",
    "フランス語（Français）",
    "スペイン語（Español）",
    "ドイツ語（Deutsch）",
    "イタリア語（Italiano）",
    "ポルトガル語（Português）",
    "アラビア語（العربية）",
    "ロシア語（Русский）",
    "タイ語（ภาษาไทย）",
    "ベトナム語（Tiếng Việt）",
]

STYLES = {
    "自然な表現": "翻訳先言語として自然で読みやすい表現を使ってください。",
    "直訳": "原文の構造にできるだけ忠実に、直接的に翻訳してください。",
    "意訳・読みやすさ重視": "意味を保ちながら、翻訳先言語の読者が読みやすいよう自由に意訳してください。",
    "フォーマル": "丁寧でフォーマルな表現を使って翻訳してください。",
    "カジュアル": "日常会話のようなカジュアルな表現で翻訳してください。",
}


def build_prompts(text, target_lang, style):
    system = f"""あなたはプロの翻訳者です。ユーザーが提示するテキストを{target_lang}に翻訳してください。

【翻訳スタイル】{STYLES[style]}
【翻訳先言語】{target_lang}

翻訳結果のみを出力してください（説明や補足は不要です）。"""

    user_content = f"【翻訳するテキスト】\n{text}"

    return system, user_content


def translator_page(model_name: str):
    st.title("🌐 翻訳")
    st.caption("テキストを貼り付けて言語を選ぶだけで、自然な翻訳を生成します。")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📝 原文**")
        text = st.text_area(
            "原文",
            height=300,
            max_chars=10000,
            placeholder="ここに翻訳したいテキストを貼り付けてください...\n\n日本語、英語など、どの言語でもOKです。",
            label_visibility="collapsed",
        )

    with col2:
        st.markdown("**✨ 翻訳結果（ここに表示されます）**")
        st.empty()

    col_lang, col_style, col_temp = st.columns([2, 2, 1])
    with col_lang:
        target_lang = st.selectbox("翻訳先の言語", LANGUAGES)
    with col_style:
        style = st.selectbox("翻訳スタイル", list(STYLES.keys()))
    with col_temp:
        temperature = st.slider(
            "創造性",
            min_value=0.0, max_value=1.0, value=0.3, step=0.1,
            help="低めにすると忠実な翻訳、高めにすると自然さが増します",
        )

    if st.button("🌐 翻訳する", type="primary", use_container_width=True):
        if not text.strip():
            st.error("❌ 翻訳したいテキストを入力してください")
            return

        system_instr, user_content = build_prompts(text, target_lang, style)
        st.divider()
        st.markdown(f"### ✨ {target_lang}への翻訳結果")
        result = st.write_stream(
            stream_generate(model_name, system_instr, user_content, temperature=temperature, max_output_tokens=4096)
        )
        if result and not str(result).startswith("\n\n⚠️"):
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**原文**")
                st.text_area("orig", value=text, height=200, disabled=True, label_visibility="collapsed")
            with col_b:
                st.markdown(f"**{target_lang}**")
                st.text_area("trans", value=str(result), height=200, label_visibility="collapsed")
            with st.expander("📋 テキストをコピー"):
                st.code(result, language=None)
