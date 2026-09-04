from pathlib import Path
import re

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

# V3.7: when playback hides the left sidebar, let the main area truly occupy the full
# vehicle display. The previous grid could collapse to a narrow column on the C16 emulator.
css = r'''.app.hideSide{display:block!important;width:100vw!important;height:100vh!important}.app.hideSide .sidebar{display:none!important}.app.hideSide .main{display:grid!important;grid-template-rows:90px 1fr!important;width:100vw!important;height:100vh!important;min-width:0!important}.app.hideSide .top{width:100%!important}.app.hideSide .content{width:100%!important;max-width:none!important;overflow-y:auto!important;padding:18px 26px 46px!important}.app.hideSide .playerPage{width:100%!important;max-width:none!important;grid-template-columns:minmax(0,2.05fr) minmax(440px,1fr)!important;gap:22px!important}.app.hideSide .playerCol{min-width:0!important}.app.hideSide .recommend{width:100%!important;max-width:none!important;max-height:calc(100vh - 122px)!important;padding:17px!important}.app.hideSide .rec{grid-template-columns:172px minmax(0,1fr)!important;gap:13px!important;margin-bottom:16px!important}.app.hideSide .rec img{width:172px!important;border-radius:12px!important}.app.hideSide .recTitle{font-size:19px!important;line-height:1.32!important;max-height:52px!important}.app.hideSide .recMeta{font-size:14px!important;line-height:1.42!important}.app.hideSide .recTabs{position:sticky;top:0;z-index:3;background:$panel;padding:0 0 10px;margin-bottom:8px!important}.app.hideSide .tab{font-size:16px!important;padding:9px 15px!important}.app.hideSide .pTitle{font-size:39px!important;line-height:1.16!important}.app.hideSide .channelRow{margin-top:16px!important}.app.hideSide .comments{margin-top:18px!important}.sidePeek{width:46px!important;height:82px!important;font-size:25px!important;box-shadow:0 8px 24px rgba(0,0,0,.22)}.homeMoreHint{display:flex;align-items:center;justify-content:center;margin:24px 0 2px;color:$sub;font-size:16px}.homeMoreHint span{background:$panel;border:1px solid $border;border-radius:22px;padding:10px 18px}@media(max-width:1500px){.app.hideSide .playerPage{grid-template-columns:minmax(0,1.8fr) minmax(390px,1fr)!important}.app.hideSide .rec{grid-template-columns:150px minmax(0,1fr)!important}.app.hideSide .rec img{width:150px!important}.app.hideSide .pTitle{font-size:34px!important}}'''
if '.homeMoreHint{' not in s:
    s = s.replace('</style><script>', css + '</style><script>', 1)

# Keep the home page clean: remove the large account status banner that sat between
# categories and the Hero. Account details remain available by tapping the avatar/name.
pattern = r'(    private fun showHome\(\) \{.*?\n    \}\n\n    private fun showCategory)'
m = re.search(pattern, s, flags=re.S)
if not m:
    raise SystemExit('v3.7 ui fix failed: showHome block not found')
block = m.group(1)
block2 = block.replace('${accountBannerHtml()}', '').replace('$loading', '')
# Load enough personalized cards for several rows; the content area scrolls vertically.
block2 = block2.replace('accountHomeVideos.take(24)', 'accountHomeVideos.take(40)')
block2 = block2.replace('allKnownVideos().take(20)', 'allKnownVideos().take(35)')
block2 = block2.replace('订阅动态 + 点赞内容', '订阅动态 + 点赞内容 · 向下滑查看更多')
# Add a visible bottom hint after the video grid without changing the actual data model.
old_tail = "${personalized.joinToString(\"\") { videoCard(it) }}</div>\""
new_tail = "${personalized.joinToString(\"\") { videoCard(it) }}</div><div class='homeMoreHint'><span>↓ 向下滑查看更多视频</span></div>\""
if old_tail in block2:
    block2 = block2.replace(old_tail, new_tail, 1)
s = s[:m.start()] + block2 + s[m.end():]

# Give the recommendation tabs clearer intent on the player page.
s = s.replace("<span class='tab on'>同作者优先</span><span class='tab'>相关内容</span>",
              "<span class='tab on'>同作者优先</span><span class='tab'>相关推荐</span>", 1)

# Player page already requests same-author videos in v3.6; load more from that author so
# the rail stays useful while the user scrolls.
s = s.replace('order=date&maxResults=20&channelId=', 'order=date&maxResults=30&channelId=', 1)

# Make comment copy clearer and keep it explicitly read-only for a car screen.
s = s.replace("<div class='commentsHead'><span>评论</span><span class='muted'>公开评论 · 只读</span></div>",
              "<div class='commentsHead'><span>评论</span><span class='muted'>YouTube 公开评论 · 车机只读</span></div>", 1)

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v3.7 full-width playback and clean home feed UI fix')
