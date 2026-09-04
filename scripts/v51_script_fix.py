from pathlib import Path

p=Path('scripts/v51_patch.py')
s=p.read_text(encoding='utf-8')
old=".driveQuick51 a{padding:10px 15px;border-radius:18px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);color:#fff;font-weight:800}\"\nif css_anchor"
new=".driveQuick51 a{padding:10px 15px;border-radius:18px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);color:#fff;font-weight:800}\"\"\"\nif css_anchor"
if old not in s:
    raise SystemExit('v5.1 script quote target missing')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('Fixed V5.1 patch script quoting')
