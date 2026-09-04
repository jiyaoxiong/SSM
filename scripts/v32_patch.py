from pathlib import Path
import re

path = Path("app/src/main/java/com/c16/video/MainActivity.kt")
s = path.read_text(encoding="utf-8")


def replace(old: str, new: str, label: str):
    global s
    if old not in s:
        raise SystemExit(f"v3.2 patch failed: missing {label}")
    s = s.replace(old, new, 1)


def sub(pattern: str, repl: str, label: str):
    global s
    s2, n = re.subn(pattern, repl, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"v3.2 patch failed: {label} matches={n}")
    s = s2

# Runtime cache for category pages fetched from YouTube search.
replace(
    '    private val accountPlaylists = mutableListOf<YtPlaylist>()\n',
    '    private val accountPlaylists = mutableListOf<YtPlaylist>()\n'
    '    private val categoryVideoCache = mutableMapOf<String, List<Video>>()\n'
    '    @Volatile private var currentCategory = "推荐"\n',
    'category caches',
)

# Include category-fetched videos in the global playable pool.
replace(
    '        (accountExtraVideos + accountSubscriptionVideos + accountLikedVideos + accountHomeVideos + videos).distinctBy { it.id }',
    '        (categoryVideoCache.values.flatten() + accountExtraVideos + accountSubscriptionVideos + accountLikedVideos + accountHomeVideos + videos).distinctBy { it.id }',
    'allKnownVideos category cache',
)

# Add compact vehicle-first styling for the v3.2 approved layout and account center.
replace(
    '</style><script>',
    ".accountCenter{max-width:1120px;margin:0 auto}.profileHero{display:flex;align-items:center;gap:20px;background:$panel;border:1px solid $border;border-radius:24px;padding:24px;margin-bottom:20px}.profileHero img{width:84px;height:84px;border-radius:50%;object-fit:cover;background:$panel2}.profileHero .profileText{flex:1}.profileHero h2{font-size:30px;margin:0 0 6px}.profileHero p{margin:0;color:$sub;font-size:16px}.statGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}.statCard{background:$panel;border:1px solid $border;border-radius:20px;padding:20px}.statCard b{display:block;font-size:32px}.statCard span{display:block;color:$sub;font-size:14px;margin-top:5px}.accountMenu{background:$panel;border:1px solid $border;border-radius:20px;overflow:hidden}.accountMenu a,.accountMenu .accountRow{min-height:66px;padding:0 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid $border;font-size:19px}.accountMenu a:last-child,.accountMenu .accountRow:last-child{border-bottom:0}.categoryEmpty{padding:28px;background:$panel;border:1px solid $border;border-radius:20px;color:$sub;font-size:18px}.chips{position:sticky;top:-20px;z-index:7;padding:4px 0 9px;background:$bg}.chip{min-width:58px;text-align:center}.playerPage{grid-template-columns:minmax(0,1fr) 320px}.recommend{padding:11px}.rec{grid-template-columns:108px 1fr}.rec img{width:108px}.action{min-width:82px;text-align:center}.accountBanner{box-shadow:0 8px 24px rgba(0,0,0,.04)}@media(max-width:1250px){.playerPage{grid-template-columns:minmax(0,1fr) 285px}.statGrid{grid-template-columns:repeat(2,1fr)}}</style><script>",
    'v3.2 CSS',
)

