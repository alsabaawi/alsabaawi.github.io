#!/usr/bin/env python3
"""
update_site.py - Academic Portfolio Automation & Maintenance Tool
Author: Aiman Al-Sabaawi (AFHEA)
Website: https://alsabaawi.github.io

Usage:
  Interactive Menu:
    python3 update_site.py

  Quick Commands:
    python3 update_site.py --metrics      # Update metrics from Google Scholar
    python3 update_site.py --add          # Interactively add a new publication
    python3 update_site.py --sync-bib     # Re-sync publications.bib from index.html
    python3 update_site.py --push         # Git commit and push changes
    python3 update_site.py --notify       # Send status notification to ntfy.sh/HPC
    python3 update_site.py --all          # One-shot update metrics, sync bib, push & notify
"""

import sys
import os
import re
import datetime
import urllib.request
import urllib.parse
import json
import subprocess

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(SITE_DIR, 'index.html')
BIB_FILE = os.path.join(SITE_DIR, 'assets', 'bibtex', 'publications.bib')
SCHOLAR_USER_ID = 'J6hrO1gAAAAJ'
NTFY_TOPIC = 'HPC'
SITE_URL = 'https://alsabaawi.github.io'

# ANSI Color codes for clean terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'


def log_info(msg):
    print(f"{BLUE}[INFO]{RESET} {msg}")


def log_success(msg):
    print(f"{GREEN}[SUCCESS]{RESET} {msg}")


def log_warn(msg):
    print(f"{YELLOW}[WARN]{RESET} {msg}")


def log_error(msg):
    print(f"{RED}[ERROR]{RESET} {msg}")


# ==============================================================================
# 1. Google Scholar Metrics Fetcher
# ==============================================================================
def fetch_scholar_metrics(user_id=SCHOLAR_USER_ID):
    """Fetches total citations, h-index, and i10-index from Google Scholar."""
    url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    }
    log_info(f"Connecting to Google Scholar (ID: {user_id})...")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        table_m = re.search(r'<table id="gsc_rsb_st".*?>(.*?)</table>', html, re.DOTALL)
        if table_m:
            vals = re.findall(r'<td class="gsc_rsb_std">(.*?)</td>', table_m.group(1))
            if len(vals) >= 6:
                cites = int(vals[0])
                h_index = int(vals[2])
                i10_index = int(vals[4])
                log_success(f"Fetched live Scholar metrics: {cites:,} Citations | h-index: {h_index} | i10-index: {i10_index}")
                return {
                    'citations': cites,
                    'h_index': h_index,
                    'i10_index': i10_index,
                    'raw_html': html
                }

        log_warn("Could not parse table from Google Scholar response.")
    except Exception as e:
        log_warn(f"Failed to fetch live stats from Google Scholar: {e}")

    return None


# ==============================================================================
# 2. Update Metrics in index.html
# ==============================================================================
def update_metrics(cites=None, h_index=None, i10_index=None):
    """Updates the metrics banner in index.html (Citations, h-index, Pub count)."""
    if not os.path.exists(INDEX_FILE):
        log_error(f"Cannot find {INDEX_FILE}")
        return False

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # Count actual publications in the file
    pub_cards = re.findall(r'<article class="pub-card"', html)
    pub_count = len(pub_cards)
    log_info(f"Detected {pub_count} publication cards in index.html")

    # If metrics not provided, try fetching live from Google Scholar
    if cites is None or h_index is None or i10_index is None:
        stats = fetch_scholar_metrics()
        if stats:
            cites = stats['citations']
            h_index = stats['h_index']
            i10_index = stats['i10_index']
        else:
            print(f"\n{YELLOW}Could not fetch automatic metrics from Google Scholar.{RESET}")
            try:
                c_input = input("Enter total citations [default 1867]: ").strip()
                cites = int(c_input) if c_input else 1867
                h_input = input("Enter h-index [default 10]: ").strip()
                h_index = int(h_input) if h_input else 10
                i_input = input("Enter i10-index [default 11]: ").strip()
                i10_index = int(i_input) if i_input else 11
            except ValueError:
                log_error("Invalid number entered.")
                return False

    # Format numbers
    cites_str = f"{cites:,}+"
    h_i10_str = f"{h_index} / {i10_index}"
    pub_str = f"{pub_count}+"

    # Replace Scholar Citations
    pattern_cites = r'(<div class="metric-number">)[^<]*(</div>\s*<div class="metric-label">Scholar Citations</div>)'
    html, n_c = re.subn(pattern_cites, rf'\g<1>{cites_str}\g<2>', html)

    # Replace h-index / i10-index
    pattern_h = r'(<div class="metric-number">)[^<]*(</div>\s*<div class="metric-label">h-index / i10-index</div>)'
    html, n_h = re.subn(pattern_h, rf'\g<1>{h_i10_str}\g<2>', html)

    # Replace Publications count
    pattern_pub = r'(<div class="metric-number">)[^<]*(</div>\s*<div class="metric-label">Publications &amp; Software</div>)'
    html, n_p = re.subn(pattern_pub, rf'\g<1>{pub_str}\g<2>', html)

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    log_success(f"Metrics banner updated in index.html:")
    print(f"   • Scholar Citations: {cites_str}")
    print(f"   • h-index / i10-index: {h_i10_str}")
    print(f"   • Publications & Software: {pub_str}")
    return True


