from pathlib import Path

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')
old = "<div id='ytPlayer'></div><span class='quality'>4K · HDR</span>"
new = "<div id='ytPlayer'></div><script src='https://www.youtube.com/iframe_api'></script><script>initC16Player('${current.id}')</script><span class='quality'>4K · HDR</span>"
if old not in s:
    raise SystemExit('v3.6 player init fix failed: target not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v3.6 player initialization fix')
