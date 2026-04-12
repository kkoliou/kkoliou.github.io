Each post is a folder under `posts/` with a static **`index.html`** (and optional `assets/`).

In the `<head>`, set:

- `<title>Your Post Title — Konstantinos Kolioulis</title>` (the generator strips the site suffix for the blog list).
- `<meta name="date" content="2026-04-10" />` for ordering on the blog index.
- `<meta name="tags" content="SwiftUI, Accessibility" />` (comma-separated).
- `<meta name="description" content="One-line summary for the blog list." />` (or `<meta name="summary" ...>`).

Copy layout and styles from `posts/dynamic-type-scaling/index.html` (header, `article.post`, Prism for Swift).

When ready, run:

```bash
python3 scripts/generate_posts_index.py
```

to regenerate `posts/index.json`.

**Optional:** a folder may use only `index.md` instead; the generator still supports it, but `index.html` takes precedence if both files exist.
