package com.android.gallery3d

import android.app.Activity
import android.content.Context
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLDecoder
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.util.concurrent.atomic.AtomicBoolean

class MainActivity : Activity() {
    private lateinit var root: FrameLayout
    private lateinit var web: WebView
    private val main = Handler(Looper.getMainLooper())
    private val prefs by lazy { getSharedPreferences("c16_youtube_v24", Context.MODE_PRIVATE) }
    private var dark = false
    private var fullscreenVideoId: String? = null
    private var currentVideoId: String? = null
    private val loginPolling = AtomicBoolean(false)
    private val commentsCache = mutableMapOf<String, List<Comment>>()
    private val commentsLoaded = mutableSetOf<String>()

    data class Video(val id: String, val title: String, val channel: String, val meta: String, val category: String)
    data class Comment(val author: String, val text: String, val avatar: String)
    data class Hero(val eyebrow: String, val title: String, val copy: String, val bg: String, val videoId: String, val badge: String)

    private val videos = listOf(
        Video("linlz7-Pnvw", "Switzerland 4K - Beautiful Nature & Scenic Relaxation", "Scenic Relaxation", "1.2亿次观看 · 3个月前", "旅行"),
        Video("Scxs7L0vhZ4", "Costa Rica 4K · Tropical Nature", "Scenic Relaxation", "4K HDR · 旅行", "旅行"),
        Video("aqz-KE-bpKQ", "Big Buck Bunny · 4K 视频测试", "Blender", "4K · 高清测试", "电影"),
        Video("ysz5S6PUM-U", "Sintel · 电影级画质测试", "Blender", "短片 · 画质测试", "电影"),
        Video("M7lc1UVf-VE", "YouTube Player Demo · 大屏播放体验", "YouTube Developers", "播放器演示 · 科技", "科技"),
        Video("jNQXAC9IVRw", "Me at the zoo · YouTube 经典视频", "YouTube", "经典内容 · 继续观看", "推荐"),
        Video("kJQP7kiw5Fk", "全球热门音乐 · 沉浸式大屏体验", "Music", "热门音乐 · 推荐", "音乐"),
        Video("dQw4w9WgXcQ", "经典流行音乐 · 驾乘氛围精选", "Music", "音乐 · 热门", "音乐"),
        Video("9bZkp7q19f0", "PSY - GANGNAM STYLE", "Officialpsy", "热门 · 音乐", "音乐"),
        Video("OPf0YbXqDm0", "Uptown Funk · Bruno Mars", "Mark Ronson", "音乐 · 推荐", "音乐"),
        Video("DsonSEllPmU", "CYBERTRUCK · Tesla", "Tesla", "汽车 · 官方视频", "汽车"),
        Video("dXOdiF4wbNU", "Porsche 911 GT3 · Official Driving", "Porsche", "跑车 · 官方视频", "汽车")
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_FULLSCREEN or
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        dark = prefs.getBoolean("dark", false)
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
            }
            webChromeClient = WebChromeClient()
        }
        root.addView(web, FrameLayout.LayoutParams(-1, -1))
    }

    private fun handleRoute(uri: Uri) {
        when (uri.host) {
            "home" -> showHome()
            "search" -> showSearch(uri.getQueryParameter("q").orEmpty())
            "category" -> showCategory(uri.getQueryParameter("name").orEmpty())
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
            "login" -> showLoginCenter()
            "startQr" -> startDeviceLogin(uri.getQueryParameter("client").orEmpty())
            "logout" -> logout()
        }
    }

    private fun load(html: String) {
        fullscreenVideoId = null
        web.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun shell(active: String, body: String, query: String = ""): String {
        val bg = if (dark) "#0f0f0f" else "#f6f7f9"
        val side = if (dark) "#151515" else "#ffffff"
        val panel = if (dark) "#181818" else "#ffffff"
        val panel2 = if (dark) "#272727" else "#eef0f3"
        val text = if (dark) "#f6f6f6" else "#151515"
        val sub = if (dark) "#aaaaaa" else "#6c737d"
        val border = if (dark) "#303030" else "#e2e5e9"
        val activeBg = if (dark) "#57252a" else "#ffdce0"
        val accountText = if (prefs.getString("access_token", "").orEmpty().isNotBlank()) "已登录" else "登录"
        fun nav(id: String, icon: String, label: String, host: String) =
            "<a class='nav ${if (active == id) "on" else ""}' href='c16://$host'><span class='navIcon'>$icon</span><b>$label</b></a>"
        val escapedQ = esc(query)
        return """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:$bg;color:$text;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC','PingFang SC',Arial,sans-serif}a{text-decoration:none;color:inherit}.app{height:100vh;display:grid;grid-template-columns:260px 1fr;background:$bg}.sidebar{background:$side;border-right:1px solid $border;padding:24px 20px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:13px;height:68px;margin-bottom:24px}.ytLogo{width:56px;height:38px;border-radius:11px;background:#ff0033;color:#fff;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:900}.brand strong{font-size:32px;letter-spacing:-1px}.nav{height:64px;border-radius:17px;display:flex;align-items:center;gap:16px;padding:0 18px;margin:3px 0;color:$text;font-size:22px}.navIcon{width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-size:22px}.nav b{font-weight:650}.nav.on{background:$activeBg}.nav.on b{font-weight:850}.main{min-width:0;display:grid;grid-template-rows:90px 1fr}.top{display:flex;align-items:center;padding:14px 28px;gap:12px;border-bottom:1px solid $border;background:$side}.search{height:58px;width:min(54%,920px);margin-left:auto;background:$panel2;border:1px solid $border;border-radius:29px;display:flex;align-items:center;padding:0 18px}.search input{flex:1;background:transparent;border:0;outline:0;color:$text;font-size:21px}.search button{border:0;background:transparent;color:$text;font-size:24px;padding:8px 10px}.pill{height:52px;border-radius:26px;background:$panel;border:1px solid $border;padding:0 19px;display:flex;align-items:center;justify-content:center;font-size:19px;font-weight:800}.iconBtn{width:52px;height:52px;border-radius:26px;background:$panel;border:1px solid $border;display:flex;align-items:center;justify-content:center;font-size:23px}.content{overflow:auto;padding:20px 28px 48px;scrollbar-width:none}.content::-webkit-scrollbar{display:none}.chips{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:16px}.chip{padding:9px 17px;border-radius:19px;background:$panel;border:1px solid $border;font-size:17px;font-weight:700}.chip.on{background:$text;color:$bg;font-weight:850}.hero{height:330px;border-radius:27px;overflow:hidden;position:relative;border:1px solid $border;background:#0d1117;box-shadow:0 16px 40px rgba(0,0,0,.10)}.heroBg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.heroShade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(4,11,18,.94) 0%,rgba(4,11,18,.78) 34%,rgba(4,11,18,.30) 58%,rgba(4,11,18,.08) 100%)}.heroCopy{position:absolute;left:40px;top:30px;width:43%;z-index:2;color:white}.eyebrow{font-size:14px;letter-spacing:3px;color:#7bc3ff;font-weight:900;margin-bottom:10px}.hero h1{font-size:48px;line-height:1.08;margin:0 0 10px;letter-spacing:-1px}.hero p{font-size:19px;line-height:1.5;color:#edf1f5;margin:0}.heroActions{display:flex;gap:11px;margin-top:20px}.primary{padding:11px 21px;background:#fff;color:#111;border-radius:22px;font-size:18px;font-weight:850}.secondary{padding:11px 21px;background:rgba(255,255,255,.16);color:#fff;border:1px solid rgba(255,255,255,.35);border-radius:22px;font-size:18px;font-weight:750}.heroBadge{position:absolute;right:28px;bottom:24px;z-index:2;background:rgba(0,0,0,.58);color:white;border:1px solid rgba(255,255,255,.22);padding:10px 14px;border-radius:14px;font-size:17px;font-weight:800}.sectionTitle{display:flex;align-items:end;justify-content:space-between;margin:26px 0 14px}.sectionTitle h2{font-size:32px;margin:0}.sectionTitle span{font-size:16px;color:$sub}.videoGrid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:25px 16px}.card{min-width:0}.thumb{position:relative;aspect-ratio:16/9;border-radius:15px;overflow:hidden;background:#161616;border:1px solid $border}.thumb img{width:100%;height:100%;object-fit:cover;display:block}.duration{position:absolute;right:7px;bottom:7px;background:rgba(0,0,0,.82);color:#fff;padding:4px 7px;border-radius:7px;font-size:12px}.ctitle{font-size:18px;font-weight:780;line-height:1.35;margin-top:9px;height:50px;overflow:hidden}.cmeta{font-size:14px;line-height:1.4;color:$sub;margin-top:2px}.result{display:grid;grid-template-columns:360px 1fr;gap:24px;padding:16px 0;border-bottom:1px solid $border}.result img{width:360px;aspect-ratio:16/9;object-fit:cover;border-radius:14px}.rtitle{font-size:25px;font-weight:800;line-height:1.35;margin:3px 0 8px}.rmeta{color:$sub;font-size:17px;line-height:1.5}.playerPage{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:22px}.playerCol{min-width:0}.playerBox{position:relative;aspect-ratio:16/9;border-radius:20px;overflow:hidden;background:#000;border:1px solid $border}.playerBox iframe{width:100%;height:100%;border:0}.quality{position:absolute;left:16px;top:16px;background:rgba(0,0,0,.64);color:#fff;padding:7px 10px;border-radius:10px;font-size:14px;font-weight:900}.fullBtn{position:absolute;right:16px;bottom:16px;background:rgba(0,0,0,.74);color:#fff;border:1px solid rgba(255,255,255,.36);padding:10px 15px;border-radius:13px;font-size:19px;font-weight:800}.pTitle{font-size:46px;font-weight:880;line-height:1.18;margin:18px 0 9px;letter-spacing:-.8px}.pMeta{color:$sub;font-size:21px}.channelRow{display:flex;align-items:center;gap:16px;margin-top:20px;padding:15px 0;border-top:1px solid $border;border-bottom:1px solid $border}.avatar{width:66px;height:66px;border-radius:50%;background:linear-gradient(135deg,#4c9fff,#253f66)}.channelInfo{flex:1}.channelInfo b{display:block;font-size:28px}.channelInfo span{display:block;color:$sub;font-size:18px;margin-top:4px}.subscribe{background:#111;color:#fff;border-radius:25px;padding:12px 23px;font-size:20px;font-weight:850}.actions{display:flex;gap:10px;margin-top:15px;flex-wrap:wrap}.action{background:$panel;border:1px solid $border;padding:11px 18px;border-radius:22px;font-size:19px;font-weight:750}.recommend{background:$panel;border:1px solid $border;border-radius:20px;padding:14px;align-self:start}.recTabs{display:flex;gap:8px;margin-bottom:13px}.tab{padding:8px 12px;border-radius:16px;background:$panel2;font-size:14px}.tab.on{background:$text;color:$bg;font-weight:800}.rec{display:grid;grid-template-columns:128px 1fr;gap:10px;margin-bottom:13px}.rec img{width:128px;aspect-ratio:16/9;object-fit:cover;border-radius:9px}.recTitle{font-size:16px;font-weight:780;line-height:1.3;max-height:43px;overflow:hidden}.recMeta{font-size:12px;color:$sub;margin-top:4px;line-height:1.35}.comments{margin-top:20px;background:$panel;border:1px solid $border;border-radius:19px;padding:18px}.commentsHead{font-size:27px;font-weight:850;margin-bottom:7px}.comment{display:grid;grid-template-columns:46px 1fr;gap:12px;padding:14px 0;border-top:1px solid $border}.comment:first-of-type{border-top:0}.comment img,.commentAvatar{width:46px;height:46px;border-radius:50%;background:$panel2;object-fit:cover}.comment b{font-size:16px}.comment p{font-size:17px;line-height:1.5;margin:4px 0 0;color:$text}.muted{color:$sub;font-size:17px}.empty{background:$panel;border:1px solid $border;border-radius:19px;padding:32px;color:$sub;font-size:20px}.historyGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px}.progress{height:5px;background:#333;position:absolute;left:0;right:0;bottom:0}.progress i{display:block;height:100%;background:#ff0033}.loginWrap{display:grid;grid-template-columns:1fr 1fr;gap:26px;max-width:1180px;margin:16px auto}.loginCard{background:$panel;border:1px solid $border;border-radius:24px;padding:30px}.loginCard h2{font-size:34px;margin:0 0 10px}.loginCard p{font-size:19px;line-height:1.55;color:$sub}.clientInput{width:100%;height:58px;border:1px solid $border;border-radius:15px;background:$panel2;color:$text;padding:0 15px;font-size:17px;outline:none}.loginButton{display:inline-flex;margin-top:15px;background:#ff0033;color:#fff;border-radius:26px;padding:13px 23px;font-size:19px;font-weight:850}.qrCard{text-align:center;background:$panel;border:1px solid $border;border-radius:24px;padding:28px}.qrCard img{width:270px;height:270px;border-radius:17px;background:#fff;padding:8px}.deviceCode{font-size:36px;font-weight:900;letter-spacing:5px;margin:15px 0 7px}.status{font-size:17px;color:$sub}.settings{max-width:1000px}.row{min-height:72px;border-bottom:1px solid $border;display:flex;align-items:center;justify-content:space-between;font-size:21px}.row span:last-child{color:$sub}@media(max-width:1250px){.app{grid-template-columns:220px 1fr}.videoGrid{grid-template-columns:repeat(4,1fr)}.playerPage{grid-template-columns:minmax(0,1fr) 330px}.pTitle{font-size:40px}}
</style><script>function goSearch(){var q=document.getElementById('q').value.trim();if(q)location.href='c16://search?q='+encodeURIComponent(q);return false}function startQr(){var c=document.getElementById('client').value.trim();location.href='c16://startQr?client='+encodeURIComponent(c)}</script></head><body><div class='app'><aside class='sidebar'><div class='brand'><div class='ytLogo'>▶</div><strong>YouTube</strong></div>${nav("home","⌂","首页","home")}${nav("search","⌕","探索","search?q=travel")}${nav("subs","▣","订阅","subscriptions")}${nav("history","◷","历史记录","history")}${nav("favorites","♡","我的收藏","favorites")}${nav("local","▤","本地视频","local")}${nav("settings","⚙","设置","settings")}<div style='flex:1'></div></aside><main class='main'><header class='top'><form class='search' onsubmit='return goSearch()'><input id='q' value='$escapedQ' placeholder='搜索 YouTube'><button>⌕</button></form><a class='pill' href='c16://login'>◉ $accountText</a><a class='iconBtn' href='c16://favorites'>♡</a><a class='iconBtn' href='c16://theme'>${if (dark) "☀" else "☾"}</a></header><section class='content'>$body</section></main></div></body></html>"""
    }

    private fun videoCard(v: Video, history: Boolean = false): String {
        val p = if (history) "<div class='progress'><i style='width:42%'></i></div>" else ""
        return "<a class='card' href='c16://watch?id=${v.id}'><div class='thumb'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><span class='duration'>${if (v.id == "linlz7-Pnvw") "12:36" else "18:24"}</span>$p</div><div class='ctitle'>${esc(v.title)}</div><div class='cmeta'>${esc(v.channel)}<br>${esc(v.meta)}</div></a>"
    }

    private fun heroFor(category: String): Hero = when (category) {
        "音乐" -> Hero("MUSIC FOR THE DRIVE", "让音乐，\n填满旅程。", "热门音乐、经典现场与驾乘氛围精选。", "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=1800&q=85", "kJQP7kiw5Fk", "Music · Immersive")
        "科技" -> Hero("EXPLORE THE FUTURE", "科技正在，\n改变世界。", "探索 AI、数码与未来体验。", "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1800&q=85", "M7lc1UVf-VE", "Tech · Future")
        "汽车" -> Hero("DRIVE THE FUTURE", "驾驭未来，\n看见性能。", "新能源、性能车与汽车科技精选。", "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1800&q=85", "DsonSEllPmU", "Cars · Performance")
        "电影" -> Hero("CINEMA ON THE ROAD", "一块大屏，\n进入电影世界。", "短片、动画与大屏画质测试。", "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1800&q=85", "aqz-KE-bpKQ", "Cinema · 4K")
        else -> Hero("DISCOVER THE WORLD", "世界很大，\n出发就好。", "把旅途交给风景，把时间留给热爱。", "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1800&q=85", "linlz7-Pnvw", "Switzerland · 8K HDR")
    }

    private fun heroHtml(hero: Hero): String {
        val title = esc(hero.title).replace("\n", "<br>")
        val fallback = "https://i.ytimg.com/vi/${hero.videoId}/hqdefault.jpg"
        return """<div class='hero'><img class='heroBg' src='${hero.bg}' onerror="this.onerror=null;this.src='$fallback'"><div class='heroShade'></div><div class='heroCopy'><div class='eyebrow'>${esc(hero.eyebrow)}</div><h1>$title</h1><p>${esc(hero.copy)}</p><div class='heroActions'><a class='primary' href='c16://watch?id=${hero.videoId}'>▶ 立即播放</a><a class='secondary' href='c16://search?q=${Uri.encode(hero.title.substringBefore("，"))}'>探索更多</a></div></div><div class='heroBadge'>${esc(hero.badge)}</div></div>"""
    }

    private fun chipsHtml(active: String): String = listOf("推荐", "音乐", "旅行", "科技", "汽车", "电影").joinToString("") {
        "<a class='chip ${if (it == active) "on" else ""}' href='c16://category?name=${Uri.encode(it)}'>$it</a>"
    }

    private fun showHome() {
        currentVideoId = null
        val cards = videos.take(10).joinToString("") { videoCard(it) }
        val body = "<div class='chips'>${chipsHtml("推荐")}</div>${heroHtml(heroFor("推荐"))}<div class='sectionTitle'><h2>为你推荐</h2><span>精选内容 · 大屏优化</span></div><div class='videoGrid'>$cards</div>"
        load(shell("home", body))
    }

    private fun showCategory(name: String) {
        val n = if (name.isBlank()) "推荐" else name
        val list = if (n == "推荐") videos else videos.filter { it.category == n }.ifEmpty { videos }
        val body = "<div class='chips'>${chipsHtml(n)}</div>${heroHtml(heroFor(n))}<div class='sectionTitle'><h2>${esc(n)}</h2><span>${list.size} 个精选视频</span></div><div class='videoGrid'>${list.joinToString("") { videoCard(it) }}</div>"
        load(shell("home", body))
    }

    private fun showSearch(q: String) {
        val decoded = try { URLDecoder.decode(q, StandardCharsets.UTF_8.name()) } catch (_: Exception) { q }
        val key = decoded.trim().lowercase()
        val pool = videos.filter { key.isBlank() || it.title.lowercase().contains(key) || it.channel.lowercase().contains(key) || it.category.lowercase().contains(key) }.ifEmpty { videos }
        val results = pool.take(12).joinToString("") { v -> "<a class='result' href='c16://watch?id=${v.id}'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><div><div class='rtitle'>${esc(v.title)}</div><div class='rmeta'>${esc(v.channel)} · ${esc(v.meta)}</div><div class='rmeta' style='margin-top:9px'>点击进入大屏播放页面</div></div></a>" }
        load(shell("search", results, decoded))
    }

    private fun showPlayer(id: String) {
        val current = videos.find { it.id == id } ?: videos.first()
        currentVideoId = current.id
        addHistory(current.id)
        val recs = videos.filter { it.id != current.id }.take(8).joinToString("") { v ->
            "<a class='rec' href='c16://watch?id=${v.id}'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><div><div class='recTitle'>${esc(v.title)}</div><div class='recMeta'>${esc(v.channel)}<br>${esc(v.meta)}</div></div></a>"
        }
        val fav = prefs.getStringSet("favorites", emptySet()).orEmpty().contains(current.id)
        val commentsHtml = buildCommentsHtml(current.id)
        val loginHint = if (prefs.getString("access_token", "").orEmpty().isBlank()) "<a class='action' href='c16://login'>◉ 手机扫码登录</a>" else ""
        val body = """<div class='playerPage'><div class='playerCol'><div class='playerBox'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0&modestbranding=1' allow='autoplay; encrypted-media; picture-in-picture'></iframe><span class='quality'>4K · HDR</span><a class='fullBtn' href='c16://fullscreen?id=${current.id}'>⛶ 全屏</a></div><div class='pTitle'>${esc(current.title)}</div><div class='pMeta'>${esc(current.meta)}　#4K #Nature</div><div class='channelRow'><div class='avatar'></div><div class='channelInfo'><b>${esc(current.channel)}</b><span>精选频道 · 大屏观看</span></div><span class='subscribe'>订阅</span></div><div class='actions'><span class='action'>👍 点赞</span><span class='action'>↗ 分享</span><a class='action' href='c16://favorite?id=${current.id}'>${if (fav) "♥ 已收藏" else "♡ 收藏"}</a><span class='action'>⋯ 更多</span>$loginHint</div>$commentsHtml</div><aside class='recommend'><div class='recTabs'><span class='tab on'>推荐</span><span class='tab'>相关</span></div>$recs</aside></div>"""
        load(shell("", body))
        if (prefs.getString("access_token", "").orEmpty().isNotBlank() && current.id !in commentsLoaded) fetchCommentsAsync(current.id)
    }

    private fun buildCommentsHtml(videoId: String): String {
        val token = prefs.getString("access_token", "").orEmpty()
        val list = commentsCache[videoId]
        val inner = when {
            token.isBlank() -> "<div class='muted'>手机扫码授权后，可读取该视频的公开评论。</div>"
            list == null -> "<div class='muted'>正在加载评论…</div>"
            list.isEmpty() -> "<div class='muted'>暂时无法读取评论，稍后再试。</div>"
            else -> list.joinToString("") { c -> "<div class='comment'>${if (c.avatar.isNotBlank()) "<img src='${escAttr(c.avatar)}'>" else "<div class='commentAvatar'></div>"}<div><b>${esc(c.author)}</b><p>${esc(c.text)}</p></div></div>" }
        }
        return "<div class='comments'><div class='commentsHead'>评论</div>$inner</div>"
    }

    private fun fetchCommentsAsync(videoId: String) {
        commentsLoaded.add(videoId)
        val token = prefs.getString("access_token", "").orEmpty()
        Thread {
            val out = mutableListOf<Comment>()
            try {
                val u = URL("https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=${URLEncoder.encode(videoId, "UTF-8")}&maxResults=4&textFormat=plainText")
                val c = (u.openConnection() as HttpURLConnection).apply {
                    requestMethod = "GET"
                    connectTimeout = 12000
                    readTimeout = 12000
                    setRequestProperty("Authorization", "Bearer $token")
                }
                val text = readResponse(c)
                if (c.responseCode in 200..299) {
                    val items = JSONObject(text).optJSONArray("items")
                    if (items != null) for (i in 0 until items.length()) {
                        val s = items.getJSONObject(i).getJSONObject("snippet").getJSONObject("topLevelComment").getJSONObject("snippet")
                        out.add(Comment(s.optString("authorDisplayName", "YouTube 用户"), s.optString("textDisplay", ""), s.optString("authorProfileImageUrl", "")))
                    }
                }
            } catch (_: Exception) { }
            commentsCache[videoId] = out
            main.post { if (currentVideoId == videoId) showPlayer(videoId) }
        }.start()
    }

    private fun showFullscreen(id: String) {
        val current = videos.find { it.id == id } ?: videos.first()
        fullscreenVideoId = current.id
        val html = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#000}.stage{position:fixed;inset:0;background:#000}.stage iframe{position:absolute;inset:0;width:100%;height:100%;border:0}.back{position:absolute;left:26px;top:22px;z-index:5;background:rgba(0,0,0,.66);color:#fff;border:1px solid rgba(255,255,255,.30);padding:13px 20px;border-radius:24px;font:800 21px sans-serif;text-decoration:none}</style></head><body><div class='stage'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0&modestbranding=1' allow='autoplay; encrypted-media; picture-in-picture'></iframe><a class='back' href='c16://watch?id=${current.id}'>‹ 返回</a></div></body></html>"""
        web.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun showLoginCenter(message: String = "") {
        val client = prefs.getString("oauth_client_id", "").orEmpty()
        val logged = prefs.getString("access_token", "").orEmpty().isNotBlank()
        val status = if (logged) "<p style='color:#1a9b50;font-weight:800'>✓ YouTube 手机授权已完成</p><a class='loginButton' href='c16://logout'>退出登录</a>" else ""
        val msg = if (message.isNotBlank()) "<p style='color:#d53a47;font-weight:700'>${esc(message)}</p>" else ""
        val body = """<div class='loginWrap'><div class='loginCard'><h2>手机扫码登录 YouTube</h2><p>在手机上完成 Google / YouTube 授权，车机无需输入账号和密码。首次使用请填入 Google Cloud 中为 TV / Limited Input Device 创建的 OAuth Client ID。</p>$msg<input class='clientInput' id='client' value='${escAttr(client)}' placeholder='粘贴 OAuth Client ID'><a class='loginButton' href='javascript:startQr()'>生成手机登录二维码</a>$status<p style='font-size:15px'>Client ID 仅保存在车机本地。扫码后如果手机页面要求授权码，请输入车机显示的代码。</p></div><div class='qrCard'><div style='font-size:56px;margin-top:66px'>▦</div><h2>扫码登录</h2><p>二维码生成后，用手机扫码并在手机上完成 YouTube 授权。</p></div></div>"""
        load(shell("", body))
    }

    private fun startDeviceLogin(clientId: String) {
        val client = clientId.trim()
        if (client.isBlank()) {
            showLoginCenter("请先填写 OAuth Client ID")
            return
        }
        prefs.edit().putString("oauth_client_id", client).apply()
        loginPolling.set(false)
        val loading = "<div class='loginWrap'><div class='loginCard'><h2>正在生成手机登录二维码</h2><p>正在连接 Google 授权服务，请稍候…</p></div><div class='qrCard'><div style='font-size:70px;margin-top:66px'>◌</div><h2>正在准备</h2></div></div>"
        load(shell("", loading))
        Thread {
            try {
                val response = postForm("https://oauth2.googleapis.com/device/code", mapOf(
                    "client_id" to client,
                    "scope" to "https://www.googleapis.com/auth/youtube.readonly"
                ))
                if (response.first !in 200..299) throw IllegalStateException(parseGoogleError(response.second))
                val j = JSONObject(response.second)
                val deviceCode = j.getString("device_code")
                val userCode = j.getString("user_code")
                val verifyUrl = j.optString("verification_url", j.optString("verification_uri", "https://www.google.com/device"))
                val expires = j.optInt("expires_in", 1800)
                val interval = j.optInt("interval", 5)
                main.post { showQrCode(userCode, verifyUrl, expires) }
                pollDeviceToken(client, deviceCode, interval, expires)
            } catch (e: Exception) {
                main.post { showLoginCenter("无法生成二维码：${e.message ?: "网络或 OAuth 配置错误"}") }
            }
        }.start()
    }

    private fun showQrCode(userCode: String, verifyUrl: String, expires: Int) {
        val qr = "https://api.qrserver.com/v1/create-qr-code/?size=360x360&data=${URLEncoder.encode(verifyUrl, "UTF-8")}" 
        val body = """<div class='loginWrap'><div class='loginCard'><h2>在手机上完成 YouTube 登录</h2><p>① 手机扫描右侧二维码<br>② 在手机上登录 Google / YouTube<br>③ 如果页面要求输入代码，请输入下方授权码</p><div class='deviceCode'>${esc(userCode)}</div><p>授权完成后车机会自动刷新登录状态。</p><div class='status'>二维码有效期约 ${expires / 60} 分钟 · 正在等待手机授权…</div></div><div class='qrCard'><img src='$qr'><h2>扫描二维码</h2><p>${esc(verifyUrl)}</p><div class='deviceCode'>${esc(userCode)}</div></div></div>"""
        load(shell("", body))
    }

    private fun pollDeviceToken(clientId: String, deviceCode: String, baseInterval: Int, expiresIn: Int) {
        if (!loginPolling.compareAndSet(false, true)) return
        Thread {
            val deadline = System.currentTimeMillis() + expiresIn * 1000L
            var waitSec = baseInterval.coerceAtLeast(5)
            try {
                while (System.currentTimeMillis() < deadline && loginPolling.get()) {
                    Thread.sleep(waitSec * 1000L)
                    val response = postForm("https://oauth2.googleapis.com/token", mapOf(
                        "client_id" to clientId,
                        "device_code" to deviceCode,
                        "grant_type" to "urn:ietf:params:oauth:grant-type:device_code"
                    ))
                    val j = JSONObject(response.second)
                    if (response.first in 200..299 && j.has("access_token")) {
                        prefs.edit()
                            .putString("access_token", j.optString("access_token"))
                            .putString("refresh_token", j.optString("refresh_token"))
                            .putLong("token_time", System.currentTimeMillis())
                            .apply()
                        loginPolling.set(false)
                        main.post {
                            Toast.makeText(this@MainActivity, "YouTube 手机授权成功", Toast.LENGTH_LONG).show()
                            showHome()
                        }
                        return@Thread
                    }
                    when (j.optString("error")) {
                        "authorization_pending" -> Unit
                        "slow_down" -> waitSec += 5
                        "access_denied" -> throw IllegalStateException("手机端已取消授权")
                        "expired_token" -> throw IllegalStateException("二维码已过期，请重新生成")
                        else -> if (j.optString("error").isNotBlank()) throw IllegalStateException(parseGoogleError(response.second))
                    }
                }
                if (loginPolling.get()) throw IllegalStateException("二维码已过期，请重新生成")
            } catch (e: Exception) {
                loginPolling.set(false)
                main.post { showLoginCenter(e.message ?: "登录失败") }
            }
        }.start()
    }

    private fun postForm(url: String, params: Map<String, String>): Pair<Int, String> {
        val data = params.entries.joinToString("&") { "${URLEncoder.encode(it.key, "UTF-8") }=${URLEncoder.encode(it.value, "UTF-8")}" }
        val c = (URL(url).openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 15000
            readTimeout = 15000
            doOutput = true
            setRequestProperty("Content-Type", "application/x-www-form-urlencoded")
        }
        c.outputStream.use { it.write(data.toByteArray(StandardCharsets.UTF_8)) }
        val text = readResponse(c)
        return c.responseCode to text
    }

    private fun readResponse(c: HttpURLConnection): String {
        val stream = if (c.responseCode in 200..299) c.inputStream else c.errorStream
        return stream?.bufferedReader()?.use { it.readText() }.orEmpty()
    }

    private fun parseGoogleError(body: String): String {
        return try {
            val j = JSONObject(body)
            j.optString("error_description", j.optString("error", "Google 授权失败"))
        } catch (_: Exception) { "Google 授权失败" }
    }

    private fun logout() {
        loginPolling.set(false)
        prefs.edit().remove("access_token").remove("refresh_token").remove("token_time").apply()
        commentsCache.clear()
        commentsLoaded.clear()
        Toast.makeText(this, "已退出 YouTube 授权", Toast.LENGTH_SHORT).show()
        showHome()
    }

    private fun addHistory(id: String) {
        val old = prefs.getString("history", "").orEmpty().split(',').filter { it.isNotBlank() }.toMutableList()
        old.remove(id)
        old.add(0, id)
        prefs.edit().putString("history", old.take(20).joinToString(",")).apply()
    }

    private fun showHistory() {
        val ids = prefs.getString("history", "").orEmpty().split(',').filter { it.isNotBlank() }
        val list = if (ids.isEmpty()) videos.take(8) else ids.mapNotNull { id -> videos.find { it.id == id } }
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
        val body = if (list.isEmpty()) "<div class='sectionTitle'><h2>我的收藏</h2></div><div class='empty'>还没有收藏视频。播放时点击“收藏”即可加入这里。</div>" else "<div class='sectionTitle'><h2>我的收藏</h2><span>${list.size} 个视频</span></div><div class='videoGrid'>${list.joinToString("") { videoCard(it) }}</div>"
        load(shell("favorites", body))
    }

    private fun showSubscriptions() {
        val body = "<div class='sectionTitle'><h2>订阅</h2><span>你关注的频道</span></div><div class='chips'><span class='chip on'>Scenic Relaxation</span><span class='chip'>YouTube</span><span class='chip'>Music</span><span class='chip'>Tesla</span><span class='chip'>Porsche</span></div><div class='videoGrid'>${videos.take(10).joinToString("") { videoCard(it) }}</div>"
        load(shell("subs", body))
    }

    private fun showLocal() {
        val body = "<div class='sectionTitle'><h2>本地视频</h2><span>车机媒体库</span></div><div class='videoGrid'><div class='empty'>▣ 电影<br><small>本地视频分类</small></div><div class='empty'>▣ 音乐 MV<br><small>本地视频分类</small></div><div class='empty'>▣ 纪录片<br><small>本地视频分类</small></div><div class='empty'>▣ 其他<br><small>本地视频分类</small></div></div>"
        load(shell("local", body))
    }

    private fun showSettings() {
        val hasClient = prefs.getString("oauth_client_id", "").orEmpty().isNotBlank()
        val logged = prefs.getString("access_token", "").orEmpty().isNotBlank()
        val body = """<div class='settings'><div class='sectionTitle'><h2>设置</h2><span>C16 YouTube v2.5</span></div><div class='row'><span>主题模式</span><span>${if (dark) "深色" else "浅色"}</span></div><div class='row'><span>首页布局</span><span>动态 Hero + 5列视频</span></div><div class='row'><span>分类联动</span><span>音乐 / 旅行 / 科技 / 汽车 / 电影</span></div><div class='row'><span>播放页布局</span><span>扩大播放器 + 窄版单列推荐</span></div><div class='row'><span>手机扫码登录</span><span>${if (logged) "已授权" else if (hasClient) "Client ID 已配置" else "未配置"}</span></div><div class='row'><span>评论</span><span>授权后读取公开视频评论</span></div><div class='row'><span>关于 YouTube</span><span>v2.5.40043</span></div></div>"""
        load(shell("settings", body))
    }

    private fun esc(s: String): String = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&#39;")
    private fun escAttr(s: String): String = esc(s)

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        val full = fullscreenVideoId
        if (full != null) showPlayer(full) else if (web.canGoBack()) web.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        loginPolling.set(false)
        CookieManager.getInstance().flush()
        web.destroy()
        super.onDestroy()
    }
}
