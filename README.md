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

## ✏️ How to Maintain and Update

### 1. Adding a New Publication
In `index.html`, add a new `<article class="pub-card" data-category="...">` block inside `<div class="pub-list">`. You can assign tags like `ai-sec`, `journal`, `conference`, or `preprint`. Also add the BibTeX entry to `assets/bibtex/publications.bib`.

### 2. Adding a News Item
In `index.html`, add a `<div class="news-item">` block inside `<div class="news-list">` with the date, badge tag (`publication`, `award`, `appointment`), and summary.

### 3. Updating Profile Information or Links
Modify the relevant section in `index.html` (e.g., hero social links, affiliation list, or contact information).

---

## 🚀 Deployment

The site deploys automatically to **`https://alsabaawi.github.io`** whenever changes are pushed to the `main` branch.

To enable GitHub Pages in your repository settings:
1. Navigate to **Settings** > **Pages** in `alsabaawi/alsabaawi.github.io`.
2. Under **Build and deployment**, select **GitHub Actions** (recommended) or **Deploy from a branch** (`main` / `/root`).
