"""
scripts/build.py
Reads every .md file in /articles, generates a styled article HTML page,
and injects a card into index.html. Skips articles already built.
"""

import os
import re
import math
import markdown
from bs4 import BeautifulSoup

# ── Paths ────────────────────────────────────────────────────────
ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(ROOT, "articles")
INDEX_PATH   = os.path.join(ROOT, "index.html")

# ── Parse front matter ───────────────────────────────────────────
def parse_frontmatter(text):
    """
    Reads the --- block at the top of a .md file.
    Returns (meta_dict, body_string).
    """
    meta = {}
    body = text

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                meta[key.strip()] = val.strip().strip('"').strip("'")
        body = text[match.end():]

    return meta, body

# ── Word count & read time ───────────────────────────────────────
def read_time(text):
    words = len(text.split())
    minutes = max(1, math.ceil(words / 200))
    return f"{minutes} min read", f"{words:,} words"

# ── Generate article HTML ────────────────────────────────────────
ARTICLE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — OJ Market Monitor</title>
  <link rel="stylesheet" href="style.css" />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet" />
</head>
<body>

  <!-- HEADER -->
  <header class="site-header">
    <div class="header-inner">
      <div class="site-brand">
        <span class="site-label">est. 2026</span>
        <a href="index.html" style="text-decoration:none;">
          <h1 class="site-title">Financial &amp; Tech Updates and Anecdotes</h1>
        </a>
      </div>
      <nav class="site-nav">
        <br>
        <a href="#">About</a>
      </nav>
    </div>
    <div class="header-rule"></div>
  </header>

  <!-- MAIN -->
  <main class="main-content">

    <section class="article-hero">
      <a href="index.html" class="article-back">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        All essays
      </a>

      <div class="article-meta">
        <span class="card-tag">{tag}</span>
        <span class="card-date">{date}</span>
      </div>

      <h1 class="article-title">{title}</h1>

      <div class="article-byline">
        <span class="author">Jeremy Angwenyi</span>
        <span class="sep"></span>
        <span>{read_time}</span>
        <span class="sep"></span>
        <span>{word_count}</span>
      </div>
    </section>

    <article class="article-body">
      <p class="lead">{excerpt}</p>
      {body_html}
    </article>

    <section class="article-footer">
      <div class="article-footer-label">Continue Reading</div>
      <div class="article-nav">
        <a href="index.html" class="article-nav-link">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back to all essays
        </a>
      </div>
    </section>

  </main>

  <!-- FOOTER -->
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="footer-title">OJ Market Monitor</span>
        <span class="footer-copy">&copy; 2026. All rights reserved to Jeremy.</span>
      </div>
      <div class="footer-socials">
        <span class="socials-label">Find me on</span>
        <div class="social-links">
          <a href="mailto:jeremyangwenyi.ja@gmail.com" class="social-link" aria-label="Email">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 7 10-7"/></svg>
            Email
          </a>
        </div>
      </div>
    </div>
  </footer>

  <script src="main.js"></script>
</body>
</html>
"""

# ── Card HTML snippet ────────────────────────────────────────────
CARD_TEMPLATE = """\
      <article class="card" data-index="{index:02d}">
        <a href="{filename}" class="card-link">
          <div class="card-meta">
            <span class="card-tag">{tag}</span>
            <span class="card-date">{date}</span>
          </div>
          <h2 class="card-title">{title}</h2>
          <p class="card-excerpt">
            {excerpt}
          </p>
          <span class="card-read">Read essay →</span>
        </a>
      </article>
"""

# ── Main ─────────────────────────────────────────────────────────
def main():
    # Load index.html
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index_soup = BeautifulSoup(f.read(), "html.parser")

    cards_section = index_soup.find("section", class_="articles-section")

    # Find highest existing data-index so we can increment
    existing = cards_section.find_all("article", class_="card")
    existing_hrefs = {a.find("a")["href"] for a in existing if a.find("a")}
    max_index = 0
    for card in existing:
        idx = card.get("data-index", "0")
        try:
            max_index = max(max_index, int(idx))
        except ValueError:
            pass

    new_cards_added = 0

    # Process each .md file
    for fname in sorted(os.listdir(ARTICLES_DIR)):
        if not fname.endswith(".md"):
            continue

        html_name = fname.replace(".md", ".html")

        # Skip if already built (card already in index)
        if html_name in existing_hrefs:
            print(f"  skip  {fname}  (already published)")
            continue

        md_path   = os.path.join(ARTICLES_DIR, fname)
        html_path = os.path.join(ROOT, html_name)

        with open(md_path, "r", encoding="utf-8") as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)

        title   = meta.get("title",   fname.replace(".md", "").replace("-", " ").title())
        tag     = meta.get("tag",     "Essay")
        date    = meta.get("date",    "")
        excerpt = meta.get("excerpt", "")

        rt, wc      = read_time(body)
        body_html   = markdown.markdown(body, extensions=["extra"])

        # Write article HTML
        article_html = ARTICLE_TEMPLATE.format(
            title      = title,
            tag        = tag,
            date       = date,
            read_time  = rt,
            word_count = wc,
            excerpt    = excerpt,
            body_html  = body_html,
        )
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(article_html)
        print(f"  built {html_name}")

        # Build card and prepend it (newest first)
        max_index += 1
        card_html = CARD_TEMPLATE.format(
            index    = max_index,
            filename = html_name,
            tag      = tag,
            date     = date,
            title    = title,
            excerpt  = excerpt,
        )
        card_soup = BeautifulSoup(card_html, "html.parser")
        new_card  = card_soup.find("article")

        # Insert after the section-label div, so newest appears at top
        label_div = cards_section.find("div", class_="section-label")
        if label_div:
            label_div.insert_after(new_card)
        else:
            cards_section.append(new_card)

        new_cards_added += 1

    # Save updated index.html
    if new_cards_added:
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(str(index_soup))
        print(f"\n  index.html updated — {new_cards_added} new card(s) added.")
    else:
        print("\n  Nothing new to publish.")

if __name__ == "__main__":
    main()
