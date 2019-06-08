import feedparser
import slackweb
import nltk
from gensim.summarization import keywords
import yaml

import re
import time
import os
import sys

# TODO: connection error; detect Robot へのエラー検出
# slack の attachment が一回につき100件まで; 超えたら死にます
# summary は textrank or lead-3
# config は yaml format; home 以下においてあること前提
# (c) Satoru Katsumata

class Entry:
    """
    arxiv の1エントリを parse していい感じに保持しておく
    entry: RSS entry parse
    abst_type: lead-3 or textrank
    """
    def __init__(self, entry, abst_type):
        # authors, url, title, abst, area
        # use lead-3 as a summary 
        author_list = [re.sub('<.+?>', '', a) for a in entry['author'].split(', ')]
        self.author = '*AUTHOR*:\t' + '; '.join(author_list)
        self.url = entry['link']
        self.title = re.sub(" \(arXiv:.+\)$", "", entry['title'])

        entire_summary = re.sub('<.+?>', '', entry['summary'])
        if abst_type == 'lead-3':
            entire_summary_list = nltk.sent_tokenize(entire_summary)
            self.summary = '\n'.join(entire_summary_list[:3])
        elif abst_type == 'textrank':
            self.summary = '*Keyword*: ' + keywords(entire_summary, lemmatize=True).replace('\n', '; ') + ';'

        supplement_info = re.search('\(arXiv:.+\)$', entry['title']).group()
        self.area = re.search('\[.+\]', supplement_info).group()
        self.title = self.title + '\t' + self.area
        if re.search('UPDATED', supplement_info):
            self.title = self.title + '\t[UPDATED]' 

    def make_attachment(self):
        # slack へ送るように整形
        attachment = dict()
        attachment['fallback'] = 'arXiv RSS feed'
        attachment['title'] = self.title
        attachment['title_link'] = self.url
        attachment['text'] = self.author + '\n' + self.summary
        attachment['color'] = '#2eb886'

        return attachment

def get_feed_time(file_path):
    # time log file から最後に更新された時間を抜き取る
    exist_log = os.path.exists(file_path)
    if not exist_log:
        return None

    with open(file_path) as log_file:
        for line in log_file:
            time = line
    return time.strip()

def write_feed_time(file_path, feed_time):
    # time log file の末尾に書き込む
    with open(file_path, 'a') as log_file:
        log_file.write(feed_time)
        log_file.write('\n')

def logging(file_path, message):
    with open(file_path, 'a') as log_file:
        current_time = time.strptime(time.ctime())
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
        log_file.write(current_time)
        log_file.write(':\t' + message)
        log_file.write('\n')

def main():
    # config file を読み込む
    config_path = os.path.join(os.environ['HOME'], '.arxiv_ntfy.yml')
    with open(config_path) as config_file:
        config = yaml.load(config_file, Loader=yaml.BaseLoader)

    # 前回の RSS feed time を読み込む
    log_path = config['time_log']
    previous_feed_time = get_feed_time(log_path)

    # slack へ飛ばす用の入れ物作成
    slack_sender = slackweb.Slack(url=config['url'])
    rss_result = feedparser.parse("http://export.arxiv.org/rss/cs.CL")
    attachment_list = list()

    # feed data を入れ物へ（多分関数化した方が良い）
    date_info = dict()
    feed_time = rss_result['feed']['updated_parsed']
    feed_time = time.strftime('%Y-%m-%d %H:%M:%S', feed_time)
    date_info['title'] = 'arXiv RSS update'
    date_info['text'] = '*FEED* *TIME*: '+ feed_time + '\n*POST* *NUM*: ' + str(len(rss_result['entries']))
    attachment_list.append(date_info)

    # 過去の feed time と今回の feed time を読み取って一致したら送らない
    if previous_feed_time == feed_time:
        message = 'do not post the arxiv, because not update at RSS feed.'
        logging(config['exec_log'], message)
        sys.exit(0)

    # 1エントリずつ parse -> 入れ物へ
    for entry in rss_result['entries']:
        parsed_entry = Entry(entry, config['abst_type'])
        attachment_list.append(parsed_entry.make_attachment())

    # 送る
    slack_sender.notify(attachments=attachment_list)
    # print(attachment_list)

    # logging
    write_feed_time(config['time_log'], feed_time)
    message = 'post the new arrival in arXiv cs.CL.'
    logging(config['exec_log'], message)

if __name__ == '__main__':
    main()
