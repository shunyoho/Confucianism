# assets/fonts

`lxgw-wenkai-tc-subset.woff2` 是「霞鶩文楷 TC（LXGW WenKai TC）Regular v1.522」的子集，
只含本站標題與經文實際用到的字（約 240 字，60KB），不是完整字型檔。

- 上游：https://github.com/lxgw/LxgwWenkaiTC
- 授權：SIL Open Font License 1.1（見同目錄 OFL.txt，散布時必須一併附上）

## 改過文案之後要重新產生

```
python tools/build-font-subset.py <完整的 LXGWWenKaiTC-Regular.ttf> index.html
```

腳本會掃描 HTML 裡套到楷書的元素（`tools/build-font-subset.py` 的 `KAI_CLASSES`），
重新切出子集。新增頁面就把檔名接在後面一起傳進去。