# ==============================================================================
# 3. Synchronize BibTeX Database (assets/bibtex/publications.bib)
# ==============================================================================
def sync_bibtex():
    """Extracts all BibTeX blocks from index.html and writes to publications.bib."""
    if not os.path.exists(INDEX_FILE):
        log_error(f"Cannot find {INDEX_FILE}")
        return False

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    bib_blocks = re.findall(
        r'<div class="bibtex-block"[^>]*>.*?<code>(.*?)</code>.*?</div>',
        html,
        re.DOTALL
    )

    if not bib_blocks:
        log_warn("No BibTeX blocks found in index.html")
        return False

    os.makedirs(os.path.dirname(BIB_FILE), exist_ok=True)
    all_bib = '\n\n'.join(b.strip() for b in bib_blocks) + '\n'

    with open(BIB_FILE, 'w', encoding='utf-8') as f:
        f.write(all_bib)

    log_success(f"Synchronized {len(bib_blocks)} BibTeX entries to {os.path.relpath(BIB_FILE, SITE_DIR)}")
    return True


# ==============================================================================
# 4. Add a New Publication
# ==============================================================================
def add_publication():
    """Interactively prompts the user to add a new publication to index.html and publications.bib."""
    print(f"\n{BOLD}{CYAN}=== Add a New Publication ==={RESET}")

    title = input(f"{BOLD}Title of Paper:{RESET} ").strip()
    if not title:
        log_error("Title is required.")
        return False

    current_year = str(datetime.datetime.now().year)
    year = input(f"{BOLD}Year [{current_year}]:{RESET} ").strip() or current_year
    authors = input(f"{BOLD}Authors [Aiman Al-Sabaawi]:{RESET} ").strip() or "Aiman Al-Sabaawi"
    venue = input(f"{BOLD}Venue (Journal / Conference / arXiv):{RESET} ").strip()
    if not venue:
        venue = "Preprint, " + year

    print(f"\n{BOLD}Select Category:{RESET}")
    print("  [1] Journal Article")
    print("  [2] Conference Paper")
    print("  [3] Book Chapter / Monograph")
    print("  [4] Preprint / Technical Report")
    cat_choice = input(f"{BOLD}Choice [1-4, default 1]:{RESET} ").strip() or "1"

    if cat_choice == "2":
        cat_class = "ai-sec conference"
        badge_type = "conference"
        badge_label = "Conference"
        bib_type = "inproceedings"
    elif cat_choice == "3":
        cat_class = "ai-sec conference"
        badge_type = "conference"
        badge_label = "Chapter"
        bib_type = "incollection"
    elif cat_choice == "4":
        cat_class = "ai-sec preprint"
        badge_type = "preprint"
        badge_label = "Preprint"
        bib_type = "article"
    else:
        cat_class = "ai-sec journal"
        badge_type = "journal"
        badge_label = "Journal"
        bib_type = "article"

    url = input(f"{BOLD}Direct Paper Link (DOI / IEEE / Springer / arXiv URL):{RESET} ").strip()
    if not url:
        url = "https://scholar.google.com/citations?user=" + SCHOLAR_USER_ID

    # Auto-detect button label from URL
    link_label = "View Paper"
    if "ieeexplore.ieee.org" in url:
        link_label = "IEEE Xplore"
    elif "springer.com" in url:
        link_label = "Springer Link"
    elif "arxiv.org" in url:
        link_label = "arXiv Link"
    elif "eprints.qut.edu.au" in url:
        link_label = "QUT ePrints"
    elif "wiley.com" in url:
        link_label = "Wiley Online"
    elif "mdpi.com" in url:
        link_label = "MDPI Journal"

    custom_label = input(f"{BOLD}Link Button Label [{link_label}]:{RESET} ").strip()
    if custom_label:
        link_label = custom_label

    abstract = input(f"{BOLD}Brief Abstract / Summary (1-2 sentences):{RESET} ").strip()
    if not abstract:
        abstract = f"Published research contribution in {venue}."

    # Generate BibTeX ID
    first_word = re.sub(r'[^a-zA-Z0-9]', '', title.split()[0].lower()) if title.split() else 'paper'
    bib_id = f"alsabaawi{year}{first_word}"

    # Format authors HTML (highlighting user's name)
    authors_html = authors.replace("Aiman Al-Sabaawi", '<span class="pub-author-me">Aiman Al-Sabaawi</span>')
    if "Aiman Al-Sabaawi" not in authors and '<span class="pub-author-me">' not in authors_html:
        authors_html = f'<span class="pub-author-me">Aiman Al-Sabaawi</span>, ' + authors_html

    # Build BibTeX
    if bib_type == "inproceedings":
        bib_content = f"""@{bib_type}{{{bib_id},
  title={{{title}}},
  author={{{authors}}},
  booktitle={{{venue}}},
  year={{{year}}},
  url={{{url}}}
}}"""
    else:
        bib_content = f"""@{bib_type}{{{bib_id},
  title={{{title}}},
  author={{{authors}}},
  journal={{{venue}}},
  year={{{year}}},
  url={{{url}}}
}}"""

    # Build Article HTML block
    article_html = f"""
          <!-- {title} -->
          <article class="pub-card" data-category="{cat_class}">
            <div class="pub-header">
              <h3 class="pub-title">{title}</h3>
              <div class="pub-badge-group">
                <span class="pub-badge {badge_type}">{badge_label}</span>
                <span class="pub-badge preprint">{year}</span>
              </div>
            </div>
            <div class="pub-authors">
              {authors_html}
            </div>
            <div class="pub-venue">{venue}</div>
            <div class="pub-abstract">
              {abstract}
            </div>
            <div class="pub-actions">
              <a href="{url}" target="_blank" rel="noopener noreferrer" class="pub-action-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                {link_label}
              </a>
              <button class="pub-action-btn toggle-bibtex-btn" data-target="{bib_id}">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
                BibTeX
              </button>
            </div>
            <div class="bibtex-block" id="{bib_id}">
              <button class="bibtex-copy-btn">Copy</button>
              <code>{bib_content}</code>
            </div>
          </article>"""

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # Prepend to the top of publication list so new papers appear first
    pub_list_marker = '<div class="pub-list" id="publications-list">'
    if pub_list_marker in html:
        html = html.replace(pub_list_marker, pub_list_marker + "\n" + article_html)
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        log_success(f"Added '{title}' to index.html")
    else:
        log_error("Could not locate pub-list in index.html")
        return False

    # Synchronize BibTeX file
    sync_bibtex()

    # Update metric counts
    update_metrics()
    return True


