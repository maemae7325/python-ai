# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 起動・実行

```bash
# アプリ起動
python3 -m streamlit run app.py

# 依存パッケージのインストール
pip3 install -r requirements.txt

# APIキーの設定（初回のみ）
cp .env.example .env
# .env に GEMINI_API_KEY=... を記入
```

Streamlit の初回起動時にメール入力プロンプトが出る場合は、先に `~/.streamlit/credentials.toml` を作成してスキップできる:
```bash
mkdir -p ~/.streamlit
printf '[general]\nemail = ""\n' > ~/.streamlit/credentials.toml
```

## テスト

テストスイートは存在しない。動作確認はアプリを起動して手動で行う。

## アーキテクチャ

### データフロー

```
app.py（ルーティング）
  └─ サイドバーで選択された機能名 → FEATURES dict → page関数(model_name) を呼び出し
       └─ features/*.py（各機能）
            └─ build_prompt() でプロンプト組み立て
                 └─ utils/gemini_client.stream_generate() → Gemini API（ストリーミング）
                      └─ st.write_stream() でリアルタイム表示
```

### 主要ファイルの役割

- **`app.py`**: `st.set_page_config`・CSS・APIキーチェック・サイドバーUI・`FEATURES` dict によるルーティングのみ。ビジネスロジックは持たない。
- **`config.py`**: `.env` から `GEMINI_API_KEY` を読み込む。`AVAILABLE_MODELS`（表示名 → モデルID のdict）を定義。
- **`utils/gemini_client.py`**: `google-genai` SDK の薄いラッパー。`get_client()` は `@st.cache_resource` でキャッシュ。`stream_generate()` はジェネレータを返し、`st.write_stream()` に直接渡せる。
- **`features/*.py`**: 各機能モジュール。それぞれ `build_prompt()` と `*_page(model_name: str)` の2関数だけを持つ。

### 新機能の追加パターン

1. `features/new_feature.py` を作成し、`build_prompt()` と `new_feature_page(model_name: str)` を実装
2. `app.py` の `FEATURES` dict に `"🆕 機能名": new_feature_page` を追加
3. `app.py` の import に追加

### Gemini API

- SDK: `google-genai`（`google.generativeai` は廃止済み・使用禁止）
- クライアント: `from google import genai` / `genai.Client(api_key=...)`
- ストリーミング: `client.models.generate_content_stream(model, contents, config)`
- 利用可能なモデル: `gemini-2.5-flash`（推奨）/ `gemini-2.0-flash` / `gemini-2.5-pro`
- モデル一覧の確認: `python3 -c "from google import genai; c=genai.Client(api_key='KEY'); [print(m.name) for m in c.models.list()]"`
- 実行環境は macOS システム Python 3.9。`google-genai` SDK が `FutureWarning` を大量出力するが動作に問題はなく無視して良い

### 出力表示の規則

- 生成結果は `st.write_stream(stream_generate(...))` で表示し、戻り値（完成テキスト）を変数に受け取る
- コピー用テキストは `st.expander` 内の `st.code(result, language=None)` で提供（コピーボタンが自動付与される）
- エラー文字列は `"\n\n⚠️ エラーが発生しました:"` で始まるため、`str(result).startswith("\n\n⚠️")` で判定できる

## 各機能の設計詳細

### 選択肢 dict の命名規則

各機能ファイルの先頭にモジュールレベルの dict を置き、**UIの表示ラベル → プロンプトに埋め込む文字列** をマッピングする。

```python
# 良い例（このプロジェクトの規則）
LEVELS = {
    "軽微な修正": "誤字脱字・表記ゆれ・句読点の修正のみ行い...",
    "標準的な改善": "誤字脱字の修正に加え、読みにくい箇所や...",
}
# UI側: st.selectbox("修正レベル", list(LEVELS.keys()))
# プロンプト側: f"【修正レベル】{LEVELS[level]}"
```

`sns_writer.py` の `PLATFORMS` だけは `{"limit": str, "style": str}` のネスト構造（プラットフォームごとに複数の属性を持つため）。

### プロンプトの記述規則

- 冒頭に役割宣言: `"あなたは〇〇の専門家です。"`
- パラメータは `【ラベル】値` 形式で列挙
- 任意入力が空の場合はそのセクションをプロンプトから除外する（`if x.strip():` で判定）
- 出力形式の指定を末尾に明示（Markdown形式、番号付きリスト、翻訳結果のみ、など）

### temperature の使い分け

| 用途 | デフォルト値 | 該当機能 |
|------|-------------|---------|
| 創作・バリエーション重視 | 0.9 | タイトル生成、アイデア出し |
| 自然な文章生成 | 0.7〜0.8 | ブログ記事、SNS投稿 |
| 定型・忠実さ重視 | 0.3〜0.4 | 翻訳、要約、校正、メール返信、文体変換 |

### max_output_tokens の使い分け

- **4096**: 長文生成（ブログ記事・校正・文体変換・翻訳）
- **3000**: アイデア出し（リスト形式で数が多い）
- **2048**: 短〜中文生成（メール・要約・SNS・タイトル）

### UIレイアウトのパターン

```python
# 標準パターン: 入力エリア左(広め) + 設定パネル右
col1, col2 = st.columns([3, 2])

# 対比パターン: 変換前後・原文と翻訳を横並びで表示（style_converter・translator）
col1, col2 = st.columns(2)

# 設定3項目横並び（summarizer・title_generator）
col1, col2, col3 = st.columns(3)
```
