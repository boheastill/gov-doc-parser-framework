#!/usr/bin/env python3
"""Generate a client-style preview HTML from a parsed JSON file.

Usage:
    python generate_preview.py samples/irishstatutebook/finance_act_2020.json -o preview.html
"""
from __future__ import annotations

import argparse
import json
import html
import hashlib


def _id():
    """Generate a fake mongo-style id."""
    import random
    return ''.join(random.choices('0123456789abcdef', k=24))


def render_article(art: dict, source_url: str) -> str:
    title = html.escape(art.get("title", ""))
    code = html.escape(art.get("code", ""))
    content = art.get("content", "")
    # Convert plain text content to HTML paragraphs
    paragraphs = content.split("\n\n")
    content_html = "".join(f"<p>{html.escape(p)}</p>" for p in paragraphs if p.strip())

    return f'''
    <div class="article" data-id="{_id()}">
      <div class="article-header" onclick="toggleContent(this)">
        <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
        <div class="article-title-block">
          <div class="article-title">{title} <a href="{html.escape(source_url)}" target="_blank" class="source-link" title="View source">&#x2197;</a></div>
          <div class="article-meta"><span class="own-code">{code}</span></div>
        </div>
      </div>
      <div class="article-content hidden">
        <div class="prose"><div><div>{content_html}</div></div></div>
      </div>
    </div>
'''


def render_section(sec: dict, source_url: str, depth: int = 0) -> str:
    title = html.escape(sec.get("title", ""))
    children = sec.get("children", [])
    count = sum(1 for c in children if c.get("type") == "article")
    count += sum(1 for c in children if c.get("type") == "section")

    children_html = ""
    for child in children:
        if child.get("type") == "section":
            children_html += render_section(child, source_url, depth + 1)
        else:
            children_html += render_article(child, source_url)

    return f'''
    <div class="section" data-id="{_id()}" data-depth="{depth}">
      <div class="section-header" onclick="toggleSection(this)"
           style="border-left:3px solid #3b82f6;font-size:0.9375rem;font-weight:600">
        <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
        <span class="section-title">{title}</span>
        <span class="count-badge">{count}</span>
      </div>
      <div class="section-children hidden">
        {children_html}
      </div>
    </div>
'''


def render_document(doc: dict) -> str:
    title = html.escape(doc.get("title", ""))
    doc_type = html.escape(doc.get("type", ""))
    status = html.escape(doc.get("status", ""))
    source_url = doc.get("source_url", "")
    stats = doc.get("stats", {})
    sections_count = stats.get("sections", 0)
    articles_count = stats.get("articles", 0)

    # Find max depth
    def max_depth(nodes, d=0):
        m = d
        for n in nodes:
            if n.get("type") == "section":
                m = max(m, max_depth(n.get("children", []), d + 1))
        return m
    depth = max_depth(doc.get("sections", []))

    # Render content
    content_html = ""
    for node in doc.get("sections", []):
        if node.get("type") == "section":
            content_html += render_section(node, source_url)
        else:
            content_html += render_article(node, source_url)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Document Preview</title>