# ==============================================================================
# 5. Git Commit, Push & Deploy
# ==============================================================================
def deploy_changes(custom_msg=None):
    """Commits and pushes changes to GitHub Pages."""
    log_info("Checking git repository status...")
    status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=SITE_DIR)

    if not status.stdout.strip():
        log_info("Working tree clean — no pending changes to deploy.")
        return True

    print("\nModified files:")
    for line in status.stdout.strip().split('\n'):
        print(f"  {line}")

    if not custom_msg:
        default_msg = f"Update publications and metrics ({datetime.datetime.now().strftime('%Y-%m-%d')})"
        custom_msg = input(f"\n{BOLD}Commit message [{default_msg}]:{RESET} ").strip() or default_msg

    try:
        subprocess.run(['git', 'add', 'index.html', 'assets/bibtex/publications.bib'], check=True, cwd=SITE_DIR)
        # Check if anything staged
        diff_cached = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=SITE_DIR)
        if diff_cached.returncode != 0:
            subprocess.run(['git', 'commit', '-m', custom_msg], check=True, cwd=SITE_DIR)
            log_info("Pushing to origin main (GitHub Pages)...")
            subprocess.run(['git', 'push', 'origin', 'main'], check=True, cwd=SITE_DIR)
            log_success("Changes pushed to GitHub successfully!")
            return True
        else:
            log_info("No staged changes to commit.")
            return True
    except subprocess.CalledProcessError as e:
        log_error(f"Git command failed: {e}")
        return False


