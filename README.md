# Always Booked — static site (Render deploy)

Ready-to-deploy copy of the agency site (`index.html` + `assets/logo.png`).
Source of truth: `C:\Users\oegar\Desktop\always_booked_agency.html`. Full ops/state/migration notes live in the Hermes skill `always-booked-ops` (`references/render-migration.md`).

## Fixed tonight (Oct 20, 2026)

- Logo now self-hosted at `assets/logo.png` (was a Netlify URL).
- Founder photo: now `assets/founder.png` (Omar's square portrait, cropped/resized to 600×600). It has a warm film filter; if he wants it neutral-cyan to match the site, ask for an unfiltered shot.
- AI widget icon: replaced broken GHL image with a brand-color SVG orb.
- Removed "LLC" from `<title>`, `og:title`, nav/hero logo alt, and footer (brand is not an LLC yet).
- Footer: dropped the false "serving nationwide since 2011" claim; added info@alwaysbookedai.tech.

## TODO before launch

- Real founder headshot (search `src="data:image/svg+xml` for the two placeholders).
- Fix remaining honest-claim issues: "Est. 2011" hero badge and "15+ Years Dominating Orlando & Nationwide" — verify the real founding date or swap for a true stat.
- Add: `favicon`, `og:image` (1200×630), `<link rel="canonical">`, GA4 snippet (new property, not PFC's), JSON-LD `ProfessionalService`.
- Add `robots.txt` and `sitemap.xml`.
- Footer links to Fiverr profile and PureFileConverter ("free tools").
- `ADR:` decide GHL renew vs Stripe + Cal.com swap (see skill reference) before the next GHL PAYMENT.

## Deploy checklist (tomorrow)

1. Create a private GitHub repo under `omareg03` (you can make it public — no secrets in these files).
2. Push this folder. (Ask Hermes for the exact commands.)
3. Render → New → Static Site → connect repo. Build command blank, Publish directory `.`.
4. Open the `*.onrender.com` URL and check every section, image, and button.
5. Render → Settings → Custom Domains → add `alwaysbookedai.tech` and `www.alwaysbookedai.tech`.
6. Namecheap → Advanced DNS → delete the GHL web records + AAAA, add `A @ → 216.24.57.1` and `CNAME www → <service>.onrender.com`. **Keep the Zoho MX/TXT rows** (email!).
7. Render → Verify → SSL in ~15–30 min.
8. Then: Search Console, sitemap, GA4, GBP — per the `seo-growth-plan` skill reference.