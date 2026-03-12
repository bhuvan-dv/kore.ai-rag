"""
scraper.py — Downloads Kore.ai docs + GitHub READMEs
Discovers URLs from the sitemap.xml instead of a hardcoded list.

Usage:
    cd backend && uv run python scraper.py
"""

import os
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

OUTPUT_DIR = "./data/documents"
KORE_DIR = os.path.join(OUTPUT_DIR, "kore-docs")
GITHUB_DIR = os.path.join(OUTPUT_DIR, "github")

# Sitemap covers all 1000+ pages — we cap at MAX_DOCS to hit ~500 docs target
SITEMAP_URL = "https://docs.kore.ai/xo/sitemap.xml"
MAX_DOCS = 496  # leaves room for 4 GitHub READMEs → ~500 total

# Skip index/home pages — they have no real content
SKIP_SUFFIXES = ["/home/", "/license/", "/xo/", "/release-notes/"]

GITHUB_REPOS = [
    "Koredotcom/BotKit",  # Bot builder SDK
    "Koredotcom/web-kore-sdk",  # Web channel SDK
    "Koredotcom/iOS-kore-sdk",  # iOS SDK
    "Koredotcom/android-kore-sdk",  # Android SDK
    "Koredotcom/react-native-botsdk",  # React Native SDK
    "Koredotcom/SearchAssist-web-sdk",  # SearchAssist SDK
    "Koredotcom/AgentAssistWidget",  # Agent Assist integration
    "Koredotcom/Public-APIs",  # Public API reference
]


# ---- Helpers ----


def fetch_sitemap_urls(sitemap_url: str) -> list[str]:
    """Pull all <loc> URLs from the sitemap."""
    r = requests.get(sitemap_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    urls = [loc.text.strip() for loc in soup.find_all("loc")]
    # filter out noise pages
    urls = [u for u in urls if not any(u.endswith(s) for s in SKIP_SUFFIXES)]
    return urls


def safe_filename(url: str) -> str:
    path = urlparse(url).path.strip("/").replace("/", "_")
    if not path:
        path = "index"
    if len(path) > 100:
        path = hashlib.md5(path.encode()).hexdigest()[:16]
    return path + ".md"


def html_to_markdown(html: str, url: str = "") -> str:
    """Extract main content from an HTML page as rough markdown."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(class_="content")
        or soup.find(id="content")
        or soup.body
    )
    if not main:
        return ""

    lines = [f"# Source: {url}\n"] if url else []

    for el in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "pre", "code"]):
        text = el.get_text(strip=True)
        if not text:
            continue
        tag = el.name
        if tag == "h1":
            lines.append(f"\n# {text}\n")
        elif tag == "h2":
            lines.append(f"\n## {text}\n")
        elif tag == "h3":
            lines.append(f"\n### {text}\n")
        elif tag == "h4":
            lines.append(f"\n#### {text}\n")
        elif tag == "li":
            lines.append(f"- {text}")
        elif tag in ("pre", "code"):
            lines.append(f"\n```\n{text}\n```\n")
        else:
            lines.append(f"\n{text}\n")

    return "\n".join(lines)


def scrape_url(url: str, out_dir: str) -> bool:
    try:
        r = requests.get(
            url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (educational)"}
        )
        r.raise_for_status()

        md = html_to_markdown(r.text, url)
        if len(md.strip()) < 50:
            print(f"  ⚠ too little content: {url}")
            return False

        path = os.path.join(out_dir, safe_filename(url))
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"  ✅ {safe_filename(url)}  ({len(md)} chars)")
        return True
    except Exception as e:
        print(f"  ❌ {url} — {e}")
        return False


def scrape_github_readme(repo: str, out_dir: str) -> bool:
    try:
        url = f"https://api.github.com/repos/{repo}/readme"
        r = requests.get(
            url,
            timeout=15,
            headers={
                "Accept": "application/vnd.github.v3.raw",
                "User-Agent": "kore-search-agent",
            },
        )
        r.raise_for_status()

        content = f"# GitHub: {repo}\n\nSource: https://github.com/{repo}\n\n{r.text}"
        fname = repo.replace("/", "_") + "_README.md"
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  ✅ {fname}  ({len(content)} chars)")
        return True
    except Exception as e:
        print(f"  ❌ {repo} — {e}")
        return False


# ---- Main ----


def scrape_all():
    os.makedirs(KORE_DIR, exist_ok=True)
    os.makedirs(GITHUB_DIR, exist_ok=True)

    print(f"🗺  Fetching sitemap from {SITEMAP_URL}…")
    all_urls = fetch_sitemap_urls(SITEMAP_URL)
    urls_to_scrape = all_urls[:MAX_DOCS]
    print(f"   Found {len(all_urls)} URLs → scraping first {len(urls_to_scrape)}\n")

    print("📖 Scraping Kore.ai docs…")
    kore_ok = 0
    for i, url in enumerate(urls_to_scrape, 1):
        ok = scrape_url(url, KORE_DIR)
        if ok:
            kore_ok += 1
        if i % 10 == 0:
            print(f"  … {i}/{len(urls_to_scrape)} done")
        time.sleep(0.3)  # be polite to the server

    print(f"\n🐙 Scraping GitHub READMEs…")
    gh_ok = sum(scrape_github_readme(r, GITHUB_DIR) or 0 for r in GITHUB_REPOS)

    total = len(os.listdir(KORE_DIR)) + len(os.listdir(GITHUB_DIR))
    print(f"\n{'='*50}")
    print(f"📊 Done! {total} files total")
    print(f"   Kore docs: {kore_ok}/{len(urls_to_scrape)}")
    print(f"   GitHub:    {gh_ok}/{len(GITHUB_REPOS)}")
    print(f"\n💡 Next: uv run python -m app.ingestion.embedder")


if __name__ == "__main__":
    scrape_all()
