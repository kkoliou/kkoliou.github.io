#!/usr/bin/env python3
"""
Scan the `posts/` folder for post directories containing `index.md` or `index.html`.
Extract basic metadata (title, date, excerpt) and write `posts/index.json`.

Run: python3 scripts/generate_posts_index.py
"""
import os
import json
import re

ROOT = os.path.dirname(os.path.dirname(__file__))
POSTS_DIR = os.path.join(ROOT, 'posts')
OUT_FILE = os.path.join(POSTS_DIR, 'index.json')

FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.S)
TITLE_RE = re.compile(r'^title:\s*["\']?(.*?)["\']?\s*$', re.I | re.M)
DATE_RE = re.compile(r'^date:\s*["\']?(.*?)["\']?\s*$', re.I | re.M)


def extract_frontmatter(md_text):
    m = FRONTMATTER_RE.match(md_text)
    if not m:
        return {}
    body = m.group(1)
    title = None
    date = None
    tm = TITLE_RE.search(body)
    if tm:
        title = tm.group(1).strip()
    dm = DATE_RE.search(body)
    if dm:
        date = dm.group(1).strip()
    return {'title': title, 'date': date}


def extract_excerpt_from_markdown(md_text):
    # remove frontmatter if present
    md = FRONTMATTER_RE.sub('', md_text, count=1)
    # find first non-empty paragraph
    parts = re.split(r'\n\s*\n', md)
    for p in parts:
        s = p.strip()
        if s:
            # strip code fences
            if s.startswith('```'):
                continue
            # return first line truncated
            line = s.splitlines()[0]
            return line[:200]
    return ''


def scan_posts():
    posts = []
    if not os.path.isdir(POSTS_DIR):
        return posts
    for name in sorted(os.listdir(POSTS_DIR), reverse=True):
        post_path = os.path.join(POSTS_DIR, name)
        if not os.path.isdir(post_path):
            continue
        # look for index.md or index.html
        md_file = os.path.join(post_path, 'index.md')
        html_file = os.path.join(post_path, 'index.html')
        title = None
        date = None
        excerpt = ''
        url = os.path.join('posts', name, '')
        if os.path.isfile(md_file):
            with open(md_file, 'r', encoding='utf-8') as f:
                text = f.read()
            fm = extract_frontmatter(text)
            title = fm.get('title')
            date = fm.get('date')
            excerpt = extract_excerpt_from_markdown(text)
        elif os.path.isfile(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                text = f.read()
            # try to extract <title> tag
            t = re.search(r'<title>(.*?)</title>', text, re.I | re.S)
            if t:
                title = t.group(1).strip()
            # extract first paragraph
            p = re.search(r'<p>(.*?)</p>', text, re.I | re.S)
            if p:
                excerpt = re.sub(r'<.*?>', '', p.group(1)).strip()[:200]
        if not title:
            title = name
        posts.append({'slug': name, 'title': title, 'date': date, 'excerpt': excerpt, 'url': url})
    return posts


def main():
    posts = scan_posts()
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f'Wrote {OUT_FILE} with {len(posts)} posts')


if __name__ == '__main__':
    main()
