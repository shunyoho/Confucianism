"""
從頁面實際用到的字，切出霞鶩文楷 TC 的 subset。

紅線：不要整包載入未 subset 的中文書法字型。所以這支腳本掃描 HTML，
只挑出「會套到楷書」的元素文字（標題、經文、六藝、落款），切成一個 woff2。
改完文案之後重跑一次即可。

用法：
    python tools/build-font-subset.py path/to/LXGWWenKaiTC-Regular.ttf index.html [more.html ...]

字型來源：https://github.com/lxgw/LxgwWenkaiTC （SIL Open Font License 1.1）
"""

import sys
import os
from html.parser import HTMLParser

# 會套到 var(--font-kai) 的 class / 標籤。改 CSS 時記得同步改這裡。
KAI_CLASSES = {
    "kai", "h2", "hero__eyebrow", "dt-row__cls", "datong__close",
    "card__title", "record__term", "chunqiu__lift", "foot__seal", "liuyi",
}
KAI_TAGS = {"h1"}

# 標點與數字一併留著，免得標題裡的「：」「，」掉回備援字型
ALWAYS = set(
    "0123456789"
    "：，。、；？！　／（）「」『』《》〈〉．"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ .,-"
)


class KaiTextCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # 每層是否處在楷書範圍內
        self.chars = set()

    def handle_starttag(self, tag, attrs):
        if tag in ("br", "img", "meta", "link", "input", "hr"):
            return
        classes = set()
        for k, v in attrs:
            if k == "class" and v:
                classes = set(v.split())
        inside = bool(self.stack and self.stack[-1])
        inside = inside or tag in KAI_TAGS or bool(classes & KAI_CLASSES)
        self.stack.append(inside)

    def handle_endtag(self, tag):
        if tag in ("br", "img", "meta", "link", "input", "hr"):
            return
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1]:
            self.chars.update(ch for ch in data if not ch.isspace() or ch == "　")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    ttf, pages = sys.argv[1], sys.argv[2:]
    collector = KaiTextCollector()
    for page in pages:
        with open(page, encoding="utf-8") as fh:
            collector.feed(fh.read())
        collector.stack.clear()

    chars = collector.chars | ALWAYS
    text = "".join(sorted(chars))
    print("楷書字數：%d" % len(chars))
    print(text)

    out_dir = os.path.join("assets", "fonts")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "lxgw-wenkai-tc-subset.woff2")

    from fontTools import subset

    subset.main([
        ttf,
        "--text=%s" % text,
        "--flavor=woff2",
        "--layout-features=*",
        "--no-hinting",
        "--desubroutinize",
        "--output-file=%s" % out,
    ])
    print("%s  %.1f KB" % (out, os.path.getsize(out) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
