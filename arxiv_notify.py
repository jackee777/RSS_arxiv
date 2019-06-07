import feedparser
import slackweb
import nltk
from gensim.summarization import keywords
import yaml

import re
import time
import os

# TODO: connection error; detect Robot へのエラー検出
# slack の attachment が一回につき100件まで; 超えたら死にます
# summary は textrank or lead-3
# config は yaml format; home 以下においてあること前提
# (c) Satoru Katsumata

class Entry:
    def __init__(self, entry, abst_type):
        # authors, url, title, abst, area
        # use lead-3 as a summary 
        author_list = [re.sub('<.+?>', '', a) for a in entry['author'].split(', ')]
        self.author = 'AUTHOR:\t' + '; '.join(author_list)
        self.url = entry['link']
        self.title = re.sub(" \(arXiv:.+\)$", "", entry['title'])

        entire_summary = re.sub('<.+?>', '', entry['summary'])
        if abst_type == 'lead-3':
            entire_summary_list = nltk.sent_tokenize(entire_summary)
            self.summary = '\n'.join(entire_summary_list[:3])
        elif abst_type == 'textrank':
            self.summary = 'Keyword: ' + keywords(entire_summary, lemmatize=True).replace('\n', '; ')

        supplement_info = re.search('\(arXiv:.+\)$', entry['title']).group()
        self.area = re.search('\[.+\]', supplement_info).group()
        self.title = self.title + '\t' + self.area
        if re.search('UPDATED', supplement_info):
            self.title = self.title + '\t[UPDATED]' 


    def make_attachment(self):
        attachment = dict()
        attachment['fallback'] = 'arXiv RSS feed'
        attachment['title'] = self.title
        attachment['title_link'] = self.url
        attachment['text'] = self.author + '\n' + self.summary
        attachment['color'] = '#2eb886'

        return attachment


def main():
    config_path = os.path.join(os.environ['HOME'], '.arxiv_ntfy.yml')
    with open(config_path) as config_file:
        config = yaml.load(config_file, Loader=yaml.BaseLoader)

    slack_sender = slackweb.Slack(url=config['url'])
    rss_result = feedparser.parse("http://export.arxiv.org/rss/cs.CL")
    attachment_list = list()

    date_info = dict()
    feed_time = rss_result['feed']['updated_parsed']
    feed_time = time.strftime('%Y-%m-%d %H:%M:%S', feed_time)
    date_info['title'] = 'arXiv RSS update'
    date_info['text'] = '*FEED* *TIME*: '+ feed_time + '\n*POST* *NUM*: ' + str(len(rss_result['entries']))
    attachment_list.append(date_info)

    for entry in rss_result['entries']:
        parsed_entry = Entry(entry, config['abst_type'])
        attachment_list.append(parsed_entry.make_attachment())

    slack_sender.notify(attachments=attachment_list)
    # print(attachment_list)

if __name__ == '__main__':
    main()
