import streamlit as st
from utils.gemini_client import stream_generate

TYPES = {
    "ブログタイトル": "読者がクリックしたくなる魅力的なブログ記事タイトル",
    "記事の見出し（H2/H3）": "記事内で使う分かりやすい見出し",
    "キャッチコピー": "商品・サービス・ブランドのキャッチフレーズ",
    "YouTube動画タイトル": "クリック率の高いYouTube動画タイトル",
    "メールの件名": "開封率を高めるメールの件名",
    "プレスリリースタイトル": "ニュース性の高いプレスリリースタイトル",
}

STYLES = {
    "クリックしたくなる（煽り系）": "好奇心を刺激し、思わずクリックしたくなる",
    "SEO重視": "検索キーワードを含み、検索上位を狙える",
    "シンプル・直接的": "内容がすぐ分かる、シンプルで明快な",
    "個性的・ユニーク": "他とは違う、印象に残る個性的な",
    "数字を使った": "「5つの」「10分で」など数字を含む具体的な",
    "疑問形": "読者に問いかける疑問形の",
}


def build_prompts(content, output_type, style, count):
    system = f"""あなたはコピーライティングの専門家です。ユーザーが提示する内容に対して、{count}個の{TYPES[output_type]}を生成してください。

【タイトルのスタイル】{STYLES[style]}タイトルにしてください
【生成数】{count}個

各タイトルを番号付きリスト形式（1. 2. 3. ...）で出力してください。
バリエーション豊かに、それぞれ異なるアプローチで作成してください。"""

    user_content = f"【内容・テーマ】\n{content}"

    return system, user_content


def title_generator_page(model_name: str):
    st.title("💡 タイトル・キャッチコピー生成")
    st.caption("内容を入力するだけで、魅力的なタイトルやキャッチコピーを複数生成します。")
    st.divider()

    content = st.text_area(
        "内容・テーマ ＊",
        height=150,
        max_chars=2000,
        placeholder="例: Pythonを使った機械学習入門の記事。初心者が最初の機械学習モデルを作れるようになることが目標。scikit-learnを使用。",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        output_type = st.selectbox("タイトルの種類", list(TYPES.keys()))
    with col2:
        style = st.selectbox("スタイル", list(STYLES.keys()))
    with col3:
        count = st.selectbox("生成数", [5, 10, 15, 20], index=0)

    temperature = st.slider(
        "創造性",
        min_value=0.0, max_value=1.0, value=0.9, step=0.1,
        help="高めにすると多様でユニークなタイトルが生成されます",
    )

    if st.button("💡 タイトルを生成", type="primary", use_container_width=True):
        if not content.strip():
            st.error("❌ 内容・テーマを入力してください")
            return

        system_instr, user_content = build_prompts(content, output_type, style, count)
        st.divider()
        st.markdown(f"### 📄 生成された{output_type}（{count}案）")
        result = st.write_stream(
            stream_generate(model_name, system_instr, user_content, temperature=temperature, max_output_tokens=2048)
        )
        if result and not str(result).startswith("\n\n⚠️"):
            st.divider()
            with st.expander("📋 テキストをコピー"):
                st.code(result, language=None)
