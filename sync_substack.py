"""Copy new Substack posts onto the Behold the Falconer website.

Runs on GitHub Actions (see .github/workflows/substack-sync.yml).
Reads the public Substack feed, adds any post the site doesn't have yet to
posts.json as a teaser (opening paragraphs + link to Substack), picks a
section from the post's words (or its Substack tag), and rebuilds index.html.
Existing posts are never changed.
"""
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser

FEED = "https://beholdthefalconer.substack.com/feed"
SKIP = {"coming-soon"}
PERTH = timezone(timedelta(hours=8))
NS = {"content": "http://purl.org/rss/1.0/modules/content/"}

# Words that point to each section. Tag a post on Substack with
# "metaphysics", "power" or "media" to override the automatic choice.
KEYWORDS = {
    "metaphysics": ["god", "soul", "plato", "platonic", "virtue", "providence", "beauty", "faith",
                    "reason", "philosoph", "divine", "logos", "conscience", "eternity", "heaven",
                    "devil", "pray", "spirit", "metaphysic", "truth", "wisdom", "passion", "monk",
                    "christ", "church", "theolog", "meaning", "existence", "manuscript", "desire"],
    "power": ["politic", "society", "institution", "government", "state", "law", "legal", "power",
              "ideolog", "progressive", "conservative", "right-wing", "left-wing", "feminis",
              "generation", "economy", "economic", "culture war", "men and women", "dating",
              "relationship", "marriage", "country", "nation", "authority", "elite", "class"],
    "media": ["film", "cinema", "movie", "poem", "poetry", "fighter", "ufc", "image", "story",
              "myth", "symbol", "television", "social media", "music", "novel", "literature",
              "art", "spectacle", "celebrity", "screen", "narrative"],
}
TAG_MAP = {"metaphysics": "metaphysics", "meaning": "metaphysics", "theology": "metaphysics",
           "philosophy": "metaphysics", "power": "power", "persuasion": "power",
           "politics": "power", "media": "media", "myth": "media", "poetry": "media"}


def classify(title, text, tags):
    for t in tags:
        key = TAG_MAP.get(t.strip().lower())
        if key:
            return key
    blob = (title + " ") * 3 + text
    blob = blob.lower()
    scores = {cat: sum(blob.count(w) for w in words) for cat, words in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "metaphysics"


class Clean(HTMLParser):
    """Keep paragraphs, emphasis, headings and quotes; drop everything else."""
    KEEP = {"p", "em", "i", "strong", "b", "h2", "h3", "blockquote", "br"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    VOID = {"br", "img", "hr", "input", "meta", "source", "link", "wbr"}

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "") or ""
        if self.skip:
            if tag not in self.VOID:
                self.skip += 1
            return
        if tag in ("script", "style", "button", "form", "figure", "svg") or \
                any(k in cls for k in ("button-wrapper", "subscription-widget", "paywall", "captioned-image")):
            if tag not in self.VOID:
                self.skip = 1
            return
        if tag in self.KEEP:
            tag = {"i": "em", "b": "strong", "h3": "h2"}.get(tag, tag)
            self.out.append("<br>" if tag == "br" else f"<{tag}>")

    def handle_endtag(self, tag):
        if self.skip:
            if tag not in self.VOID:
                self.skip -= 1
            return
        if tag in self.KEEP and tag != "br":
            tag = {"i": "em", "b": "strong", "h3": "h2"}.get(tag, tag)
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(html.escape(data, quote=False))


def clean_html(raw):
    c = Clean()
    c.feed(raw or "")
    out = "".join(c.out)
    out = re.sub(r"<p>\s*</p>", "", out)
    out = re.sub(r"<p>\s*Read more\s*</p>", "", out, flags=re.I)
    return out.strip()


def plain(raw):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw or ""))).strip()


def first_sentence(text, limit=240):
    m = re.match(r"(.+?[.?!])(\s|$)", text)
    s = m.group(1) if m else text
    return s if len(s) <= limit else s[:limit].rsplit(" ", 1)[0] + "…"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "beholdthefalconer-sync/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main(feed_path=None):
    posts = json.load(open("posts.json", encoding="utf-8"))
    have = {p["slug"] for p in posts}
    xml = open(feed_path, "rb").read() if feed_path else fetch(FEED)
    root = ET.fromstring(xml)
    added = []
    for item in root.iter("item"):
        link = (item.findtext("link") or "").strip()
        m = re.search(r"/p/([^/?#]+)", link)
        if not m:
            continue
        slug = m.group(1)
        if slug in have or slug in SKIP:
            continue
        title = (item.findtext("title") or "").strip()
        raw = item.findtext("content:encoded", namespaces=NS) or item.findtext("description") or ""
        body = clean_html(raw)
        text = plain(raw)
        if not title or not text:
            continue
        tags = [c.text or "" for c in item.findall("category")]
        date = parsedate_to_datetime(item.findtext("pubDate")).astimezone(PERTH).strftime("%Y-%m-%d")
        sub = (item.findtext("description") or "").strip()
        post = {
            "slug": slug, "title": title, "cat": classify(title, text, tags), "date": date,
            "excerpt": plain(sub) if sub and len(plain(sub)) < 300 and plain(sub) != text else first_sentence(text),
            "body": body, "substack": link,
        }
        posts.insert(0, post)
        have.add(slug)
        added.append(f"{title} -> {post['cat']}")
    if not added:
        print("No new posts.")
        return
    json.dump(posts, open("posts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    page = open("index.html", encoding="utf-8").read()
    data = json.dumps(posts, ensure_ascii=False, indent=1).replace("</", "<\\/")
    page, n = re.subn(r"/\*POSTS_START\*/.*?/\*POSTS_END\*/",
                      lambda _: "/*POSTS_START*/const POSTS = " + data + ";/*POSTS_END*/", page, flags=re.S)
    if n != 1:
        sys.exit("Could not find the POSTS markers in index.html")
    open("index.html", "w", encoding="utf-8").write(page)
    print("Added:\n" + "\n".join(added))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
