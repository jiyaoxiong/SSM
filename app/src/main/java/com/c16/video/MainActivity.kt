package com.android.gallery3d

import android.app.Activity
import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.Gravity
import android.view.KeyEvent
import android.view.View
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import org.json.JSONArray
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

class MainActivity : Activity() {
    private lateinit var root: FrameLayout
    private lateinit var appShell: LinearLayout
    private lateinit var sidebar: LinearLayout
    private lateinit var mainColumn: LinearLayout
    private lateinit var topBar: LinearLayout
    private lateinit var webView: WebView
    private lateinit var searchBox: EditText
    private lateinit var themeButton: TextView
    private lateinit var favoriteButton: TextView
    private lateinit var loginButton: TextView

    private var customView: View? = null
    private var customViewCallback: WebChromeClient.CustomViewCallback? = null
    private var isDark = true
    private var currentSection = "home"

    private val prefs by lazy { getSharedPreferences("c16_video", Context.MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
        isDark = prefs.getBoolean("dark_theme", true)
        buildUi()
        showHome()
    }

    private fun buildUi() {
        root = FrameLayout(this)
        setContentView(root)
        appShell = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        root.addView(appShell, FrameLayout.LayoutParams(-1, -1))

        sidebar = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(18, 24, 18, 24)
        }
        appShell.addView(sidebar, LinearLayout.LayoutParams(360, -1))

        mainColumn = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        appShell.addView(mainColumn, LinearLayout.LayoutParams(0, -1, 1f))

        buildSidebar()
        buildTopBar()
        buildWebView()
        applyTheme(false)
    }

    private fun buildSidebar() {
        val brand = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(10, 4, 8, 18)
        }
        val logo = TextView(this).apply {
            text = "▶"
            textSize = 34f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            background = rounded(Color.rgb(255, 35, 42), 22f)
        }
        brand.addView(logo, LinearLayout.LayoutParams(76, 62))

