# 8月冬眠中｜365日の詩

poem.knittinghiyori.com 的網站檔案（GitHub Pages）。

- `poems.json`：所有詩的內容（日中英），新增詩只改這裡
- `build.py`：讀 poems.json，產生首頁、每首詩的頁面、預覽圖、sitemap
- `icons/`、`site.webmanifest`：網站圖示（編織日和）
- `CNAME`：自訂網域，請勿刪除

## 每首詩的製作流程

1. 把 `poems.json` 加上新詩（日中英）
2. `python3 build.py` 產生網站頁面
3. `python3 tools/make_images.py 0102` 產生三張 X 圖（輸出到 out/，不用上傳 GitHub）
