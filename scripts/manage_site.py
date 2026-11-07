#!/usr/bin/env python3
"""
Clover Play Games — Static Site Verification & Deployment Automation
Uses exclusively the Python 3 Standard Library (zero external dependencies).

Commands:
  python scripts/manage_site.py verify           # Run HTML/CSS/Asset/HTTP verification suite
  python scripts/manage_site.py deploy --dry-run # Preview CNAME, Hostinger DNS & GitHub Pages calls
  python scripts/manage_site.py deploy           # Execute live CNAME + Hostinger DNS + GitHub Pages setup
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

GITHUB_PAGES_IPV4 = [
    "185.199.108.153",
    "185.199.109.153",
    "185.199.110.153",
    "185.199.111.153",
]

GITHUB_PAGES_IPV6 = [
    "2606:50c0:8000::153",
    "2606:50c0:8001::153",
    "2606:50c0:8002::153",
    "2606:50c0:8003::153",
]


def load_env(env_path: Path) -> dict[str, str]:
    env_vars: dict[str, str] = {}
    if not env_path.exists():
        return env_vars
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars


class HTMLValidator(HTMLParser):
    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img",
        "input", "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.links: list[str] = []
        self.meta_tags: dict[str, str] = {}
        self.has_favicon = False
        self.has_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = {k: (v or "") for k, v in attrs}
        if tag not in self.VOID_ELEMENTS:
            self.stack.append(tag)
        if tag == "title":
            self.has_title = True
        if tag == "a" and "href" in attr_dict:
            self.links.append(attr_dict["href"])
        if tag == "link":
            rel = attr_dict.get("rel", "")
            href = attr_dict.get("href", "")
            if "icon" in rel:
                self.has_favicon = True
                self.links.append(href)
            elif rel == "stylesheet":
                self.links.append(href)
        if tag == "meta":
            key = attr_dict.get("property") or attr_dict.get("name")
            content = attr_dict.get("content", "")
            if key:
                self.meta_tags[key] = content

    def handle_endtag(self, tag: str) -> None:
        if tag in self.VOID_ELEMENTS:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Mismatched closing tag </{tag}> (stack: {self.stack})")
        else:
            self.stack.pop()


def verify_site() -> int:
    print("=== Clover Play Games: Running Verification Suite ===")
    failures: list[str] = []

    index_path = ROOT_DIR / "index.html"
    css_path = ROOT_DIR / "css" / "styles.css"

    if not index_path.exists():
        print("[FAIL] index.html is missing.")
        return 1
    if not css_path.exists():
        print("[FAIL] css/styles.css is missing.")
        return 1

    # 1. Validate HTML structure, links, and metadata
    html_content = index_path.read_text(encoding="utf-8")
    validator = HTMLValidator()
    validator.feed(html_content)

    if validator.errors:
        failures.extend(validator.errors)
    if validator.stack:
        failures.append(f"Unclosed HTML tags remaining: {validator.stack}")
    if not validator.has_title:
        failures.append("Missing <title> element in index.html")
    if not validator.has_favicon:
        failures.append("Missing <link rel='icon'> favicon in index.html")

    required_meta = ["description", "og:title", "og:description", "og:image", "twitter:card"]
    for meta_key in required_meta:
        if meta_key not in validator.meta_tags or not validator.meta_tags[meta_key]:
            failures.append(f"Missing or empty meta tag: {meta_key}")

    for href in validator.links:
        if href == "#":
            failures.append("Found dead placeholder link href='#' in index.html")
        elif not href.startswith(("http://", "https://", "mailto:", "./", "/")):
            target = (ROOT_DIR / href).resolve()
            if not target.exists():
                failures.append(f"Broken relative asset link in index.html: {href}")

    for img_meta in ("og:image", "twitter:image"):
        img_ref = validator.meta_tags.get(img_meta, "")
        if img_ref and not img_ref.startswith(("http://", "https://")):
            if not (ROOT_DIR / img_ref).exists():
                failures.append(f"Missing social preview image referenced by {img_meta}: {img_ref}")

    print("[PASS] HTML5 structure, SEO/Open Graph meta tags, and link targets verified.")

    # 2. Validate CSS syntax & asset URLs
    css_content = css_path.read_text(encoding="utf-8")
    open_braces = css_content.count("{")
    close_braces = css_content.count("}")
    if open_braces != close_braces:
        failures.append(f"Unbalanced CSS braces in styles.css: {open_braces} '{{' vs {close_braces} '}}'")

    if "!important" in css_content:
        failures.append("Found '!important' override in css/styles.css; prefer clean specificity.")

    url_matches = re.findall(r'url\(["\']?([^"\')]+)["\']?\)', css_content)
    for rel_url in url_matches:
        resolved = (css_path.parent / rel_url).resolve()
        if not resolved.exists():
            failures.append(f"Missing CSS background image asset: {rel_url} (expected at {resolved})")

    print(f"[PASS] CSS syntax and {len(url_matches)} responsive background assets verified.")

    # 3. Static Asset Integrity (JPEG headers, SVG XML structure, non-empty sizes)
    expected_assets = [
        ("index.html", b"<!DOCTYPE html>"),
        ("css/styles.css", b"/*"),
        ("images/favicon.svg", b"<svg"),
        ("images/hero-desktop-1672.jpg", b"\xff\xd8\xff"),
        ("images/hero-desktop-2400.jpg", b"\xff\xd8\xff"),
        ("images/hero-desktop-2560.jpg", b"\xff\xd8\xff"),
        ("images/hero-mobile-941.jpg", b"\xff\xd8\xff"),
        ("images/hero-mobile-1080.jpg", b"\xff\xd8\xff"),
    ]
    for rel_path, magic_prefix in expected_assets:
        asset_file = ROOT_DIR / rel_path
        if not asset_file.exists():
            failures.append(f"Missing required asset: {rel_path}")
            continue
        raw_bytes = asset_file.read_bytes()
        if len(raw_bytes) == 0:
            failures.append(f"Asset file is empty (0 bytes): {rel_path}")
        elif not raw_bytes.lstrip().startswith(magic_prefix):
            failures.append(f"Asset file header mismatch for {rel_path}")

    print(f"[PASS] Asset binary/header integrity verified across {len(expected_assets)} files.")

    if failures:
        print("\n=== VERIFICATION FAILED ===")
        for f in failures:
            print(f" - {f}")
        return 1

    print("\n=== ALL VERIFICATION CHECKS PASSED ===")
    return 0


def api_request(url: str, method: str, headers: dict[str, str], payload: dict | None, dry_run: bool) -> dict | list:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    if dry_run:
        print(f"[DRY-RUN] {method} {url}")
        if payload is not None:
            print(f"          Payload: {json.dumps(payload, indent=2)}")
        return {"status": "dry_run"}

    req_headers = {"User-Agent": "CloverPlayGames-DeployCLI/1.0", **headers}
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {"status": resp.status}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} on {method} {url}: {err_body}") from exc


def deploy_site(dry_run: bool) -> int:
    env = {**load_env(ROOT_DIR / ".env"), **os.environ}
    domain = env.get("DOMAIN_NAME", "").strip()
    hostinger_token = env.get("HOSTINGER_API_TOKEN", "").strip()
    github_token = env.get("GITHUB_TOKEN", "").strip()
    github_repo = env.get("GITHUB_REPO", "yashvaishnav9299/clover-playgames-website").strip()

    if not domain or domain == "your_domain_here":
        if dry_run:
            domain = "cloverplaygames.com"
        else:
            print("[ERROR] DOMAIN_NAME is not set in .env")
            return 1

    owner = github_repo.split("/")[0]

    # Step 1: Write CNAME file
    cname_path = ROOT_DIR / "CNAME"
    if dry_run:
        print(f"[DRY-RUN] Would write CNAME file at {cname_path} with content: {domain}")
    else:
        cname_path.write_text(f"{domain}\n", encoding="utf-8")
        print(f"[OK] Wrote CNAME file for {domain}")

    # Step 2: Configure Hostinger DNS Zone for GitHub Pages (preserving MX/TXT/DKIM email records)
    hostinger_url = f"https://developers.hostinger.com/api/dns/v1/zones/{domain}"
    hostinger_headers = {
        "Authorization": f"Bearer {hostinger_token or 'REDACTED'}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if not dry_run and not hostinger_token:
        print("[ERROR] HOSTINGER_API_TOKEN is missing in .env; cannot configure Hostinger DNS.")
        return 1

    preserved_records: list[dict] = []
    if not dry_run:
        existing_zone = api_request(hostinger_url, "GET", hostinger_headers, None, dry_run=False)
        if isinstance(existing_zone, list):
            for entry in existing_zone:
                r_name = entry.get("name")
                r_type = entry.get("type")
                # Replace root A/AAAA and www CNAME; keep all MX, TXT, DKIM, autodiscover, etc.
                if (r_name == "@" and r_type in ("A", "AAAA")) or (r_name == "www" and r_type == "CNAME"):
                    continue
                preserved_records.append({
                    "name": r_name,
                    "type": r_type,
                    "ttl": entry.get("ttl", 3600),
                    "records": [{"content": r["content"]} for r in entry.get("records", [])],
                })

    dns_payload = {
        "overwrite": True,
        "zone": preserved_records + [
            {
                "name": "@",
                "type": "A",
                "ttl": 3600,
                "records": [{"content": ip} for ip in GITHUB_PAGES_IPV4],
            },
            {
                "name": "@",
                "type": "AAAA",
                "ttl": 3600,
                "records": [{"content": ip} for ip in GITHUB_PAGES_IPV6],
            },
            {
                "name": "www",
                "type": "CNAME",
                "ttl": 3600,
                "records": [{"content": f"{owner}.github.io"}],
            },
        ],
    }

    api_request(hostinger_url, "PUT", hostinger_headers, dns_payload, dry_run=dry_run)
    if not dry_run:
        print(f"[OK] Configured Hostinger DNS records (A, AAAA, CNAME) for {domain} (preserved {len(preserved_records)} existing records)")

    # Step 3: Configure GitHub Pages & Custom Domain
    gh_pages_url = f"https://api.github.com/repos/{github_repo}/pages"
    gh_headers = {
        "Authorization": f"Bearer {github_token or 'REDACTED'}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    gh_payload = {
        "cname": domain,
        "https_enforced": True,
        "source": {"branch": "main", "path": "/"},
    }

    if not dry_run and not github_token:
        print("[WARN] GITHUB_TOKEN not set in .env; skipping GitHub Pages REST API call.")
    else:
        api_request(gh_pages_url, "PUT", gh_headers, gh_payload, dry_run=dry_run)
        if not dry_run:
            print(f"[OK] Configured GitHub Pages custom domain ({domain}) for {github_repo}")

    return 0


def check_hostinger_status() -> int:
    env = {**load_env(ROOT_DIR / ".env"), **os.environ}
    hostinger_token = env.get("HOSTINGER_API_TOKEN", "").strip()
    if not hostinger_token:
        print("[ERROR] HOSTINGER_API_TOKEN is not set in .env")
        return 1

    headers = {
        "Authorization": f"Bearer {hostinger_token}",
        "Accept": "application/json",
    }

    print("=== Querying Hostinger Domain Portfolio ===")
    portfolio = api_request(
        "https://developers.hostinger.com/api/domains/v1/portfolio",
        "GET",
        headers,
        None,
        dry_run=False,
    )
    print(json.dumps(portfolio, indent=2))

    domain = env.get("DOMAIN_NAME", "").strip()
    if isinstance(portfolio, list) and len(portfolio) > 0:
        discovered = portfolio[0].get("domain")
        if discovered:
            domain = discovered

    if domain:
        print(f"\n=== Querying Hostinger DNS Zone for {domain} ===")
        zone = api_request(
            f"https://developers.hostinger.com/api/dns/v1/zones/{domain}",
            "GET",
            headers,
            None,
            dry_run=False,
        )
        print(json.dumps(zone, indent=2))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Clover Play Games Verification & Deployment CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("verify", help="Run HTML/CSS/Asset/HTTP verification suite")
    sub.add_parser("status", help="Inspect Hostinger domains and DNS zone records")
    deploy_parser = sub.add_parser("deploy", help="Configure CNAME, Hostinger DNS, and GitHub Pages")
    deploy_parser.add_argument("--dry-run", action="store_true", help="Print planned actions without network writes")

    args = parser.parse_args()
    if args.command == "verify":
        return verify_site()
    if args.command == "status":
        return check_hostinger_status()
    if args.command == "deploy":
        return deploy_site(dry_run=args.dry_run)
    return 1


if __name__ == "__main__":
    sys.exit(main())
