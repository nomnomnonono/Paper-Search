# 論文検索アプリ
## 概要
axXiv APIのPythonラッパーであるarxivライブラリを用いて取得した任意の論文データセットに対して、タイトルとアブストラクトが類似した論文を検索できます。


Hugging Faceにて機械学習における公平性の論文検索アプリを公開しているので是非ご活用ください。[link](https://huggingface.co/spaces/nomnomnonono/fairness-paper-search)

## TODO
- 他分野の検索を可能にする
- 検索精度の向上
  - pkeでキーワード抽出を行い、キーワードベクトルを作成して検索することを試みたが、抽出されるキーワードの精度が低かったため中止した
  - Sentence BERTのFTをしたいが、ある文章と類似する文章のペアをどのように作成するかを検討中
