# RSS_arxiv
arxiv cs cl RSS からいい感じに新着をとってくるスクリプト

## 概要図
![fig](./image/fig.pdf)

## 取ってくる内容物
- title
- author
- url
- abstract
- area info

### abstract について
普通に取ってくると長いので以下の2種類で要約した
- TextRank
- lead-3

## config
HOME 以下に yaml format で置く  
- `_arxiv_ntfy.yml`: config 例、log path だけ変えてください
- url: slack webhook url
- abst\_type: textrank or lead-3
- time\_log: log path (feed time が入ってくる)
- exec\_log: log path (logging が入ってくる)

## requirements
- feedparser
- slackweb
- nltk
- gensim
- pyyaml (yaml)

## Note
- arXiv の更新タイミング例: 
`<pubDate>Tue, 18 Jun 2019 00:30:00 GMT</pubDate>` -> JST 9:30

## 参考
- https://qiita.com/TatsuyaMizuguchi17/items/35dd3dd1396864006031
