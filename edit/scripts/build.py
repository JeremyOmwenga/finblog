"""
=============================================================================
build.py — OJ Market Monitor / Blog Auto-Builder
=============================================================================

WHAT THIS SCRIPT DOES
---------------------
1. Scans the /articles directory for all .md (Markdown) files.
2. For each .md file that does NOT already have a matching .html file,
   it generates a full article HTML page using your site's template.
3. It then inserts a new <article class="card"> element at the TOP of
   the card list in index.html, so new articles appear first.
4. It tracks which articles have already been built using a simple
   JSON manifest file (articles/manifest.json), so it never
   processes the same article twice.

HOW TO RUN LOCALLY (for testing)
---------------------------------
    pip install markdown beautifulsoup4
    python scripts/build.py

This will process any new .md files in /articles and update index.html.

DEPENDENCIES
------------
    markdown       — converts Markdown body text to HTML
    beautifulsoup4 — reads and edits index.html safely

Both are installed automatically by the GitHub Action workflow.

=============================================================================
"""

import os
import re
import json
import math
import markdown
from datetime import datetime
from bs4 import BeautifulSoup


# =============================================================================
# CONFIGURATION — edit these to match your site
# =============================================================================

SITE_TITLE      = "Financial & Tech Updates and Anecdotes"   # shown in header
SITE_LABEL      = "est. 2026"                                 # small label above site title
SITE_FOOTER     = "OJ Market Monitor"                        # footer brand name
AUTHOR          = "Jeremy Angwenyi"                          # your name on bylines
CONTACT_EMAIL   = "jeremyangwenyi.ja@gmail.com"              # footer email link
COPYRIGHT       = "© 2026. All rights reserved to Jeremy."   # footer copyright line

# Paths — relative to the repo root (where you run the script from)
ARTICLES_DIR    = "articles"          # folder where your .md files live
OUTPUT_DIR      = "."                 # where article HTML files are written (repo root)
INDEX_FILE      = "index.html"        # your homepage
MANIFEST_FILE   = os.path.join(ARTICLES_DIR, "manifest.json")  # tracks built articles

# The HTML comment in index.html that marks where new cards are inserted.
# Make sure this exact comment exists inside your <section class="articles-section">.
CARD_INSERT_MARKER = "<!-- CARDS -->"


# =============================================================================
# STEP 1 — MANIFEST
# Tracks which .md files have already been turned into HTML pages,
# so re-running the script never duplicates anything.
# =============================================================================

def load_manifest():
    """
    Load the manifest JSON file.
    Returns a dict like: { "my-article.md": "my-article.html", ... }
    If the file doesn't exist yet, returns an empty dict.
    """
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_manifest(manifest):
    """
    Save the updated manifest back to disk.
    Called after every new article is successfully built.
    """
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


# =============================================================================
# STEP 2 — FRONT MATTER PARSER
# Reads the --- block at the top of each .md file to extract metadata.
# =============================================================================

def parse_front_matter(raw_text):
    """
    Parses the YAML-style front matter block from a Markdown file.

    Expected format at the top of every .md file:
    ---
    title: "Your Article Title"
    tag: "Opinion"
    date: "Mar 21, 2026"
    excerpt: "A short description shown on the index card."
    ---

    Returns a tuple: (metadata_dict, body_text)
    - metadata_dict: all key/value pairs from the front matter block
    - body_text: everything AFTER the closing ---
    """
    # Match the opening and closing --- delimiters
    pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)', re.DOTALL)
    match = pattern.match(raw_text)

    if not match:
        raise ValueError(
            "No front matter found. Every .md file must start with a --- block.\n"
            "See sample-article.md for an example."
        )

    front_matter_raw = match.group(1)
    body = match.group(2).strip()

    # Parse each line as key: "value"
    metadata = {}
    for line in front_matter_raw.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            # Strip whitespace and surrounding quotes
            metadata[key.strip()] = value.strip().strip('"').strip("'")

    # Validate required fields
    required = ["title", "tag", "date", "excerpt"]
    for field in required:
        if field not in metadata:
            raise ValueError(f"Missing required front matter field: '{field}'")

    return metadata, body


