from pathlib import Path
import re

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

# V4.0: large-screen YouTube-style horizontal content rails.
css = r'''.homeRailSectionV40{position:relative;margin:28px 0 10px}.homeRailHeadV40{display:flex;align-items:end;justify-content:space-between;margin-bottom:14px}.homeRailHeadV40 h2{margin:0;font-size:31px;line-height:1.15}.homeRailHeadV40 span{color:$sub;font-size:15px}.homeRailWrapV40{position:relative}.homeRailV40{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding:2px 56px 12px 1px}.homeRailV40::-webkit-scrollbar{display:none}.homeRailV40 .card{flex:0 0 min(310px,23.5vw);scroll-snap-align:start}.homeRailV40 .ctitle{height:auto;min-height:48px}.homeRailArrowV40{position:absolute;right:7px;top:50%;transform:translateY(-62%);z-index:6;width:52px;height:52px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:$panel;border:1px solid $border;box-shadow:0 8px 24px rgba(0,0,0,.18);font-size:34px;font-weight:500}.homeRailArrowV40:active{transform:translateY(-62%) scale(.96)}.homeRailEmptyV40{padding:18px 20px;border-radius:18px;background:$panel;border:1px solid $border;color:$sub;font-size:17px}.homeIntroV40{display:flex;align-items:center;justify-content:space-between;margin:24px 0 2px}.homeIntroV40 b{font-size:20px}.homeIntroV40 span{color:$sub;font-size:14px}.channelCard{display:block}@media(max-width:1500px){.homeRailV40 .card{flex-basis:285px}.homeRailHeadV40 h2{font-size:28px}}'''
if '.homeRailSectionV40{' not in s:
    s = s.replace('</style><script>', css + "</style><script>function scrollHomeRail(id){var e=document.getElementById(id);if(e)e.scrollBy({left:e.clientWidth*.86,behavior:'smooth'})}", 1)

marker = '    private fun showHome() {'
helper = r'''    private fun homeRailHtmlV40(title: String, meta: String, id: String, items: List<Video>): String {
        if (items.isEmpty()) return ""
        val cards = items.distinctBy { it.id }.take(24).joinToString("") { videoCard(it) }
        return "<section class='homeRailSectionV40'><div class='homeRailHeadV40'><h2>${esc(title)}</h2><span>${esc(meta)}</span></div><div class='homeRailWrapV40'><div class='homeRailV40' id='${escAttr(id)}'>$cards</div><a class='homeRailArrowV40' href=\"javascript:scrollHomeRail('${escAttr(id)}')\">›</a></div></section>"
    }

    private fun homeHistoryVideosV40(): List<Video> {
        val raw = prefs.getString("history", "").orEmpty()
        if (raw.isBlank()) return emptyList()
        val ids = raw.split(',').map { it.trim() }.filter { it.isNotBlank() }
        val known = allKnownVideos()
        return ids.mapNotNull { id -> known.firstOrNull { it.id == id } }.distinctBy { it.id }.take(20)
    }

'''
if 'private fun homeRailHtmlV40' not in s:
    if marker not in s:
        raise SystemExit('v4.0 patch failed: showHome marker missing')
    s = s.replace(marker, helper + marker, 1)

# Replace ONLY showHome. v3.2 inserts categoryQuery/matchesCategory/fetchCategoryAsync
# between showHome and showCategory; preserve those helpers.
pattern = r'    private fun showHome\(\) \{.*?\n    \}\n\n    private fun categoryQuery'
replacement = r'''    private fun showHome() {
        currentVideoId = null
        currentCategory = "推荐"
        val signed = isSignedIn()
        if (signed && !accountLoaded && !accountLoading.get()) refreshAccountData { showHome() }

        val heroSource = when {
            signed && accountHomeVideos.isNotEmpty() -> accountHomeVideos.first()
            signed && accountSubscriptionVideos.isNotEmpty() -> accountSubscriptionVideos.first()
            else -> null
        }
        val hero = if (heroSource != null) Hero(
            "为你精选",
            heroSource.title.take(42),
            "来自你的订阅、点赞与近期频道动态。",
            "https://i.ytimg.com/vi/${heroSource.id}/maxresdefault.jpg",
            heroSource.id,
            heroSource.channel
        ) else heroFor("推荐")

        val history = homeHistoryVideosV40()
        val subs = accountSubscriptionVideos.distinctBy { it.id }
        val likes = accountLikedVideos.distinctBy { it.id }
        val mixed = (accountHomeVideos + accountExtraVideos + accountSubscriptionVideos + accountLikedVideos + videos)
            .distinctBy { it.id }
            .filter { v -> history.none { it.id == v.id } }

        val loading = if (signed && !accountLoaded) "<div class='syncState'>正在同步你的 YouTube 内容，完成后首页会自动补充更多视频。</div>" else ""
        val intro = if (signed) "<div class='homeIntroV40'><b>你的 YouTube</b><span>订阅 · 点赞 · 观看记录</span></div>" else ""
        val rails = buildString {
            append(homeRailHtmlV40("继续观看", "你的车机观看记录", "railHistory", history))
            append(homeRailHtmlV40("订阅频道更新", "来自你订阅的频道", "railSubs", subs))
            append(homeRailHtmlV40("点赞回看", "来自你的 YouTube 点赞", "railLikes", likes))
            append(homeRailHtmlV40(if (signed) "为你探索" else "为你推荐", if (signed) "结合账号内容与精选视频" else "精选内容 · 大屏优化", "railExplore", mixed))
        }
        val body = "<div class='chips'>${chipsHtml("推荐")}</div>$loading${heroHtml(hero)}$intro$rails"
        load(shell("home", body))
    }

    private fun categoryQuery'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'v4.0 patch failed: showHome matches={n}')
s = s2

old = "<div class='channelCard'>${if (c.avatar.isNotBlank()) \"<img src='${escAttr(c.avatar)}'>\" else \"<div class='avatar' style='margin:auto;width:72px;height:72px'></div>\"}<b>${esc(c.title)}</b><span>已订阅</span></div>"
new = "<a class='channelCard' href='c16://channel?name=${Uri.encode(c.title)}'>${if (c.avatar.isNotBlank()) \"<img src='${escAttr(c.avatar)}'>\" else \"<div class='avatar' style='margin:auto;width:72px;height:72px'></div>\"}<b>${esc(c.title)}</b><span>已订阅 · 查看频道 ›</span></a>"
if old in s:
    s = s.replace(old, new, 1)

s = s.replace('C16 YouTube v3.9.1', 'C16 YouTube v4.0')
s = s.replace('v3.9.1.40056', 'v4.0.40057')
s = s.replace('C16 YouTube v3.9', 'C16 YouTube v4.0')
s = s.replace('v3.9.40055', 'v4.0.40057')

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v4.0 large-screen personalized home rails and clickable channel cards')
