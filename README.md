## WebpagePack-FireCrawl

## 謝辞

以下にインスパイアされて作りました。著者の@yamadashyさんに深く感謝します。

[ClaudeやChatGPTにリポジトリを丸ごと読み込ませるコマンドを作りました！](https://qiita.com/yamadashy/items/d150576759b84ea36274)

## 何をするもの？

指定したURLのコンテンツを1ファイルにまとめてくれるツールです。ClaudeやChatGPTに丸ごと読み込ませることができます。

以前作ったものはJina Readerを使用していましたが、これをFireCrawlに変更したものです。
https://github.com/kun432/webpagepack-jina

FireCrawlは、クラウドサービス・セルフホストの両方に対応しています。

![](/public/streamlit.png)

## 必要なもの

- VS Code
- Docker
- FireCrawl
  - FireCrawlのホスティングサービスを使う場合にはAPIキーが必要です。
  - セルフホストを使う場合には別途FireCrawlサーバの構築が必要です。

## 使い方

```
git clone https://github.com/kun432/webpagepack-firecrawl && cd webpagepack-firecrawl
docker compose up -d
```

## 免責

- 本ツールを使用して、スクレイピング先に損害を与えた場合でも、利用者の責任とし、スクリプト作成者は一切の責任を追わないものとします。**スクレイピングは自己責任でお願いします！**
