from pathlib import Path

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

# V3.5 defaults to the approved dark car UI on a clean install.
s = s.replace('dark = prefs.getBoolean("dark", false)', 'dark = prefs.getBoolean("dark", true)', 1)

# Runtime state for smarter current-video recommendations.
if 'private var currentCategory = "推荐"' in s and 'relatedVideoCache' not in s:
    s = s.replace(
        '    @Volatile private var currentCategory = "推荐"\n',
        '    @Volatile private var currentCategory = "推荐"\n'
        '    private val relatedVideoCache = mutableMapOf<String, List<Video>>()\n',
        1,
    )

# New driving-mode entry point.
if '"drive" -> showDrivingMode()' not in s:
    s = s.replace('            "home" -> showHome()\n', '            "home" -> showHome()\n            "drive" -> showDrivingMode()\n', 1)

# Approved category order. Keep internal key "科技" so existing API matching still works,
# but present it to the user as "科技AI".
old_chips = '''    private fun chipsHtml(active: String): String = listOf("推荐", "音乐", "旅行", "科技", "汽车", "电影", "哲学").joinToString("") {
        "<a class='chip ${if (it == active) "on" else ""}' href='c16://category?name=${Uri.encode(it)}'>$it</a>"
    }'''
new_chips = '''    private fun chipsHtml(active: String): String = listOf(
        "推荐" to "推荐", "科技" to "科技AI", "汽车" to "汽车", "音乐" to "音乐",
        "旅行" to "旅行", "电影" to "电影", "哲学" to "哲学"
    ).joinToString("") { (key, label) ->
        "<a class='chip ${if (key == active) "on" else ""}' href='c16://category?name=${Uri.encode(key)}'>$label</a>"
    }'''
if old_chips in s:
    s = s.replace(old_chips, new_chips, 1)

# More content per screen: categories/search/home/subscriptions/favorites can scroll down
# instead of stopping after one or two rows.
s = s.replace('maxResults=15&q=$q', 'maxResults=40&q=$q', 1)
s = s.replace('val list = accountFirst.take(20)', 'val list = accountFirst.take(36)', 1)
s = s.replace('val personalized = if (signed && accountHomeVideos.isNotEmpty()) accountHomeVideos.take(10) else videos.take(10)',
              'val personalized = if (signed && accountHomeVideos.isNotEmpty()) accountHomeVideos.take(24) else allKnownVideos().take(20)', 1)
s = s.replace('val results = pool.take(12).joinToString("")', 'val results = pool.take(30).joinToString("")', 1)
s = s.replace('likes.take(15).joinToString("")', 'likes.take(30).joinToString("")', 1)
s = s.replace('accountSubscriptionVideos.take(15).joinToString("")', 'accountSubscriptionVideos.take(30).joinToString("")', 1)

# The v3.3 patch hid recommendation scrolling. Restore a scrollable recommendation rail.
s = s.replace('height:calc(100vh - 160px);overflow:hidden;scrollbar-width:none',
              'max-height:calc(100vh - 132px);overflow:auto;scrollbar-width:none', 1)

# Make the category heading read 科技AI, while the API still uses the internal 科技 key.
s = s.replace('<div class=\'sectionTitle\'><h2>${esc(n)}</h2><span>$status</span></div>',
              '<div class=\'sectionTitle\'><h2>${esc(if (n == "科技") "科技AI" else n)}</h2><span>$status</span></div>', 1)

# Smart recommendation scoring: same channel first, then same inferred category, then shared
# high-value topic keywords. This prevents a technology video from getting a philosophy-only rail.
player_marker = '    private fun showPlayer(id: String) {'
if player_marker in s and 'private fun relatedVideos(current: Video)' not in s:
    helper = '''    private fun inferredCategory(v: Video): String {
        val ordered = listOf("科技", "汽车", "音乐", "旅行", "电影", "哲学")
        return ordered.firstOrNull { matchesCategory(v, it) } ?: v.category
    }

    private fun relatedVideos(current: Video): List<Video> {
        relatedVideoCache[current.id]?.let { return it }
        val currentCategory = inferredCategory(current)
        val currentTitle = current.title.lowercase()
        val topicKeys = listOf(
            "ai", "人工智能", "npu", "芯片", "电脑", "iphone", "apple", "科技", "数码",
            "汽车", "新能源", "tesla", "零跑", "音乐", "music", "旅行", "travel", "4k",
            "电影", "film", "哲学", "philosophy", "宇宙", "心理", "思想"
        )
        val sorted = allKnownVideos().filter { it.id != current.id }.sortedWith(
            compareByDescending<Video> { v ->
                var score = 0
                if (v.channel.equals(current.channel, ignoreCase = true)) score += 60
                if (inferredCategory(v) == currentCategory) score += 36
                val candidateTitle = v.title.lowercase()
                score += topicKeys.count { currentTitle.contains(it) && candidateTitle.contains(it) } * 10
                if (v.category == current.category) score += 8
                score
            }.thenBy { it.title }
        ).take(12)
        relatedVideoCache[current.id] = sorted
        return sorted
    }

'''
    s = s.replace(player_marker, helper + player_marker, 1)

