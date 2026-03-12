"""
scraper.py — Downloads Kore.ai docs + GitHub READMEs
Run once to populate data/documents/, then use the ingestion pipeline.

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

# ---- URLs to scrape ----
# Add more to reach ~500 docs. These are the main sections.
KORE_DOC_URLS = [
    # Getting Started
    "https://docs.kore.ai/xo/getting-started/kore-ai-overview/",
    "https://docs.kore.ai/xo/getting-started/about-xo-platform/",
    "https://docs.kore.ai/xo/getting-started/creating-a-virtual-assistant/",
    # Virtual Assistants
    "https://docs.kore.ai/xo/virtual-assistants/overview/",
    "https://docs.kore.ai/xo/virtual-assistants/va-versions/",
    # Dialog Tasks
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/dialog-tasks-overview/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-dialog-node/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-entity-node/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-message-node/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-confirmation-node/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-service-node/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-script-node/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-logic-node/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-agent-transfer-node/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-webhook-node/",
    "https://docs.kore.ai/xo/automation/use-cases/dialogs/node-types/working-with-the-form-node/",
    # Alert Tasks
    "https://docs.kore.ai/xo/automation/use-cases/alert-tasks/",
    # NLP / Training
    "https://docs.kore.ai/xo/automation/natural-language/training/machine-learning-engine/",
    "https://docs.kore.ai/xo/automation/natural-language/training/fundamental-meaning/",
    "https://docs.kore.ai/xo/automation/natural-language/training/traits/",
    "https://docs.kore.ai/xo/automation/natural-language/training/ranking-and-resolver/",
    "https://docs.kore.ai/xo/automation/natural-language/nlu-configurations/engine-tuning/",
    # Knowledge Graph
    "https://docs.kore.ai/xo/automation/knowledge-ai/knowledge-graph-overview/",
    "https://docs.kore.ai/xo/automation/knowledge-ai/create-a-knowledge-graph/",
    "https://docs.kore.ai/xo/automation/knowledge-ai/build-a-knowledge-graph/",
    # Channels
    "https://docs.kore.ai/xo/channels/adding-channels-to-your-bot/",
    "https://docs.kore.ai/xo/channels/add-slack-channel/",
    "https://docs.kore.ai/xo/channels/add-microsoft-teams-channel/",
    "https://docs.kore.ai/xo/channels/add-whatsapp-business-messaging-channel/",
    "https://docs.kore.ai/xo/channels/add-web-mobile-client/",
    "https://docs.kore.ai/xo/channels/add-telegram-channel/",
    # APIs
    "https://docs.kore.ai/xo/apis/api-list/",
    "https://docs.kore.ai/xo/apis/automation/api-introduction/",
    "https://docs.kore.ai/xo/apis/automation/get-api-scope/",
    # Testing & Analytics
    "https://docs.kore.ai/xo/automation/testing/test-your-bot-with-nlp/",
    "https://docs.kore.ai/xo/analytics/overview/",
    "https://docs.kore.ai/xo/analytics/automations/conversations-history/",
    # Deployment
    "https://docs.kore.ai/xo/deploy/publishing-bot/",
    "https://docs.kore.ai/xo/deploy/bot-management/",
    # Search AI
    "https://docs.kore.ai/searchassist/getting-started/searchai-overview/",
    "https://docs.kore.ai/searchassist/getting-started/setup-guide/",
    "https://docs.kore.ai/searchassist/concepts/content-extraction/",
    "https://docs.kore.ai/searchassist/concepts/chunk-browser/",
    # Agent AI
    "https://docs.kore.ai/agentassist/getting-started/introduction/",
    "https://docs.kore.ai/agentassist/getting-started/setup-guide/",
    # GALE
    "https://docs.kore.ai/gale/getting-started/introduction/",
    "https://docs.kore.ai/gale/models/overview/",
    "https://docs.kore.ai/gale/models/fine-tune-models/",
    "https://docs.kore.ai/gale/playground/playground/",
    # SDKs
    "https://docs.kore.ai/xo/sdks/bot-sdk/",
    "https://docs.kore.ai/xo/sdks/web-mobile-sdk/",
    # Admin
    "https://docs.kore.ai/xo/administration/security-and-control/using-single-sign-on/",
    "https://docs.kore.ai/xo/administration/billing/",
]

GITHUB_REPOS = [
    "Koredotcom/BotKit",
    "Koredotcom/web-kore-sdk",
    "Koredotcom/iOS-kore-sdk",
    "Koredotcom/android-kore-sdk",
]


# ---- Helpers ----


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

    # strip noise
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # find content area
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

    print("📖 Scraping Kore.ai docs…")
    kore_ok = sum(
        scrape_url(u, KORE_DIR) or time.sleep(0.5) or 0 for u in KORE_DOC_URLS
    )
    # time.sleep(0.5) between requests — be polite to their server

    print(f"\n🐙 Scraping GitHub READMEs…")
    gh_ok = sum(scrape_github_readme(r, GITHUB_DIR) or 0 for r in GITHUB_REPOS)

    total = len(os.listdir(KORE_DIR)) + len(os.listdir(GITHUB_DIR))
    print(f"\n{'='*50}")
    print(f"📊 Done! {total} files total")
    print(f"   Kore docs: {kore_ok}/{len(KORE_DOC_URLS)}")
    print(f"   GitHub:    {gh_ok}/{len(GITHUB_REPOS)}")
    print(f"\n💡 Next: uv run python -m app.ingestion.embedder")


if __name__ == "__main__":
    scrape_all()
