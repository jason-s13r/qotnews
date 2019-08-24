import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

import praw
from praw.models import MoreComments

SUBREDDITS = 'Economics+Foodforthought+Futurology+TrueReddit+business+science+technology'

SITE_LINK = lambda x : 'https://old.reddit.com/{}'.format(x)
SITE_AUTHOR_LINK = lambda x : 'https://old.reddit.com/u/{}'.format(x)

reddit = praw.Reddit('bot')

def feed():
    return [x.id for x in reddit.subreddit(SUBREDDITS).hot(limit=30)]

def good_comment(c):
    if isinstance(c, MoreComments):
        return False
    if c.body == '[removed]':
        return False
    if c.author and c.author.name == 'AutoModerator':
        return False
    return True

def comment(i):
    c = {}
    c['author'] = i.author.name if i.author else '[Deleted]'
    c['score'] = i.score
    c['date'] = i.created_utc
    c['text'] = i.body.replace('\n', '<br />')
    c['comments'] = [comment(j) for j in i.replies if good_comment(j)]
    return c

def story(ref):
    r = reddit.submission(ref)
    if not r: return False

    s = {}
    s['author'] = r.author.name if r.author else '[Deleted]'
    s['author_link'] = SITE_AUTHOR_LINK(r.author)
    s['score'] = r.score
    s['date'] = r.created_utc
    s['title'] = r.title
    s['link'] = SITE_LINK(r.permalink)
    s['url'] = r.url
    s['comments'] = [comment(i) for i in r.comments if good_comment(i)]
    s['num_comments'] = r.num_comments

    if r.selftext:
        s['text'] = r.selftext

    return s

if __name__ == '__main__':
    print(feed())
    print(reddit.submission(feed()[0]).permalink)
    print()
    print(story('cuozg4'))
