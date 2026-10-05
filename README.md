# Aiman Al-Sabaawi — Academic Profile Website

Personal academic website and research portfolio for **Aiman Al-Sabaawi (AFHEA)**, PhD Researcher in Cybersecurity at Queensland University of Technology (QUT), Lecturer at APIC, and Principal Cyber Security Advisor at SECBLOK.

Live at: **[alsabaawi.github.io](https://alsabaawi.github.io)**

---

## 🌟 Key Features

- **Blazing Fast & Zero Dependencies**: Built with clean, modern HTML5, CSS3, and vanilla JavaScript. No Ruby, Gemfile, or Hugo build breakage. Instant deployment via GitHub Pages.
- **Dark / Light Mode Toggle**: Smooth theme switching with automatic system preference detection (`prefers-color-scheme`) and persistent preference caching.
- **Interactive Publications Showcase**:
  - Real-time search across titles, authors, venues, and keywords.
  - Category filter pills (All, AI & Cybersecurity, Journals, Conferences, Preprints).
  - 1-click **BibTeX modal** with instant clipboard copy and feedback toast.
  - Direct links to DOI, arXiv, and code repositories.
- **Research Focus & Core Themes**: Dedicated sections for AI-assisted vulnerability detection, trustworthy AI, mobile forensics, and cryptanalysis.
- **News & Milestones**: Structured timeline for awards, appointments, and research releases.
- **Teaching, Editorial & Academic Service**: Clear highlights for APIC, QUT, AFHEA fellowship, editorial boards, and professional memberships (IEEE, ACS, AISA, IACR, AustMS).
- **Curriculum Vitae (CV)**:
  - Interactive online career history and skills matrix.
  - Printable / Export-to-PDF ready with custom `@media print` styles.
  - Downloadable BibTeX database (`assets/bibtex/publications.bib`).
- **Responsive & Accessible**: Seamlessly adapts to desktop, tablet, and mobile devices.

---

## 📁 Repository Structure

```text
alsabaawi.github.io/
├── index.html                   # Main academic profile page
├── .nojekyll                    # Ensures GitHub Pages serves static files directly
├── README.md                    # Documentation & guide
├── .github/
│   └── workflows/
│       └── pages.yml            # Automated GitHub Actions deployment to Pages
└── assets/
    ├── css/
    │   └── style.css            # Stylesheet (dark/light themes, print formatting)
    ├── js/
    │   └── main.js              # Theme switcher, scrollspy, filters, BibTeX copy
    ├── bibtex/
    │   └── publications.bib     # Standalone BibTeX citation file
    └── images/
        └── avatar.jpg           # Profile picture
```

---

## ⚡ Automated Site Maintenance Tool (`update_site.py`)

A built-in script is included to automatically update Scholar metrics, citations, publications, and BibTeX database.

### Run Interactive Menu:
```bash
python3 update_site.py
```

### Quick Commands:
```bash
python3 update_site.py --metrics    # Fetch live citations, h-index, i10-index from Google Scholar
python3 update_site.py --add        # Wizard to add a new paper to HTML & BibTeX
python3 update_site.py --sync-bib   # Sync assets/bibtex/publications.bib from index.html
python3 update_site.py --push       # Git commit and push changes to GitHub Pages
python3 update_site.py --notify     # Send status notification to ntfy.sh/HPC
python3 update_site.py --all        # Complete pipeline: update metrics, sync bib, push & notify
```

---

## ✏️ Manual Maintenance and Updates

---

## 🚀 Deployment

The site deploys automatically to **`https://alsabaawi.github.io`** whenever changes are pushed to the `main` branch.

To enable GitHub Pages in your repository settings:
1. Navigate to **Settings** > **Pages** in `alsabaawi/alsabaawi.github.io`.
2. Under **Build and deployment**, select **GitHub Actions** (recommended) or **Deploy from a branch** (`main` / `/root`).
