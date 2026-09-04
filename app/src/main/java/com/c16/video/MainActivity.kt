package com.android.gallery3d

import android.app.Activity
import android.content.Context
import android.content.Intent
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
            "theme" -> {
                dark = !dark
                prefs.edit().putBoolean("dark", dark).apply()
                showHome()
            }
            "favorite" -> toggleFavorite(uri.getQueryParameter("id").orEmpty())
            "login" -> showLoginPage()
            "loginExternal" -> openExternalLogin()
        }
    }

    private fun load(html: String) {
        fullscreenVideoId = null
        web.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun shell(active: String, body: String, query: String = ""): String {
        val bg = if (dark) "#07111b" else "#f4f7fa"
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
        *{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:$bg;color:$text;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC','PingFang SC',Arial,sans-serif}a{text-decoration:none;color:inherit}.app{height:100vh;display:grid;grid-template-columns:315px 1fr;background:$bg}.sidebar{background:$side;border-right:1px solid $border;padding:30px 24px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:16px;height:82px;margin-bottom:25px}.logo{width:66px;height:50px;border-radius:15px;background:#ff1f2d;color:white;display:flex;align-items:center;justify-content:center;font-size:26px}.brandText strong{display:block;font-size:34px;line-height:1.02}.brandText small{display:block;color:$sub;font-size:17px;margin-top:6px}.nav{height:76px;border-radius:18px;display:flex;align-items:center;gap:19px;padding:0 21px;margin:4px 0;color:$text;font-size:25px}.nav span{width:31px;text-align:center;font-size:27px}.nav b{font-weight:650}.nav.on{background:$activeBg;color:$activeText}.main{min-width:0;display:grid;grid-template-rows:112px 1fr}.top{display:flex;align-items:center;padding:20px 32px 16px;gap:16px;border-bottom:1px solid $border;background:$bg}.search{height:70px;flex:1;background:$panel2;border:1px solid $border;border-radius:35px;display:flex;align-items:center;padding:0 24px}.search input{flex:1;background:transparent;border:0;outline:0;color:$text;font-size:25px}.search button{border:0;background:transparent;color:$text;font-size:28px;padding:10px 14px}.pill{height:64px;border-radius:32px;background:$panel2;border:1px solid $border;padding:0 24px;display:flex;align-items:center;justify-content:center;font-size:21px;font-weight:750}.iconBtn{width:64px;height:64px;border-radius:32px;background:$panel2;border:1px solid $border;display:flex;align-items:center;justify-content:center;font-size:27px}.content{overflow:auto;padding:24px 32px 48px;scrollbar-width:none}.content::-webkit-scrollbar{display:none}.sectionTitle{display:flex;align-items:end;justify-content:space-between;margin:30px 0 18px}.sectionTitle h2{font-size:38px;margin:0}.sectionTitle span{font-size:19px;color:$sub}.videoGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:28px 22px}.card{min-width:0}.thumb{position:relative;aspect-ratio:16/9;border-radius:17px;overflow:hidden;background:#111;border:1px solid $border}.thumb img{width:100%;height:100%;object-fit:cover;display:block}.duration{position:absolute;right:9px;bottom:9px;background:rgba(0,0,0,.78);color:#fff;padding:5px 8px;border-radius:7px;font-size:15px}.ctitle{font-size:23px;font-weight:700;line-height:1.36;margin-top:11px;min-height:62px;max-height:62px;overflow:hidden}.cmeta{font-size:18px;line-height:1.45;color:$sub;margin-top:4px}.hero{height:300px;border-radius:26px;overflow:hidden;position:relative;background:linear-gradient(90deg,rgba(0,0,0,.15),rgba(0,0,0,.70)),url('https://i.ytimg.com/vi/linlz7-Pnvw/maxresdefault.jpg') center/cover;border:1px solid $border;display:flex;align-items:center;padding:44px}.heroText{max-width:820px}.hero h1{font-size:58px;line-height:1.05;margin:0 0 14px;color:#fff}.hero p{font-size:26px;line-height:1.5;color:#eef4fa;margin:0}.heroBtn{display:inline-flex;margin-top:22px;background:#fff;color:#111;padding:14px 26px;border-radius:26px;font-size:22px;font-weight:750}.chips{display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap}.chip{padding:11px 19px;border-radius:20px;background:$panel2;border:1px solid $border;font-size:19px}.chip.on{background:$text;color:$bg;font-weight:750}.result{display:grid;grid-template-columns:410px 1fr;gap:28px;padding:17px 0;border-bottom:1px solid $border}.result img{width:410px;aspect-ratio:16/9;object-fit:cover;border-radius:16px}.rtitle{font-size:28px;font-weight:750;line-height:1.34;margin:5px 0 10px}.rmeta{color:$sub;font-size:19px;line-height:1.55}.empty{background:$panel;border:1px solid $border;border-radius:22px;padding:38px;color:$sub;font-size:24px}.settings{max-width:1100px}.row{min-height:82px;border-bottom:1px solid $border;display:flex;align-items:center;justify-content:space-between;font-size:24px}.row span:last-child{color:$sub}.playerPage{display:grid;grid-template-columns:minmax(0,1fr) 510px;gap:28px}.playerCol{min-width:0}.playerBox{position:relative;aspect-ratio:16/9;border-radius:22px;overflow:hidden;background:#000;border:1px solid $border}.playerBox iframe{width:100%;height:100%;border:0}.fullBtn{position:absolute;right:18px;bottom:18px;background:rgba(0,0,0,.72);color:#fff;border:1px solid rgba(255,255,255,.35);padding:11px 16px;border-radius:14px;font-size:18px;font-weight:700}.pTitle{font-size:34px;font-weight:780;line-height:1.33;margin:18px 0 9px}.pMeta{color:$sub;font-size:19px}.channelRow{display:flex;align-items:center;gap:16px;margin-top:20px;padding-bottom:18px;border-bottom:1px solid $border}.avatar{width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#3aa0ff,#204b88)}.channelInfo{flex:1}.channelInfo b{display:block;font-size:23px}.channelInfo span{display:block;color:$sub;font-size:17px;margin-top:4px}.subscribe{background:#fff;color:#111;border-radius:24px;padding:12px 22px;font-size:19px;font-weight:750}.actions{display:flex;gap:11px;margin-top:17px;flex-wrap:wrap}.action{background:$panel2;border:1px solid $border;padding:12px 18px;border-radius:22px;font-size:19px}.desc{background:$panel;border:1px solid $border;border-radius:18px;margin-top:18px;padding:18px 20px;color:$sub;line-height:1.65;font-size:18px}.recommend{background:$panel;border:1px solid $border;border-radius:20px;padding:16px}.tabs{display:flex;gap:9px;margin-bottom:16px}.tab{padding:10px 15px;border-radius:17px;background:$panel2;font-size:17px}.tab.on{background:#fff;color:#111;font-weight:750}.rec{display:grid;grid-template-columns:185px 1fr;gap:13px;margin-bottom:16px}.rec img{width:185px;aspect-ratio:16/9;object-fit:cover;border-radius:11px}.recTitle{font-size:18px;font-weight:700;line-height:1.32;max-height:48px;overflow:hidden}.recMeta{font-size:15px;color:$sub;margin-top:5px;line-height:1.4}.historyGrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:25px}.progress{height:5px;background:#25303c;position:absolute;left:0;right:0;bottom:0}.progress i{display:block;height:100%;background:#ff2d35}.loginCard{max-width:900px;background:$panel;border:1px solid $border;border-radius:24px;padding:34px}.loginCard h2{font-size:38px;margin:0 0 15px}.loginCard p{font-size:22px;line-height:1.65;color:$sub}.loginButton{display:inline-flex;background:#fff;color:#111;border-radius:28px;padding:15px 25px;font-size:22px;font-weight:750;margin-top:10px}.loginNote{font-size:17px!important;margin-top:20px!important}@media(max-width:1700px){.app{grid-template-columns:285px 1fr}.videoGrid{grid-template-columns:repeat(4,1fr)}.playerPage{grid-template-columns:minmax(0,1fr) 440px}.rec{grid-template-columns:165px 1fr}.result{grid-template-columns:370px 1fr}.result img{width:370px}}
        </style><script>function goSearch(){var q=document.getElementById('q').value.trim();if(q)location.href='c16://search?q='+encodeURIComponent(q);return false}</script></head><body><div class='app'><aside class='sidebar'><div class='brand'><div class='logo'>▶</div><div class='brandText'><strong>C16 YouTube</strong><small>Video for a better drive</small></div></div>${nav("home","⌂","首页","home")}${nav("search","⌕","探索","search?q=travel")}${nav("subs","▣","订阅","subscriptions")}${nav("history","◷","历史记录","history")}${nav("favorites","♡","我的收藏","favorites")}${nav("local","▤","本地视频","local")}${nav("settings","⚙","设置","settings")}<div style='flex:1'></div></aside><main class='main'><header class='top'><form class='search' onsubmit='return goSearch()'><input id='q' value='$escapedQ' placeholder='搜索 YouTube，发现更大的世界'><button>⌕</button></form><a class='pill' href='c16://login'>登录</a><a class='iconBtn' href='c16://favorites'>♡</a><a class='iconBtn' href='c16://theme'>${if (dark) "☀" else "☾"}</a></header><section class='content'>$body</section></main></div></body></html>"""
    }

    private fun videoCard(v: Video, history: Boolean = false): String {
        val p = if (history) "<div class='progress'><i style='width:38%'></i></div>" else ""
        return "<a class='card' href='c16://watch?id=${v.id}'><div class='thumb'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><span class='duration'>${if (v.id == "linlz7-Pnvw") "12:36" else "18:24"}</span>$p</div><div class='ctitle'>${v.title}</div><div class='cmeta'>${v.channel}<br>${v.meta}</div></a>"
    }

    private fun showHome() {
        val cards = videos.take(8).joinToString("") { videoCard(it) }
        val body = """<div class='chips'><a class='chip on'>推荐</a><a class='chip' href='c16://search?q=music'>音乐</a><a class='chip' href='c16://search?q=travel'>旅行</a><a class='chip' href='c16://search?q=technology'>科技</a><a class='chip' href='c16://search?q=cars'>汽车</a><a class='chip' href='c16://search?q=food'>美食</a></div><div class='hero'><div class='heroText'><h1>去看更大的世界</h1><p>让每一次出发，都有新的风景。在路上，也遇见更好的自己。</p><a class='heroBtn' href='c16://watch?id=linlz7-Pnvw'>开始探索 ›</a></div></div><div class='sectionTitle'><h2>为你推荐</h2><span>精选内容 · 大屏优化</span></div><div class='videoGrid'>$cards</div>"""
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
        val body = """<div class='playerPage'><div class='playerCol'><div class='playerBox'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0' allow='autoplay; encrypted-media; picture-in-picture'></iframe><a class='fullBtn' href='c16://fullscreen?id=${current.id}'>⛶ 全屏</a></div><div class='pTitle'>${current.title}</div><div class='pMeta'>${current.meta}　#Travel #4K #C16</div><div class='channelRow'><div class='avatar'></div><div class='channelInfo'><b>${current.channel}</b><span>482万订阅者</span></div><span class='subscribe'>订阅</span></div><div class='actions'><span class='action'>👍 56万</span><span class='action'>👎</span><span class='action'>↗ 分享</span><a class='action' href='c16://favorite?id=${current.id}'>${if (fav) "♥ 已收藏" else "♡ 收藏"}</a><span class='action'>•••</span></div><div class='desc'>播放器使用 YouTube 原生播放能力，但全屏切换改由 C16 YouTube 自己控制，避免退出全屏后出现黑屏。标题、频道、操作按钮与右侧推荐保持统一大字号。</div></div><aside class='recommend'><div class='tabs'><span class='tab on'>推荐</span><span class='tab'>相关视频</span><span class='tab'>来自作者</span></div>$recs</aside></div>"""
        load(shell("", body))
    }

    private fun showFullscreen(id: String) {
        val current = videos.find { it.id == id } ?: videos.first()
        fullscreenVideoId = current.id
        val html = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#000}.stage{position:fixed;inset:0;background:#000}.stage iframe{position:absolute;inset:0;width:100%;height:100%;border:0}.back{position:absolute;left:28px;top:24px;z-index:5;background:rgba(0,0,0,.62);color:#fff;border:1px solid rgba(255,255,255,.28);padding:14px 20px;border-radius:24px;font:700 22px sans-serif;text-decoration:none}</style></head><body><div class='stage'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0' allow='autoplay; encrypted-media; picture-in-picture'></iframe><a class='back' href='c16://watch?id=${current.id}'>‹ 返回</a></div></body></html>"""
        web.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun addHistory(id: String) {
        val old = prefs.getString("history", "").orEmpty().split(',').filter { it.isNotBlank() }.toMutableList()
        old.remove(id)
        old.add(0, id)
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
        val body = """<div class='sectionTitle'><h2>订阅</h2><span>你关注的频道</span></div><div class='chips'><span class='chip on'>Scenic Relaxation</span><span class='chip'>The Jazz Hop Café</span><span class='chip'>National Geographic</span><span class='chip'>TED</span><span class='chip'>Marques Brownlee</span></div><div class='videoGrid'>${videos.take(8).joinToString("") { videoCard(it) }}</div>"""
        load(shell("subs", body))
    }

    private fun showLocal() {
        val body = """<div class='sectionTitle'><h2>本地视频</h2><span>车机媒体库</span></div><div class='videoGrid'><div class='empty'>📁 电影<br><small>本地视频分类</small></div><div class='empty'>📁 音乐 MV<br><small>本地视频分类</small></div><div class='empty'>📁 纪录片<br><small>本地视频分类</small></div><div class='empty'>📁 其他<br><small>本地视频分类</small></div></div>"""
        load(shell("local", body))
    }

    private fun showLoginPage() {
        val body = """<div class='loginCard'><h2>YouTube / Google 登录</h2><p>Google 会限制在嵌入式 WebView 中直接输入账号密码，因此这一版不再强行把 Google 登录页塞进播放器。点击下面按钮后，会交给车机中的系统浏览器完成登录，这是更稳定也更安全的方式。</p><a class='loginButton' href='c16://loginExternal'>在浏览器中打开 YouTube 登录 ›</a><p class='loginNote'>说明：浏览器登录与本 App 的自定义界面账号同步是两件事。要让“订阅、个人推荐、账号头像”等真正同步到 C16 YouTube，需要下一步配置 Google OAuth 客户端 ID。当前版本先解决“能进入官方登录流程”和 WebView 登录被拦截的问题。</p></div>"""
        load(shell("", body))
    }

    private fun openExternalLogin() {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://accounts.google.com/ServiceLogin?service=youtube&continue=https%3A%2F%2Fwww.youtube.com%2F"))
            startActivity(intent)
            Toast.makeText(this, "已打开系统浏览器，请完成 YouTube 登录", Toast.LENGTH_LONG).show()
        } catch (_: Exception) {
            Toast.makeText(this, "车机没有可用浏览器，暂时无法打开 Google 登录", Toast.LENGTH_LONG).show()
            showLoginPage()
        }
    }

    private fun showSettings() {
        val body = """<div class='settings'><div class='sectionTitle'><h2>设置</h2><span>C16 YouTube v2.1</span></div><div class='row'><span>主题模式</span><span>${if (dark) "深色" else "浅色"} ›</span></div><div class='row'><span>界面字号</span><span>车机大字版（+40%）</span></div><div class='row'><span>视频画质</span><span>自动（推荐） ›</span></div><div class='row'><span>全屏方式</span><span>C16 自定义全屏</span></div><div class='row'><span>账号登录</span><span>系统浏览器 / OAuth 待配置</span></div><div class='row'><span>语言</span><span>简体中文 ›</span></div><div class='row'><span>关于 C16 YouTube</span><span>v2.1.40039</span></div></div>"""
        load(shell("settings", body))
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        val full = fullscreenVideoId
        if (full != null) {
            showPlayer(full)
        } else if (web.canGoBack()) {
            web.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        web.destroy()
        super.onDestroy()
    }
}
