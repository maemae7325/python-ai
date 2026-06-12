import streamlit as st
from utils.gemini_client import stream_generate

PLATFORMS = {
    "X（旧Twitter）": {
        "limit": "140文字以内（日本語）",
        "style": "簡潔でインパクトのある文体。改行を効果的に使う。",
    },
    "Instagram": {
        "limit": "2200文字以内",
        "style": "視覚的なイメージを喚起する文体。絵文字を適度に使う。改行で読みやすく。",
    },
    "LinkedIn": {
        "limit": "3000文字以内",
        "style": "プロフェッショナルで洞察のある文体。ビジネス価値を伝える。",
    },
    "Facebook": {
        "limit": "63,206文字以内",
        "style": "親しみやすく会話的な文体。コミュニティとの対話を意識する。",
    },
    "note": {
        "limit": "制限なし",
        "style": "読み物として楽しめる、丁寧で読み応えのある文体。",
    },
    "Threads": {
        "limit": "500文字以内",
        "style": "自然で会話的な文体。気軽に読めるように。",
    },
}

TONES = ["情報的・役立つ", "親しみやすい・フレンドリー", "プロフェッショナル", "感情的・共感を呼ぶ", "ユーモアを交えた"]


def build_prompts(content, platform, tone, use_hashtags, variations):
    platform_info = PLATFORMS[platform]
    hashtag_instruction = "末尾に関連するハッシュタグを5〜10個追加してください。" if use_hashtags else "ハッシュタグは使わないでください。"
    variations_instruction = f"{variations}パターンの投稿文を生成してください。それぞれ「--- パターン1 ---」のように区切ってください。" if variations > 1 else "1つの投稿文を生成してください。"

    system = f"""あなたはSNSマーケティングの専門家です。ユーザーが提示するテーマをもとに、{platform}用の投稿文を作成してください。

【プラットフォーム】{platform}
【文字数制限】{platform_info['limit']}
【求める文体・スタイル】{platform_info['style']}
【トーン】{tone}
【ハッシュタグ】{hashtag_instruction}
【バリエーション】{variations_instruction}

エンゲージメント（いいね・シェア・コメント）を促進する効果的な投稿文を作成してください。"""

    user_content = f"【投稿内容・テーマ】\n{content}"

    return system, user_content


def sns_writer_page(model_name: str):
    st.title("📱 SNS投稿文生成")
    st.caption("投稿したい内容を入力するだけで、各プラットフォームに最適化した投稿文を生成します。")
    st.divider()

    col1, col2 = st.columns([3, 2])
    with col1:
        content = st.text_area(
            "投稿したい内容・テーマ ＊",
            height=180,
            max_chars=2000,
            placeholder="例:\n新しいカフェをオープンしました！\n・場所: 渋谷駅から徒歩3分\n・自家焙煎のコーヒーが自慢\n・毎日7時〜22時営業",
        )
    with col2:
        platform = st.selectbox("プラットフォーム", list(PLATFORMS.keys()))
        tone = st.selectbox("トーン", TONES)
        variations = st.selectbox("生成パターン数", [1, 3, 5], help="複数のバリエーションから選べます")
        use_hashtags = st.checkbox("ハッシュタグを追加する", value=True)
        temperature = st.slider(
            "創造性",
            min_value=0.0, max_value=1.0, value=0.8, step=0.1,
        )

    # プラットフォームのヒント表示
    if platform in PLATFORMS:
        st.info(f"💡 **{platform}**: {PLATFORMS[platform]['limit']}")

    if st.button("📱 投稿文を生成", type="primary", use_container_width=True):
        if not content.strip():
            st.error("❌ 投稿したい内容・テーマを入力してください")
            return

        system_instr, user_content = build_prompts(content, platform, tone, use_hashtags, int(variations))
        st.divider()
        st.markdown("### 📄 生成された投稿文")
        result = st.write_stream(
            stream_generate(model_name, system_instr, user_content, temperature=temperature, max_output_tokens=2048)
        )
        if result and not str(result).startswith("\n\n⚠️"):
            st.divider()
            with st.expander("📋 テキストをコピー"):
                st.code(result, language=None)
