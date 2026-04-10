#!/usr/bin/env python3
"""
Scan the `posts/` folder for post directories containing `index.md` or `index.html`.
Extract basic metadata (title, date, excerpt) and write `posts/index.json`.

Run: python3 scripts/generate_posts_index.py
"""
import os
import json
import re
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
POSTS_DIR = os.path.join(ROOT, 'posts')
OUT_FILE = os.path.join(POSTS_DIR, 'index.json')

FRONTMATTER_YAML_RE = re.compile(r'^---\s*\n([\s\S]*?)\n---\s*\n', re.M)
FRONTMATTER_COMMENT_YAML_RE = re.compile(r'^<!--\s*---\s*\n([\s\S]*?)\n---\s*-->\s*\n', re.M)


def extract_frontmatter(md_text):
    """Return (meta_dict, stripped_markdown_text).

    Accepts YAML frontmatter at top or YAML wrapped inside an HTML comment.
    """
    m = FRONTMATTER_YAML_RE.match(md_text)
    if not m:
        m = FRONTMATTER_COMMENT_YAML_RE.match(md_text)
    if not m:
        return {}, md_text
    fm_text = m.group(1)
    meta = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or ':' not in line:
            continue
        k, v = line.split(':', 1)
        meta[k.strip()] = v.strip().strip('\'"')
    stripped = md_text[len(m.group(0)):]
    return meta, stripped


# summary is taken from frontmatter `summary` field; no excerpt logic needed



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
        summary = ''
        tags = []
        url = os.path.join('posts', name, '')
        if os.path.isfile(md_file):
            with open(md_file, 'r', encoding='utf-8') as f:
                text = f.read()
            meta, _ = extract_frontmatter(text)
            title = meta.get('title')
            date = meta.get('date')
            # tags may be a comma-separated string or a YAML-like list
            raw_tags = meta.get('tags')
            if raw_tags:
                # handle inline list like [a, b]
                rt = raw_tags.strip()
                if rt.startswith('[') and rt.endswith(']'):
                    rt = rt[1:-1]
                # split on commas
                tags = [t.strip().strip('\"\'') for t in re.split(r',\s*', rt) if t.strip()]
            else:
                # try to detect YAML block list inside frontmatter (lines starting with - )
                m_block = re.search(r'(^|\n)tags:\s*\n([\s\S]*?)(\n\S|$)', text)
                if m_block:
                    block = m_block.group(2)
                    items = re.findall(r'-\s*(.+)', block)
                    tags = [t.strip().strip('\"\'') for t in items if t.strip()]
            # prefer explicit `summary` in frontmatter
            summary = meta.get('summary', '').strip()
        elif os.path.isfile(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                text = f.read()
            # try to extract <title> tag
            t = re.search(r'<title>(.*?)</title>', text, re.I | re.S)
            if t:
                title = t.group(1).strip()
            # prefer explicit `summary` in frontmatter for HTML posts too
            meta_html = {}
            tmeta = re.search(r'<meta name="summary" content="(.*?)"', text, re.I | re.S)
            if tmeta:
                summary = tmeta.group(1).strip()
        if not title:
            title = name
        posts.append({'slug': name, 'title': title, 'date': date, 'tags': tags, 'summary': summary, 'url': url})

    # sort posts by date (newest first). If date missing or unparsable, treat as oldest.
    def parse_date(d):
        if not d:
            return datetime.min
        for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'):
            try:
                return datetime.strptime(d, fmt)
            except Exception:
                continue
        return datetime.min

    posts.sort(key=lambda p: parse_date(p.get('date')), reverse=True)
    return posts


def main():
    posts = scan_posts()
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f'Wrote {OUT_FILE} with {len(posts)} posts')


if __name__ == '__main__':
    main()
