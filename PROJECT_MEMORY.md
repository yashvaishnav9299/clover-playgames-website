# PROJECT MEMORY — Clover Play Games Website

> **Single Source of Truth** for system architecture, environment state, active sprint tracking, and operational runbooks. Maintained per the Autonomous Engineering & Project Operating Protocol.

---

## 1. System Architecture & Tech Stack Decisions

### Overview
- **Project**: Clover Play Games — Official Company "Coming Soon" Teaser Website
- **Repository**: `https://github.com/yashvaishnav9299/clover-playgames-website.git`
- **Hosting & DNS Architecture**: **GitHub Pages** (global CDN, automatic deploy from `main` `/` root, free managed TLS/SSL) + **Hostinger Custom Domain DNS** (`A`, `AAAA`, and `CNAME` records managed via Hostinger API).
- **Application Stack**: Zero-build, dependency-free static web application (HTML5 + CSS3 + vanilla ES6) with Python 3 standard-library verification and deployment automation (`scripts/manage_site.py`).
- **Design Rationale**:
  - **Zero External Runtime Dependencies**: Eliminates bundler complexity, supply-chain vulnerabilities, and build-step latency for a single-page teaser site.
  - **Art-Directed Responsive Backgrounds**: Uses CSS media queries (`min-width`, `max-width`, and `min-resolution` / `-webkit-min-device-pixel-ratio`) in `css/styles.css` to serve resolution-appropriate 16:9 desktop (`1672px`, `2400px`, `2560px`) and 9:16 mobile (`941px`, `1080px`) hero illustrations.
  - **Typography**: Google Fonts (`Poppins` weights 400–900) loaded with `preconnect` hints for optimal First Contentful Paint (FCP).

### Directory Structure
```text
clover-playgames-website/
├── index.html             # Semantic HTML5 markup, SEO/Open Graph meta, inline SVG logo, micro-interaction script
├── css/
│   └── styles.css         # Custom properties, responsive layout, art-direction breakpoints, animations
├── images/
│   ├── favicon.svg             # 5-petal gradient clover SVG browser tab icon
│   ├── hero-desktop-1672.jpg   # Base desktop (1672x941, 16:9)
│   ├── hero-desktop-2400.jpg   # Large desktop (2400x1350, 16:9)
│   ├── hero-desktop-2560.jpg   # 4K/Ultra-wide desktop (2560x1440, 16:9)
│   ├── hero-mobile-941.jpg     # Standard mobile portrait (941x1672, 9:16)
│   └── hero-mobile-1080.jpg    # Retina mobile portrait (1080x1920, 9:16)
├── scripts/
│   └── manage_site.py     # Zero-dependency Python 3 CLI for verification (`verify`) & DNS/Pages deployment (`deploy`)
├── .env.example           # Template for local deployment & DNS automation secrets (never committed with real values)
├── .gitignore             # Git exclusion rules (OS artifacts, logs, .env secrets, private keys)
├── LICENSE                # Project license
├── PROJECT_MEMORY.md      # Persistent architectural & project state documentation
└── README.md              # Developer quick-start and deployment documentation
```

---

## 2. Environment & Toolchain Prerequisites

### Audited Local Workstation State (Windows)
- **OS**: Windows (`powershell` shell)
- **Git**: Configured (`user.name=Yash Vaishnav`, `user.email=yashvaishnav9299@gmail.com`, `credential.helper=manager`, `core.autocrlf=true`)
- **Python**: `Python 3.13.7` available (`python scripts/manage_site.py verify` and `python scripts/manage_site.py deploy`)
- **SSH Client**: `OpenSSH_for_Windows_9.5p2` available
- **Not Installed Locally**: `node` / `npm`, `gh` (GitHub CLI) — all automation scripts rely strictly on Python 3.13 standard library (`urllib.request`, `html.parser`, `json`, `pathlib`).

---

## 3. Active Sprint State & Milestones

### Completed Milestones
- [x] **Initial Site & Artwork (`c719752`, `d87bef9`)**: Responsive hero background switching and typography.
- [x] **Phase 1 — Architectural & Product Decisions**:
  - Selected **GitHub Pages + Hostinger DNS** architecture.
  - Selected **Full Production Polish** scope.
  - Configured `.coming-soon` hero element as a static `<span>` status badge (no dead `#` jump).
  - Configured header Instagram link to `https://www.instagram.com/cloverplaygames/` with `target="_blank" rel="noopener noreferrer"`.
