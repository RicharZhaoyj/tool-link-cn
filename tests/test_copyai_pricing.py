"""Offline regression checks for the official Copy.ai Chat pricing correction.
update: 2026-10-21
"""
import ast
import json
import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_static
import build_tool_pages


class CopyAiPricing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tools = json.loads((ROOT / "tools.json").read_text(encoding="utf-8"))
        cls.tool = next(x for x in cls.tools if x["id"] == "CUR-002")
        cls.home = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.detail = (ROOT / "tools/cur-002-copy-ai.html").read_text(encoding="utf-8")

    def test_next_sync_preserves_verified_record(self):
        tree = ast.parse((ROOT / "update.py").read_text(encoding="utf-8"))
        fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "get_manual_curated_deals")
        curated = ast.literal_eval(next(x.value for x in fn.body if isinstance(x, ast.Return)))
        self.assertEqual(self.tool, next(x for x in curated if x["id"] == "CUR-002"))

    def test_annual_and_monthly_not_lifetime_or_discount(self):
        self.assertEqual(self.tool["price"], "$24")
        self.assertEqual(self.tool["priceSuffix"], "/月起（年付）")
        self.assertEqual(self.tool["pricingModel"], "订阅")
        self.assertEqual(self.tool["originalPrice"], "")
        for value in ("$29", "$288", "5席位", "2026-10-21", "并非终身买断"):
            self.assertIn(value, self.tool["pricingNote"])
        self.assertIsNone(build_static.get_discount(self.tool["price"], self.tool["originalPrice"]))

    def test_home_live_and_noscript_cards(self):
        self.assertNotIn("$36", self.home)
        self.assertNotIn("$96", self.home)
        self.assertIn("SEO_NOSCRIPT_START", self.home)
        self.assertEqual(self.home.count("https://www.copy.ai/prices"), 3)
        self.assertEqual(self.home.count("/月起（年付）"), 2)
        self.assertIn('data-tool-id="CUR-002"', self.home)

    def test_jsonld_home_and_detail(self):
        for html in (self.home, self.detail):
            data = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
            self.assertGreater(len(data), 0)
            records = [r["item"] for x in data if x.get("@type") == "ItemList" for r in x["itemListElement"]]
            records += [x for x in data if x.get("@type") == "SoftwareApplication"]
            copy = next(x for x in records if x.get("name") == "Copy.ai")
            self.assertEqual(float(copy["offers"]["price"]), 24)
            self.assertEqual(copy["url"], "https://www.copy.ai/prices")

    def test_detail_and_cta(self):
        for value in ("$24", "$29", "$288", "订阅方案", "并非终身买断"):
            self.assertIn(value, self.detail)
        self.assertNotIn("$36", self.detail)
        self.assertNotIn("$96", self.detail)
        self.assertIn('href="https://www.copy.ai/prices" target="_blank" rel="nofollow noopener" data-growth-event="tool_click"', self.detail)
        self.assertEqual(build_tool_pages.get_cta(self.tool, {})[0], self.tool["url"])

    def test_related_cards_do_not_retain_old_price(self):
        real = [x for x in self.tools if x["id"] != "SYNC-INFO"]
        checked = 0
        for t in real:
            if any(x["id"] == "CUR-002" for x in build_tool_pages.get_related_tools(t, real)):
                html = (ROOT / "tools" / build_tool_pages.make_filename(t)).read_text(encoding="utf-8")
                card = re.search(r'<a href="cur-002-copy-ai.html".*?</a>', html, re.S).group(0)
                self.assertIn("$24", card)
                self.assertIn("年付$288", card)
                self.assertNotIn("$36", card)
                checked += 1
        self.assertEqual(checked, 16)

    def test_legacy_guide_no_copyai_ltd_claim(self):
        html = (ROOT / "guides/best-ai-writing-ltd.html").read_text(encoding="utf-8")
        section = html.split('<h2 id="copyai">')[1].split('<h2 id="writesonic">')[0]
        for value in ("$29/月", "$288/年", "未核验到在售LTD", "https://www.copy.ai/prices"):
            self.assertIn(value, section)
        self.assertNotIn("$299", section)
        self.assertNotIn("Copy.ai LTD Tier", html)
        self.assertNotIn("<td>Copy.ai</td><td>$2940", html)

    def test_only_existing_tool_count_and_slug(self):
        self.assertEqual(len(self.tools), 55)
        self.assertEqual(len({x["id"] for x in self.tools}), 55)
        self.assertEqual(build_tool_pages.make_filename(self.tool), "cur-002-copy-ai.html")


if __name__ == "__main__":
    unittest.main(verbosity=2)