# Add philosophy hero and make the technology copy explicitly AI-focused.
replace(
    '        "科技" -> Hero("EXPLORE THE FUTURE", "科技正在，\\n改变世界。", "探索 AI、数码与未来体验。", "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1800&q=85", "M7lc1UVf-VE", "Tech · Future")',
    '        "科技" -> Hero("AI & TECHNOLOGY", "科技正在，\\n改变世界。", "探索 AI、数码、芯片与未来体验。", "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1800&q=85", "M7lc1UVf-VE", "AI · Tech · Future")',
    'tech hero',
)
replace(
    '        "电影" -> Hero("CINEMA ON THE ROAD", "一块大屏，\\n进入电影世界。", "短片、动画与',
    '        "哲学" -> Hero("THINK DEEPER", "在路上，\\n也可以思考世界。", "哲学、思想、文明、心理与宇宙。", "https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=1800&q=85", "jNQXAC9IVRw", "Philosophy · Ideas")\n        "电影" -> Hero("CINEMA ON THE ROAD", "一块大屏，\\n进入电影世界。", "短片、动画与',
    'philosophy hero insertion',
)

# v3.2 chips: account-driven categories plus Philosophy.
sub(
    r'    private fun chipsHtml\(active: String\): String = listOf\([^\n]+\)\.joinToString\(""\) \{\n        "<a class=\'chip \$\{if \(it == active\) "on" else ""\}\' href=\'c16://category\?name=\$\{Uri\.encode\(it\)\}\'>\$it</a>"\n    \}',
    '''    private fun chipsHtml(active: String): String = listOf("推荐", "音乐", "旅行", "科技", "汽车", "电影", "哲学").joinToString("") {
        "<a class='chip ${if (it == active) "on" else ""}' href='c16://category?name=${Uri.encode(it)}'>$it</a>"
    }''',
    'chips list',
)

# Category keyword matcher + YouTube search fallback so tabs are no longer static test-data filters.
marker = '    private fun showCategory(name: String) {'
helper = r'''    private fun categoryQuery(category: String): String = when (category) {
        "音乐" -> "音乐 live music MV 热门"
        "旅行" -> "旅行 旅游 风景 4K travel"
        "科技" -> "AI 人工智能 科技 数码 芯片 iPhone"
        "汽车" -> "汽车 新能源 Tesla 零跑 试驾"
        "电影" -> "电影 纪录片 短片 cinema"
        "哲学" -> "哲学 思想 文明 心理 宇宙 人生"
        else -> category
    }

    private fun matchesCategory(v: Video, category: String): Boolean {
        if (category == "推荐") return true
        val text = (v.title + " " + v.channel + " " + v.meta + " " + v.category).lowercase()
        val keys = when (category) {
            "音乐" -> listOf("音乐", "music", "song", "live", "remix", "mv", "concert", "funk", "psy")
            "旅行" -> listOf("旅行", "旅游", "travel", "nature", "4k", "风景", "switzerland", "norway", "costa")
            "科技" -> listOf("ai", "人工智能", "科技", "tech", "iphone", "apple", "codex", "obsidian", "模型", "芯片", "电脑", "dlss", "数码")
            "汽车" -> listOf("汽车", "car", "auto", "tesla", "零跑", "bmw", "porsche", "model 3", "cybertruck", "试驾", "新能源")
            "电影" -> listOf("电影", "movie", "film", "cinema", "短片", "blender", "动画", "纪录片")
            "哲学" -> listOf("哲学", "philosophy", "思想", "文明", "心理", "宇宙", "宗教", "佛", "道", "人生", "存在", "认知", "历史")
            else -> listOf(category.lowercase())
        }
        return keys.any { text.contains(it) }
    }

    private fun fetchCategoryAsync(category: String) {
        if (!isSignedIn() || category == "推荐" || categoryVideoCache.containsKey(category)) return
        Thread {
            try {
                val token = ensureAccessToken()
                if (token.isBlank()) return@Thread
                val q = URLEncoder.encode(categoryQuery(category), "UTF-8")
                val url = "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&videoEmbeddable=true&safeSearch=moderate&maxResults=15&q=$q"
                val r = apiGet(url, token)
                if (r.first in 200..299) {
                    val items = JSONObject(r.second).optJSONArray("items")
                    val out = mutableListOf<Video>()
                    if (items != null) for (i in 0 until items.length()) {
                        val item = items.optJSONObject(i) ?: continue
                        val id = item.optJSONObject("id")?.optString("videoId", "").orEmpty()
                        val sn = item.optJSONObject("snippet")
                        if (id.isBlank() || sn == null) continue
                        out.add(Video(id, sn.optString("title", "YouTube 视频"), sn.optString("channelTitle", "YouTube"), "YouTube · $category", category))
                    }
                    if (out.isNotEmpty()) {
                        categoryVideoCache[category] = out.distinctBy { it.id }
                        main.post { if (currentCategory == category) showCategory(category) }
                    }
                }
            } catch (_: Exception) { }
        }.start()
    }

'''
if marker not in s:
    raise SystemExit('v3.2 patch failed: showCategory marker')
