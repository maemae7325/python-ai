# ✍️ AI Writing Tool

Gemini API を使った個人用 AI ライティングツールです。

## 機能一覧

| 機能 | 説明 |
|------|------|
| 📝 ブログ記事生成 | トピックから SEO を意識したブログ記事を自動生成 |
| 📧 メール返信文生成 | 受信メールへの適切な返信文を生成 |
| 📋 文章要約 | 長い文章を指定した長さ・スタイルで要約 |
| ✏️ 文章校正・改善 | 誤字脱字修正から全体リライトまで対応 |
| 📱 SNS 投稿文生成 | X / Instagram / LinkedIn 等に最適化した投稿文を生成 |
| 💡 タイトル・キャッチコピー生成 | 魅力的なタイトルやキャッチコピーを複数案生成 |
| 🔄 文体変換 | 敬語 ↔ カジュアル、ビジネス調、学術調など文体を自動変換 |
| 🌐 翻訳 | 14 言語への自然な翻訳 |
| 🧠 アイデア出し | コンテンツネタ・企画アイデアをブレインストーミング |

## セットアップ

### 1. APIキーの取得

[Google AI Studio](https://aistudio.google.com/app/apikey) から Gemini API キーを取得してください。

### 2. 環境構築

```bash
# リポジトリのクローン（またはファイルをダウンロード）
cd python-ai

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. APIキーの設定

```bash
cp .env.example .env
```

`.env` ファイルを開いて APIキーを設定:

```
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. アプリの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動で開きます。

## プロジェクト構成

```
python-ai/
├── app.py                  # メインアプリ（ナビゲーション・ルーティング）
├── config.py               # 設定（APIキー・モデル）
├── requirements.txt        # 依存パッケージ
├── .env                    # APIキー（要作成・gitignore推奨）
├── .env.example            # APIキーのテンプレート
├── utils/
│   └── gemini_client.py    # Gemini API ラッパー（ストリーミング対応）
└── features/
    ├── blog_writer.py      # ブログ記事生成
    ├── email_reply.py      # メール返信文生成
    ├── summarizer.py       # 文章要約
    ├── proofreader.py      # 文章校正・改善
    ├── sns_writer.py       # SNS 投稿文生成
    ├── title_generator.py  # タイトル・キャッチコピー生成
    ├── style_converter.py  # 文体変換
    ├── translator.py       # 翻訳
    └── brainstorm.py       # アイデア出し
```

## 使用モデル

サイドバーから使用するモデルを切り替えられます:

- **Gemini 2.0 Flash**（推奨・高速）: バランスが良く、日常的な用途に最適
- **Gemini 1.5 Flash**（高速・安定）: 安定性重視
- **Gemini 1.5 Pro**（高品質）: より高品質な出力が必要な場合
