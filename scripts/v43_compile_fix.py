from pathlib import Path

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')
old = ';val menu=if(c)"›" else "‹"'
new = '\n        val menu = if (c) "›" else "‹"'
if old not in s:
    raise SystemExit('v4.3 compile-fix target not found')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
print('Applied V4.3 Kotlin compile fix')
