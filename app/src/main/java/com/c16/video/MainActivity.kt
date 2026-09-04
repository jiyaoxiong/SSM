package com.android.gallery3d

import android.app.Activity
import android.content.Context
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.Gravity
import android.view.KeyEvent
import android.view.View
import android.view.ViewGroup
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView
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

    private var customView: View? = null
    private var customViewCallback: WebChromeClient.CustomViewCallback? = null
    private var isDark = true
    private var currentSection = "home"

    private val prefs by lazy { getSharedPreferences("c16_video", Context.MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.decorView.systemUiVisibility = (
            View.SYSTEM_UI_FLAG_FULLSCREEN or
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            )

        isDark = prefs.getBoolean("dark_theme", true)
        buildUi()
        showHome()
    }

    private fun buildUi() {
        root = FrameLayout(this)
        setContentView(root)

        appShell = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
        }
        root.addView(appShell, FrameLayout.LayoutParams(-1, -1))

        sidebar = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(18, 24, 18, 24)
        }
        appShell.addView(sidebar, LinearLayout.LayoutParams(300, -1))

        mainColumn = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
        }
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
            textSize = 31f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            background = rounded(Color.rgb(255, 35, 42), 22f)
        }
        brand.addView(logo, LinearLayout.LayoutParams(72, 58))

        val brandText = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(14, 0, 0, 0)
        }
        val title = TextView(this).apply {
            text = "C16 Video"
            textSize = 28f
            setTypeface(typeface, android.graphics.Typeface.BOLD)
        }
        val subtitle = TextView(this).apply {
            text = "Enjoy a bigger world"
            textSize = 14f
        }
        brandText.addView(title)
        brandText.addView(subtitle)
        brand.addView(brandText)
        sidebar.addView(brand, LinearLayout.LayoutParams(-1, 104))

        addNav("⌂", "首页", "home") { showHome() }
        addNav("◉", "YouTube", "youtube") { openUrl("https://www.youtube.com/") }
        addNav("⌕", "探索", "explore") { openUrl("https://www.youtube.com/feed/explore") }
        addNav("◷", "历史记录", "history") { showHistory() }
        addNav("♡", "我的收藏", "favorites") { showFavorites() }
        addNav("▣", "本地视频", "local") { showMessagePage("本地视频", "本地媒体库将在下一版本加入。") }
        addNav("⚙", "设置", "settings") { showSettings() }

        val spacer = View(this)
        sidebar.addView(spacer, LinearLayout.LayoutParams(-1, 0, 1f))

        val carCard = TextView(this).apply {
            text = "🚙  零跑 C16\n     SA8295P · 2560×1440"
            textSize = 15f
            setPadding(16, 14, 12, 14)
        }
        sidebar.addView(carCard, LinearLayout.LayoutParams(-1, 82))
    }

    private fun addNav(icon: String, label: String, section: String, action: () -> Unit) {
        val item = TextView(this).apply {
            text = "$icon   $label"
            textSize = 20f
            gravity = Gravity.CENTER_VERTICAL
            setPadding(20, 0, 10, 0)
            tag = section
            setOnClickListener {
                currentSection = section
                refreshNavStyles()
                action()
            }
        }
        sidebar.addView(item, LinearLayout.LayoutParams(-1, 74).apply { setMargins(0, 4, 0, 4) })
    }

    private fun buildTopBar() {
        topBar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(20, 14, 22, 12)
        }
        mainColumn.addView(topBar, LinearLayout.LayoutParams(-1, 104))

        searchBox = EditText(this).apply {
            hint = "搜索 YouTube，发现更大的世界"
            textSize = 20f
            singleLine = true
            setPadding(24, 0, 20, 0)
            setOnEditorActionListener { _, _, _ ->
                doSearch()
                true
            }
            setOnKeyListener { _, keyCode, event ->
                if (keyCode == KeyEvent.KEYCODE_ENTER && event.action == KeyEvent.ACTION_UP) {
                    doSearch(); true
                } else false
            }
        }
        topBar.addView(searchBox, LinearLayout.LayoutParams(0, 66, 1f).apply { setMargins(0, 0, 18, 0) })

        val searchBtn = topAction("⌕") { doSearch() }
        topBar.addView(searchBtn)

        favoriteButton = topAction("♡") { toggleFavorite() }
        topBar.addView(favoriteButton)

        themeButton = topAction(if (isDark) "☀" else "☾") {
            isDark = !isDark
            prefs.edit().putBoolean("dark_theme", isDark).apply()
            applyTheme(true)
        }
        topBar.addView(themeButton)
    }

    private fun topAction(text: String, action: () -> Unit): TextView {
        return TextView(this).apply {
            this.text = text
            textSize = 27f
            gravity = Gravity.CENTER
            setOnClickListener { action() }
            layoutParams = LinearLayout.LayoutParams(70, 66).apply { setMargins(7, 0, 7, 0) }
        }
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
                    if (url.contains("youtube.com/watch") || url.contains("youtu.be/")) {
                        addHistory(url)
                    }
                    updateFavoriteState(url)
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

    private fun doSearch() {
        val q = searchBox.text.toString().trim()
        if (q.isEmpty()) return
        val encoded = URLEncoder.encode(q, StandardCharsets.UTF_8.name())
        currentSection = "explore"
        refreshNavStyles()
        openUrl("https://www.youtube.com/results?search_query=$encoded")
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
        return """
            <!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
            <style>
            *{box-sizing:border-box} body{margin:0;padding:18px 18px 34px;background:$bg;color:$text;font-family:Arial,'Noto Sans SC',sans-serif}
            .chips{display:flex;gap:12px;margin-bottom:18px}.chip{padding:11px 22px;border-radius:24px;background:$card2;color:$text;text-decoration:none;font-size:18px}.chip.hot{background:#ff2d35;color:white}
            .hero{height:330px;border-radius:28px;overflow:hidden;position:relative;background:linear-gradient(120deg,#0f6eb8,#14243f 65%,#e28459);padding:38px;border:1px solid $border;margin-bottom:26px}
            .hero:after{content:'';position:absolute;inset:0;background:radial-gradient(circle at 74% 36%,rgba(255,255,255,.20),transparent 24%),linear-gradient(90deg,rgba(0,0,0,.12),rgba(0,0,0,.38));pointer-events:none}
            .hero h1{font-size:54px;margin:0 0 12px;position:relative;z-index:1}.hero p{font-size:22px;color:#e8f1ff;position:relative;z-index:1}.hero .go{display:inline-block;margin-top:34px;background:#fff;color:#121722;padding:15px 28px;border-radius:28px;font-size:19px;text-decoration:none;position:relative;z-index:1;font-weight:bold}
            h2{font-size:27px;margin:24px 0 16px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.card{background:$card;border:1px solid $border;border-radius:22px;padding:0;overflow:hidden;text-decoration:none;color:$text;min-height:210px;box-shadow:0 8px 24px rgba(0,0,0,.08)}
            .thumb{height:132px;background:linear-gradient(135deg,#2b8bd7,#0a4a86);display:flex;align-items:flex-end;padding:14px;font-size:38px}.thumb.music{background:linear-gradient(135deg,#5d3fd3,#e96fa8)}.thumb.travel{background:linear-gradient(135deg,#0e8d86,#55bfa9)}.thumb.car{background:linear-gradient(135deg,#626c78,#263340)}.thumb.news{background:linear-gradient(135deg,#d25b35,#7a1c2c)}.thumb.movie{background:linear-gradient(135deg,#534197,#1a2344)}.thumb.food{background:linear-gradient(135deg,#d68b33,#6b3824)}.thumb.live{background:linear-gradient(135deg,#d31e32,#661827)}
            .meta{padding:14px 16px}.title{font-size:20px;font-weight:700;margin-bottom:7px}.sub{font-size:15px;color:$sub}
            .foot{margin-top:28px;padding:18px 22px;background:$card;border:1px solid $border;border-radius:20px;color:$sub;font-size:16px}
            </style></head><body>
            <div class='chips'>
              <a class='chip hot' href='https://www.youtube.com/'>推荐</a><a class='chip' href='https://www.youtube.com/results?search_query=music'>音乐</a><a class='chip' href='https://www.youtube.com/results?search_query=travel+4k'>旅行</a><a class='chip' href='https://www.youtube.com/results?search_query=technology'>科技</a><a class='chip' href='https://www.youtube.com/results?search_query=cars'>汽车</a><a class='chip' href='https://www.youtube.com/results?search_query=food'>美食</a><a class='chip' href='https://www.youtube.com/feed/trending'>热门</a>
            </div>
            <section class='hero'><h1>去看更大的世界</h1><p>为零跑 C16 打造的大屏视频体验 · YouTube 已验证可播放</p><a class='go' href='https://www.youtube.com/'>开始探索 YouTube ▶</a></section>
            <h2>为你准备</h2>
            <div class='grid'>
              <a class='card' href='https://www.youtube.com/results?search_query=Switzerland+4K'><div class='thumb travel'>🏔️</div><div class='meta'><div class='title'>4K 风景与旅行</div><div class='sub'>雪山 · 湖泊 · 城市漫游</div></div></a>
              <a class='card' href='https://www.youtube.com/results?search_query=lofi+music'><div class='thumb music'>🎧</div><div class='meta'><div class='title'>音乐与氛围</div><div class='sub'>Lo-fi · Jazz · Relax</div></div></a>
              <a class='card' href='https://www.youtube.com/results?search_query=Leapmotor+C16'><div class='thumb car'>🚙</div><div class='meta'><div class='title'>零跑 C16</div><div class='sub'>评测 · 技巧 · 用车分享</div></div></a>
              <a class='card' href='https://www.youtube.com/feed/trending'><div class='thumb live'>🔥</div><div class='meta'><div class='title'>热门内容</div><div class='sub'>看看 YouTube 正在流行什么</div></div></a>
              <a class='card' href='https://www.youtube.com/results?search_query=technology+documentary'><div class='thumb'>💡</div><div class='meta'><div class='title'>科技与知识</div><div class='sub'>纪录片 · 科普 · 数码</div></div></a>
              <a class='card' href='https://www.youtube.com/results?search_query=movie+trailer'><div class='thumb movie'>🎬</div><div class='meta'><div class='title'>影视</div><div class='sub'>预告 · 影评 · 访谈</div></div></a>
              <a class='card' href='https://www.youtube.com/results?search_query=street+food'><div class='thumb food'>🍜</div><div class='meta'><div class='title'>美食</div><div class='sub'>街头美食 · 烹饪 · 探店</div></div></a>
              <a class='card' href='https://www.youtube.com/results?search_query=world+news'><div class='thumb news'>🌍</div><div class='meta'><div class='title'>世界资讯</div><div class='sub'>新闻 · 访谈 · 深度内容</div></div></a>
            </div>
            <div class='foot'>C16 Video v1.0 · 深色 / 浅色主题可切换 · 长按或全屏播放时保留 YouTube 原生播放能力</div>
            </body></html>
        """.trimIndent()
    }

    private fun showHistory() {
        val items = prefs.getStringSet("history", emptySet())?.toList().orEmpty().reversed()
        showListPage("历史记录", items, "还没有播放记录。")
    }

    private fun showFavorites() {
        val items = prefs.getStringSet("favorites", emptySet())?.toList().orEmpty().reversed()
        showListPage("我的收藏", items, "还没有收藏内容。播放或打开页面后点右上角 ♡。")
    }

    private fun showListPage(title: String, urls: List<String>, emptyText: String) {
        val bg = if (isDark) "#0b1017" else "#f4f7fb"
        val card = if (isDark) "#151c26" else "#ffffff"
        val text = if (isDark) "#f7f9fc" else "#12161d"
        val sub = if (isDark) "#98a4b5" else "#6c7580"
        val rows = if (urls.isEmpty()) "<div class='empty'>$emptyText</div>" else urls.joinToString("") { u ->
            val safe = u.replace("&", "&amp;").replace("\"", "&quot;")
            "<a class='row' href=\"$safe\"><div class='play'>▶</div><div><div class='name'>YouTube 内容</div><div class='url'>$safe</div></div></a>"
        }
        val html = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>
            body{margin:0;padding:30px;background:$bg;color:$text;font-family:Arial,'Noto Sans SC',sans-serif}h1{font-size:36px}.row{display:flex;align-items:center;gap:18px;background:$card;border-radius:20px;padding:18px;margin:12px 0;color:$text;text-decoration:none}.play{width:60px;height:60px;border-radius:18px;background:#ff2d35;display:flex;align-items:center;justify-content:center;color:white;font-size:22px}.name{font-size:21px;font-weight:bold}.url{font-size:14px;color:$sub;margin-top:7px;max-width:1400px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.empty{padding:28px;background:$card;border-radius:20px;color:$sub;font-size:19px}</style></head><body><h1>$title</h1>$rows</body></html>"""
        webView.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun showSettings() {
        val mode = if (isDark) "深色" else "浅色"
        showMessagePage("设置", "当前主题：$mode。点击右上角 ☀ / ☾ 可随时切换。\n\nC16 Video v1.0\n宿主包：com.android.gallery3d\n版本号：40032")
    }

    private fun showMessagePage(title: String, message: String) {
        val bg = if (isDark) "#0b1017" else "#f4f7fb"
        val card = if (isDark) "#151c26" else "#ffffff"
        val text = if (isDark) "#f7f9fc" else "#12161d"
        val safe = message.replace("\n", "<br>")
        val html = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{margin:0;padding:34px;background:$bg;color:$text;font-family:Arial,'Noto Sans SC',sans-serif}h1{font-size:38px}.box{margin-top:24px;background:$card;border-radius:24px;padding:28px;font-size:21px;line-height:1.8}</style></head><body><h1>$title</h1><div class='box'>$safe</div></body></html>"""
        webView.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun addHistory(url: String) {
        val existing = LinkedHashSet(prefs.getStringSet("history", emptySet()).orEmpty())
        existing.remove(url)
        existing.add(url)
        while (existing.size > 20) existing.remove(existing.first())
        prefs.edit().putStringSet("history", existing).apply()
    }

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
        favoriteButton.text = if (url != null && set.contains(url)) "♥" else "♡"
        favoriteButton.setTextColor(if (url != null && set.contains(url)) Color.rgb(255, 55, 65) else currentTextColor())
    }

    private fun applyTheme(reloadCustomPage: Boolean) {
        val bg = if (isDark) Color.rgb(10, 15, 22) else Color.rgb(245, 247, 251)
        val side = if (isDark) Color.rgb(13, 20, 29) else Color.rgb(255, 255, 255)
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
        searchBox.background = rounded(field, 30f)

        for (i in 0 until sidebar.childCount) {
            val v = sidebar.getChildAt(i)
            if (v is TextView) v.setTextColor(text)
            if (v is LinearLayout) {
                for (j in 0 until v.childCount) {
                    val c = v.getChildAt(j)
                    if (c is TextView && c.text != "▶") c.setTextColor(if (c.textSize < 18f) sub else text)
                }
            }
        }
        themeButton.text = if (isDark) "☀" else "☾"
        themeButton.setTextColor(text)
        favoriteButton.setTextColor(text)
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
                v.setTextColor(if (active) Color.WHITE else text)
                v.background = if (active) rounded(if (isDark) Color.rgb(82, 58, 67) else Color.rgb(255, 225, 228), 20f) else Color.TRANSPARENT.toDrawable()
            }
        }
    }

    private fun currentTextColor(): Int = if (isDark) Color.rgb(242, 245, 250) else Color.rgb(26, 31, 38)

    private fun rounded(color: Int, radius: Float): GradientDrawable = GradientDrawable().apply {
        setColor(color)
        cornerRadius = radius
    }

    private fun Int.toDrawable(): GradientDrawable = GradientDrawable().apply { setColor(this@toDrawable) }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (customView != null) {
            webView.webChromeClient?.onHideCustomView()
        } else if (webView.canGoBack()) {
            webView.goBack()
        } else if (currentSection != "home") {
            showHome()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
