import streamlit as st
from utils.gemini_client import stream_generate
from utils.validators import contains_injection

IDEA_TYPES = {
    "ブログ記事ネタ": "ブログ記事のトピック・ネタ案",
    "コンテンツ企画": "コンテンツマーケティングの企画案",
    "タイトル・切り口のアイデア": "同じテーマでも異なる切り口・アングル",
    "ターゲット別アイデア": "異なるターゲット・読者層向けのアプローチ案",
    "記事の構成案": "記事の章立て・目次案",
    "FAQ・よくある質問": "読者がよく持つ疑問・質問リスト",
    "事業・プロダクトアイデア": "新規事業・プロダクトのアイデア",
    "マーケティングアイデア": "プロモーション・マーケティング施策案",
}

PERSPECTIVES = {
    "バランス良く": "様々な観点からバランス良く",
    "ニッチ・マニア向け": "専門的・マニア向けのニッチな視点で",
    "初心者・入門向け": "初心者にも分かりやすい入門的な視点で",
    "逆張り・意外性": "一般的な見方とは逆の、意外性のある視点で",
    "トレンド重視": "最新トレンドや時事性を意識した視点で",
    "実用・課題解決重視": "読者の実際の課題解決に焦点を当てた視点で",
}


def build_prompts(topic, idea_type, perspective, count, extra):
    system = f"""あなたはクリエイティブなコンテンツストラテジストです。ユーザーが提示するテーマに関する{IDEA_TYPES[idea_type]}を{count}個生成してください。

【アイデアの視点】{PERSPECTIVES[perspective]}アイデアを出してください
【生成数】{count}個

番号付きリスト形式で出力し、各アイデアに簡単な説明（1〜2文）を加えてください。
バリエーション豊かで、実際に使えるアイデアを提案してください。"""

    parts = [f"【テーマ】{topic}"]
    if extra.strip():
        parts.append(f"【追加条件】{extra}")
    user_content = "\n".join(parts)

    return system, user_content


def brainstorm_page(model_name: str):
    st.title("🧠 アイデア出し（ブレインストーミング）")
    st.caption("テーマを入力するだけで、コンテンツのアイデアや切り口を大量に生成します。")
    st.divider()

    col1, col2 = st.columns([3, 2])
    with col1:
        topic = st.text_input(
            "テーマ ＊",
            placeholder="例: 在宅ワーク, 健康的な食事, Python機械学習, 副業",
            max_chars=200,
        )
        extra = st.text_area(
            "追加条件・制約（任意）",
            height=100,
            max_chars=1000,
            placeholder="例:\n- 30代の共働き夫婦向け\n- 予算1万円以内\n- 初心者でもすぐ試せる内容",
        )
    with col2:
        idea_type = st.selectbox("アイデアの種類", list(IDEA_TYPES.keys()))
        perspective = st.selectbox("視点・アングル", list(PERSPECTIVES.keys()))
        count = st.selectbox("生成数", [5, 10, 15, 20], index=1)

    temperature = 0.9
    if st.button("🧠 アイデアを生成", type="primary", use_container_width=True):
        if not topic.strip():
            st.error("❌ テーマを入力してください")
            return
        if contains_injection(topic, extra):
            st.error("❌ 入力に不正なパターンが検出されました。内容を確認してください。")
            return

        system_instr, user_content = build_prompts(topic, idea_type, perspective, count, extra)
        st.divider()
        st.markdown(f"### 💡 「{topic}」に関する{IDEA_TYPES[idea_type]}（{count}案）")
        result = st.write_stream(
            stream_generate(model_name, system_instr, user_content, temperature=temperature, max_output_tokens=3000)
        )
        if result and not str(result).startswith("\n\n⚠️"):
            st.divider()
            with st.expander("📋 テキストをコピー"):
                st.code(result, language=None)
