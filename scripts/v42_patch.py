from pathlib import Path
import re

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

# V4.2: interaction polish for the 14.6-inch C16 screen.
# - two-way rail navigation with larger touch targets
# - better channel rail density
# - stronger player/recommendation balance
# - sticky recommendation controls and calmer metadata
css = r'''.homeRailArrowLeftV42{position:absolute;left:7px;top:50%;transform:translateY(-62%);z-index:7;width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:$panel;border:1px solid $border;box-shadow:0 8px 24px rgba(0,0,0,.20);font-size:38px;font-weight:500}.homeRailArrowLeftV42:active{transform:translateY(-62%) scale(.96)}.homeRailV40{padding-left:58px!important;scroll-padding-left:58px!important}.homeRailArrowV40{z-index:7!important}.channelRailV39{padding:2px 58px 14px!important;gap:18px!important}.channelRailV39 .card{flex:0 0 calc((100% - 72px)/5)!important;min-width:230px!important}.railActionsV39{gap:10px!important}.railArrowLeftV42{width:46px;height:46px;border-radius:50%;background:$panel;border:1px solid $border;display:flex;align-items:center;justify-content:center;font-size:31px;box-shadow:0 6px 18px rgba(0,0,0,.12)}.channelHeroV36{padding:24px 26px!important}.channelHeroV36 .channelText h1{font-size:34px!important}.channelTabsV39{margin-top:12px!important}.app.hideSide .playerPage{grid-template-columns:minmax(0,2.35fr) minmax(470px,1fr)!important;gap:22px!important}.app.hideSide .recommend{max-height:calc(100vh - 116px)!important;border-radius:22px!important}.app.hideSide .recTabs{position:sticky!important;top:0!important;z-index:8!important;padding:4px 0 12px!important;background:$panel!important}.app.hideSide .rec{grid-template-columns:190px minmax(0,1fr)!important;gap:14px!important;padding:5px 0!important}.app.hideSide .rec img{width:190px!important}.app.hideSide .recTitle{font-size:20px!important;line-height:1.28!important;max-height:54px!important}.app.hideSide .recMeta{font-size:14px!important;line-height:1.38!important}.app.hideSide .pTitle{font-size:40px!important;max-width:95%!important}.app.hideSide .pMeta{font-size:18px!important}.app.hideSide .channelInfo b{font-size:25px!important}.app.hideSide .channelInfo span{font-size:16px!important}.app.hideSide .actions{gap:9px!important}.app.hideSide .action{font-size:17px!important;padding:10px 16px!important}.comments{max-width:100%!important}.commentsHead{display:flex!important;align-items:center!important;justify-content:space-between!important}.railSwipeHintV42{font-size:14px;color:$sub;white-space:nowrap}@media(max-width:1500px){.channelRailV39 .card{flex-basis:calc((100% - 54px)/4)!important;min-width:225px!important}.app.hideSide .playerPage{grid-template-columns:minmax(0,2fr) minmax(410px,1fr)!important}.app.hideSide .rec{grid-template-columns:160px minmax(0,1fr)!important}.app.hideSide .rec img{width:160px!important}.app.hideSide .recTitle{font-size:18px!important}}'''
if '.homeRailArrowLeftV42{' not in s:
    s = s.replace('</style><script>', css + '</style><script>', 1)

# Reuse the existing smooth-scroll helpers and add left/right controls for home rails.
if 'function scrollHomeRailV42' not in s:
    js = "function scrollHomeRailV42(id,dir){var e=document.getElementById(id);if(e)e.scrollBy({left:dir*e.clientWidth*.88,behavior:'smooth'})}"
    s = s.replace('</script></head>', js + '</script></head>', 1)

# Replace the V4.0 rail helper with a two-arrow variant. Keep the exact data model intact.
pattern = r'''    private fun homeRailHtmlV40\(title: String, meta: String, id: String, items: List<Video>\): String \{.*?\n    \}\n'''
replacement = '''    private fun homeRailHtmlV40(title: String, meta: String, id: String, items: List<Video>): String {
        if (items.isEmpty()) return ""
        val cards = items.distinctBy { it.id }.take(24).joinToString("") { videoCard(it) }
        return "<section class='homeRailSectionV40'><div class='homeRailHeadV40'><h2>${esc(title)}</h2><span>${esc(meta)}</span></div><div class='homeRailWrapV40'><a class='homeRailArrowLeftV42' href=\\"javascript:scrollHomeRailV42('${escAttr(id)}',-1)\\">‹</a><div class='homeRailV40' id='${escAttr(id)}'>$cards</div><a class='homeRailArrowV40' href=\\"javascript:scrollHomeRailV42('${escAttr(id)}',1)\\">›</a></div></section>"
    }
'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n == 1:
    s = s2
else:
    raise SystemExit(f'v4.2 patch failed: home rail helper matches={n}')

# Upgrade the channel-page rail header to support both directions and make the affordance explicit.
old = "<div class='railHeaderV39'><h2>为你推荐</h2><div class='railActionsV39'><span>${known.size} 个已读取</span><a class='railArrowV39' href=\\\"javascript:scrollRail('channelRail',1)\\\">›</a></div></div>$rail"
new = "<div class='railHeaderV39'><h2>为你推荐</h2><div class='railActionsV39'><span class='railSwipeHintV42'>${known.size} 个已读取 · 横向查看更多</span><a class='railArrowLeftV42' href=\\\"javascript:scrollRail('channelRail',-1)\\\">‹</a><a class='railArrowV39' href=\\\"javascript:scrollRail('channelRail',1)\\\">›</a></div></div>$rail"
if old in s:
    s = s.replace(old, new, 1)
else:
    # Fallback for slightly different escaping after earlier patches.
    s = s.replace("<div class='railHeaderV39'><h2>为你推荐</h2><div class='railActionsV39'><span>${known.size} 个已读取</span>", "<div class='railHeaderV39'><h2>为你推荐</h2><div class='railActionsV39'><span class='railSwipeHintV42'>${known.size} 个已读取 · 横向查看更多</span><a class='railArrowLeftV42' href=\\\"javascript:scrollRail('channelRail',-1)\\\">‹</a>", 1)

# Rename recommendation tabs slightly for clearer touch semantics without changing data behavior.
s = s.replace('>同作者优先</a><a id=\'tabRelated\'', '>同频道优先</a><a id=\'tabRelated\'', 1)

# V4.2 visible labels.
s = s.replace('C16 YouTube v4.1', 'C16 YouTube v4.2')
s = s.replace('v4.1.40058', 'v4.2.40059')

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v4.2 rail navigation, channel density and player recommendation polish')