# =============================================================================
# STEP 3 — READING TIME CALCULATOR
# Estimates how long the article takes to read.
# =============================================================================

def reading_time(body_text):
    """
    Estimates reading time based on average adult reading speed (200 wpm).
    Returns a string like "4 min read".
    """
    word_count = len(body_text.split())
    minutes = math.ceil(word_count / 200)
    return f"{minutes} min read", word_count


# =============================================================================
# STEP 4 — SLUG GENERATOR
# Turns the article title or filename into a clean URL-safe filename.
# =============================================================================

def slugify(text):
    """
    Converts a string into a lowercase, hyphen-separated filename.
    Example: "Is the NSE Overheated?" → "is-the-nse-overheated"
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)   # remove punctuation
    text = re.sub(r"[\s_]+", "-", text)    # spaces to hyphens
    text = re.sub(r"-+", "-", text)        # collapse multiple hyphens
    return text.strip("-")


# =============================================================================
# STEP 5 — HTML GENERATOR
# Takes metadata + converted body HTML and builds the full article page.
# =============================================================================

def generate_article_html(metadata, body_html, read_time, word_count, output_filename):
    """
    Builds a complete article HTML page string from the template.

    Uses the metadata dict from the front matter and the body_html
    which has already been converted from Markdown.

    Returns the full HTML as a string.
    """
    title       = metadata["title"]
    tag         = metadata["tag"]
    date        = metadata["date"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — {SITE_FOOTER}</title>
  <link rel="stylesheet" href="style.css" />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet" />
</head>
<body>

  <!-- HEADER -->
  <header class="site-header">
    <div class="header-inner">
      <div class="site-brand">
        <span class="site-label">{SITE_LABEL}</span>
        <a href="index.html" style="text-decoration:none;">
          <h1 class="site-title">{SITE_TITLE}</h1>
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

    <!-- ARTICLE HERO -->
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
        <span class="author">{AUTHOR}</span>
        <span class="sep"></span>
        <span>{read_time}</span>
        <span class="sep"></span>
        <span>{word_count:,} words</span>
      </div>
    </section>

    <!-- ARTICLE BODY -->
    <article class="article-body">
      {body_html}
    </article>

    <!-- ARTICLE FOOTER NAV -->
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
        <span class="footer-title">{SITE_FOOTER}</span>
        <span class="footer-copy">{COPYRIGHT}</span>
      </div>
      <div class="footer-socials">
        <span class="socials-label">Find me on</span>
        <div class="social-links">
          <a href="mailto:{CONTACT_EMAIL}" class="social-link" aria-label="Email">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 7 10-7"/></svg>
            Email
          </a>
        </div>
      </div>
    </div>
  </footer>

  <script src="main.js"></script>
</body>
</html>"""

    return html


# =============================================================================
# STEP 6 — INDEX CARD GENERATOR
# Builds the <article class="card"> HTML to inject into index.html.
# =============================================================================

def generate_card_html(metadata, output_filename, card_index):
    """
    Builds the card HTML snippet that goes into index.html.

    card_index: integer used for data-index attribute (e.g. 1 → "01")
    output_filename: the article's HTML filename (e.g. "my-article.html")
    """
    title    = metadata["title"]
    tag      = metadata["tag"]
    date     = metadata["date"]
    excerpt  = metadata["excerpt"]
    index_str = str(card_index).zfill(2)  # e.g. 1 → "01", 12 → "12"

    return f"""
      <article class="card" data-index="{index_str}">
        <a href="{output_filename}" class="card-link">
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
      </article>"""


# =============================================================================
# STEP 7 — INDEX UPDATER
# Inserts the new card into index.html at the marker position.
# =============================================================================

