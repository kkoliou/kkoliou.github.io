#!/usr/bin/env python3
"""
Scan the `posts/` folder for post directories containing `index.html` or `index.md`.
If both exist, `index.html` is used (static posts are the source of truth).

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


def strip_site_title_suffix(title):
    if not title:
        return title
    return re.sub(r'\s*[—–-]\s*Konstantinos Kolioulis\s*$', '', title, flags=re.I).strip()


def parse_html_post_meta(html_text):
    """Read optional <meta> fields used for the blog index."""
    meta = {'title': None, 'date': None, 'tags': [], 'summary': ''}
    t = re.search(r'<title>(.*?)</title>', html_text, re.I | re.S)
    if t:
        meta['title'] = strip_site_title_suffix(t.group(1).strip())
    for name, key in (('date', 'date'), ('tags', '_tags_raw'), ('summary', 'summary')):
        m = re.search(
            rf'<meta\s+[^>]*name=["\']{name}["\'][^>]*content=["\']([^"\']*)["\']',
            html_text,
            re.I,
        )
        if not m:
            m = re.search(
                rf'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']{name}["\']',
                html_text,
                re.I,
            )
        if m and key != '_tags_raw':
            meta[key] = m.group(1).strip()
        elif m and key == '_tags_raw':
            raw = m.group(1).strip()
            meta['tags'] = [x.strip().strip('\'"') for x in re.split(r',\s*', raw) if x.strip()]
    if not meta.get('summary'):
        m = re.search(
            r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
            html_text,
            re.I,
        )
        if not m:
            m = re.search(
                r'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',
                html_text,
                re.I,
            )
        if m:
            meta['summary'] = m.group(1).strip()
    return meta


def scan_posts():
    posts = []
    if not os.path.isdir(POSTS_DIR):
        return posts
    for name in sorted(os.listdir(POSTS_DIR), reverse=True):
        post_path = os.path.join(POSTS_DIR, name)
        if not os.path.isdir(post_path):
            continue
        md_file = os.path.join(post_path, 'index.md')
        html_file = os.path.join(post_path, 'index.html')
        title = None
        date = None
        excerpt = ''
        summary = ''
        tags = []
        url = f'posts/{name}/'
        has_md = os.path.isfile(md_file)
        has_html = os.path.isfile(html_file)
        if has_html:
            with open(html_file, 'r', encoding='utf-8') as f:
                text = f.read()
            hm = parse_html_post_meta(text)
            title = hm.get('title')
            date = hm.get('date')
            tags = hm.get('tags') or []
            summary = hm.get('summary') or ''
        elif has_md:
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
        else:
            continue
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
