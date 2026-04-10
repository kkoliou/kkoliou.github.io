---
title: "Your Post Title"
date: 2026-04-10
tags: [swift]
summary: "A one-line summary or excerpt shown on the blog list."
---

Write your post here. Keep paragraphs short and use fenced code blocks for Swift snippets.

Example Swift snippet:

```swift
// Example helper
extension Array {
  func chunked(into size: Int) -> [[Element]] {
    guard size > 0 else { return [self] }
    return stride(from: 0, to: count, by: size).map { Array(self[$0..<Swift.min($0 + size, count)]) }
  }
}
```

Optional tips:
- Use `title` and `date` in frontmatter for the blog index.
- Keep `index.md` as the post filename inside a post folder, e.g. `posts/2026-04-10-my-post/index.md`.
- Add images or other assets in the same folder and reference them with relative paths.

When ready, run:

```bash
python3 scripts/generate_posts_index.py
```

to update the posts list.
