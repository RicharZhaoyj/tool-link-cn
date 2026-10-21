---
update: 2026-10-21T09:12:47+08:00
---

# Copy.ai Chat price correction

- Official evidence read 2026-10-21: https://www.copy.ai/prices (the old /pricing URL redirects here). Chat is $29/month, or $288/year equivalent to $24/month; 5 seats. GTM workflow plans are separate. The page does not establish a current lifetime deal.
- Incorrect catalog baseline: CUR-002 showed $36 and a $96 crossed-out reference, no verified billing period. Correct only this product's source record, cached record, homepage/schema/noscript, its detail and existing related cards, and this product's legacy-guide statements. Do not rerun network scraping or change other tools, affiliate configuration, sitemap dates, or site/payment settings.
- The writing category already states $29 monthly / $288 annually and remains unchanged. Homepage order and other tools' older generated content are deliberately preserved, not refreshed incidentally.
- Regression: `python -B -m unittest discover -s tests -p test_copyai_pricing.py -v` (offline). Also check JSON-LD, official direct CTA, no $36/$96 or fake discount in Copy.ai blocks, only CUR-002 differs in tools.json; production GET checks after Git push.
- Traffic baseline: tool.link.cn 7-day sessions 0 versus 13, 30-day 15 versus 13 (windows ending 2026-10-20); tracked tool_click 0 in these windows. No causal connection to pricing is established.
- Hypothesis: explicit billing period and reliable official link remove a misleading purchase signal. Acceptance is correct delivered content preserved by later sync, not a promised traffic uplift. Observe 2026-10-21–2026-11-04; record tool_click and detail-page sessions, treat low sample/no events as inconclusive, and do not stack another Copy.ai conversion experiment during observation. Keep original RSS 10/16–23 and report-logic 10/17–24 windows unchanged.
- Reversal if a regression is verified: revert the isolated correction commit, without resetting the repository or unrelated automation updates. No new domains, payment operations, messages, or pricing for Link's own paid products.