# ==============================================================================
# 6. Send Notification via ntfy.sh
# ==============================================================================
def send_notification(title="Academic Portfolio Updated", message=None):
    """Sends a notification to ntfy.sh/HPC."""
    if not message:
        message = f"Website updated and deployed successfully to {SITE_URL}"

    ntfy_url = f"https://ntfy.sh/{NTFY_TOPIC}"
    req = urllib.request.Request(
        ntfy_url,
        data=message.encode('utf-8'),
        headers={
            'Title': title,
            'Priority': 'default',
            'Tags': 'white_check_mark,globe_with_meridians',
            'Click': SITE_URL,
            'Actions': f'view, Open Website, {SITE_URL}'
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            log_success(f"Notification delivered to ntfy.sh/{NTFY_TOPIC}")
            return True
    except Exception as e:
        log_warn(f"Failed to send notification to ntfy.sh: {e}")
        return False


# ==============================================================================
# 7. Complete All-in-One Automated Pipeline
# ==============================================================================
def run_all():
    """Runs metric fetch, bibtex sync, git deploy, and notification in one command."""
    print(f"\n{BOLD}{CYAN}=== Starting Complete Website Sync & Deploy ==={RESET}\n")
    update_metrics()
    sync_bibtex()
    pushed = deploy_changes("Update citations, metrics, and publications database")
    if pushed:
        send_notification(
            title="Portfolio Updated & Deployed",
            message=f"Live metrics & publications synced and deployed to {SITE_URL}"
        )
    log_success("All tasks completed successfully!")


# ==============================================================================
# 8. Interactive CLI Menu
# ==============================================================================
def show_menu():
    while True:
        print(f"\n{BOLD}{CYAN}╔═════════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{CYAN}║            Aiman Al-Sabaawi - Website Update Tool               ║{RESET}")
        print(f"{BOLD}{CYAN}║                    https://alsabaawi.github.io                  ║{RESET}")
        print(f"{BOLD}{CYAN}╚═════════════════════════════════════════════════════════════════╝{RESET}")
        print(f" {BOLD}[1]{RESET} {GREEN}Update Metrics & Citations{RESET} (Live from Google Scholar)")
        print(f" {BOLD}[2]{RESET} {BLUE}Add a New Publication{RESET} (Interactive wizard)")
        print(f" {BOLD}[3]{RESET} {YELLOW}Synchronize BibTeX Database{RESET} (assets/bibtex/publications.bib)")
        print(f" {BOLD}[4]{RESET} {CYAN}Complete Auto-Sync & Push{RESET} (Metrics + BibTeX + Git Push + ntfy)")
        print(f" {BOLD}[5]{RESET} Deploy / Push Changes to GitHub Pages")
        print(f" {BOLD}[6]{RESET} Send Notification to ntfy.sh/{NTFY_TOPIC}")
        print(f" {BOLD}[0]{RESET} Exit")

        choice = input(f"\n{BOLD}Select an option [0-6]:{RESET} ").strip()

        if choice == '1':
            update_metrics()
        elif choice == '2':
            add_publication()
        elif choice == '3':
            sync_bibtex()
        elif choice == '4':
            run_all()
        elif choice == '5':
            deploy_changes()
        elif choice == '6':
            send_notification()
        elif choice == '0' or choice.lower() in ('q', 'exit'):
            print("Goodbye!")
            break
        else:
            log_warn("Invalid option, please choose between 0 and 6.")


# ==============================================================================
# Entry Point
# ==============================================================================
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ('--metrics', '-m'):
            update_metrics()
        elif arg in ('--add', '-a'):
            add_publication()
        elif arg in ('--sync-bib', '-b'):
            sync_bibtex()
        elif arg in ('--push', '-p'):
            deploy_changes()
        elif arg in ('--notify', '-n'):
            send_notification()
        elif arg in ('--all', '-A'):
            run_all()
        elif arg in ('--help', '-h'):
            print(__doc__)
        else:
            print(f"Unknown option '{arg}'. Use --help for usage details.")
    else:
        show_menu()
