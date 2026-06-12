import streamlit as st
from config import GEMINI_API_KEY, AVAILABLE_MODELS, DEFAULT_MODEL
from features.blog_writer import blog_writer_page
from features.email_reply import email_reply_page
from features.summarizer import summarizer_page
from features.proofreader import proofreader_page
from features.sns_writer import sns_writer_page
from features.title_generator import title_generator_page
from features.style_converter import style_converter_page
from features.translator import translator_page
from features.brainstorm import brainstorm_page

# ─── ページ設定 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Writing Tool",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── カスタムCSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* サイドバーのスタイル */
[data-testid="stSidebar"] {
    background-color: #1E1E2E;
}
[data-testid="stSidebar"] * {
    color: #CDD6F4 !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem !important;
    padding: 0.25rem 0;
}
[data-testid="stSidebar"] h1 {
    color: #CBA6F7 !important;
    font-size: 1.4rem !important;
}

/* プライマリボタン */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    border: none;
    color: white !important;
    font-weight: 600;
    font-size: 1rem;
    padding: 0.65rem 1.5rem;
    border-radius: 0.5rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.45);
}
.stButton > button[kind="primary"]:active {
    transform: translateY(0);
}

/* メインコンテナ */
.main .block-container {
    padding-top: 1.5rem;
    max-width: 1100px;
}

/* タイトル */
h1 { color: #1E293B; font-weight: 700; }
h2, h3 { color: #334155; }

/* セパレーター */
hr { border-color: #E2E8F0; margin: 1.2rem 0; }

/* コードブロック（コピー用） */
[data-testid="stCodeBlock"] {
    border-radius: 0.5rem;
}

/* info ボックス */
.stAlert {
    border-radius: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ─── APIキーチェック ────────────────────────────────────────────────────────
if not GEMINI_API_KEY:
    st.error("""
    ⚠️ **Gemini APIキーが設定されていません**

    以下の手順で設定してください:

    1. `.env.example` を `.env` にコピー
    2. [Google AI Studio](https://aistudio.google.com/app/apikey) でAPIキーを取得
    3. `.env` ファイルの `GEMINI_API_KEY=` にキーを設定
    4. アプリを再起動

    ```bash
    cp .env.example .env
    # .env を編集して GEMINI_API_KEY を設定
    ```
    """)
    st.stop()

# ─── サイドバー ────────────────────────────────────────────────────────────
FEATURES = {
    "📝 ブログ記事生成": blog_writer_page,
    "📧 メール返信文生成": email_reply_page,
    "📋 文章要約": summarizer_page,
    "✏️ 文章校正・改善": proofreader_page,
    "📱 SNS投稿文生成": sns_writer_page,
    "💡 タイトル・キャッチコピー生成": title_generator_page,
    "🔄 文体変換": style_converter_page,
    "🌐 翻訳": translator_page,
    "🧠 アイデア出し": brainstorm_page,
}

with st.sidebar:
    st.markdown("# ✍️ AI Writing Tool")
    st.markdown("---")

    # モデル選択
    st.markdown("### ⚙️ モデル設定")
    model_display = st.selectbox(
        "使用するモデル",
        list(AVAILABLE_MODELS.keys()),
        label_visibility="collapsed",
    )
    model_name = AVAILABLE_MODELS[model_display]

    st.markdown("---")

    # ナビゲーション
    st.markdown("### 🛠️ 機能一覧")
    selected_feature = st.radio(
        "機能を選択",
        options=list(FEATURES.keys()),
        label_visibility="collapsed",
    )

    st.markdown("---")

    # API状態
    st.markdown("**✅ Gemini API 接続済み**")
    st.caption(f"モデル: `{model_name}`")

    st.markdown("---")
    st.caption(
        "🔒 個人利用ツール\n\n"
        "入力データは Gemini API に送信されます。"
    )

# ─── メインコンテンツ ───────────────────────────────────────────────────────
page_fn = FEATURES[selected_feature]
page_fn(model_name=model_name)