<style>
  :root {{
    --bg: #ffffff;
    --fg: #0f172a;
    --muted: #64748b;
    --border: #e2e8f0;
    --primary: #3b82f6;
    --primary-light: #eff6ff;
    --article-border: #93c5fd;
    --article-bg: #f0f9ff;
    --radius: 0.5rem;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: var(--font); color: var(--fg); background: var(--bg); line-height: 1.6; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}
  .doc-header {{ margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 2px solid var(--border); }}
  .doc-header h1 {{ font-size: 1.75rem; font-weight: 700; margin-bottom: 0.75rem; }}
  .doc-meta {{ display: flex; flex-wrap: wrap; gap: 0.5rem 1.5rem; font-size: 0.8125rem; color: var(--muted); }}
  .doc-meta strong {{ color: var(--fg); }}
  .doc-meta a {{ color: var(--primary); }}
  .doc-stats {{ margin-top: 0.75rem; display: flex; gap: 0.75rem; }}
  .stat-badge {{ display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.25rem 0.625rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }}
  .stat-sections {{ background: #dbeafe; color: #1d4ed8; }}
  .stat-articles {{ background: #dcfce7; color: #16a34a; }}
  .stat-depth {{ background: #fef3c7; color: #b45309; }}
  .controls {{ margin-bottom: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }}
  .controls button {{ padding: 0.375rem 0.75rem; border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg); color: var(--muted); font-size: 0.8125rem; cursor: pointer; transition: all 0.15s; }}
  .controls button:hover {{ background: var(--primary-light); color: var(--primary); border-color: var(--primary); }}
  .search-box {{ margin-bottom: 1rem; }}
  .search-box input {{ width: 100%; padding: 0.5rem 0.75rem; border: 1px solid var(--border); border-radius: var(--radius); font-size: 0.875rem; outline: none; transition: border-color 0.15s; }}
  .search-box input:focus {{ border-color: var(--primary); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }}
  .section {{ margin-bottom: 0.25rem; border-radius: var(--radius); overflow: hidden; }}
  .section-header {{ display: flex; align-items: center; gap: 0.5rem; padding: 0.625rem 0.75rem; cursor: pointer; user-select: none; border-radius: var(--radius); transition: background 0.15s; }}
  .section-header:hover {{ background: #f1f5f9; }}
  .section-title {{ flex: 1; }}
  .section-children {{ padding-left: 1rem; }}
  .count-badge {{ font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 9999px; background: #e2e8f0; color: var(--muted); white-space: nowrap; }}
  .article {{ margin-bottom: 0.125rem; border-radius: var(--radius); }}
  .article-header {{ display: flex; align-items: flex-start; gap: 0.5rem; padding: 0.5rem 0.75rem; cursor: pointer; user-select: none; border-left: 3px solid var(--article-border); border-radius: var(--radius); transition: background 0.15s; }}
  .article-header:hover {{ background: var(--article-bg); }}
  .article-title-block {{ flex: 1; min-width: 0; }}
  .article-title {{ font-size: 0.8125rem; font-weight: 500; }}
  .article-meta {{ font-size: 0.6875rem; color: var(--muted); margin-top: 0.125rem; }}
  .article-meta .citation {{ background: #f0fdf4; color: #15803d; padding: 0.0625rem 0.375rem; border-radius: 0.25rem; font-weight: 500; }}
  .article-meta .own-code {{ color: #94a3b8; }}
  .source-link {{ color: var(--primary); text-decoration: none; font-size: 0.75rem; opacity: 0.6; }}
  .source-link:hover {{ opacity: 1; }}
  .article-content {{ padding: 0.75rem 0.75rem 0.75rem 1.5rem; border-left: 3px solid var(--article-border); }}
  .prose {{ font-size: 0.8125rem; line-height: 1.7; color: #334155; }}
  .prose p {{ margin: 0.5em 0; }}
  .prose p:first-child {{ margin-top: 0; }}
  .prose p:last-child {{ margin-bottom: 0; }}
  .chevron {{ width: 1rem; height: 1rem; min-width: 1rem; color: var(--muted); transition: transform 0.2s; margin-top: 0.125rem; }}
  .open > .chevron {{ transform: rotate(90deg); }}
  .hidden {{ display: none; }}
</style>
</head>
<body>
<div class="container">
  <div class="doc-header">
    <h1>{title}</h1>
    <div class="doc-meta">
      <div><strong>Type:</strong> {doc_type}</div>
      <div><strong>Status:</strong> {status}</div>
      <div><strong>Source:</strong> <a href="{html.escape(source_url)}" target="_blank">{html.escape(source_url)}</a></div>
    </div>
    <div class="doc-stats">
      <span class="stat-badge stat-sections">Sections: {sections_count}</span>
      <span class="stat-badge stat-articles">Articles: {articles_count}</span>
      <span class="stat-badge stat-depth">Max depth: {depth}</span>
    </div>
  </div>

  <div class="search-box">
    <input type="text" id="searchInput" placeholder="Search articles by title, citation, or content..." oninput="searchArticles(this.value)">
  </div>

  <div class="controls">
    <button onclick="expandAll()">Expand All</button>
    <button onclick="collapseAll()">Collapse All</button>
    <button onclick="expandSections()">Sections Only</button>
  </div>

  <div id="content">
    {content_html}
  </div>
</div>

<script>
function toggleSection(header) {{ header.classList.toggle('open'); header.nextElementSibling.classList.toggle('hidden'); }}
function toggleContent(header) {{ header.classList.toggle('open'); header.nextElementSibling.classList.toggle('hidden'); }}
function expandAll() {{
  document.querySelectorAll('.section-header, .article-header').forEach(h => {{
    h.classList.add('open'); h.nextElementSibling.classList.remove('hidden');
  }});
}}
function collapseAll() {{
  document.querySelectorAll('.section-header, .article-header').forEach(h => {{
    h.classList.remove('open'); h.nextElementSibling.classList.add('hidden');
  }});
}}
function expandSections() {{
  document.querySelectorAll('.section-header').forEach(h => {{
    h.classList.add('open'); h.nextElementSibling.classList.remove('hidden');
  }});
  document.querySelectorAll('.article-header').forEach(h => {{
    h.classList.remove('open'); h.nextElementSibling.classList.add('hidden');
  }});
}}
function searchArticles(query) {{
  const articles = document.querySelectorAll('.article');
  const sections = document.querySelectorAll('.section');
  if (!query.trim()) {{
    articles.forEach(a => a.style.display = '');
    sections.forEach(s => s.style.display = '');
    return;
  }}
  const q = query.toLowerCase();
  sections.forEach(s => s.style.display = '');
  articles.forEach(a => {{
    const t = a.querySelector('.article-title')?.textContent?.toLowerCase() || '';
    const c = a.querySelector('.citation')?.textContent?.toLowerCase() || '';
    const p = a.querySelector('.prose')?.textContent?.toLowerCase() || '';
    const match = t.includes(q) || c.includes(q) || p.includes(q);
    a.style.display = match ? '' : 'none';
    if (match) {{
      let el = a.parentElement;
      while (el) {{
        if (el.classList.contains('section-children')) {{
          el.classList.remove('hidden');
          el.previousElementSibling?.classList.add('open');
        }}
        el = el.parentElement;
      }}
    }}
  }});
}}
</script>
</body>
</html>'''


def main():
    ap = argparse.ArgumentParser(description="Generate a client-style preview HTML from parsed JSON.")
    ap.add_argument("json_file", help="path to a parsed JSON file")
    ap.add_argument("-o", "--out", default="", help="output HTML file (default: stdout)")
    args = ap.parse_args()

    with open(args.json_file, encoding="utf-8") as f:
        doc = json.load(f)

    result = render_document(doc)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"wrote {args.out}")
    else:
        print(result)


if __name__ == "__main__":
    main()