s = s.replace(marker, helper + marker, 1)

sub(
    r'    private fun showCategory\(name: String\) \{.*?\n    \}\n\n    private fun showSearch',
    '''    private fun showCategory(name: String) {
        val n = if (name.isBlank()) "推荐" else name
        currentCategory = n
        if (n == "推荐") {
            showHome()
            return
        }
        val accountFirst = (categoryVideoCache[n].orEmpty() + accountHomeVideos + accountLikedVideos + accountSubscriptionVideos + videos)
            .distinctBy { it.id }
            .filter { matchesCategory(it, n) }
        val list = accountFirst.take(20)
        val status = if (categoryVideoCache.containsKey(n)) "来自 YouTube 与你的账号" else "正在结合你的账号内容与 YouTube 搜索"
        val cards = if (list.isEmpty()) "<div class='categoryEmpty'>正在为“${esc(n)}”寻找相关内容…</div>" else "<div class='videoGrid'>${list.joinToString("") { videoCard(it) }}</div>"
        val body = "<div class='chips'>${chipsHtml(n)}</div>${heroHtml(heroFor(n))}<div class='sectionTitle'><h2>${esc(n)}</h2><span>$status</span></div>$cards"
        load(shell("home", body))
        fetchCategoryAsync(n)
    }

    private fun showSearch''',
    'account-aware showCategory',
)

# Make personalized home wording feel like a finished product rather than a debug label.
replace(
    '            "YOUR YOUTUBE",',
    '            "为你精选",',
    'personalized hero eyebrow',
)
replace(
    '            "来自你订阅的频道与点赞内容。",',
    '            "来自你的订阅、点赞与近期频道动态。",',
    'personalized hero copy',
)

# Simplify player controls for a car display while keeping the useful layout toggles.
replace(
    "<div class='actions'><span class='action'>👍 点赞</span><span class='action'>↗ 分享</span><a class='action' href='c16://favorite?id=${current.id}'>${if (fav) \"♥ 已收藏\" else \"♡ 收藏\"}</a><span class='action'>⋯ 更多</span><a class='action' href='javascript:toggleSide()'>☰ 左栏</a><a class='action' href='javascript:toggleRec()'>▥ 推荐</a><a class='action' href='javascript:toggleCinema()'>▣ 影院模式</a>$loginHint</div>",
    "<div class='actions'><span class='action'>👍 点赞</span><a class='action' href='c16://favorite?id=${current.id}'>${if (fav) \"♥ 已收藏\" else \"♡ 收藏\"}</a><a class='action' href='javascript:toggleSide()'>☰ 左栏</a><a class='action' href='javascript:toggleRec()'>▥ 推荐</a><a class='action' href='javascript:toggleCinema()'>▣ 影院模式</a>$loginHint</div>",
    'simplified player actions',
)

