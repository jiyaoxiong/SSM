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
import java.net.URLDecoder
import java.nio.charset.StandardCharsets

class MainActivity : Activity() {
    private lateinit var root: FrameLayout
    private lateinit var web: WebView
    private var customView: View? = null
    private var customCallback: WebChromeClient.CustomViewCallback? = null
    private var dark = true
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
            webChromeClient = object : WebChromeClient() {
                override fun onShowCustomView(view: View?, callback: CustomViewCallback?) {
                    if (view == null) return
                    customView = view
                    customCallback = callback
                    visibility = View.GONE
                    root.addView(view, FrameLayout.LayoutParams(-1, -1))
                }
                override fun onHideCustomView() {
                    val v = customView ?: return
                    root.removeView(v)
                    customView = null
                    customCallback?.onCustomViewHidden()
                    customCallback = null
                    visibility = View.VISIBLE
                }
            }
        }
        root.addView(web, FrameLayout.LayoutParams(-1, -1))
    }

    private fun handleRoute(uri: Uri) {
        when (uri.host) {
            "home" -> showHome()
            "search" -> showSearch(uri.getQueryParameter("q").orEmpty())
            "watch" -> showPlayer(uri.getQueryParameter("id").orEmpty())
            "history" -> showHistory()
            "favorites" -> showFavorites()
            "subscriptions" -> showSubscriptions()
            "local" -> showLocal()
            "settings" -> showSettings()
            "theme" -> { dark = !dark; prefs.edit().putBoolean("dark", dark).apply(); showHome() }
            "favorite" -> toggleFavorite(uri.getQueryParameter("id").orEmpty())
            "login" -> web.loadUrl("https://www.youtube.com/signin?app=desktop&next=%2F")
        }
    }

    private fun load(html: String) {
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
        fun nav(id:String, icon:String, label:String, host:String) = "<a class='nav ${if(active==id) "on" else ""}' href='c16://$host'><span>$icon</span><b>$label</b></a>"
        val escapedQ = query.replace("'", "&#39;").replace("\"", "&quot;")
        return """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>
        *{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:$bg;color:$text;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC','PingFang SC',Arial,sans-serif}a{text-decoration:none;color:inherit}.app{height:100vh;display:grid;grid-template-columns:270px 1fr;background:$bg}.sidebar{background:$side;border-right:1px solid $border;padding:26px 20px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:14px;height:72px;margin-bottom:24px}.logo{width:56px;height:42px;border-radius:13px;background:#ff1f2d;color:white;display:flex;align-items:center;justify-content:center;font-size:22px}.brandText strong{display:block;font-size:28px;line-height:1.05}.brandText small{display:block;color:$sub;font-size:13px;margin-top:5px}.nav{height:62px;border-radius:16px;display:flex;align-items:center;gap:17px;padding:0 18px;margin:3px 0;color:$text;font-size:20px}.nav span{width:26px;text-align:center;font-size:22px}.nav b{font-weight:600}.nav.on{background:$activeBg;color:$activeText}.main{min-width:0;display:grid;grid-template-rows:94px 1fr}.top{display:flex;align-items:center;padding:16px 28px 12px;gap:14px;border-bottom:1px solid $border;background:$bg}.search{height:58px;flex:1;background:$panel2;border:1px solid $border;border-radius:29px;display:flex;align-items:center;padding:0 20px}.search input{flex:1;background:transparent;border:0;outline:0;color:$text;font-size:20px}.search button{border:0;background:transparent;color:$text;font-size:22px;padding:10px 14px}.pill{height:52px;border-radius:26px;background:$panel2;border:1px solid $border;padding:0 19px;display:flex;align-items:center;justify-content:center;font-size:17px;font-weight:700}.iconBtn{width:52px;height:52px;border-radius:26px;background:$panel2;border:1px solid $border;display:flex;align-items:center;justify-content:center;font-size:22px}.content{overflow:auto;padding:20px 28px 42px;scrollbar-width:none}.content::-webkit-scrollbar{display:none}.sectionTitle{display:flex;align-items:end;justify-content:space-between;margin:26px 0 16px}.sectionTitle h2{font-size:30px;margin:0}.sectionTitle span{font-size:15px;color:$sub}.videoGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px 18px}.card{min-width:0}.thumb{position:relative;aspect-ratio:16/9;border-radius:15px;overflow:hidden;background:#111;border:1px solid $border}.thumb img{width:100%;height:100%;object-fit:cover;display:block}.duration{position:absolute;right:8px;bottom:8px;background:rgba(0,0,0,.78);color:#fff;padding:4px 7px;border-radius:7px;font-size:12px}.ctitle{font-size:18px;font-weight:650;line-height:1.35;margin-top:9px;height:49px;overflow:hidden}.cmeta{font-size:14px;line-height:1.45;color:$sub;margin-top:3px}.hero{height:330px;border-radius:24px;overflow:hidden;position:relative;background:linear-gradient(90deg,rgba(0,0,0,.12),rgba(0,0,0,.68)),url('https://i.ytimg.com/vi/linlz7-Pnvw/maxresdefault.jpg') center/cover;border:1px solid $border;display:flex;align-items:center;padding:44px}.heroText{max-width:720px}.hero h1{font-size:56px;line-height:1.05;margin:0 0 16px;color:#fff}.hero p{font-size:22px;line-height:1.55;color:#eef4fa;margin:0}.heroBtn{display:inline-flex;margin-top:24px;background:#fff;color:#111;padding:13px 24px;border-radius:24px;font-size:18px;font-weight:700}.chips{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}.chip{padding:9px 16px;border-radius:18px;background:$panel2;border:1px solid $border;font-size:15px}.chip.on{background:$text;color:$bg;font-weight:700}.result{display:grid;grid-template-columns:340px 1fr;gap:22px;padding:13px 0;border-bottom:1px solid $border}.result img{width:340px;aspect-ratio:16/9;object-fit:cover;border-radius:14px}.rtitle{font-size:22px;font-weight:700;line-height:1.35;margin:4px 0 8px}.rmeta{color:$sub;font-size:15px;line-height:1.55}.empty{background:$panel;border:1px solid $border;border-radius:20px;padding:34px;color:$sub;font-size:20px}.settings{max-width:980px}.row{height:68px;border-bottom:1px solid $border;display:flex;align-items:center;justify-content:space-between;font-size:19px}.row span:last-child{color:$sub}.playerPage{display:grid;grid-template-columns:minmax(0,1fr) 420px;gap:24px}.playerCol{min-width:0}.playerBox{aspect-ratio:16/9;border-radius:20px;overflow:hidden;background:#000;border:1px solid $border}.playerBox iframe{width:100%;height:100%;border:0}.pTitle{font-size:26px;font-weight:750;line-height:1.35;margin:16px 0 8px}.pMeta{color:$sub;font-size:15px}.channelRow{display:flex;align-items:center;gap:14px;margin-top:18px;padding-bottom:16px;border-bottom:1px solid $border}.avatar{width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#3aa0ff,#204b88)}.channelInfo{flex:1}.channelInfo b{display:block;font-size:17px}.channelInfo span{display:block;color:$sub;font-size:13px;margin-top:3px}.subscribe{background:#fff;color:#111;border-radius:21px;padding:11px 20px;font-weight:700}.actions{display:flex;gap:10px;margin-top:15px}.action{background:$panel2;border:1px solid $border;padding:10px 16px;border-radius:20px;font-size:15px}.desc{background:$panel;border:1px solid $border;border-radius:16px;margin-top:16px;padding:16px 18px;color:$sub;line-height:1.65;font-size:14px}.recommend{background:$panel;border:1px solid $border;border-radius:18px;padding:14px}.tabs{display:flex;gap:8px;margin-bottom:13px}.tab{padding:8px 14px;border-radius:16px;background:$panel2;font-size:13px}.tab.on{background:#fff;color:#111;font-weight:700}.rec{display:grid;grid-template-columns:145px 1fr;gap:11px;margin-bottom:13px}.rec img{width:145px;aspect-ratio:16/9;object-fit:cover;border-radius:10px}.recTitle{font-size:14px;font-weight:650;line-height:1.3;max-height:38px;overflow:hidden}.recMeta{font-size:12px;color:$sub;margin-top:4px;line-height:1.35}.historyGrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.progress{height:4px;background:#25303c;position:absolute;left:0;right:0;bottom:0}.progress i{display:block;height:100%;background:#ff2d35}.favMark{position:absolute;left:10px;top:10px;background:rgba(0,0,0,.65);padding:5px 8px;border-radius:8px;color:white;font-size:12px}@media(max-width:1700px){.app{grid-template-columns:235px 1fr}.videoGrid{grid-template-columns:repeat(4,1fr)}.playerPage{grid-template-columns:minmax(0,1fr) 360px}.rec{grid-template-columns:125px 1fr}.result{grid-template-columns:300px 1fr}.result img{width:300px}}
        </style><script>function goSearch(){var q=document.getElementById('q').value.trim();if(q)location.href='c16://search?q='+encodeURIComponent(q);return false}</script></head><body><div class='app'><aside class='sidebar'><div class='brand'><div class='logo'>▶</div><div class='brandText'><strong>C16 YouTube</strong><small>Video for a better drive</small></div></div>${nav("home","⌂","首页","home")}${nav("search","⌕","探索","search?q=travel")}${nav("subs","▣","订阅","subscriptions")}${nav("history","◷","历史记录","history")}${nav("favorites","♡","我的收藏","favorites")}${nav("local","▤","本地视频","local")}${nav("settings","⚙","设置","settings")}<div style='flex:1'></div></aside><main class='main'><header class='top'><form class='search' onsubmit='return goSearch()'><input id='q' value='$escapedQ' placeholder='搜索 YouTube，发现更大的世界'><button>⌕</button></form><a class='pill' href='c16://login'>账号</a><a class='iconBtn' href='c16://favorites'>♡</a><a class='iconBtn' href='c16://theme'>${if(dark) "☀" else "☾"}</a></header><section class='content'>$body</section></main></div></body></html>"""
    }

    private fun videoCard(v: Video, history: Boolean = false): String {
        val p = if (history) "<div class='progress'><i style='width:38%'></i></div>" else ""
        return "<a class='card' href='c16://watch?id=${v.id}'><div class='thumb'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><span class='duration'>${if(v.id=="linlz7-Pnvw") "12:36" else "18:24"}</span>$p</div><div class='ctitle'>${v.title}</div><div class='cmeta'>${v.channel}<br>${v.meta}</div></a>"
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
        val body = """<div class='playerPage'><div class='playerCol'><div class='playerBox'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0' allow='autoplay; encrypted-media; picture-in-picture' allowfullscreen></iframe></div><div class='pTitle'>${current.title}</div><div class='pMeta'>${current.meta}　#Travel #4K #C16</div><div class='channelRow'><div class='avatar'></div><div class='channelInfo'><b>${current.channel}</b><span>482万订阅者</span></div><span class='subscribe'>订阅</span></div><div class='actions'><span class='action'>👍 56万</span><span class='action'>👎</span><span class='action'>↗ 分享</span><a class='action' href='c16://favorite?id=${current.id}'>${if(fav) "♥ 已收藏" else "♡ 收藏"}</a><span class='action'>•••</span></div><div class='desc'>沉浸式大屏播放界面。播放器保留 YouTube 原生解码与控制能力，标题、频道、操作按钮和右侧推荐均由 C16 YouTube 自己绘制。</div></div><aside class='recommend'><div class='tabs'><span class='tab on'>推荐</span><span class='tab'>相关视频</span><span class='tab'>来自作者</span></div>$recs</aside></div>"""
        load(shell("", body))
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
        val body = """<div class='sectionTitle'><h2>订阅</h2><span>你关注的频道</span></div><div class='chips'><span class='chip on'>Scenic Relaxation</span><span class='chip'>The Jazz Hop Café</span><span class='chip'>National Geographic</span><span class='chip'>TED</span><span class='chip'>Marques Brownlee</span></div><div class='videoGrid'>${videos.take(8).joinToString("") { videoCard(it) }}</div>"""
        load(shell("subs", body))
    }

    private fun showLocal() {
        val body = """<div class='sectionTitle'><h2>本地视频</h2><span>车机媒体库</span></div><div class='videoGrid'><div class='empty'>📁 电影<br><small>本地视频分类</small></div><div class='empty'>📁 音乐 MV<br><small>本地视频分类</small></div><div class='empty'>📁 纪录片<br><small>本地视频分类</small></div><div class='empty'>📁 其他<br><small>本地视频分类</small></div></div>"""
        load(shell("local", body))
    }

    private fun showSettings() {
        val body = """<div class='settings'><div class='sectionTitle'><h2>设置</h2><span>C16 YouTube v2.0</span></div><div class='row'><span>主题模式</span><span>${if(dark) "深色" else "浅色"} ›</span></div><div class='row'><span>视频画质</span><span>自动（推荐） ›</span></div><div class='row'><span>播放设置</span><span>默认 1.0x ›</span></div><div class='row'><span>语言</span><span>简体中文 ›</span></div><div class='row'><span>数据与存储</span><span>清除缓存 ›</span></div><div class='row'><span>关于 C16 YouTube</span><span>v2.0.40038</span></div></div>"""
        load(shell("settings", body))
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (customView != null) {
            web.webChromeClient?.onHideCustomView()
        } else if (web.url?.contains("youtube.com/signin") == true || web.url?.contains("accounts.google.com") == true) {
            showHome()
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