- [x] **Phase 2 — Git History Reconciliation**:
  - Merged `origin/main` (`41fa7a1` — structural flex/width stability fixes) with local `main` (`c9292f3`, `fc183cb` + working tree updates: 5-petal clover SVG, `SOMETHING FUN IS LOADING.` copy, and `.loading-progress` bar) and pushed to `origin/main`.
- [x] **Phase 3 — Production Readiness, SEO & Verification Suite**:
  - Created `images/favicon.svg` from the 5-petal gradient clover mark and linked in `<head>`.
  - Added canonical URL (`https://cloverplaygames.com/`), Open Graph (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`, `og:site_name`), and Twitter Card (`summary_large_image`) meta tags in `index.html`.
  - Cleaned up `css/styles.css`: replaced dead `border-color` hover on borderless `.icon-btn` with `color: var(--green)`, removed unused `@keyframes instagram-press`, removed `!important` overrides on `.coming-soon`, and increased mobile Instagram SVG icon from `14px` to `22px` for visual balance.
  - Built `scripts/manage_site.py` (`verify`, `status`, and `deploy` subcommands) and verified all checks pass (`python scripts/manage_site.py verify`).
- [x] **Phase 4A — Hostinger DNS Provisioning & `CNAME` Setup**:
  - Connected to Hostinger API (`developers.hostinger.com`) for `cloverplaygames.com` (`id: 34360046`, active until `2027-09-10`).
  - Replaced legacy Netlify DNS records (`75.2.60.5` and `magic-sort-webdemo.netlify.app.`) with GitHub Pages `A` records (`185.199.108.153`..`111.153`), `AAAA` IPv6 records (`2606:50c0:8000::153`..`8003::153`), and `www` `CNAME` (`yashvaishnav9299.github.io`), while preserving all 8 Hostinger email records (`MX`, `SPF`, `DMARC`, `DKIM`, `autoconfig`, `autodiscover`).
  - Added `CNAME` (`cloverplaygames.com`) to repository root.
- [x] **Phase 4B — GitHub Pages Activation & HTTPS Enforcement**:
  - Enabled GitHub Pages (`main` branch, `/` root) via GitHub REST API (`PUT /repos/yashvaishnav9299/clover-playgames-website/pages`).
  - Provisioned Let's Encrypt TLS certificate (`state: approved`, expires `2027-02-05`) covering both `cloverplaygames.com` and `www.cloverplaygames.com`.
  - Enabled `https_enforced: true` and verified `status: built` at `https://cloverplaygames.com/`.
- [x] **Phase 4C — Hostinger Agentic Mail API Integration**:
  - Connected `scripts/manage_site.py mail` to `https://api.mail.hostinger.com/api/v1` using `HOSTINGER_MAIL_API_TOKEN` in `.env`.
  - Verified active mailbox resource `ACdd7d5abbaa2024c8efdf34986ab4` (`info@cloverplaygames.com`, order `OR47a2a52ea5c0be690b521356cbca`) and folder access (`INBOX`, `Drafts`, `Junk`, `Sent`, `Trash`).
  - Updated website header CTA and footer contact links in `index.html` from `hello@cloverplaygames.com` to `info@cloverplaygames.com`.

### Immediate Pending Tasks
- None — all current sprint milestones are complete and live in production at `https://cloverplaygames.com/`.

---

## 4. Known Edge Cases, Workarounds & Runbooks

1. **Running Verification Locally**:
   ```powershell
   python scripts/manage_site.py verify
   ```
   Validates HTML5 tag balance, required SEO/Open Graph meta tags, zero `href="#"` placeholders, CSS brace balance, zero `!important` overrides, responsive image existence, and binary file headers (JPEG `FF D8 FF` magic bytes, SVG `<svg` root).
2. **Deploying Custom Domain & DNS**:
   ```powershell
   # 1. Preview changes safely
   python scripts/manage_site.py deploy --dry-run

   # 2. Apply live (requires .env with DOMAIN_NAME, HOSTINGER_API_TOKEN, GITHUB_TOKEN)
   python scripts/manage_site.py deploy
   ```
3. **Preserving Email (`MX` / `TXT`) Records on Hostinger**:
   - `scripts/manage_site.py deploy` sends `"overwrite": false` to `PUT https://developers.hostinger.com/api/dns/v1/zones/{domain}` so existing `MX`, `SPF`, `DKIM`, and `DMARC` records for `hello@cloverplaygames.com` are preserved while adding the GitHub Pages `A`, `AAAA`, and `www` `CNAME` records.
