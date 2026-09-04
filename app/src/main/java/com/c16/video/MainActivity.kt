package com.android.gallery3d

import android.app.Activity
import android.content.Context
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import java.net.URLDecoder
import java.nio.charset.StandardCharsets

class MainActivity : Activity() {
    private lateinit var root: FrameLayout
    private lateinit var web: WebView
    private var dark = true
    private var fullscreenVideoId: String? = null
    private var inLoginFlow = false
    private val prefs by lazy { getSharedPreferences("c16_v2", Context.MODE_PRIVATE) }

    data class Video(val id: String, val title: String, val channel: String, val meta: String)

    private val videos = listOf(
        Video("linlz7-Pnvw", "Switzerland 4K - Beautiful Nature & Scenic Relaxation", "Scenic Relaxation", "1.2亿次观看 · 3个月前"),
        Video("M7lc1UVf-VE", "YouTube Player Demo · 大屏播放体验", "YouTube Developers", "播放器演示 · 适配 C16"),
        Video("jNQXAC9IVRw", "Me at the zoo · YouTube 经典视频", "YouTube", "经典内容 · 继续观看"),
        Video("kJQP7kiw5Fk", "全球热门音乐 · 沉浸式大屏体验", "Music", "热门音乐 · 推荐"),
        Video("dQw4w9WgXcQ", "经典流行音乐 · 驾乘氛围精选", "Music", "音乐 · 热门"),
        Video("aqz-KE-bpKQ", "Big Buck Bunny · 4K 视频测试", "Blender", "4K · 高清测试"),
        Video("ysz5S6PUM-U", "Sintel · 电影级画质测试", "Blender", "短片 · 画质测试"),
        Video("Scxs7L0vhZ4", "Costa Rica 4K · Tropical Nature", "Scenic Relaxation", "4K HDR · 旅行"),
        Video("L_jWHffIx5E", "Smash Mouth - All Star", "Music", "音乐 · 经典"),
        Video("9bZkp7q19f0", "PSY - GANGNAM STYLE", "Officialpsy", "热门 · 音乐"),
        Video("OPf0YbXqDm0", "Uptown Funk · Bruno Mars", "Mark Ronson", "音乐 · 推荐"),
        Video("RgKAFK5djSk", "See You Again · Wiz Khalifa", "Music", "经典 · 音乐")
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        dark = prefs.getBoolean("dark", true)
        root = FrameLayout(this)
        setContentView(root)
        buildWeb()
        showHome()
    }

    private fun buildWeb() {
        web = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.databaseEnabled = true
            settings.mediaPlaybackRequiresUserGesture = false
            settings.useWideViewPort = true
            settings.loadWithOverviewMode = true
            settings.setSupportZoom(false)
            settings.textZoom = 100
            settings.userAgentString = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            setBackgroundColor(Color.BLACK)
            CookieManager.getInstance().setAcceptCookie(true)
            CookieManager.getInstance().setAcceptThirdPartyCookies(this, true)
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                    val u = request?.url ?: return false
                    if (u.scheme == "c16") {
                        handleRoute(u)
                        return true
                    }
                    return false
                }

