#!/usr/bin/env python3
"""重產 index.html（歷史週報目錄）與 latest.html（永遠導到最新一期）。
每次新增 kol_weekly_XXX.html 後跑一次：python3 scripts/build_index.py
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def read_issue(path):
    text = path.read_text(encoding="utf-8")
    number = re.search(r"kol_weekly_(\d{3})\.html", path.name).group(1)
    date = re.search(r"(\d{4}) · (\d{2}) · (\d{2}) 發布", text)
    hero = re.search(r'lede-hero">(.*?)</div>', text, re.S)
    headline = ""
    if hero:
        headline = re.sub(r"<[^>]+>", "", html.unescape(hero.group(1)))
        headline = re.sub(r"\s+", " ", headline).strip()
    return {
        "number": number,
        "file": path.name,
        "date": f"{date.group(1)}/{date.group(2)}/{date.group(3)}" if date else "",
        "headline": headline,
    }


issues = sorted(
    (read_issue(p) for p in ROOT.glob("kol_weekly_[0-9][0-9][0-9].html")),
    key=lambda issue: issue["number"],
    reverse=True,
)
latest = issues[0]

VISIBLE_COUNT = 6  # 嵌入 Google Sites 的框高度固定，只顯示最近幾期，其餘收進「更早的期數」


def render_row(issue):
    is_latest = issue is latest
    return f'''    <a class="row{' latest' if is_latest else ''}" href="{issue['file']}" target="_top">
      <span class="num">#{issue['number']}</span>
      <span class="date">{issue['date']}</span>
      <span class="head">{html.escape(issue['headline'])}</span>
      {'<span class="tag">本週</span>' if is_latest else ''}
    </a>'''


recent_rows = "\n".join(render_row(issue) for issue in issues[:VISIBLE_COUNT])
older_issues = issues[VISIBLE_COUNT:]
older_block = (
    f'''  <details class="older">
    <summary>看更早的 {len(older_issues)} 期</summary>
{"\n".join(render_row(issue) for issue in older_issues)}
  </details>'''
    if older_issues
    else ""
)
rows = recent_rows + "\n" + older_block

index_html = f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KOL Weekly Pulse｜Cofit 網紅中心週報</title>
<style>
  :root {{ --dark:#004f51; --green:#168e6b; --orange:#ffb46e; --yellow:#ffea85; --ink:#1f2a2a; --mute:#5f6b6b; --line:#e3e8e6; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:#f7f8f6; color:var(--ink); font-family:"PingFang TC","Noto Sans TC",sans-serif; }}
  .wrap {{ max-width:760px; margin:0 auto; padding:32px 16px 48px; }}
  h1 {{ margin:0 0 4px; font-size:24px; color:var(--dark); }}
  .sub {{ margin:0 0 24px; color:var(--mute); font-size:14px; }}
  .cta {{ display:inline-block; margin-bottom:24px; padding:10px 18px; border-radius:999px; background:var(--dark); color:#fff; text-decoration:none; font-weight:700; transition:background .2s; }}
  .cta:hover {{ background:var(--green); }}
  .row {{ display:grid; grid-template-columns:56px 96px 1fr auto; gap:12px; align-items:center; padding:14px 16px; margin-bottom:8px; background:#fff; border:1px solid var(--line); border-radius:12px; color:inherit; text-decoration:none; transition:border-color .2s, transform .2s; }}
  .row:hover {{ border-color:var(--green); transform:translateY(-1px); }}
  .row.latest {{ border-color:var(--orange); }}
  .num {{ font-weight:800; color:var(--dark); }}
  .date {{ color:var(--mute); font-size:13px; }}
  .head {{ font-size:14px; line-height:1.5; }}
  .tag {{ background:var(--yellow); color:var(--dark); font-size:12px; font-weight:700; padding:2px 8px; border-radius:8px; }}
  .older summary {{ cursor:pointer; padding:10px 4px; color:var(--dark); font-weight:700; font-size:14px; }}
  .older summary:hover {{ color:var(--green); }}
  @media (max-width:560px) {{ .row {{ grid-template-columns:48px 1fr auto; }} .date {{ display:none; }} }}
</style>
</head>
<body>
<div class="wrap">
  <h1>網紅中心週報 KOL Weekly Pulse</h1>
  <p class="sub">每週二發布 · 共 {len(issues)} 期 · 最新一期 #{latest['number']}（{latest['date']}）</p>
  <a class="cta" href="{latest['file']}" target="_top">▸ 看本週 #{latest['number']}</a>
{rows}
</div>
</body>
</html>
'''

latest_html = f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={latest['file']}">
<title>KOL Weekly Pulse #{latest['number']}</title>
</head>
<body><a href="{latest['file']}">前往最新一期 #{latest['number']}</a></body>
</html>
'''

(ROOT / "index.html").write_text(index_html, encoding="utf-8")
(ROOT / "latest.html").write_text(latest_html, encoding="utf-8")
print(f"index.html / latest.html → #{latest['number']}（共 {len(issues)} 期）")
