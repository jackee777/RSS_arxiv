# RSS_arxiv
arxiv cs cl RSS からいい感じに新着をとってくるスクリプト

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
- url: slack webhook url
- abst\_type: textrank or lead-3

## requirements
- feedparser
- slackweb
- nltk
- gensim
- pyyaml (yaml)