                override fun onPageFinished(view: WebView?, url: String?) {
                    super.onPageFinished(view, url)
                    val u = url.orEmpty()
                    if (inLoginFlow && u.contains("youtube.com") && !u.contains("signin") && !u.contains("accounts.google.com")) {
                        inLoginFlow = false
                        CookieManager.getInstance().flush()
                        prefs.edit().putBoolean("login_attempted", true).apply()
                        Toast.makeText(this@MainActivity, "YouTube 登录流程已返回，账号 Cookie 已保存", Toast.LENGTH_LONG).show()
                        showHome()
                    }
                }
            }
            webChromeClient = WebChromeClient()
        }
        root.addView(web, FrameLayout.LayoutParams(-1, -1))
    }

    private fun handleRoute(uri: Uri) {
        when (uri.host) {
            "home" -> showHome()
            "search" -> showSearch(uri.getQueryParameter("q").orEmpty())
            "watch" -> showPlayer(uri.getQueryParameter("id").orEmpty())
            "fullscreen" -> showFullscreen(uri.getQueryParameter("id").orEmpty())
            "history" -> showHistory()
            "favorites" -> showFavorites()
            "subscriptions" -> showSubscriptions()
            "local" -> showLocal()
            "settings" -> showSettings()
            "theme" -> { dark = !dark; prefs.edit().putBoolean("dark", dark).apply(); showHome() }
            "favorite" -> toggleFavorite(uri.getQueryParameter("id").orEmpty())
            "login" -> showLoginPage()
            "loginWeb" -> beginInAppLogin()
        }
    }

    private fun load(html: String) {
        fullscreenVideoId = null
        inLoginFlow = false
        web.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun shell(active: String, body: String, query: String = ""): String {
        val bg = if (dark) "#07111b" else "#f5f7fa"
        val side = if (dark) "#09131d" else "#ffffff"
        val panel = if (dark) "#0d1925" else "#ffffff"
        val panel2 = if (dark) "#142130" else "#edf1f5"
        val text = if (dark) "#f7f9fc" else "#111820"
        val sub = if (dark) "#91a0b2" else "#697583"
        val border = if (dark) "#1c2b39" else "#dfe5eb"
        val activeBg = if (dark) "#8d2f40" else "#ffd7dc"
        val activeText = if (dark) "#ffffff" else "#b21f32"
        fun nav(id: String, icon: String, label: String, host: String) = "<a class='nav ${if (active == id) "on" else ""}' href='c16://$host'><span>$icon</span><b>$label</b></a>"
        val escapedQ = query.replace("'", "&#39;").replace("\"", "&quot;")
        return """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>
        *{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:$bg;color:$text;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC','PingFang SC',Arial,sans-serif}a{text-decoration:none;color:inherit}.app{height:100vh;display:grid;grid-template-columns:315px 1fr;background:$bg}.sidebar{background:$side;border-right:1px solid $border;padding:30px 24px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:16px;height:82px;margin-bottom:25px}.logo{width:66px;height:50px;border-radius:15px;background:#ff1f2d;color:white;display:flex;align-items:center;justify-content:center;font-size:26px}.brandText strong{display:block;font-size:34px;line-height:1.02}.brandText small{display:block;color:$sub;font-size:17px;margin-top:6px}.nav{height:76px;border-radius:18px;display:flex;align-items:center;gap:19px;padding:0 21px;margin:4px 0;color:$text;font-size:25px}.nav span{width:31px;text-align:center;font-size:27px}.nav b{font-weight:650}.nav.on{background:$activeBg;color:$activeText}.main{min-width:0;display:grid;grid-template-rows:112px 1fr}.top{display:flex;align-items:center;padding:20px 32px 16px;gap:16px;border-bottom:1px solid $border;background:$bg}.search{height:70px;flex:1;background:$panel2;border:1px solid $border;border-radius:35px;display:flex;align-items:center;padding:0 24px}.search input{flex:1;background:transparent;border:0;outline:0;color:$text;font-size:25px}.search button{border:0;background:transparent;color:$text;font-size:28px;padding:10px 14px}.pill{height:64px;border-radius:32px;background:$panel2;border:1px solid $border;padding:0 24px;display:flex;align-items:center;justify-content:center;font-size:21px;font-weight:750}.iconBtn{width:64px;height:64px;border-radius:32px;background:$panel2;border:1px solid $border;display:flex;align-items:center;justify-content:center;font-size:27px}.content{overflow:auto;padding:24px 32px 48px;scrollbar-width:none}.content::-webkit-scrollbar{display:none}.sectionTitle{display:flex;align-items:end;justify-content:space-between;margin:30px 0 18px}.sectionTitle h2{font-size:38px;margin:0}.sectionTitle span{font-size:19px;color:$sub}.videoGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:28px 22px}.card{min-width:0}.thumb{position:relative;aspect-ratio:16/9;border-radius:17px;overflow:hidden;background:#111;border:1px solid $border}.thumb img{width:100%;height:100%;object-fit:cover;display:block}.duration{position:absolute;right:9px;bottom:9px;background:rgba(0,0,0,.78);color:#fff;padding:5px 8px;border-radius:7px;font-size:15px}.ctitle{font-size:23px;font-weight:700;line-height:1.36;margin-top:11px;min-height:62px;max-height:62px;overflow:hidden}.cmeta{font-size:18px;line-height:1.45;color:$sub;margin-top:4px}.chips{display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap}.chip{padding:11px 19px;border-radius:20px;background:$panel2;border:1px solid $border;font-size:19px}.chip.on{background:$text;color:$bg;font-weight:750}.discover{height:286px;border-radius:28px;overflow:hidden;border:1px solid $border;display:grid;grid-template-columns:43% 57%;background:$panel;box-shadow:0 18px 50px rgba(0,0,0,.10)}.discoverCopy{padding:34px 38px;display:flex;flex-direction:column;justify-content:center;background:linear-gradient(135deg,${if (dark) "#101f31,#0b1622" else "#ffffff,#eef4f8"})}.eyebrow{font-size:16px;letter-spacing:2.2px;color:#5da8ff;font-weight:800;margin-bottom:12px}.discover h1{font-size:46px;line-height:1.08;margin:0 0 13px}.discover p{font-size:22px;line-height:1.55;color:$sub;margin:0;max-width:680px}.discoverActions{display:flex;gap:12px;margin-top:22px}.discoverBtn{display:inline-flex;padding:12px 21px;border-radius:23px;background:$text;color:$bg;font-size:18px;font-weight:800}.discoverGhost{display:inline-flex;padding:12px 21px;border-radius:23px;background:$panel2;border:1px solid $border;font-size:18px;font-weight:700}.discoverVisual{position:relative;overflow:hidden;background:#000}.discoverVisual img{width:100%;height:100%;object-fit:cover;display:block}.discoverVisual:after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.18),rgba(0,0,0,0) 40%,rgba(0,0,0,.18))}.visualTag{position:absolute;z-index:2;left:24px;bottom:22px;background:rgba(0,0,0,.64);backdrop-filter:blur(8px);color:white;padding:10px 14px;border-radius:14px;font-size:17px;font-weight:700}.result{display:grid;grid-template-columns:410px 1fr;gap:28px;padding:17px 0;border-bottom:1px solid $border}.result img{width:410px;aspect-ratio:16/9;object-fit:cover;border-radius:16px}.rtitle{font-size:28px;font-weight:750;line-height:1.34;margin:5px 0 10px}.rmeta{color:$sub;font-size:19px;line-height:1.55}.empty{background:$panel;border:1px solid $border;border-radius:22px;padding:38px;color:$sub;font-size:24px}.settings{max-width:1100px}.row{min-height:82px;border-bottom:1px solid $border;display:flex;align-items:center;justify-content:space-between;font-size:24px}.row span:last-child{color:$sub}
        .playerPage{display:grid;grid-template-columns:minmax(0,1fr) 620px;gap:30px}.playerCol{min-width:0}.playerBox{position:relative;aspect-ratio:16/9;border-radius:24px;overflow:hidden;background:#000;border:1px solid $border}.playerBox iframe{width:100%;height:100%;border:0}.fullBtn{position:absolute;right:20px;bottom:20px;background:rgba(0,0,0,.76);color:#fff;border:1px solid rgba(255,255,255,.36);padding:14px 20px;border-radius:16px;font-size:25px;font-weight:800}.pTitle{font-size:51px;font-weight:800;line-height:1.24;margin:22px 0 11px}.pMeta{color:$sub;font-size:28px}.channelRow{display:flex;align-items:center;gap:20px;margin-top:24px;padding-bottom:22px;border-bottom:1px solid $border}.avatar{width:78px;height:78px;border-radius:50%;background:linear-gradient(135deg,#3aa0ff,#204b88)}.channelInfo{flex:1}.channelInfo b{display:block;font-size:34px}.channelInfo span{display:block;color:$sub;font-size:25px;margin-top:5px}.subscribe{background:#fff;color:#111;border-radius:30px;padding:15px 27px;font-size:28px;font-weight:800}.actions{display:flex;gap:13px;margin-top:20px;flex-wrap:wrap}.action{background:$panel2;border:1px solid $border;padding:15px 21px;border-radius:27px;font-size:27px}.desc{background:$panel;border:1px solid $border;border-radius:20px;margin-top:21px;padding:22px 24px;color:$sub;line-height:1.68;font-size:26px}.recommend{background:$panel;border:1px solid $border;border-radius:22px;padding:18px}.tabs{display:flex;gap:10px;margin-bottom:19px;flex-wrap:wrap}.tab{padding:11px 17px;border-radius:18px;background:$panel2;font-size:24px}.tab.on{background:#fff;color:#111;font-weight:800}.rec{display:grid;grid-template-columns:220px 1fr;gap:15px;margin-bottom:20px}.rec img{width:220px;aspect-ratio:16/9;object-fit:cover;border-radius:13px}.recTitle{font-size:26px;font-weight:750;line-height:1.28;max-height:68px;overflow:hidden}.recMeta{font-size:21px;color:$sub;margin-top:7px;line-height:1.4}.historyGrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:25px}.progress{height:5px;background:#25303c;position:absolute;left:0;right:0;bottom:0}.progress i{display:block;height:100%;background:#ff2d35}.loginCard{max-width:980px;background:$panel;border:1px solid $border;border-radius:26px;padding:38px}.loginCard h2{font-size:42px;margin:0 0 16px}.loginCard p{font-size:23px;line-height:1.7;color:$sub}.loginButton{display:inline-flex;background:$text;color:$bg;border-radius:30px;padding:16px 27px;font-size:24px;font-weight:800;margin-top:12px}.loginNote{font-size:18px!important;margin-top:22px!important}.loginSteps{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:24px 0}.step{background:$panel2;border:1px solid $border;border-radius:18px;padding:20px}.step b{font-size:26px;display:block;margin-bottom:8px}.step span{font-size:18px;color:$sub;line-height:1.5}@media(max-width:1700px){.app{grid-template-columns:285px 1fr}.playerPage{grid-template-columns:minmax(0,1fr) 540px}.rec{grid-template-columns:190px 1fr}.rec img{width:190px}.videoGrid{grid-template-columns:repeat(4,1fr)}.result{grid-template-columns:370px 1fr}.result img{width:370px}}
        </style><script>function goSearch(){var q=document.getElementById('q').value.trim();if(q)location.href='c16://search?q='+encodeURIComponent(q);return false}</script></head><body><div class='app'><aside class='sidebar'><div class='brand'><div class='logo'>▶</div><div class='brandText'><strong>C16 YouTube</strong><small>Video for a better drive</small></div></div>${nav("home","⌂","首页","home")}${nav("search","⌕","探索","search?q=travel")}${nav("subs","▣","订阅","subscriptions")}${nav("history","◷","历史记录","history")}${nav("favorites","♡","我的收藏","favorites")}${nav("local","▤","本地视频","local")}${nav("settings","⚙","设置","settings")}<div style='flex:1'></div></aside><main class='main'><header class='top'><form class='search' onsubmit='return goSearch()'><input id='q' value='$escapedQ' placeholder='搜索 YouTube，发现更大的世界'><button>⌕</button></form><a class='pill' href='c16://login'>登录</a><a class='iconBtn' href='c16://favorites'>♡</a><a class='iconBtn' href='c16://theme'>${if (dark) "☀" else "☾"}</a></header><section class='content'>$body</section></main></div></body></html>"""
    }

    private fun videoCard(v: Video, history: Boolean = false): String {
        val p = if (history) "<div class='progress'><i style='width:38%'></i></div>" else ""
        return "<a class='card' href='c16://watch?id=${v.id}'><div class='thumb'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><span class='duration'>${if (v.id == "linlz7-Pnvw") "12:36" else "18:24"}</span>$p</div><div class='ctitle'>${v.title}</div><div class='cmeta'>${v.channel}<br>${v.meta}</div></a>"
    }

    private fun showHome() {
        val cards = videos.take(8).joinToString("") { videoCard(it) }
        val body = """<div class='chips'><a class='chip on'>推荐</a><a class='chip' href='c16://search?q=music'>音乐</a><a class='chip' href='c16://search?q=travel'>旅行</a><a class='chip' href='c16://search?q=technology'>科技</a><a class='chip' href='c16://search?q=cars'>汽车</a><a class='chip' href='c16://search?q=food'>美食</a></div><div class='discover'><div class='discoverCopy'><div class='eyebrow'>C16 · IMMERSIVE VIDEO</div><h1>去看更大的世界</h1><p>一块屏幕连接远方，把旅途、音乐与影像变成触手可及的风景。</p><div class='discoverActions'><a class='discoverBtn' href='c16://watch?id=linlz7-Pnvw'>立即播放</a><a class='discoverGhost' href='c16://search?q=travel'>发现更多</a></div></div><a class='discoverVisual' href='c16://watch?id=linlz7-Pnvw'><img src='https://i.ytimg.com/vi/linlz7-Pnvw/maxresdefault.jpg'><div class='visualTag'>Switzerland 4K · Scenic Relaxation</div></a></div><div class='sectionTitle'><h2>为你推荐</h2><span>精选内容 · 大屏优化</span></div><div class='videoGrid'>$cards</div>"""
        load(shell("home", body))
    }

    private fun showSearch(q: String) {
        val decoded = try { URLDecoder.decode(q, StandardCharsets.UTF_8.name()) } catch (_: Exception) { q }
        val pool = if (decoded.lowercase().contains("music")) videos.filter { it.channel.contains("Music", true) || it.title.contains("音乐") } else videos
        val results = pool.take(7).joinToString("") { v -> "<a class='result' href='c16://watch?id=${v.id}'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><div><div class='rtitle'>${v.title}</div><div class='rmeta'>${v.channel} · ${v.meta}</div><div class='rmeta' style='margin-top:12px'>为 C16 大屏优化的视频内容，点击即可进入沉浸式播放页面。</div></div></a>" }
        val body = "<div class='chips'><span class='chip on'>全部</span><span class='chip'>视频</span><span class='chip'>频道</span><span class='chip'>播放列表</span><span class='chip'>电影</span><span class='chip'>直播</span></div>$results"
        load(shell("search", body, decoded))
    }

    private fun showPlayer(id: String) {
        val current = videos.find { it.id == id } ?: videos.first()
        addHistory(current.id)
        val recs = videos.filter { it.id != current.id }.take(6).joinToString("") { v -> "<a class='rec' href='c16://watch?id=${v.id}'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><div><div class='recTitle'>${v.title}</div><div class='recMeta'>${v.channel}<br>${v.meta}</div></div></a>" }
        val fav = prefs.getStringSet("favorites", emptySet()).orEmpty().contains(current.id)
        val body = """<div class='playerPage'><div class='playerCol'><div class='playerBox'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0' allow='autoplay; encrypted-media; picture-in-picture'></iframe><a class='fullBtn' href='c16://fullscreen?id=${current.id}'>⛶ 全屏</a></div><div class='pTitle'>${current.title}</div><div class='pMeta'>${current.meta}　#Travel #4K #C16</div><div class='channelRow'><div class='avatar'></div><div class='channelInfo'><b>${current.channel}</b><span>482万订阅者</span></div><span class='subscribe'>订阅</span></div><div class='actions'><span class='action'>👍 56万</span><span class='action'>👎</span><span class='action'>↗ 分享</span><a class='action' href='c16://favorite?id=${current.id}'>${if (fav) "♥ 已收藏" else "♡ 收藏"}</a><span class='action'>•••</span></div><div class='desc'>播放器使用 YouTube 原生播放能力，界面字号已经按车机观看距离重新放大。全屏切换仍由 C16 YouTube 自己控制，避免退出后黑屏。</div></div><aside class='recommend'><div class='tabs'><span class='tab on'>推荐</span><span class='tab'>相关视频</span><span class='tab'>来自作者</span></div>$recs</aside></div>"""
        load(shell("", body))
    }

    private fun showFullscreen(id: String) {
        val current = videos.find { it.id == id } ?: videos.first()
        fullscreenVideoId = current.id
        val html = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#000}.stage{position:fixed;inset:0;background:#000}.stage iframe{position:absolute;inset:0;width:100%;height:100%;border:0}.back{position:absolute;left:28px;top:24px;z-index:5;background:rgba(0,0,0,.62);color:#fff;border:1px solid rgba(255,255,255,.28);padding:16px 23px;border-radius:26px;font:800 26px sans-serif;text-decoration:none}</style></head><body><div class='stage'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0' allow='autoplay; encrypted-media; picture-in-picture'></iframe><a class='back' href='c16://watch?id=${current.id}'>‹ 返回</a></div></body></html>"""
        web.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun addHistory(id: String) {
        val old = prefs.getString("history", "").orEmpty().split(',').filter { it.isNotBlank() }.toMutableList()
        old.remove(id); old.add(0, id)
        prefs.edit().putString("history", old.take(18).joinToString(",")).apply()
    }

    private fun showHistory() {
        val ids = prefs.getString("history", "").orEmpty().split(',').filter { it.isNotBlank() }
        val list = if (ids.isEmpty()) videos.take(6) else ids.mapNotNull { id -> videos.find { it.id == id } }
        val body = "<div class='sectionTitle'><h2>历史记录</h2><span>继续上次的观看</span></div><div class='historyGrid'>${list.joinToString("") { videoCard(it, true) }}</div>"
        load(shell("history", body))
    }

    private fun toggleFavorite(id: String) {
        val set = prefs.getStringSet("favorites", emptySet())?.toMutableSet() ?: mutableSetOf()
        if (!set.add(id)) set.remove(id)
        prefs.edit().putStringSet("favorites", set).apply()
        showPlayer(id)
    }

    private fun showFavorites() {
        val set = prefs.getStringSet("favorites", emptySet()).orEmpty()
        val list = set.mapNotNull { id -> videos.find { it.id == id } }
        val body = if (list.isEmpty()) "<div class='sectionTitle'><h2>我的收藏</h2></div><div class='empty'>还没有收藏视频。播放视频时点击“收藏”即可加入这里。</div>" else "<div class='sectionTitle'><h2>我的收藏</h2><span>${list.size} 个视频</span></div><div class='videoGrid'>${list.joinToString("") { videoCard(it) }}</div>"
        load(shell("favorites", body))
    }

    private fun showSubscriptions() {
        val body = """<div class='sectionTitle'><h2>订阅</h2><span>你关注的频道</span></div><div class='chips'><span class='chip on'>Scenic Relaxation</span><span class='chip'>The Jazz Hop Café</span><span class='chip'>National Geographic</span><span class='chip'>TED</span></div><div class='videoGrid'>${videos.take(8).joinToString("") { videoCard(it) }}</div>"""
        load(shell("subs", body))
    }

    private fun showLocal() {
        val body = """<div class='sectionTitle'><h2>本地视频</h2><span>车机媒体库</span></div><div class='videoGrid'><div class='empty'>📁 电影<br><small>本地视频分类</small></div><div class='empty'>📁 音乐 MV<br><small>本地视频分类</small></div><div class='empty'>📁 纪录片<br><small>本地视频分类</small></div><div class='empty'>📁 其他<br><small>本地视频分类</small></div></div>"""
        load(shell("local", body))
    }

    private fun showLoginPage() {
        val body = """<div class='loginCard'><h2>在车机内登录 YouTube</h2><p>你的 C16 没有系统浏览器，因此这一版把登录流程直接放回 App 内部。我们会用独立登录页面打开 Google / YouTube，并保存 Cookie；完成后会自动回到 C16 YouTube 首页。</p><div class='loginSteps'><div class='step'><b>① 进入登录</b><span>点击下面按钮，在 App 内打开 Google 登录页。</span></div><div class='step'><b>② 完成验证</b><span>按 Google 提示输入账号、密码和二次验证。</span></div><div class='step'><b>③ 自动返回</b><span>登录跳转回 YouTube 后，App 会保存 Cookie 并回到首页。</span></div></div><a class='loginButton' href='c16://loginWeb'>在车机内打开 Google 登录 ›</a><p class='loginNote'>注意：Google 有时会限制嵌入式 WebView 登录。如果出现“此浏览器或应用可能不安全”，就需要下一阶段接入 Google OAuth 设备码/手机扫码登录；那种方式需要为这个 App 配置一个 OAuth Client ID。</p></div>"""
        load(shell("", body))
    }

    private fun beginInAppLogin() {
        inLoginFlow = true
        fullscreenVideoId = null
        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(web, true)
        web.loadUrl("https://accounts.google.com/ServiceLogin?service=youtube&continue=https%3A%2F%2Fwww.youtube.com%2F")
    }

    private fun showSettings() {
        val body = """<div class='settings'><div class='sectionTitle'><h2>设置</h2><span>C16 YouTube v2.2</span></div><div class='row'><span>主题模式</span><span>${if (dark) "深色" else "浅色"} ›</span></div><div class='row'><span>播放页字号</span><span>超大字版（约 +50%）</span></div><div class='row'><span>视频画质</span><span>自动（推荐） ›</span></div><div class='row'><span>全屏方式</span><span>C16 自定义全屏</span></div><div class='row'><span>账号登录</span><span>App 内 Google 登录</span></div><div class='row'><span>语言</span><span>简体中文 ›</span></div><div class='row'><span>关于 C16 YouTube</span><span>v2.2.40040</span></div></div>"""
        load(shell("settings", body))
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        val full = fullscreenVideoId
        if (full != null) {
            showPlayer(full)
        } else if (inLoginFlow) {
            inLoginFlow = false
            showLoginPage()
        } else if (web.canGoBack()) {
            web.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        CookieManager.getInstance().flush()
        web.destroy()
        super.onDestroy()
    }
}
