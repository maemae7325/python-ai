# app.py の仕組み

## 概要

`app.py` は **ルーター兼シェル** として機能します。ビジネスロジックは一切持たず、以下の3つの役割だけを担っています。

---

## 1. 起動時の初期化（1〜83行）

```python
st.set_page_config()   # ブラウザタブのタイトル・アイコン・レイアウト設定
st.markdown(CSS)       # カスタムスタイルをHTMLとして注入
```

Streamlit はPythonスクリプトをトップから順に実行するため、この2つは必ず先頭に置く必要があります。

---

## 2. APIキーガード（86〜102行）

```python
if not GEMINI_API_KEY:
    st.error(...)
    st.stop()   # ここで処理を止める（以降のコードは実行されない）
```

`.env` にキーがなければエラーを表示して終了します。`st.stop()` が Streamlit のアーリーリターン相当です。

---

## 3. サイドバー + ルーティング（105〜154行）

### FEATURESディクショナリ

```python
FEATURES = {
    "📝 ブログ記事生成":          blog_writer_page,
    "📧 メール返信文生成":        email_reply_page,
    "📋 文章要約":                summarizer_page,
    # ...
}
```

| 要素 | 内容 |
|------|------|
| キー | UIに表示する機能名（絵文字付き文字列） |
| 値   | `features/*.py` で定義された page 関数 |

### ルーティングの流れ

```
st.radio() でユーザーが機能を選択
       ↓
selected_feature = "📝 ブログ記事生成"
       ↓
page_fn = FEATURES[selected_feature]   # blog_writer_page を取得
       ↓
page_fn(model_name=model_name)         # 各機能ページを描画
```

### モデル選択

```python
model_display = st.selectbox(...)           # 表示名を選択
model_name = AVAILABLE_MODELS[model_display]  # モデルIDに変換
# 例: "Gemini 2.5 Flash" → "gemini-2.5-flash"
```

---

## Streamlit の実行モデルとの関係

Streamlit はボタンクリックやウィジェット操作のたびに **スクリプト全体を上から再実行** します。そのため `app.py` は毎回以下の流れを辿ります。

```
① CSS を再注入
② APIキーを確認
③ サイドバーを描画（前回の選択状態は Streamlit がセッションで復元）
④ FEATURES[selected_feature] を呼び出す
```

状態管理が必要な場合は `st.session_state` を使いますが、`app.py` 自体はステートレスに保たれています。

---

## データフロー全体図

```
app.py（ルーティング）
  └─ サイドバーで選択された機能名 → FEATURES dict → page関数(model_name) を呼び出し
       └─ features/*.py（各機能）
            └─ build_prompt() でプロンプト組み立て
                 └─ utils/gemini_client.stream_generate() → Gemini API（ストリーミング）
                      └─ st.write_stream() でリアルタイム表示
```