        val brandText = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(16, 0, 0, 0)
        }
        brandText.addView(TextView(this).apply {
            text = "C16 Video"
            textSize = 36f
            setTypeface(typeface, Typeface.BOLD)
        })
        brandText.addView(TextView(this).apply {
            text = "Enjoy a bigger world"
            textSize = 20f
        })
        brand.addView(brandText)
        sidebar.addView(brand, LinearLayout.LayoutParams(-1, 122))

        addNav("⌂", "首页", "home") { showHome() }
        addNav("◉", "YouTube", "youtube") { openUrl("https://www.youtube.com/") }
        addNav("⌕", "探索", "explore") { openUrl("https://www.youtube.com/feed/explore") }
        addNav("◷", "历史记录", "history") { showHistory() }
        addNav("♡", "我的收藏", "favorites") { showFavorites() }
        addNav("▣", "本地视频", "local") { showMessagePage("本地视频", "本地媒体库将在后续版本加入。") }
        addNav("⚙", "设置", "settings") { showSettings() }

        sidebar.addView(View(this), LinearLayout.LayoutParams(-1, 0, 1f))
    }

    private fun addNav(icon: String, label: String, section: String, action: () -> Unit) {
        val item = TextView(this).apply {
            text = "$icon   $label"
            textSize = 30f
            gravity = Gravity.CENTER_VERTICAL
            setPadding(24, 0, 10, 0)
            tag = section
            setOnClickListener {
                currentSection = section
                refreshNavStyles()
                action()
            }
        }
        sidebar.addView(item, LinearLayout.LayoutParams(-1, 88).apply { setMargins(0, 5, 0, 5) })
    }

    private fun buildTopBar() {
        topBar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(20, 14, 22, 12)
        }
        mainColumn.addView(topBar, LinearLayout.LayoutParams(-1, 118))

        searchBox = EditText(this).apply {
            hint = "搜索 YouTube，发现更大的世界"
            textSize = 30f
            setSingleLine(true)
            setPadding(28, 0, 22, 0)
            setOnEditorActionListener { _, _, _ -> doSearch(); true }
            setOnKeyListener { _, keyCode, event ->
                if (keyCode == KeyEvent.KEYCODE_ENTER && event.action == KeyEvent.ACTION_UP) {
                    doSearch(); true
                } else false
            }
        }
        topBar.addView(searchBox, LinearLayout.LayoutParams(0, 78, 1f).apply { setMargins(0, 0, 16, 0) })
        topBar.addView(topAction("⌕") { doSearch() })

        loginButton = TextView(this).apply {
            text = "登录"
            textSize = 24f
            gravity = Gravity.CENTER
            setTypeface(typeface, Typeface.BOLD)
            setPadding(18, 0, 18, 0)
            setOnClickListener { openYouTubeLogin() }
        }
        topBar.addView(loginButton, LinearLayout.LayoutParams(132, 72).apply { setMargins(8, 0, 8, 0) })

        favoriteButton = topAction("♡") { toggleFavorite() }
        topBar.addView(favoriteButton)
        themeButton = topAction(if (isDark) "☀" else "☾") {
            isDark = !isDark
            prefs.edit().putBoolean("dark_theme", isDark).apply()
            applyTheme(true)
        }
        topBar.addView(themeButton)
    }

    private fun topAction(textValue: String, action: () -> Unit): TextView = TextView(this).apply {
        text = textValue
        textSize = 36f
        gravity = Gravity.CENTER
        setOnClickListener { action() }
        layoutParams = LinearLayout.LayoutParams(78, 72).apply { setMargins(7, 0, 7, 0) }
    }

    private fun buildWebView() {
        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.databaseEnabled = true
            settings.mediaPlaybackRequiresUserGesture = false
            settings.loadsImagesAutomatically = true
            settings.useWideViewPort = true
            settings.loadWithOverviewMode = true
            settings.textZoom = 122
            settings.allowContentAccess = true
            settings.allowFileAccess = false
            settings.setSupportZoom(false)
            setBackgroundColor(Color.TRANSPARENT)

            CookieManager.getInstance().setAcceptCookie(true)
            CookieManager.getInstance().setAcceptThirdPartyCookies(this, true)

            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean = false

                override fun onPageFinished(view: WebView?, url: String?) {
                    url ?: return
                    if (url.contains("youtube.com")) tuneYouTubeLayout(view)
                    if (url.contains("youtube.com/watch") || url.contains("youtu.be/")) captureHistory(view, url)
                    updateFavoriteState(url)
                    updateLoginState(url)
                    CookieManager.getInstance().flush()
                }
            }

            webChromeClient = object : WebChromeClient() {
                override fun onShowCustomView(view: View?, callback: CustomViewCallback?) {
                    if (view == null) return
                    if (customView != null) {
                        callback?.onCustomViewHidden()
                        return
                    }
                    customView = view
                    customViewCallback = callback
                    appShell.visibility = View.GONE
                    root.addView(view, FrameLayout.LayoutParams(-1, -1))
                }

                override fun onHideCustomView() {
                    val v = customView ?: return
                    root.removeView(v)
                    customView = null
                    customViewCallback?.onCustomViewHidden()
                    customViewCallback = null
                    appShell.visibility = View.VISIBLE
                }
            }
        }
        mainColumn.addView(webView, LinearLayout.LayoutParams(-1, 0, 1f).apply { setMargins(18, 0, 22, 18) })
    }

    private fun tuneYouTubeLayout(view: WebView?) {
        val js = """
            (function(){
              var old=document.getElementById('c16-tune-style'); if(old) old.remove();
              var s=document.createElement('style'); s.id='c16-tune-style';
              s.textContent=`
                html{font-size:18px!important}
                body{overflow-x:hidden!important}
                ytd-rich-grid-renderer{--ytd-rich-grid-items-per-row:4!important;--ytd-rich-grid-posts-per-row:4!important}
                ytd-rich-item-renderer{min-width:0!important}
                #video-title{font-size:18px!important;line-height:1.35!important;font-weight:600!important}
                #metadata-line,.ytd-video-meta-block{font-size:14px!important}
                ytd-watch-flexy[flexy] #primary{min-width:0!important}
                ytd-watch-flexy[flexy] #secondary{width:520px!important;min-width:520px!important;max-width:520px!important;padding-left:20px!important}
                ytd-watch-next-secondary-results-renderer #items{display:block!important}
                ytd-compact-video-renderer{display:block!important;width:100%!important;max-width:100%!important;margin-bottom:16px!important}
                ytd-compact-video-renderer #dismissible{display:flex!important;width:100%!important}
                ytd-thumbnail.ytd-compact-video-renderer{width:220px!important;min-width:220px!important;height:124px!important}
                ytd-compact-video-renderer #details{min-width:0!important;padding-left:12px!important}
                ytd-compact-video-renderer #video-title{font-size:17px!important;line-height:1.35!important;max-height:3.9em!important}
                ytd-compact-video-renderer #metadata-line{font-size:13px!important}
              `;
              document.head.appendChild(s);
            })();
        """.trimIndent()
        view?.evaluateJavascript(js, null)
    }

    private fun doSearch() {
        val q = searchBox.text.toString().trim()
        if (q.isEmpty()) return
        val encoded = URLEncoder.encode(q, StandardCharsets.UTF_8.name())
        currentSection = "explore"
        refreshNavStyles()
        openUrl("https://www.youtube.com/results?search_query=$encoded")
    }

    private fun openYouTubeLogin() {
        currentSection = "youtube"
        refreshNavStyles()
        loginButton.text = "登录中…"
        Toast.makeText(this, "正在打开 YouTube 登录页面", Toast.LENGTH_SHORT).show()
        webView.requestFocus(View.FOCUS_DOWN)
        webView.loadUrl("https://www.youtube.com/signin?app=desktop&next=%2F")
    }

    private fun updateLoginState(url: String) {
        if (!::loginButton.isInitialized) return
        val cookies = CookieManager.getInstance().getCookie("https://www.youtube.com/").orEmpty()
        val likelySignedIn = cookies.contains("SAPISID=") || cookies.contains("__Secure-3PAPISID=") || cookies.contains("LOGIN_INFO=")
        loginButton.text = if (likelySignedIn) "账号" else if (url.contains("accounts.google.com")) "登录中…" else "登录"
    }

    private fun openUrl(url: String) {
        webView.loadUrl(url)
        updateFavoriteState(url)
    }

    private fun showHome() {
        currentSection = "home"
        refreshNavStyles()
        webView.loadDataWithBaseURL("https://c16.local/", homeHtml(), "text/html", "UTF-8", null)
    }

    private fun homeHtml(): String {
        val bg = if (isDark) "#0b1017" else "#f4f7fb"
        val card = if (isDark) "#151c26" else "#ffffff"
        val card2 = if (isDark) "#1b2430" else "#eef2f7"
        val text = if (isDark) "#f7f9fc" else "#12161d"
        val sub = if (isDark) "#9da8b7" else "#6d7682"
        val border = if (isDark) "#253140" else "#e0e6ee"

        return """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>
        *{box-sizing:border-box}body{margin:0;padding:22px 22px 44px;background:$bg;color:$text;font-family:Arial,'Noto Sans SC',sans-serif}.chips{display:flex;gap:14px;margin-bottom:20px;flex-wrap:wrap}.chip{padding:15px 28px;border-radius:28px;background:$card2;color:$text;text-decoration:none;font-size:27px}.chip.hot{background:#ff2d35;color:white;font-weight:800}.hero{min-height:430px;border-radius:32px;overflow:hidden;position:relative;background:linear-gradient(118deg,#0b69b8 0%,#10233f 58%,#c86a48 100%);padding:48px 52px;border:1px solid $border;margin-bottom:32px;display:flex;align-items:center}.hero:after{content:'';position:absolute;inset:0;background:radial-gradient(circle at 78% 35%,rgba(255,255,255,.22),transparent 26%),linear-gradient(90deg,rgba(0,0,0,.08),rgba(0,0,0,.36));pointer-events:none}.heroContent{position:relative;z-index:1;max-width:1220px}.hero h1{font-size:68px;line-height:1.12;margin:0 0 22px}.hero p{font-size:28px;line-height:1.55;color:#eef5ff;margin:0;max-width:1080px}.hero .go{display:inline-block;margin-top:28px;background:#fff;color:#121722;padding:18px 34px;border-radius:30px;font-size:26px;text-decoration:none;font-weight:800}.sectionHead{display:flex;align-items:end;justify-content:space-between;margin:32px 0 18px}.sectionHead h2{font-size:38px;margin:0}.sectionHead span{font-size:21px;color:$sub}.videoGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}.videoCard{display:block;background:$card;border:1px solid $border;border-radius:24px;overflow:hidden;text-decoration:none;color:$text;box-shadow:0 8px 24px rgba(0,0,0,.08)}.videoThumb{position:relative;aspect-ratio:16/9;background:#111;overflow:hidden}.videoThumb img{width:100%;height:100%;object-fit:cover;display:block}.playBadge{position:absolute;left:18px;bottom:16px;width:56px;height:56px;border-radius:50%;background:rgba(255,30,45,.94);display:flex;align-items:center;justify-content:center;color:#fff;font-size:23px;padding-left:4px}.videoMeta{padding:16px 18px 18px}.videoTitle{font-size:27px;font-weight:800;line-height:1.28;min-height:69px}.videoSub{font-size:20px;color:$sub;margin-top:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}.card{background:$card;border:1px solid $border;border-radius:24px;padding:0;overflow:hidden;text-decoration:none;color:$text;min-height:255px;box-shadow:0 8px 24px rgba(0,0,0,.08)}.thumb{height:150px;background:linear-gradient(135deg,#2b8bd7,#0a4a86);display:flex;align-items:flex-end;padding:16px;font-size:46px}.thumb.music{background:linear-gradient(135deg,#5d3fd3,#e96fa8)}.thumb.travel{background:linear-gradient(135deg,#0e8d86,#55bfa9)}.thumb.car{background:linear-gradient(135deg,#626c78,#263340)}.thumb.news{background:linear-gradient(135deg,#d25b35,#7a1c2c)}.thumb.movie{background:linear-gradient(135deg,#534197,#1a2344)}.thumb.food{background:linear-gradient(135deg,#d68b33,#6b3824)}.thumb.live{background:linear-gradient(135deg,#d31e32,#661827)}.meta{padding:17px 18px 20px}.title{font-size:29px;font-weight:800;margin-bottom:9px;line-height:1.25}.sub{font-size:21px;line-height:1.38;color:$sub}.foot{margin-top:32px;padding:20px 24px;background:$card;border:1px solid $border;border-radius:20px;color:$sub;font-size:21px}</style></head><body>
        <div class='chips'><a class='chip hot' href='https://www.youtube.com/'>推荐</a><a class='chip' href='https://www.youtube.com/results?search_query=music'>音乐</a><a class='chip' href='https://www.youtube.com/results?search_query=travel+4k'>旅行</a><a class='chip' href='https://www.youtube.com/results?search_query=technology'>科技</a><a class='chip' href='https://www.youtube.com/results?search_query=cars'>汽车</a><a class='chip' href='https://www.youtube.com/results?search_query=food'>美食</a><a class='chip' href='https://www.youtube.com/feed/trending'>热门</a></div>
        <section class='hero'><div class='heroContent'><h1>去看更大的世界</h1><p>光影在屏幕上流动，声音沿旅途延伸。让每一次播放，都成为车窗之外另一段风景的开始。</p><a class='go' href='https://www.youtube.com/'>开始探索 YouTube ▶</a></div></section>

        <div class='sectionHead'><h2>YouTube 精选</h2><span>点击封面即可播放 · 支持全屏</span></div>
        <div class='videoGrid'>
          <a class='videoCard' href='https://www.youtube.com/watch?v=jNQXAC9IVRw'><div class='videoThumb'><img src='https://i.ytimg.com/vi/jNQXAC9IVRw/hqdefault.jpg'><div class='playBadge'>▶</div></div><div class='videoMeta'><div class='videoTitle'>Me at the zoo · YouTube 经典视频</div><div class='videoSub'>YouTube · 直接播放测试</div></div></a>
          <a class='videoCard' href='https://www.youtube.com/watch?v=M7lc1UVf-VE'><div class='videoThumb'><img src='https://i.ytimg.com/vi/M7lc1UVf-VE/hqdefault.jpg'><div class='playBadge'>▶</div></div><div class='videoMeta'><div class='videoTitle'>YouTube Player Demo · 播放能力验证</div><div class='videoSub'>YouTube Developers</div></div></a>
          <a class='videoCard' href='https://www.youtube.com/watch?v=dQw4w9WgXcQ'><div class='videoThumb'><img src='https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg'><div class='playBadge'>▶</div></div><div class='videoMeta'><div class='videoTitle'>音乐精选 · 经典流行视频</div><div class='videoSub'>Music · Full screen ready</div></div></a>
          <a class='videoCard' href='https://www.youtube.com/watch?v=kJQP7kiw5Fk'><div class='videoThumb'><img src='https://i.ytimg.com/vi/kJQP7kiw5Fk/hqdefault.jpg'><div class='playBadge'>▶</div></div><div class='videoMeta'><div class='videoTitle'>全球热门音乐 · 沉浸大屏体验</div><div class='videoSub'>Music · YouTube</div></div></a>
        </div>

        <div class='sectionHead'><h2>为你准备</h2><span>按兴趣快速进入 YouTube</span></div><div class='grid'>
        <a class='card' href='https://www.youtube.com/results?search_query=Switzerland+4K'><div class='thumb travel'>🏔️</div><div class='meta'><div class='title'>4K 风景与旅行</div><div class='sub'>雪山 · 湖泊 · 城市漫游</div></div></a>
        <a class='card' href='https://www.youtube.com/results?search_query=lofi+music'><div class='thumb music'>🎧</div><div class='meta'><div class='title'>音乐与氛围</div><div class='sub'>Lo-fi · Jazz · Relax</div></div></a>
        <a class='card' href='https://www.youtube.com/results?search_query=Leapmotor+C16'><div class='thumb car'>🚙</div><div class='meta'><div class='title'>零跑 C16</div><div class='sub'>评测 · 技巧 · 用车分享</div></div></a>
        <a class='card' href='https://www.youtube.com/feed/trending'><div class='thumb live'>🔥</div><div class='meta'><div class='title'>热门内容</div><div class='sub'>看看 YouTube 正在流行什么</div></div></a>
        <a class='card' href='https://www.youtube.com/results?search_query=technology+documentary'><div class='thumb'>💡</div><div class='meta'><div class='title'>科技与知识</div><div class='sub'>纪录片 · 科普 · 数码</div></div></a>
        <a class='card' href='https://www.youtube.com/results?search_query=movie+trailer'><div class='thumb movie'>🎬</div><div class='meta'><div class='title'>影视</div><div class='sub'>预告 · 影评 · 访谈</div></div></a>
        <a class='card' href='https://www.youtube.com/results?search_query=street+food'><div class='thumb food'>🍜</div><div class='meta'><div class='title'>美食</div><div class='sub'>街头美食 · 烹饪 · 探店</div></div></a>
        <a class='card' href='https://www.youtube.com/results?search_query=world+news'><div class='thumb news'>🌍</div><div class='meta'><div class='title'>世界资讯</div><div class='sub'>新闻 · 访谈 · 深度内容</div></div></a>
        </div><div class='foot'>C16 Video v1.3 · 统一 YouTube 显示比例 · 视频化历史记录 · 播放页单列推荐</div></body></html>"""
    }

    private fun showHistory() {
        val urls = prefs.getStringSet("history", emptySet())?.toList().orEmpty().reversed()
        showHistoryPage(urls)
    }

    private fun showHistoryPage(urls: List<String>) {
        val bg = if (isDark) "#0b1017" else "#f4f7fb"
        val card = if (isDark) "#151c26" else "#ffffff"
        val text = if (isDark) "#f7f9fc" else "#12161d"
        val sub = if (isDark) "#98a4b5" else "#6c7580"
        val border = if (isDark) "#253140" else "#e0e6ee"
        val cards = if (urls.isEmpty()) {
            "<div class='empty'>还没有播放记录。</div>"
        } else {
            urls.joinToString("") { url ->
                val id = youtubeVideoId(url)
                val safeUrl = htmlEscape(url)
                val title = htmlEscape(prefs.getString("history_title_${id ?: url.hashCode()}", "YouTube 视频") ?: "YouTube 视频")
                val thumb = if (id != null) "https://i.ytimg.com/vi/$id/hqdefault.jpg" else ""
                """<a class='hcard' href='$safeUrl'><div class='pic'>${if (thumb.isNotEmpty()) "<img src='$thumb'>" else "<div class='fallback'>▶</div>"}<div class='badge'>▶</div></div><div class='hm'><div class='ht'>$title</div><div class='hs'>YouTube · 继续观看</div></div></a>"""
            }
        }
        val html = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>
            *{box-sizing:border-box}body{margin:0;padding:34px;background:$bg;color:$text;font-family:Arial,'Noto Sans SC',sans-serif}h1{font-size:54px;margin:0 0 24px}.historyGrid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.hcard{display:block;background:$card;border:1px solid $border;border-radius:24px;overflow:hidden;color:$text;text-decoration:none}.pic{position:relative;aspect-ratio:16/9;background:#111;overflow:hidden}.pic img{width:100%;height:100%;object-fit:cover;display:block}.fallback{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:56px;color:white}.badge{position:absolute;left:16px;bottom:14px;width:52px;height:52px;border-radius:50%;background:#ff2d35;color:white;display:flex;align-items:center;justify-content:center;font-size:22px}.hm{padding:17px 18px 20px}.ht{font-size:29px;font-weight:800;line-height:1.3;height:76px;overflow:hidden}.hs{font-size:20px;color:$sub;margin-top:9px}.empty{padding:34px;background:$card;border-radius:22px;color:$sub;font-size:29px}</style></head><body><h1>历史记录</h1><div class='historyGrid'>$cards</div></body></html>"""
        webView.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun showFavorites() {
        showListPage("我的收藏", prefs.getStringSet("favorites", emptySet())?.toList().orEmpty().reversed(), "还没有收藏内容。播放或打开页面后点右上角 ♡。")
    }

    private fun showListPage(title: String, urls: List<String>, emptyText: String) {
        val bg = if (isDark) "#0b1017" else "#f4f7fb"
        val card = if (isDark) "#151c26" else "#ffffff"
        val text = if (isDark) "#f7f9fc" else "#12161d"
        val sub = if (isDark) "#98a4b5" else "#6c7580"
        val rows = if (urls.isEmpty()) {
            "<div class='empty'>$emptyText</div>"
        } else {
            urls.joinToString("") { u ->
                val safe = htmlEscape(u)
                "<a class='row' href=\"$safe\"><div class='play'>▶</div><div><div class='name'>YouTube 内容</div><div class='url'>$safe</div></div></a>"
            }
        }
        val html = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{margin:0;padding:36px;background:$bg;color:$text;font-family:Arial,'Noto Sans SC',sans-serif}h1{font-size:54px}.row{display:flex;align-items:center;gap:22px;background:$card;border-radius:22px;padding:24px;margin:15px 0;color:$text;text-decoration:none}.play{width:72px;height:72px;border-radius:20px;background:#ff2d35;display:flex;align-items:center;justify-content:center;color:white;font-size:30px}.name{font-size:31px;font-weight:bold}.url{font-size:21px;color:$sub;margin-top:8px;max-width:1400px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.empty{padding:34px;background:$card;border-radius:22px;color:$sub;font-size:29px}</style></head><body><h1>$title</h1>$rows</body></html>"""
        webView.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun showSettings() {
        showMessagePage("设置", "当前主题：${if (isDark) "深色" else "浅色"}。点击右上角 ☀ / ☾ 可随时切换。\n\nYouTube 页面已针对 C16 放大并统一布局；播放页右侧推荐强制单列显示。\n\nC16 Video v1.3\n宿主包：com.android.gallery3d\n版本号：40035")
    }

    private fun showMessagePage(title: String, message: String) {
        val bg = if (isDark) "#0b1017" else "#f4f7fb"
        val card = if (isDark) "#151c26" else "#ffffff"
        val text = if (isDark) "#f7f9fc" else "#12161d"
        val safe = message.replace("\n", "<br>")
        webView.loadDataWithBaseURL(
            "https://c16.local/",
            "<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{margin:0;padding:40px;background:$bg;color:$text;font-family:Arial,'Noto Sans SC',sans-serif}h1{font-size:57px}.box{margin-top:26px;background:$card;border-radius:26px;padding:34px;font-size:31px;line-height:1.8}</style></head><body><h1>$title</h1><div class='box'>$safe</div></body></html>",
            "text/html", "UTF-8", null
        )
    }

    private fun captureHistory(view: WebView?, url: String) {
        val js = "(function(){return document.title||'YouTube 视频';})();"
        view?.evaluateJavascript(js) { raw ->
            val title = try { JSONArray("[$raw]").getString(0).removeSuffix(" - YouTube") } catch (_: Exception) { "YouTube 视频" }
            addHistory(url, title)
        } ?: addHistory(url, "YouTube 视频")
    }

    private fun addHistory(url: String, title: String) {
        val existing = LinkedHashSet(prefs.getStringSet("history", emptySet()).orEmpty())
        existing.remove(url)
        existing.add(url)
        while (existing.size > 20) existing.remove(existing.first())
        val id = youtubeVideoId(url)
        prefs.edit()
            .putStringSet("history", existing)
            .putString("history_title_${id ?: url.hashCode()}", title.ifBlank { "YouTube 视频" })
            .apply()
    }

    private fun youtubeVideoId(url: String): String? {
        val watch = Regex("[?&]v=([A-Za-z0-9_-]{6,})").find(url)?.groupValues?.getOrNull(1)
        if (!watch.isNullOrBlank()) return watch
        return Regex("youtu\\.be/([A-Za-z0-9_-]{6,})").find(url)?.groupValues?.getOrNull(1)
    }

    private fun htmlEscape(value: String): String = value.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&#39;").replace("<", "&lt;").replace(">", "&gt;")

    private fun toggleFavorite() {
        val url = webView.url ?: return
        if (!url.startsWith("http")) return
        val favorites = LinkedHashSet(prefs.getStringSet("favorites", emptySet()).orEmpty())
        if (favorites.contains(url)) favorites.remove(url) else favorites.add(url)
        prefs.edit().putStringSet("favorites", favorites).apply()
        updateFavoriteState(url)
    }

    private fun updateFavoriteState(url: String?) {
        if (!::favoriteButton.isInitialized) return
        val set = prefs.getStringSet("favorites", emptySet()).orEmpty()
        val active = url != null && set.contains(url)
        favoriteButton.text = if (active) "♥" else "♡"
        favoriteButton.setTextColor(if (active) Color.rgb(255, 55, 65) else currentTextColor())
    }

    private fun applyTheme(reloadCustomPage: Boolean) {
        val bg = if (isDark) Color.rgb(10, 15, 22) else Color.rgb(245, 247, 251)
        val side = if (isDark) Color.rgb(13, 20, 29) else Color.WHITE
        val top = if (isDark) Color.rgb(11, 17, 24) else Color.rgb(250, 251, 253)
        val text = currentTextColor()
        val sub = if (isDark) Color.rgb(150, 161, 177) else Color.rgb(103, 112, 125)
        val field = if (isDark) Color.rgb(27, 35, 47) else Color.rgb(235, 239, 245)

        root.setBackgroundColor(bg)
        sidebar.setBackgroundColor(side)
        mainColumn.setBackgroundColor(bg)
        topBar.setBackgroundColor(top)
        searchBox.setTextColor(text)
        searchBox.setHintTextColor(sub)
        searchBox.background = rounded(field, 34f)

        for (i in 0 until sidebar.childCount) {
            val v = sidebar.getChildAt(i)
            if (v is TextView) v.setTextColor(text)
            if (v is LinearLayout) {
                for (j in 0 until v.childCount) {
                    val c = v.getChildAt(j)
                    if (c is TextView && c.text != "▶") c.setTextColor(if (c.textSize < 28f) sub else text)
                }
            }
        }

        themeButton.text = if (isDark) "☀" else "☾"
        themeButton.setTextColor(text)
        favoriteButton.setTextColor(text)
        loginButton.setTextColor(text)
        loginButton.background = rounded(field, 26f)
        refreshNavStyles()

        if (reloadCustomPage && webView.url?.startsWith("https://c16.local/") == true) {
            when (currentSection) {
                "home" -> showHome()
                "history" -> showHistory()
                "favorites" -> showFavorites()
                "settings" -> showSettings()
            }
        }
    }

    private fun refreshNavStyles() {
        val text = currentTextColor()
        for (i in 0 until sidebar.childCount) {
            val v = sidebar.getChildAt(i)
            if (v is TextView && v.tag is String) {
                val active = v.tag == currentSection
                v.setTextColor(if (active && isDark) Color.WHITE else if (active) Color.rgb(190, 30, 45) else text)
                v.setTypeface(v.typeface, if (active) Typeface.BOLD else Typeface.NORMAL)
                v.background = if (active) {
                    rounded(if (isDark) Color.rgb(82, 58, 67) else Color.rgb(255, 225, 228), 22f)
                } else transparentDrawable()
            }
        }
    }

    private fun currentTextColor(): Int = if (isDark) Color.rgb(242, 245, 250) else Color.rgb(26, 31, 38)
    private fun rounded(color: Int, radius: Float): GradientDrawable = GradientDrawable().apply { setColor(color); cornerRadius = radius }
    private fun transparentDrawable(): GradientDrawable = GradientDrawable().apply { setColor(Color.TRANSPARENT) }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (customView != null) webView.webChromeClient?.onHideCustomView()
        else if (webView.canGoBack()) webView.goBack()
        else if (currentSection != "home") showHome()
        else super.onBackPressed()
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
