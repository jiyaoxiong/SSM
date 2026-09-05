from pathlib import Path
import re

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# Normalize the player author row across the accumulated patch chain so V6.2 can
# replace it deterministically. This does not touch the player WebView/IFrame core.
target="<div class='channel'><div class='avatar'></div><a class='channelText' href='c16://category?name=${Uri.encode(v.category)}'><b>${esc(v.channel)}</b><span>点击查看更多相关内容</span></a><a class='subscribe' href='c16://subscriptions'>订阅</a></div>"
pat=r"<div class='channel'>\s*<div class='avatar'[^>]*></div>\s*<a class='channelText'[^>]*>.*?</a>\s*<a class='subscribe'[^>]*>.*?</a>\s*</div>"
s2,n=re.subn(pat,target,s,count=1,flags=re.S)
if n!=1:
    # Some versions add an id/class to the avatar div; use a slightly broader
    # bounded pattern while still requiring the channelText + subscribe row.
    pat2=r"<div class='channel'>.*?<a class='channelText'[^>]*>.*?</a>.*?<a class='subscribe'[^>]*>.*?</a>.*?</div>"
    s2,n=re.subn(pat2,target,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit('v6.2 compat could not locate player channel row')
p.write_text(s2,encoding='utf-8')
print('Normalized player channel row for V6.2')
