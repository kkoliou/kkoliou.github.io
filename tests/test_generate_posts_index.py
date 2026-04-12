import os
import tempfile
import json
import shutil
import importlib.util
import sys

# import the generator module
spec = importlib.util.spec_from_file_location('gen', os.path.join(os.path.dirname(__file__), '..', 'scripts', 'generate_posts_index.py'))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


def write_md(dirpath, fm, body='Content'):
    os.makedirs(dirpath, exist_ok=True)
    with open(os.path.join(dirpath, 'index.md'), 'w', encoding='utf-8') as f:
        f.write(fm + '\n' + body)


def test_extract_frontmatter_plain_yaml():
    md = '---\ntitle: Test Post\ndate: 2026-04-10\ntags: [a, b]\nsummary: S1\n---\n# Hello\n'
    meta, rest = gen.extract_frontmatter(md)
    assert meta['title'] == 'Test Post'
    assert meta['date'] == '2026-04-10'
    assert 'a' in meta['tags'] or isinstance(meta.get('tags'), str)
    assert meta['summary'] == 'S1'
    assert rest.lstrip().startswith('# Hello')


def test_extract_frontmatter_commented_yaml():
    md = '<!--\n---\ntitle: Commented\ndate: 2026-04-09\ntags:\n- x\n- y\nsummary: S2\n---\n-->\nContent'
    meta, rest = gen.extract_frontmatter(md)
    assert meta['title'] == 'Commented'
    assert meta['date'] == '2026-04-09'
    assert meta['summary'] == 'S2'
    assert rest.lstrip().startswith('Content')


def test_scan_posts_and_sorting(tmp_path):
    root = tmp_path / 'posts'
    # post A (older)
    a = root / 'a'
    fm_a = '---\ntitle: A\ndate: 2020-01-01\ntags: [swift]\nsummary: A summary\n---\n\nBody A'
    write_md(str(a), fm_a)
    # post B (newer)
    b = root / 'b'
    fm_b = '---\ntitle: B\ndate: 2021-06-05\ntags: [swift,access]\nsummary: B summary\n---\n\nBody B'
    write_md(str(b), fm_b)

    # point the module to this posts dir
    gen.POSTS_DIR = str(root)
    posts = gen.scan_posts()
    assert len(posts) == 2
    # newest first -> B then A
    assert posts[0]['title'] == 'B'
    assert posts[1]['title'] == 'A'
    assert posts[0]['summary'] == 'B summary'
    assert 'access' in posts[0]['tags']


def test_html_meta_summary(tmp_path):
    root = tmp_path / 'posts'
    h = root / 'htmlpost'
    os.makedirs(str(h), exist_ok=True)
    html = '<html><head><title>H</title><meta name="summary" content="Html summary"></head><body></body></html>'
    with open(os.path.join(str(h), 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    gen.POSTS_DIR = str(root)
    posts = gen.scan_posts()
    assert any(p['summary'] == 'Html summary' for p in posts)


def test_html_prefers_over_md(tmp_path):
    root = tmp_path / 'posts'
    d = root / 'both'
    os.makedirs(str(d), exist_ok=True)
    fm = '---\ntitle: From Markdown\ndate: 2026-01-01\n---\n'
    write_md(str(d), fm)
    html = (
        '<html><head><title>From HTML — Konstantinos Kolioulis</title>'
        '<meta name="date" content="2026-06-01" />'
        '<meta name="tags" content="a, b" />'
        '<meta name="description" content="D1" />'
        '</head><body></body></html>'
    )
    with open(os.path.join(str(d), 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    gen.POSTS_DIR = str(root)
    posts = gen.scan_posts()
    assert len(posts) == 1
    assert posts[0]['title'] == 'From HTML'
    assert posts[0]['date'] == '2026-06-01'
    assert posts[0]['tags'] == ['a', 'b']
    assert posts[0]['summary'] == 'D1'