# ZEN Study 確認テスト取得ツール

ZEN大学の学習プラットフォーム「ZEN Study」から、受講中のオンデマンド授業の確認テスト（問題文・選択肢）を自動取得するCLIツールです。

## 機能

- 受講中のオンデマンドコース一覧を自動取得
- 各コースの確認テスト（exercise）を抽出
- 問題文と選択肢をパースしてJSON形式で出力
- セッションCookie認証に対応

## 必要要件

- Python 3.12+
- `uv` パッケージマネージャー

## インストール

```bash
# 依存関係のインストール
uv sync
```

## 使い方

### 1. セッションCookieの取得

1. ブラウザで ZEN Study (https://www.nnn.ed.nico) にログイン
2. DevTools (開発者ツール) を開く（F12キー）
3. Application / Storage タブ → Cookies → `https://www.nnn.ed.nico` を選択
4. `_zane_session` Cookieの値をコピー

### 2. 環境変数の設定

**方法1: .envファイルを使う（推奨）**

プロジェクトルートに `.env` ファイルを作成して、以下を記載：

```bash
ZANE_SESSION=your_session_cookie_value_here
```

`.env.example` をコピーして使うこともできます：

```bash
cp .env.example .env
# .envファイルを編集してセッションCookieの値を設定
```

**方法2: 環境変数で設定**

```bash
export ZANE_SESSION="your_session_cookie_value_here"
```

### 3. 実行

```bash
# uvを使って実行
uv run python -m src.main

# または仮想環境を有効化してから
source .venv/bin/activate
python -m src.main
```

## 出力

問題を取得するたびに、即座に個別のJSONファイルとして保存されます。

### ディレクトリ構造

```
output/
├── summary.json                           # 全体のサマリーJSON
├── 法学Ⅰ_【選択必修】オンデマンド_1288861581/
│   ├── 01._イントロダクション_267405152/
│   │   ├── 確認テスト_64293338822_q1.json
│   │   ├── 確認テスト_64293338822_q2.json
│   │   └── ...
│   └── 02._次のチャプター_xxxxx/
│       └── ...
└── 数学的思考とは何か_【選択必修】オンデマンド_1146336120/
    └── ...
```

### 個別問題ファイルの形式

各問題ファイル（例: `確認テスト_64293338822_q1.json`）の内容：

```json
{
  "course_id": 1288861581,
  "course_title": "法学Ⅰ:【選択必修】オンデマンド",
  "chapter_id": 267405152,
  "chapter_title": "01. イントロダクション",
  "exercise_id": 64293338822,
  "exercise_title": "確認テスト",
  "question_number": 1,
  "question": {
    "statement": "この授業の学習内容として適切なものはどれか。",
    "choices": [
      { "number": 1, "text": "特定の判例について詳細に学ぶ。" },
      { "number": 2, "text": "法の基本的な考え方、法の体系や役割について学ぶ。" },
      { "number": 3, "text": "具体的な法律を詳細に学ぶ。" },
      { "number": 4, "text": "法律事務所での実務内容について学ぶ。" }
    ]
  }
}
```

### サマリーファイルの形式

`output/summary.json` には全コース・チャプター・確認テストの構造が保存されます（問題の詳細を含む）。

## プロジェクト構成

```
zen-study-exercise/
├── pyproject.toml          # プロジェクト設定とパッケージ情報
├── README.md               # このファイル
├── .env                    # セッションCookie設定（gitignore対象）
├── .env.example            # .envファイルのテンプレート
├── src/
│   ├── __init__.py
│   ├── main.py            # メインエントリーポイント
│   ├── config.py          # 設定管理（.envファイル読み込み）
│   ├── client.py          # HTTPクライアント (httpx)
│   ├── parser.py          # HTMLパーサー (BeautifulSoup)
│   └── models.py          # データモデル (dataclass)
└── output/                # 出力先ディレクトリ
    ├── summary.json       # 全体サマリー
    └── [各コース]/[各チャプター]/[問題].json
```

## 注意事項

- セッションCookieには有効期限があります。認証エラーが出た場合は、新しいCookieを取得してください
- APIリクエスト間には1秒の遅延を入れています（サーバー負荷軽減のため）
- このツールはオンデマンドコースのみを対象としています（ライブ映像コースは除外）
- 取得できるのは問題文と選択肢のみで、正解情報は含まれません

## トラブルシューティング

### 「環境変数 ZANE_SESSION が設定されていません」

セッションCookieが設定されていません。以下のいずれかの方法で設定してください：

**方法1: .envファイルを作成**

```bash
# プロジェクトルートに .env ファイルを作成
echo 'ZANE_SESSION=your_session_cookie_value' > .env
```

**方法2: 環境変数で設定**

```bash
export ZANE_SESSION="your_session_cookie_value"
```

### 「認証に失敗しました」

セッションCookieの有効期限が切れています。ブラウザから新しいCookieを取得して再設定してください。

### 「問題が見つかりませんでした」

HTMLの構造が想定と異なる可能性があります。該当のexerciseをスキップして次に進みます。

## ライセンス

このツールは教育目的で作成されています。ZEN Studyの利用規約に従ってご利用ください。