s = s.replace(
    '        val recs = allKnownVideos().filter { it.id != current.id }.take(8).joinToString("") { v ->',
    '        val recs = relatedVideos(current).joinToString("") { v ->',
    1,
)

# Add the approved V3.5 driving-mode visual language.
if '.driveMode{' not in s:
    css = ".driveMode{max-width:1480px;margin:0 auto}.driveHero{position:relative;min-height:260px;border-radius:28px;overflow:hidden;margin-bottom:20px;background:linear-gradient(120deg,#07111d,#12375a);border:1px solid $border}.driveHero:after{content:'';position:absolute;inset:0;background:radial-gradient(circle at 78% 35%,rgba(77,160,255,.28),transparent 35%)}.driveHeroText{position:relative;z-index:2;padding:38px 42px;max-width:720px}.driveHeroText .eyebrow{font-size:14px}.driveHeroText h1{margin:8px 0 10px;font-size:46px;line-height:1.08}.driveHeroText p{margin:0;color:$sub;font-size:20px;line-height:1.5}.driveGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.driveTile{min-height:150px;border-radius:24px;padding:24px;background:$panel;border:1px solid $border;display:flex;flex-direction:column;justify-content:flex-end;position:relative;overflow:hidden}.driveTile:after{content:'';position:absolute;right:-34px;top:-50px;width:180px;height:180px;border-radius:50%;background:rgba(73,145,255,.12)}.driveTile b{font-size:30px;position:relative;z-index:2}.driveTile span{font-size:17px;color:$sub;margin-top:6px;position:relative;z-index:2}.driveQuick{display:flex;gap:10px;margin-top:18px;flex-wrap:wrap}.driveQuick a{padding:12px 18px;border-radius:24px;background:$panel;border:1px solid $border;font-size:18px;font-weight:750}@media(max-width:1250px){.driveGrid{grid-template-columns:1fr 1fr}.driveHeroText h1{font-size:40px}}"
    s = s.replace('</style><script>', css + '</style><script>', 1)

# Add a dedicated Driving Mode page and wire it into the sidebar.
home_marker = '    private fun showHome() {'
if home_marker in s and 'private fun showDrivingMode()' not in s:
    drive_func = '''    private fun showDrivingMode() {
        currentVideoId = null
        val body = """<div class='driveMode'><div class='driveHero'><div class='driveHeroText'><div class='eyebrow'>DRIVING MODE</div><h1>更少操作，更多内容。</h1><p>为 C16 横屏和行车场景优化的大按钮入口。选择一个主题即可开始浏览。</p><div class='driveQuick'><a href='c16://home'>返回首页</a><a href='c16://favorites'>我的收藏</a><a href='c16://history'>观看记录</a></div></div></div><div class='driveGrid'><a class='driveTile' href='c16://category?name=汽车'><b>汽车资讯</b><span>新能源 · 智能驾驶 · 车型体验</span></a><a class='driveTile' href='c16://category?name=科技'><b>AI 每日精选</b><span>人工智能 · 芯片 · 数码科技</span></a><a class='driveTile' href='c16://category?name=音乐'><b>精选音乐</b><span>让旅途更有节奏</span></a><a class='driveTile' href='c16://category?name=旅行'><b>世界旅行</b><span>风景 · 4K · 纪录片</span></a></div></div>"""
        load(shell("drive", body))
    }

'''
    s = s.replace(home_marker, drive_func + home_marker, 1)

nav_old = '${nav("home","⌂","首页","home")}${nav("search","⌕","探索","search?q=travel")}'
nav_new = '${nav("home","⌂","首页","home")}${nav("drive","▣","驾驶模式","drive")}${nav("search","⌕","探索","search?q=travel")}'
s = s.replace(nav_old, nav_new, 1)

# Give the v2.8 SVG navigation helper a dedicated car/drive icon.
if '"drive" -> "<svg' not in s:
    s = s.replace(
        '                "search" -> "<svg viewBox=\'0 0 24 24\'><circle cx=\'10.8\' cy=\'10.8\' r=\'6.2\'/><path d=\'m15.4 15.4 5 5\'/></svg>"',
        '                "drive" -> "<svg viewBox=\'0 0 24 24\'><path d=\'M5 15.5h14l-1.4-5.2a2 2 0 0 0-1.9-1.5H8.3a2 2 0 0 0-1.9 1.5z\'/><path d=\'M4 15.5v2.5M20 15.5v2.5M7.5 15.5h.1M16.4 15.5h.1\'/></svg>"\n                "search" -> "<svg viewBox=\'0 0 24 24\'><circle cx=\'10.8\' cy=\'10.8\' r=\'6.2\'/><path d=\'m15.4 15.4 5 5\'/></svg>"',
        1,
    )

# V3.5 visible labels.
s = s.replace('C16 YouTube v3.3', 'C16 YouTube v3.5')
s = s.replace('v3.3.40051', 'v3.5.40052')
s = s.replace('C16 YouTube v3.2', 'C16 YouTube v3.5')
s = s.replace('v3.2.40050', 'v3.5.40052')

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v3.5 driving mode, category scrolling and smart recommendation patch')
