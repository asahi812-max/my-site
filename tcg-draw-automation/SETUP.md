# 最後の公開設定（最初の1回だけ）

## 1. 一覧ページを公開する

このリポジトリには既存の個人サイトがあるため、ルートの `index.html` は変更していません。抽選ノートはサブフォルダ `tcg-draw-automation/` にあります。

1. GitHubで `https://github.com/asahi812-max/my-site` を開く
2. **Settings → Pages** を開く
3. Build and deployment の Source を **Deploy from a branch** にする
4. Branch を **main**、フォルダを **/(root)** にして Save
5. 数分待ち、 `https://asahi812-max.github.io/my-site/tcg-draw-automation/` を開く

すでに Pages が有効なら、設定を変えず上のURLを確認してください。既存サイトのルートページはそのまま残ります。

## 2. 自動収集を手動で一度テストする

1. リポジトリの **Actions** を開く
2. 左の **Collect TCG lottery candidates** を選ぶ
3. **Run workflow → Run workflow** を押す
4. 実行が緑のチェックになったら、 `tcg-draw-automation/data/collected.json` の更新時刻と件数を確認する

通常は毎日21時（日本時間）を目安に自動実行します。GitHubの混雑などで実行時刻がずれることがあります。

## 3. 現在の自動化範囲と注意点

- 公開RSS検索から、直近60日以内のカード抽選・応募関連の記事候補を集めます。
- 候補には古い告知や第三者記事が混ざることがあります。**募集が有効か、公式か、締切・発表日・本人確認・名義条件が何かは、元の告知を確認する必要があります。**
- 今の収集処理は、締切や本人確認条件を記事本文から確定抽出する機能ではありません。不確かな条件は「未確認」のままです。
- Xの全投稿を巡回する機能は未接続です。無料で使えるAPIアクセスが確認できた場合に別途追加します。
- 応募フォームの自動送信、ログイン、BOT対策回避は行いません。
