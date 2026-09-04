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
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLDecoder
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

class MainActivity : Activity() {
    private lateinit var root: FrameLayout
    private lateinit var web: WebView
    private var dark = true
    private var fullscreenVideoId: String? = null
    private val prefs by lazy { getSharedPreferences("c16_v23", Context.MODE_PRIVATE) }

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
            "watch" -> showPlayer(uri.getQueryParameter("id").orEmpty())
            "fullscreen" -> showFullscreen(uri.getQueryParameter("id").orEmpty())
            "history" -> showHistory()
            "favorites" -> showFavorites()
            "subscriptions" -> showSubscriptions()
            "local" -> showLocal()
            "settings" -> showSettings()
            "theme" -> { dark = !dark; prefs.edit().putBoolean("dark", dark).apply(); showHome() }
            "favorite" -> toggleFavorite(uri.getQueryParameter("id").orEmpty())
            "login" -> showDeviceLogin()
            "saveClient" -> {
                val id = uri.getQueryParameter("id").orEmpty().trim()
                prefs.edit().putString("oauth_client_id", id).apply()
                showDeviceLogin()
            }
            "deviceStart" -> startDeviceFlow()
            "logout" -> {
                prefs.edit().remove("access_token").remove("refresh_token").remove("account_name").apply()
                Toast.makeText(this, "已退出账号", Toast.LENGTH_SHORT).show()
                showHome()
            }
        }
    }

    private fun load(html: String) {
        fullscreenVideoId = null
        web.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun esc(s: String): String = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&#39;")

    private fun shell(active: String, body: String, query: String = ""): String {
        val bg = if (dark) "#0b0c0f" else "#f6f7f9"
        val side = if (dark) "#101216" else "#ffffff"
        val panel = if (dark) "#15181d" else "#ffffff"
        val panel2 = if (dark) "#20242b" else "#eef1f4"
        val text = if (dark) "#f7f8fa" else "#17191c"
        val sub = if (dark) "#9aa2ad" else "#68717c"
        val border = if (dark) "#252a31" else "#e2e6ea"
        val activeBg = if (dark) "#3d1f29" else "#ffe3e6"
        val activeText = if (dark) "#ffffff" else "#b21f32"
        fun nav(id: String, icon: String, label: String, host: String) = "<a class='nav ${if (active == id) "on" else ""}' href='c16://$host'><span>$icon</span><b>$label</b></a>"
        val logged = prefs.getString("access_token", "").orEmpty().isNotBlank()
        val account = prefs.getString("account_name", "").orEmpty()
        val accountLabel = if (logged) (if (account.isBlank()) "已登录" else esc(account)) else "登录"
        val q = esc(query)
        return """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>
        *{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:$bg;color:$text;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Noto Sans SC',Arial,sans-serif}a{text-decoration:none;color:inherit}.app{height:100vh;display:grid;grid-template-columns:300px 1fr}.sidebar{background:$side;border-right:1px solid $border;padding:28px 22px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:15px;height:76px;margin-bottom:22px}.logo{width:62px;height:46px;border-radius:14px;background:#ff1f2d;color:#fff;display:flex;align-items:center;justify-content:center;font-size:25px}.brand strong{font-size:31px}.brand small{display:block;color:$sub;font-size:15px;margin-top:4px}.nav{height:72px;border-radius:17px;display:flex;align-items:center;gap:18px;padding:0 20px;margin:4px 0;font-size:24px}.nav span{width:30px;text-align:center}.nav b{font-weight:700}.nav.on{background:$activeBg;color:$activeText}.main{min-width:0;display:grid;grid-template-rows:104px 1fr}.top{display:flex;align-items:center;gap:15px;padding:18px 28px 14px;border-bottom:1px solid $border}.search{height:66px;flex:1;background:$panel2;border:1px solid $border;border-radius:33px;display:flex;align-items:center;padding:0 22px}.search input{flex:1;border:0;outline:0;background:transparent;color:$text;font-size:24px}.search button{border:0;background:transparent;color:$text;font-size:27px}.pill{height:58px;padding:0 22px;border-radius:29px;background:$panel2;border:1px solid $border;display:flex;align-items:center;font-size:20px;font-weight:800}.iconBtn{width:58px;height:58px;border-radius:29px;background:$panel2;border:1px solid $border;display:flex;align-items:center;justify-content:center;font-size:25px}.content{overflow:auto;padding:24px 28px 46px}.content::-webkit-scrollbar{display:none}.chips{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:18px}.chip{padding:10px 17px;border-radius:18px;background:$panel2;border:1px solid $border;font-size:18px}.chip.on{background:$text;color:$bg;font-weight:800}.sectionTitle{display:flex;justify-content:space-between;align-items:end;margin:28px 0 17px}.sectionTitle h2{font-size:34px;margin:0}.sectionTitle span{font-size:18px;color:$sub}.discover{height:292px;border-radius:28px;overflow:hidden;border:1px solid $border;display:grid;grid-template-columns:44% 56%;background:$panel}.discoverCopy{padding:34px 38px;display:flex;flex-direction:column;justify-content:center;background:linear-gradient(135deg,${if (dark) "#151b24,#0f1319" else "#ffffff,#eef4f8"})}.eyebrow{font-size:15px;letter-spacing:2px;color:#4f9dff;font-weight:900;margin-bottom:10px}.discover h1{font-size:46px;line-height:1.08;margin:0 0 12px}.discover p{font-size:21px;line-height:1.5;color:$sub;margin:0}.discoverActions{display:flex;gap:12px;margin-top:20px}.discoverBtn,.discoverGhost{padding:12px 20px;border-radius:22px;font-size:18px;font-weight:800}.discoverBtn{background:$text;color:$bg}.discoverGhost{background:$panel2;border:1px solid $border}.discoverVisual{position:relative;overflow:hidden;background:#000}.discoverVisual img{width:100%;height:100%;object-fit:cover}.visualTag{position:absolute;left:22px;bottom:20px;background:rgba(0,0,0,.68);color:#fff;padding:9px 13px;border-radius:13px;font-size:16px;font-weight:800}.videoGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:25px 18px}.thumb{position:relative;aspect-ratio:16/9;border-radius:15px;overflow:hidden;background:#111;border:1px solid $border}.thumb img{width:100%;height:100%;object-fit:cover}.duration{position:absolute;right:8px;bottom:8px;background:rgba(0,0,0,.8);color:#fff;padding:4px 7px;border-radius:6px;font-size:14px}.ctitle{font-size:22px;font-weight:750;line-height:1.35;margin-top:9px;height:59px;overflow:hidden}.cmeta{font-size:17px;line-height:1.45;color:$sub}.playerPage{display:grid;grid-template-columns:minmax(0,1fr) 560px;gap:28px}.playerBox{position:relative;aspect-ratio:16/9;border-radius:22px;overflow:hidden;background:#000;border:1px solid $border}.playerBox iframe{width:100%;height:100%;border:0}.fullBtn{position:absolute;right:18px;bottom:18px;background:rgba(0,0,0,.76);color:#fff;padding:13px 18px;border:1px solid rgba(255,255,255,.3);border-radius:15px;font-size:23px;font-weight:800}.pTitle{font-size:47px;font-weight:850;line-height:1.23;margin:22px 0 10px}.pMeta{font-size:27px;color:$sub}.channelRow{display:flex;align-items:center;gap:18px;margin-top:22px;padding-bottom:20px;border-bottom:1px solid $border}.avatar{width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,#3188ff,#203b72)}.channelInfo{flex:1}.channelInfo b{display:block;font-size:31px}.channelInfo span{display:block;color:$sub;font-size:23px}.subscribe{background:$text;color:$bg;border-radius:28px;padding:14px 25px;font-size:25px;font-weight:850}.actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}.action{background:$panel2;border:1px solid $border;padding:13px 18px;border-radius:24px;font-size:24px}.desc{background:$panel;border:1px solid $border;border-radius:19px;margin-top:19px;padding:20px 22px;color:$sub;line-height:1.65;font-size:23px}.recommend{background:$panel;border:1px solid $border;border-radius:20px;padding:16px}.tabs{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}.tab{padding:10px 14px;border-radius:17px;background:$panel2;font-size:20px}.tab.on{background:$text;color:$bg;font-weight:800}.rec{display:grid;grid-template-columns:205px 1fr;gap:13px;margin-bottom:17px}.rec img{width:205px;aspect-ratio:16/9;object-fit:cover;border-radius:11px}.recTitle{font-size:23px;font-weight:780;line-height:1.28;max-height:60px;overflow:hidden}.recMeta{font-size:18px;color:$sub;margin-top:5px;line-height:1.4}.historyGrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.progress{height:5px;background:#333;position:absolute;left:0;right:0;bottom:0}.progress i{display:block;height:100%;background:#ff2d35}.result{display:grid;grid-template-columns:390px 1fr;gap:24px;padding:15px 0;border-bottom:1px solid $border}.result img{width:390px;aspect-ratio:16/9;object-fit:cover;border-radius:14px}.rtitle{font-size:27px;font-weight:800;line-height:1.35;margin:4px 0 8px}.rmeta{font-size:18px;line-height:1.5;color:$sub}.empty,.loginCard{background:$panel;border:1px solid $border;border-radius:22px;padding:34px}.loginCard{max-width:1120px}.loginCard h2{font-size:38px;margin:0 0 14px}.loginCard p{font-size:21px;line-height:1.65;color:$sub}.clientRow{display:flex;gap:12px;margin-top:18px}.clientRow input{flex:1;height:58px;border:1px solid $border;background:$panel2;color:$text;border-radius:16px;padding:0 18px;font-size:18px;outline:none}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:54px;border-radius:25px;padding:0 22px;font-size:19px;font-weight:850;background:$text;color:$bg}.btn.alt{background:$panel2;color:$text;border:1px solid $border}.deviceCard{display:grid;grid-template-columns:1fr 300px;gap:28px;align-items:center;margin-top:20px;padding:24px;border-radius:20px;background:$panel2;border:1px solid $border}.code{font-size:54px;letter-spacing:8px;font-weight:900;margin:8px 0}.url{font-size:24px;color:#4f9dff;font-weight:800}.status{font-size:19px;color:$sub;margin-top:10px}.phone{height:210px;border-radius:26px;background:linear-gradient(145deg,#10141b,#2b3544);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px}.phone b{font-size:25px}.phone span{font-size:16px;color:#b9c2cf;margin-top:9px}.settings{max-width:1100px}.row{min-height:80px;border-bottom:1px solid $border;display:flex;align-items:center;justify-content:space-between;font-size:23px}.row span:last-child{color:$sub}@media(max-width:1700px){.app{grid-template-columns:270px 1fr}.playerPage{grid-template-columns:minmax(0,1fr) 470px}.rec{grid-template-columns:170px 1fr}.rec img{width:170px}.pTitle{font-size:42px}.pMeta{font-size:24px}.channelInfo b{font-size:28px}.action{font-size:22px}.desc{font-size:21px}}
        </style><script>function goSearch(){var q=document.getElementById('q').value.trim();if(q)location.href='c16://search?q='+encodeURIComponent(q);return false}function saveClient(){var v=document.getElementById('cid').value.trim();location.href='c16://saveClient?id='+encodeURIComponent(v)}</script></head><body><div class='app'><aside class='sidebar'><div class='brand'><div class='logo'>▶</div><div><strong>C16 YouTube</strong><small>Video for a better drive</small></div></div>${nav("home","⌂","首页","home")}${nav("search","⌕","探索","search?q=travel")}${nav("subs","▣","订阅","subscriptions")}${nav("history","◷","历史记录","history")}${nav("favorites","♡","我的收藏","favorites")}${nav("local","▤","本地视频","local")}${nav("settings","⚙","设置","settings")}<div style='flex:1'></div></aside><main class='main'><header class='top'><form class='search' onsubmit='return goSearch()'><input id='q' value='$q' placeholder='搜索 YouTube，发现更大的世界'><button>⌕</button></form><a class='pill' href='c16://login'>$accountLabel</a><a class='iconBtn' href='c16://favorites'>♡</a><a class='iconBtn' href='c16://theme'>${if (dark) "☀" else "☾"}</a></header><section class='content'>$body</section></main></div></body></html>"""
    }

    private fun videoCard(v: Video, history: Boolean = false): String {
        val p = if (history) "<div class='progress'><i style='width:42%'></i></div>" else ""
        return "<a class='card' href='c16://watch?id=${v.id}'><div class='thumb'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><span class='duration'>${if (v.id == "linlz7-Pnvw") "12:36" else "18:24"}</span>$p</div><div class='ctitle'>${esc(v.title)}</div><div class='cmeta'>${esc(v.channel)}<br>${esc(v.meta)}</div></a>"
    }

    private fun showHome() {
        val cards = videos.take(8).joinToString("") { videoCard(it) }
        val body = """<div class='chips'><span class='chip on'>推荐</span><a class='chip' href='c16://search?q=music'>音乐</a><a class='chip' href='c16://search?q=travel'>旅行</a><a class='chip' href='c16://search?q=technology'>科技</a><a class='chip' href='c16://search?q=cars'>汽车</a></div><div class='discover'><div class='discoverCopy'><div class='eyebrow'>C16 · IMMERSIVE VIDEO</div><h1>世界很大，出发就好。</h1><p>把旅途交给风景，把时间留给热爱。每一次播放，都像打开另一扇窗。</p><div class='discoverActions'><a class='discoverBtn' href='c16://watch?id=linlz7-Pnvw'>立即播放</a><a class='discoverGhost' href='c16://search?q=travel'>探索更多</a></div></div><a class='discoverVisual' href='c16://watch?id=linlz7-Pnvw'><img src='https://i.ytimg.com/vi/linlz7-Pnvw/maxresdefault.jpg'><span class='visualTag'>Switzerland 4K · Scenic Relaxation</span></a></div><div class='sectionTitle'><h2>为你推荐</h2><span>精选内容 · 大屏优化</span></div><div class='videoGrid'>$cards</div>"""
        load(shell("home", body))
    }

    private fun showSearch(q: String) {
        val decoded = try { URLDecoder.decode(q, StandardCharsets.UTF_8.name()) } catch (_: Exception) { q }
        val pool = if (decoded.lowercase().contains("music")) videos.filter { it.channel.contains("Music", true) || it.title.contains("音乐") } else videos
        val results = pool.take(7).joinToString("") { v -> "<a class='result' href='c16://watch?id=${v.id}'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><div><div class='rtitle'>${esc(v.title)}</div><div class='rmeta'>${esc(v.channel)} · ${esc(v.meta)}</div><div class='rmeta' style='margin-top:10px'>为 C16 大屏优化，点击进入沉浸式播放。</div></div></a>" }
        load(shell("search", "<div class='chips'><span class='chip on'>全部</span><span class='chip'>视频</span><span class='chip'>频道</span><span class='chip'>播放列表</span></div>$results", decoded))
    }

    private fun showPlayer(id: String) {
        val current = videos.find { it.id == id } ?: videos.first()
        addHistory(current.id)
        val fav = prefs.getStringSet("favorites", emptySet()).orEmpty().contains(current.id)
        val recs = videos.filter { it.id != current.id }.take(6).joinToString("") { v -> "<a class='rec' href='c16://watch?id=${v.id}'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><div><div class='recTitle'>${esc(v.title)}</div><div class='recMeta'>${esc(v.channel)}<br>${esc(v.meta)}</div></div></a>" }
        val body = """<div class='playerPage'><div><div class='playerBox'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0' allow='autoplay; encrypted-media; picture-in-picture'></iframe><a class='fullBtn' href='c16://fullscreen?id=${current.id}'>⛶ 全屏</a></div><div class='pTitle'>${esc(current.title)}</div><div class='pMeta'>${esc(current.meta)}　#4K #C16</div><div class='channelRow'><div class='avatar'></div><div class='channelInfo'><b>${esc(current.channel)}</b><span>频道内容 · 为车机大屏优化</span></div><span class='subscribe'>订阅</span></div><div class='actions'><span class='action'>👍 56万</span><span class='action'>↗ 分享</span><a class='action' href='c16://favorite?id=${current.id}'>${if (fav) "♥ 已收藏" else "♡ 收藏"}</a><span class='action'>•••</span></div><div class='desc'>播放页面采用车机大字号排版，标题、频道信息、操作按钮和右侧推荐均针对 2560×1440 横屏重新放大。</div></div><aside class='recommend'><div class='tabs'><span class='tab on'>推荐</span><span class='tab'>相关视频</span><span class='tab'>来自作者</span></div>$recs</aside></div>"""
        load(shell("", body))
    }

    private fun showFullscreen(id: String) {
        val current = videos.find { it.id == id } ?: videos.first()
        fullscreenVideoId = current.id
        val html = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#000}.stage{position:fixed;inset:0}.stage iframe{width:100%;height:100%;border:0}.back{position:absolute;left:26px;top:22px;z-index:5;background:rgba(0,0,0,.65);color:#fff;padding:14px 20px;border-radius:24px;font:800 22px sans-serif;text-decoration:none}</style></head><body><div class='stage'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0' allow='autoplay; encrypted-media; picture-in-picture'></iframe><a class='back' href='c16://watch?id=${current.id}'>‹ 返回</a></div></body></html>"""
        web.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun addHistory(id: String) {
        val list = prefs.getString("history", "").orEmpty().split(',').filter { it.isNotBlank() }.toMutableList()
        list.remove(id); list.add(0, id)
        prefs.edit().putString("history", list.take(18).joinToString(",")).apply()
    }

    private fun showHistory() {
        val ids = prefs.getString("history", "").orEmpty().split(',').filter { it.isNotBlank() }
        val list = if (ids.isEmpty()) videos.take(6) else ids.mapNotNull { id -> videos.find { it.id == id } }
        load(shell("history", "<div class='sectionTitle'><h2>历史记录</h2><span>继续上次的观看</span></div><div class='historyGrid'>${list.joinToString("") { videoCard(it, true) }}</div>"))
    }

    private fun toggleFavorite(id: String) {
        val set = prefs.getStringSet("favorites", emptySet())?.toMutableSet() ?: mutableSetOf()
        if (!set.add(id)) set.remove(id)
        prefs.edit().putStringSet("favorites", set).apply(); showPlayer(id)
    }

    private fun showFavorites() {
        val list = prefs.getStringSet("favorites", emptySet()).orEmpty().mapNotNull { id -> videos.find { it.id == id } }
        val body = if (list.isEmpty()) "<div class='sectionTitle'><h2>我的收藏</h2></div><div class='empty'>还没有收藏视频。</div>" else "<div class='sectionTitle'><h2>我的收藏</h2><span>${list.size} 个视频</span></div><div class='videoGrid'>${list.joinToString("") { videoCard(it) }}</div>"
        load(shell("favorites", body))
    }

    private fun showSubscriptions() = load(shell("subs", "<div class='sectionTitle'><h2>订阅</h2><span>登录后可同步 YouTube 订阅</span></div><div class='videoGrid'>${videos.take(8).joinToString("") { videoCard(it) }}</div>"))
    private fun showLocal() = load(shell("local", "<div class='sectionTitle'><h2>本地视频</h2><span>车机媒体库</span></div><div class='empty'>本地视频索引将在后续版本接入。</div>"))

    private fun showDeviceLogin() {
        val clientId = prefs.getString("oauth_client_id", "").orEmpty()
        val token = prefs.getString("access_token", "").orEmpty()
        val account = prefs.getString("account_name", "").orEmpty()
        val body = if (token.isNotBlank()) {
            """<div class='loginCard'><h2>Google / YouTube 已授权</h2><p>${if (account.isBlank()) "设备授权已经完成。" else "当前账号：${esc(account)}"}</p><div style='display:flex;gap:12px;margin-top:18px'><a class='btn' href='c16://home'>返回首页</a><a class='btn alt' href='c16://logout'>退出账号</a></div></div>"""
        } else {
            """<div class='loginCard'><h2>手机设备码登录</h2><p>这台 C16 不需要安装浏览器。车机会向 Google 请求一个设备码，你只需用手机打开 Google 的设备授权页面并输入验证码即可。整个流程不需要在车机里输入 Google 密码。</p><div class='clientRow'><input id='cid' value='${esc(clientId)}' placeholder='粘贴 Google OAuth Client ID（TVs and Limited Input devices）'><a class='btn alt' href='javascript:saveClient()'>保存 Client ID</a></div><p style='font-size:16px'>需要先在 Google Cloud 创建“TVs and Limited Input devices”类型 OAuth 客户端，并启用 YouTube Data API。Client ID 只用于设备授权，不需要 Client Secret。</p>${if (clientId.isNotBlank()) "<a class='btn' href='c16://deviceStart'>生成设备码</a>" else ""}</div>"""
        }
        load(shell("", body))
    }

    private fun startDeviceFlow() {
        val clientId = prefs.getString("oauth_client_id", "").orEmpty().trim()
        if (clientId.isBlank()) { Toast.makeText(this, "请先填写 OAuth Client ID", Toast.LENGTH_LONG).show(); showDeviceLogin(); return }
        showDeviceStatus("正在向 Google 请求设备码…", "", "", false)
        Thread {
            try {
                val response = postForm("https://oauth2.googleapis.com/device/code", mapOf("client_id" to clientId, "scope" to "openid profile email https://www.googleapis.com/auth/youtube.readonly"))
                val json = JSONObject(response)
                if (!json.has("device_code")) throw IllegalStateException(json.optString("error_description", json.optString("error", "无法获取设备码")))
                val deviceCode = json.getString("device_code")
                val userCode = json.getString("user_code")
                val verification = json.optString("verification_url", json.optString("verification_uri", "https://www.google.com/device"))
                val interval = json.optInt("interval", 5).coerceAtLeast(5)
                val expires = json.optInt("expires_in", 1800)
                runOnUiThread { showDeviceStatus("请用手机完成授权", userCode, verification, true) }
                pollToken(clientId, deviceCode, interval, expires)
            } catch (e: Exception) {
                runOnUiThread { showDeviceStatus("设备登录启动失败：${esc(e.message ?: "未知错误")}", "", "", false) }
            }
        }.start()
    }

    private fun showDeviceStatus(title: String, code: String, url: String, active: Boolean) {
        val detail = if (active) """<div class='deviceCard'><div><div style='font-size:24px;font-weight:850'>$title</div><div class='code'>${esc(code)}</div><div class='url'>${esc(url)}</div><div class='status'>在手机浏览器打开上面的地址，登录 Google 后输入此验证码。车机会自动检测授权结果。</div></div><div class='phone'><b>📱 用手机完成登录</b><span>无需在车机输入账号密码<br>无需安装浏览器</span></div></div>""" else "<div class='deviceCard'><div><div style='font-size:24px;font-weight:850'>$title</div><div class='status'>请稍候…</div></div></div>"
        load(shell("", "<div class='loginCard'><h2>Google 设备登录</h2>$detail</div>"))
    }

    private fun pollToken(clientId: String, deviceCode: String, initialInterval: Int, expiresIn: Int) {
        Thread {
            var interval = initialInterval
            val deadline = System.currentTimeMillis() + expiresIn * 1000L
            while (System.currentTimeMillis() < deadline) {
                Thread.sleep(interval * 1000L)
                try {
                    val response = postForm("https://oauth2.googleapis.com/token", mapOf("client_id" to clientId, "device_code" to deviceCode, "grant_type" to "urn:ietf:params:oauth:grant-type:device_code"))
                    val json = JSONObject(response)
                    if (json.has("access_token")) {
                        val access = json.getString("access_token")
                        val refresh = json.optString("refresh_token", "")
                        prefs.edit().putString("access_token", access).putString("refresh_token", refresh).apply()
                        val name = fetchAccountName(access)
                        if (name.isNotBlank()) prefs.edit().putString("account_name", name).apply()
                        runOnUiThread { Toast.makeText(this, "Google / YouTube 授权成功", Toast.LENGTH_LONG).show(); showDeviceLogin() }
                        return@Thread
                    }
                    when (json.optString("error")) {
                        "authorization_pending" -> Unit
                        "slow_down" -> interval += 5
                        "access_denied" -> { runOnUiThread { showDeviceStatus("授权已取消", "", "", false) }; return@Thread }
                        "expired_token" -> { runOnUiThread { showDeviceStatus("设备码已过期，请重新生成", "", "", false) }; return@Thread }
                    }
                } catch (_: Exception) { }
            }
            runOnUiThread { showDeviceStatus("设备码已过期，请重新生成", "", "", false) }
        }.start()
    }

    private fun fetchAccountName(accessToken: String): String {
        return try {
            val c = URL("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true").openConnection() as HttpURLConnection
            c.requestMethod = "GET"; c.setRequestProperty("Authorization", "Bearer $accessToken"); c.connectTimeout = 12000; c.readTimeout = 12000
            val text = c.inputStream.bufferedReader().use { it.readText() }
            JSONObject(text).optJSONArray("items")?.optJSONObject(0)?.optJSONObject("snippet")?.optString("title", "").orEmpty()
        } catch (_: Exception) { "" }
    }

    private fun postForm(endpoint: String, params: Map<String, String>): String {
        val body = params.entries.joinToString("&") { "${URLEncoder.encode(it.key, "UTF-8") }=${URLEncoder.encode(it.value, "UTF-8")}" }
        val c = URL(endpoint).openConnection() as HttpURLConnection
        c.requestMethod = "POST"; c.doOutput = true; c.connectTimeout = 15000; c.readTimeout = 15000
        c.setRequestProperty("Content-Type", "application/x-www-form-urlencoded")
        c.outputStream.use { it.write(body.toByteArray(StandardCharsets.UTF_8)) }
        val stream = if (c.responseCode in 200..299) c.inputStream else c.errorStream
        return stream.bufferedReader().use { it.readText() }
    }

    private fun showSettings() {
        val clientReady = prefs.getString("oauth_client_id", "").orEmpty().isNotBlank()
        val logged = prefs.getString("access_token", "").orEmpty().isNotBlank()
        val body = """<div class='settings'><div class='sectionTitle'><h2>设置</h2><span>C16 YouTube v2.3</span></div><div class='row'><span>主题模式</span><span>${if (dark) "深色" else "浅色"}</span></div><div class='row'><span>播放页字号</span><span>车机超大字版</span></div><div class='row'><span>登录方式</span><span>Google 设备码授权</span></div><div class='row'><span>OAuth Client ID</span><span>${if (clientReady) "已配置" else "未配置"}</span></div><div class='row'><span>账号状态</span><span>${if (logged) "已授权" else "未登录"}</span></div><div class='row'><span>关于</span><span>v2.3.40041</span></div></div>"""
        load(shell("settings", body))
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        val full = fullscreenVideoId
        if (full != null) showPlayer(full) else if (web.canGoBack()) web.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        CookieManager.getInstance().flush(); web.destroy(); super.onDestroy()
    }
}
