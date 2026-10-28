# N&R Auction Gallery

A responsive English/Chinese auction gallery website recreated from the supplied reference, hosted on GitHub Pages.

## Business details

- Website: https://www.nrauctiongallery.com
- Contact: screed@rosesantiques.com
- Mailing address: PO Box 59041, Rockville, MD 20859

## Pages and interactions

The site contains 17 pages: homepage, upcoming auctions, three catalogues, nine lot details, past results, selling, and buying information. Catalogue search and department filters run in the browser. The language switch remembers the visitor's preference.

Valuation and absentee-bid forms validate the entered information and prepare an email addressed to the gallery. Visitors must send the email themselves. The website does not process payments, accept binding bids, or store visitor submissions. A copy option is available if an email application is not configured.

Auction descriptions, images, dates, estimates, and results currently reproduce the supplied reference website. Edit the HTML fragments in `content/` to update inventory. Edit `assets/translations.json` for translations, and `assets/enhancements.css` for additional styling.

## Build and preview

No package installation or build framework is required. The published HTML and assets are ready to serve.

From the GitHub checkout, regenerate pages with:

```sh
python3 scripts/build.py .
python3 -m http.server 4173
```

In the original Codex workspace, output is in `site/`; run `python3 scripts/build.py` and serve that directory.

## Hosting

GitHub Pages publishes the `main` branch root. The `www` DNS CNAME should point directly to `nathancreed2018-blip.github.io`. Configure the custom domain in the repository's Settings → Pages before changing DNS. The `.nojekyll` file disables unnecessary processing. The site uses relative internal URLs and works under a GitHub repository path or custom domain.

The website loads Cormorant Garamond and Karla fonts from Google Fonts. All gallery images and other application assets are included in the repository.