# Logged-in account chip opens a real account center instead of showing OAuth credentials again.
sub(
    r'    private fun showLoginCenter\(message: String = ""\) \{.*?\n    \}\n\n    private fun startDeviceLogin',
    r'''    private fun showLoginCenter(message: String = "") {
        val client = prefs.getString("oauth_client_id", "").orEmpty()
        val secret = prefs.getString("oauth_client_secret", "").orEmpty()
        val logged = isSignedIn()
        if (logged) {
            if (!accountLoaded && !accountLoading.get()) refreshAccountData { showLoginCenter() }
            val title = prefs.getString("channel_title", "").orEmpty().ifBlank { "你的 YouTube" }
            val avatar = prefs.getString("channel_avatar", "").orEmpty()
            val avatarHtml = if (avatar.isNotBlank()) "<img src='${escAttr(avatar)}'>" else "<div class='avatar' style='width:84px;height:84px'></div>"
            val body = """<div class='accountCenter'><div class='profileHero'>$avatarHtml<div class='profileText'><h2>${esc(title)}</h2><p>已通过手机授权关联 YouTube 账号</p></div><a class='syncBtn' href='c16://sync'>↻ 同步账号</a></div><div class='statGrid'><div class='statCard'><b>${accountSubscriptions.size}</b><span>订阅频道</span></div><div class='statCard'><b>${accountLikedVideos.size}</b><span>点赞视频</span></div><div class='statCard'><b>${accountPlaylists.size}</b><span>播放列表</span></div><div class='statCard'><b>${prefs.getString("history", "").orEmpty().split(',').count { it.isNotBlank() }}</b><span>车机观看记录</span></div></div><div class='accountMenu'><a href='c16://subscriptions'><span>我的订阅</span><b>›</b></a><a href='c16://favorites'><span>点赞、播放列表与收藏</span><b>›</b></a><a href='c16://history'><span>观看历史</span><b>›</b></a><div class='accountRow'><span>账号同步状态</span><span>${if (accountSyncError.isBlank()) "正常" else esc(accountSyncError.take(80))}</span></div><a href='c16://logout'><span>退出 YouTube 账号</span><b>退出</b></a></div></div>"""
            load(shell("", body))
            return
        }
        val msg = if (message.isNotBlank()) "<p style='color:#d53a47;font-weight:700'>${esc(message)}</p>" else ""
        val body = """<div class='loginWrap'><div class='loginCard'><h2>手机扫码登录 YouTube</h2><p>在手机上完成 Google / YouTube 授权，车机无需输入账号和密码。首次使用请填入 Google Cloud 中为 TV / Limited Input Device 创建的 OAuth Client ID 与 Client Secret。</p>$msg<input class='clientInput' id='client' value='${escAttr(client)}' placeholder='粘贴 OAuth Client ID'><div style='height:12px'></div><input class='clientInput' type='password' id='secret' value='${escAttr(secret)}' placeholder='粘贴 OAuth Client Secret'><a class='loginButton' href='javascript:startQr()'>生成手机登录二维码</a><p style='font-size:15px'>凭据仅保存在车机本地。扫码后在手机上完成 Google 授权即可。</p></div><div class='qrCard'><div style='font-size:56px;margin-top:66px'>▦</div><h2>扫码登录</h2><p>二维码生成后，用手机扫码并完成 YouTube 授权。</p></div></div>"""
        load(shell("", body))
    }

    private fun startDeviceLogin''',
    'account center login function',
)

# Clear category cache when signing out so the next account starts fresh.
replace(
    '        accountLikedVideos.clear(); accountSubscriptionVideos.clear(); accountHomeVideos.clear(); accountExtraVideos.clear(); accountSubscriptions.clear(); accountPlaylists.clear()',
    '        accountLikedVideos.clear(); accountSubscriptionVideos.clear(); accountHomeVideos.clear(); accountExtraVideos.clear(); accountSubscriptions.clear(); accountPlaylists.clear(); categoryVideoCache.clear()',
    'logout category cleanup',
)

s = s.replace("C16 YouTube v3.1", "C16 YouTube v3.2")
s = s.replace("v3.1.40049", "v3.2.40050")

path.write_text(s, encoding="utf-8")
print("Applied C16 YouTube v3.2 vehicle UI, account center and smart category patch")