def update_index(card_html):
    """
    Reads index.html, finds the CARD_INSERT_MARKER comment, and inserts
    the new card HTML immediately after it.

    The marker comment must exist in index.html inside the articles section:
        <!-- CARDS -->

    Cards are inserted at the TOP (newest first).
    """
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if CARD_INSERT_MARKER not in content:
        raise ValueError(
            f"Could not find '{CARD_INSERT_MARKER}' in {INDEX_FILE}.\n"
            f"Add this comment inside your <section class='articles-section'> "
            f"right after the section-label div."
        )

    # Insert the new card right after the marker
    updated = content.replace(
        CARD_INSERT_MARKER,
        CARD_INSERT_MARKER + "\n" + card_html
    )

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(updated)


# =============================================================================
# STEP 8 — RENUMBER EXISTING CARDS
# After inserting a new card at the top, re-sequences all data-index values
# so they stay in order (01, 02, 03...) top to bottom.
# =============================================================================

def renumber_cards():
    """
    Opens index.html with BeautifulSoup and rewrites all data-index
    attributes on .card elements so they run sequentially from 01.

    This keeps the numbering clean after every new article is added.
    """
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    cards = soup.select("article.card")
    for i, card in enumerate(cards, start=1):
        card["data-index"] = str(i).zfill(2)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))


# =============================================================================
# MAIN — ties everything together
# =============================================================================

def main():
    """
    Entry point. Scans /articles for new .md files and processes each one.
    """
    print("=" * 60)
    print("OJ Market Monitor — Article Builder")
    print("=" * 60)

    # Make sure the articles directory exists
    if not os.path.isdir(ARTICLES_DIR):
        print(f"ERROR: '{ARTICLES_DIR}' directory not found.")
        print("Create it and add your .md files there.")
        return

    # Load the manifest so we know what's already been built
    manifest = load_manifest()

    # Find all .md files in the articles directory
    md_files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".md")]

    if not md_files:
        print("No .md files found in /articles. Nothing to do.")
        return

    # Filter to only unprocessed files
    new_files = [f for f in md_files if f not in manifest]

    if not new_files:
        print("All articles are already built. Nothing new to process.")
        return

    print(f"Found {len(new_files)} new article(s) to process.\n")

    # Count existing cards in index.html to assign correct data-index values
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        existing_html = f.read()
    existing_card_count = existing_html.count('class="card"')

    built_count = 0

    for md_filename in new_files:
        md_path = os.path.join(ARTICLES_DIR, md_filename)
        print(f"Processing: {md_filename}")

        try:
            # Read the raw markdown file
            with open(md_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            # Parse front matter and body
            metadata, body_text = parse_front_matter(raw_text)
            print(f"  Title   : {metadata['title']}")
            print(f"  Tag     : {metadata['tag']}")
            print(f"  Date    : {metadata['date']}")

            # Convert markdown body to HTML
            # 'extra' extension supports tables, fenced code blocks, etc.
            body_html = markdown.markdown(body_text, extensions=["extra"])

            # Calculate reading time
            read_time, word_count = reading_time(body_text)
            print(f"  Reading : {read_time} ({word_count} words)")

            # Generate output filename from the md filename
            # e.g. "my-article.md" → "my-article.html"
            base_name = os.path.splitext(md_filename)[0]
            output_filename = base_name + ".html"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            # Generate and write the article HTML file
            article_html = generate_article_html(
                metadata, body_html, read_time, word_count, output_filename
            )
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(article_html)
            print(f"  Written : {output_path}")

            # Generate the index card and inject into index.html
            # New articles get index 1 (they're inserted at the top)
            card_html = generate_card_html(metadata, output_filename, card_index=1)
            update_index(card_html)
            print(f"  Card    : injected into {INDEX_FILE}")

            # Record in manifest so this file is never processed again
            manifest[md_filename] = output_filename
            save_manifest(manifest)

            built_count += 1
            print(f"  Done ✓\n")

        except Exception as e:
            # If anything goes wrong with one file, report it and continue
            print(f"  ERROR: {e}\n")
            continue

    # Re-sequence all data-index values after all insertions are done
    if built_count > 0:
        renumber_cards()
        print(f"Renumbered all cards in {INDEX_FILE}.")
        print(f"\nDone. Built {built_count} new article(s).")
    else:
        print("No articles were successfully built.")


if __name__ == "__main__":
    main()
