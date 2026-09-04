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
    private lateinit var shell: LinearLayout
    private lateinit var sidebar: LinearLayout
    private lateinit var main: LinearLayout
    private lateinit var topbar: LinearLayout
    private lateinit var web: WebView
    private lateinit var search: EditText
    private lateinit var login: TextView
    private lateinit var favorite: TextView
    private lateinit var theme: TextView

    private var customView: View? = null
    private var customCallback: WebChromeClient.CustomViewCallback? = null
    private var dark = true
    private var section = "home"
    private var watchMode = false
    private val prefs by lazy { getSharedPreferences("c16_video", Context.MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        dark = prefs.getBoolean("dark_theme", true)
        buildUi()
        showHome()
    }

    private fun buildUi() {
        root = FrameLayout(this)
        setContentView(root)
        shell = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        root.addView(shell, FrameLayout.LayoutParams(-1, -1))

        sidebar = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(22, 24, 22, 22)
        }
        shell.addView(sidebar, LinearLayout.LayoutParams(330, -1))

        main = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        shell.addView(main, LinearLayout.LayoutParams(0, -1, 1f))

        buildSidebar()
        buildTopbar()
        buildWebView()
        applyTheme(false)
    }

    private fun buildSidebar() {
        val brand = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(2, 0, 0, 26)
        }
        val logo = TextView(this).apply {
            text = "▶"
            textSize = 28f
            gravity = Gravity.CENTER
            setTextColor(Color.WHITE)
            background = rounded(Color.rgb(255, 28, 40), 18f)
        }
        brand.addView(logo, LinearLayout.LayoutParams(64, 52))
        val titles = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(14, 0, 0, 0) }
        titles.addView(TextView(this).apply { text = "C16 YouTube"; textSize = 28f; setTypeface(typeface, Typeface.BOLD) })
        titles.addView(TextView(this).apply { text = "Video for a better drive"; textSize = 15f })
        brand.addView(titles)
        sidebar.addView(brand, LinearLayout.LayoutParams(-1, 92))

        addNav("⌂", "首页", "home") { showHome() }
        addNav("⌕", "探索", "explore") { openUrl("https://www.youtube.com/feed/explore") }
        addNav("▣", "订阅", "subs") { openUrl("https://www.youtube.com/feed/subscriptions") }
        addNav("◷", "历史记录", "history") { showHistory() }
        addNav("♡", "我的收藏", "favorites") { showFavorites() }
        addNav("▤", "本地视频", "local") { showLocal() }
        addNav("⚙", "设置", "settings") { showSettings() }
        sidebar.addView(View(this), LinearLayout.LayoutParams(-1, 0, 1f))
    }

    private fun addNav(icon: String, title: String, id: String, action: () -> Unit) {
        val v = TextView(this).apply {
            text = "$icon   $title"
            textSize = 25f
            gravity = Gravity.CENTER_VERTICAL
            setPadding(22, 0, 10, 0)
            tag = id
            setOnClickListener {
                section = id
                refreshNav()
                action()
            }
        }
        sidebar.addView(v, LinearLayout.LayoutParams(-1, 72).apply { setMargins(0, 4, 0, 4) })
    }

    private fun buildTopbar() {
        topbar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(18, 12, 18, 10)
        }
        main.addView(topbar, LinearLayout.LayoutParams(-1, 96))

        search = EditText(this).apply {
            hint = "搜索 YouTube，发现更大的世界"
            textSize = 24f
            setSingleLine(true)
            setPadding(26, 0, 20, 0)
            setOnEditorActionListener { _, _, _ -> doSearch(); true }
            setOnKeyListener { _, keyCode, event ->
                if (keyCode == KeyEvent.KEYCODE_ENTER && event.action == KeyEvent.ACTION_UP) { doSearch(); true } else false
            }
        }
        topbar.addView(search, LinearLayout.LayoutParams(0, 64, 1f).apply { setMargins(0, 0, 10, 0) })
        topbar.addView(action("⌕") { doSearch() })

        login = TextView(this).apply {
            text = "账号"
            textSize = 21f
            gravity = Gravity.CENTER
            setTypeface(typeface, Typeface.BOLD)
            setOnClickListener { openLogin() }
        }
        topbar.addView(login, LinearLayout.LayoutParams(112, 60).apply { setMargins(8, 0, 8, 0) })
        favorite = action("♡") { toggleFavorite() }
        topbar.addView(favorite)
        theme = action(if (dark) "☀" else "☾") {
            dark = !dark
            prefs.edit().putBoolean("dark_theme", dark).apply()
            applyTheme(true)
        }
        topbar.addView(theme)
    }

    private fun action(label: String, tap: () -> Unit) = TextView(this).apply {
        text = label
        textSize = 30f
        gravity = Gravity.CENTER
        setOnClickListener { tap() }
        layoutParams = LinearLayout.LayoutParams(66, 60).apply { setMargins(5, 0, 5, 0) }
    }

    private fun buildWebView() {
        web = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.databaseEnabled = true
            settings.mediaPlaybackRequiresUserGesture = false
            settings.loadsImagesAutomatically = true
            settings.useWideViewPort = true
            settings.loadWithOverviewMode = true
            settings.textZoom = 100
            settings.setSupportZoom(false)
            settings.allowFileAccess = false
            setBackgroundColor(Color.TRANSPARENT)
            CookieManager.getInstance().setAcceptCookie(true)
            CookieManager.getInstance().setAcceptThirdPartyCookies(this, true)

            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean = false
                override fun onPageFinished(view: WebView?, url: String?) {
                    url ?: return
                    val watch = url.contains("youtube.com/watch") || url.contains("youtu.be/")
                    setWatchMode(watch)
                    if (url.contains("youtube.com")) tuneYoutube(view, watch)
                    if (watch) captureHistory(view, url)
                    updateFavorite(url)
                    updateLogin(url)
                    CookieManager.getInstance().flush()
                }
            }
            webChromeClient = object : WebChromeClient() {
                override fun onShowCustomView(view: View?, callback: CustomViewCallback?) {
                    if (view == null) return
                    customView = view
                    customCallback = callback
                    shell.visibility = View.GONE
                    root.addView(view, FrameLayout.LayoutParams(-1, -1))
                }
                override fun onHideCustomView() {
                    val v = customView ?: return
                    root.removeView(v)
                    customView = null
                    customCallback?.onCustomViewHidden()
                    customCallback = null
                    shell.visibility = View.VISIBLE
                }
            }
        }
        main.addView(web, LinearLayout.LayoutParams(-1, 0, 1f).apply { setMargins(14, 0, 18, 16) })
    }

    private fun setWatchMode(enabled: Boolean) {
        if (watchMode == enabled) return
        watchMode = enabled
        sidebar.visibility = if (enabled) View.GONE else View.VISIBLE
        search.hint = if (enabled) "搜索其他视频" else "搜索 YouTube，发现更大的世界"
    }

    private fun tuneYoutube(view: WebView?, watch: Boolean) {
        val css = if (watch) """
          ytd-masthead{display:none!important}
          ytd-app #content{margin-top:0!important}
          ytd-watch-flexy #columns{display:grid!important;grid-template-columns:minmax(0,1fr) 460px!important;gap:20px!important;margin:0 16px!important;max-width:none!important;padding:0!important}
          ytd-watch-flexy #primary{min-width:0!important;width:auto!important;max-width:none!important;padding:0!important;margin:0!important}
          ytd-watch-flexy #secondary{width:460px!important;min-width:460px!important;max-width:460px!important;padding:0!important;margin:0!important}
          #player-container-outer,#player-container-inner,#movie_player{border-radius:18px!important;overflow:hidden!important}
          ytd-watch-metadata #title h1 yt-formatted-string{font-size:22px!important;line-height:1.35!important;font-weight:650!important}
          #secondary ytd-watch-next-secondary-results-renderer #items{display:flex!important;flex-direction:column!important;gap:12px!important}
          #secondary ytd-compact-video-renderer{width:100%!important;margin:0 0 10px!important}
          #secondary ytd-compact-video-renderer #dismissible{display:grid!important;grid-template-columns:190px minmax(0,1fr)!important;gap:11px!important;width:100%!important}
          #secondary ytd-thumbnail.ytd-compact-video-renderer{width:190px!important;min-width:190px!important;height:107px!important;margin:0!important}
          #secondary ytd-compact-video-renderer #details{min-width:0!important;padding:0!important}
          #secondary ytd-compact-video-renderer #video-title{font-size:15px!important;line-height:1.35!important;font-weight:600!important;max-height:2.7em!important}
          #secondary ytd-compact-video-renderer #metadata-line{font-size:12px!important}
          #secondary ytd-reel-shelf-renderer,#secondary ytd-rich-section-renderer{display:none!important}
        """ else """
          ytd-masthead{display:none!important}
          ytd-app #content{margin-top:0!important}
          ytd-rich-grid-renderer{--ytd-rich-grid-items-per-row:4!important;--ytd-rich-grid-posts-per-row:4!important}
          ytd-rich-item-renderer{min-width:0!important;margin-bottom:20px!important}
          #video-title{font-size:16px!important;line-height:1.35!important;font-weight:600!important}
          #metadata-line,.ytd-video-meta-block{font-size:12px!important;line-height:1.35!important}
          ytd-search ytd-video-renderer{margin:0 0 22px!important}
          ytd-search ytd-video-renderer ytd-thumbnail{width:340px!important;min-width:340px!important;height:191px!important}
          ytd-search ytd-video-renderer #video-title{font-size:18px!important;line-height:1.35!important}
        """
        val js = """
          (function(){
            var old=document.getElementById('c16-desktop-style'); if(old) old.remove();
            var s=document.createElement('style'); s.id='c16-desktop-style';
            s.textContent=`html{font-size:16px!important}body{overflow-x:hidden!important}$css`;
            document.head.appendChild(s);
          })();
        """.trimIndent()
        view?.evaluateJavascript(js, null)
    }

    private fun doSearch() {
        val q = search.text.toString().trim()
        if (q.isEmpty()) return
        section = "explore"
        refreshNav()
        openUrl("https://www.youtube.com/results?search_query=" + URLEncoder.encode(q, StandardCharsets.UTF_8.name()))
    }

    private fun openLogin() {
        login.text = "登录中…"
        Toast.makeText(this, "正在打开 YouTube 登录", Toast.LENGTH_SHORT).show()
        web.loadUrl("https://www.youtube.com/signin?app=desktop&next=%2F")
    }

    private fun updateLogin(url: String) {
        val c = CookieManager.getInstance().getCookie("https://www.youtube.com/").orEmpty()
        val ok = c.contains("SAPISID=") || c.contains("__Secure-3PAPISID=") || c.contains("LOGIN_INFO=")
        login.text = if (ok) "账号" else if (url.contains("accounts.google.com")) "登录中…" else "登录"
    }

    private fun openUrl(url: String) { web.loadUrl(url) }

    private fun showHome() {
        setWatchMode(false)
        section = "home"
        refreshNav()
        web.loadDataWithBaseURL("https://c16.local/", homeHtml(), "text/html", "UTF-8", null)
    }

    private fun homeHtml(): String {
        val bg = if (dark) "#07111b" else "#f5f7fa"
        val panel = if (dark) "#0d1824" else "#ffffff"
        val text = if (dark) "#f7f9fc" else "#111820"
        val sub = if (dark) "#95a4b5" else "#6b7682"
        val border = if (dark) "#1d2c3b" else "#dfe5ec"
        return """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>
          *{box-sizing:border-box}body{margin:0;padding:18px 20px 38px;background:$bg;color:$text;font-family:Arial,'Noto Sans SC',sans-serif}.hero{height:350px;border-radius:22px;overflow:hidden;position:relative;background:linear-gradient(90deg,rgba(6,18,32,.2),rgba(6,18,32,.72)),url('https://i.ytimg.com/vi/linlz7-Pnvw/maxresdefault.jpg') center/cover;border:1px solid $border;display:flex;align-items:center;padding:42px}.hero h1{font-size:52px;margin:0 0 14px}.hero p{font-size:24px;line-height:1.55;margin:0;color:#e6eef8}.hero a{display:inline-block;margin-top:24px;background:#fff;color:#111;padding:13px 26px;border-radius:24px;text-decoration:none;font-size:20px;font-weight:700}.head{display:flex;justify-content:space-between;align-items:center;margin:24px 0 14px}.head h2{font-size:30px;margin:0}.head span{font-size:16px;color:$sub}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.card{color:$text;text-decoration:none}.thumb{aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#111}.thumb img{width:100%;height:100%;object-fit:cover}.title{font-size:18px;font-weight:650;line-height:1.35;margin-top:10px;height:49px;overflow:hidden}.meta{font-size:14px;color:$sub;line-height:1.45;margin-top:4px}.strip{display:flex;gap:12px;margin:0 0 16px}.chip{background:$panel;border:1px solid $border;color:$text;padding:9px 18px;border-radius:18px;text-decoration:none;font-size:15px}.chip.on{background:#fff;color:#111;font-weight:700}</style></head><body>
          <div class='strip'><a class='chip on' href='https://www.youtube.com/'>推荐</a><a class='chip' href='https://www.youtube.com/results?search_query=music'>音乐</a><a class='chip' href='https://www.youtube.com/results?search_query=travel+4k'>旅行</a><a class='chip' href='https://www.youtube.com/results?search_query=technology'>科技</a><a class='chip' href='https://www.youtube.com/results?search_query=cars'>汽车</a></div>
          <section class='hero'><div><h1>去看更大的世界</h1><p>让每一次出发，都有新的风景。<br>在路上，遇见更好的自己。</p><a href='https://www.youtube.com/'>开始探索 ›</a></div></section>
          <div class='head'><h2>为你推荐</h2><span>桌面级大屏布局</span></div>
          <div class='grid'>
            ${homeCard("linlz7-Pnvw","Switzerland 4K - Beautiful Nature & Scenic Relaxation","Scenic Relaxation · 4K Travel")}
            ${homeCard("M7lc1UVf-VE","Coffee Shop Ambience · Cozy Jazz Music","Relax · Jazz · Ambience")}
            ${homeCard("jNQXAC9IVRw","零跑 C16 深度体验","汽车 · 评测 · 用车")}
            ${homeCard("kJQP7kiw5Fk","Japan 4K - Autumn in Kyoto","Travel · 4K Relaxation")}
          </div>
        </body></html>"""
    }

    private fun homeCard(id: String, title: String, meta: String): String = """
      <a class='card' href='https://www.youtube.com/watch?v=$id'><div class='thumb'><img src='https://i.ytimg.com/vi/$id/hqdefault.jpg'></div><div class='title'>$title</div><div class='meta'>$meta</div></a>
    """.trimIndent()

    private fun showHistory() {
        setWatchMode(false)
        val list = prefs.getStringSet("history", emptySet())?.toList().orEmpty().reversed()
        showVideoGrid("历史记录", list, "还没有播放记录。")
    }

    private fun showFavorites() {
        setWatchMode(false)
        val list = prefs.getStringSet("favorites", emptySet())?.toList().orEmpty().reversed()
        showVideoGrid("我的收藏", list, "还没有收藏内容。")
    }

    private fun showVideoGrid(title: String, urls: List<String>, empty: String) {
        val bg = if (dark) "#07111b" else "#f5f7fa"
        val card = if (dark) "#0d1824" else "#ffffff"
        val text = if (dark) "#f7f9fc" else "#111820"
        val sub = if (dark) "#95a4b5" else "#6b7682"
        val items = if (urls.isEmpty()) "<div class='empty'>$empty</div>" else urls.joinToString("") { url ->
            val id = videoId(url)
            val key = id ?: url.hashCode().toString()
            val t = escape(prefs.getString("history_title_$key", "YouTube 视频") ?: "YouTube 视频")
            val img = if (id != null) "https://i.ytimg.com/vi/$id/hqdefault.jpg" else ""
            "<a class='card' href='${escape(url)}'><div class='thumb'>${if(img.isNotEmpty()) "<img src='$img'>" else "<div class='fallback'>▶</div>"}</div><div class='title'>$t</div><div class='meta'>YouTube · 继续观看</div></a>"
        }
        val html = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>*{box-sizing:border-box}body{margin:0;padding:26px;background:$bg;color:$text;font-family:Arial,'Noto Sans SC',sans-serif}h1{font-size:34px;margin:0 0 20px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}.card{color:$text;text-decoration:none;background:$card;border-radius:16px;overflow:hidden;padding-bottom:14px}.thumb{aspect-ratio:16/9;background:#111;overflow:hidden}.thumb img{width:100%;height:100%;object-fit:cover}.fallback{height:100%;display:flex;align-items:center;justify-content:center;font-size:50px}.title{font-size:18px;font-weight:650;line-height:1.35;margin:12px 14px 0;height:49px;overflow:hidden}.meta{font-size:14px;color:$sub;margin:6px 14px}.empty{font-size:20px;color:$sub}</style></head><body><h1>$title</h1><div class='grid'>$items</div></body></html>"""
        web.loadDataWithBaseURL("https://c16.local/", html, "text/html", "UTF-8", null)
    }

    private fun showLocal() = showMessage("本地视频", "本地媒体库将在后续版本加入。")
    private fun showSettings() = showMessage("设置", "主题模式：${if (dark) "深色" else "浅色"}<br><br>显示风格：桌面 Web<br>视频列表：4 列<br>播放推荐：右侧单列<br><br>C16 YouTube v1.5")
    private fun showMessage(title: String, body: String) {
        setWatchMode(false)
        val bg = if (dark) "#07111b" else "#f5f7fa"
        val card = if (dark) "#0d1824" else "#ffffff"
        val text = if (dark) "#f7f9fc" else "#111820"
        web.loadDataWithBaseURL("https://c16.local/", "<html><meta name='viewport' content='width=device-width,initial-scale=1'><body style='margin:0;padding:32px;background:$bg;color:$text;font-family:Arial'><h1 style='font-size:36px'>$title</h1><div style='font-size:20px;line-height:1.8;background:$card;padding:28px;border-radius:18px'>$body</div></body></html>", "text/html", "UTF-8", null)
    }

    private fun captureHistory(view: WebView?, url: String) {
        view?.evaluateJavascript("(function(){return document.title||'YouTube 视频';})();") { raw ->
            val title = try { JSONArray("[$raw]").getString(0).removeSuffix(" - YouTube") } catch (_: Exception) { "YouTube 视频" }
            val set = LinkedHashSet(prefs.getStringSet("history", emptySet()).orEmpty())
            set.remove(url); set.add(url); while (set.size > 30) set.remove(set.first())
            val id = videoId(url)
            prefs.edit().putStringSet("history", set).putString("history_title_${id ?: url.hashCode()}", title).apply()
        }
    }

    private fun videoId(url: String): String? {
        Regex("[?&]v=([A-Za-z0-9_-]{6,})").find(url)?.groupValues?.getOrNull(1)?.let { return it }
        return Regex("youtu\\.be/([A-Za-z0-9_-]{6,})").find(url)?.groupValues?.getOrNull(1)
    }

    private fun toggleFavorite() {
        val url = web.url ?: return
        if (!url.startsWith("http")) return
        val set = LinkedHashSet(prefs.getStringSet("favorites", emptySet()).orEmpty())
        if (set.contains(url)) set.remove(url) else set.add(url)
        prefs.edit().putStringSet("favorites", set).apply()
        updateFavorite(url)
    }

    private fun updateFavorite(url: String?) {
        val on = url != null && prefs.getStringSet("favorites", emptySet()).orEmpty().contains(url)
        favorite.text = if (on) "♥" else "♡"
        favorite.setTextColor(if (on) Color.rgb(255, 55, 65) else currentText())
    }

    private fun applyTheme(reload: Boolean) {
        val bg = if (dark) Color.rgb(6, 15, 24) else Color.rgb(245, 247, 250)
        val side = if (dark) Color.rgb(8, 20, 31) else Color.WHITE
        val top = if (dark) Color.rgb(7, 17, 27) else Color.rgb(250, 251, 253)
        val field = if (dark) Color.rgb(25, 42, 60) else Color.rgb(233, 238, 244)
        val text = currentText()
        root.setBackgroundColor(bg); sidebar.setBackgroundColor(side); main.setBackgroundColor(bg); topbar.setBackgroundColor(top)
        search.setTextColor(text); search.setHintTextColor(if (dark) Color.rgb(184,195,207) else Color.rgb(100,112,124)); search.background = rounded(field, 30f)
        login.setTextColor(text); login.background = rounded(field, 24f); theme.setTextColor(text); favorite.setTextColor(text)
        for (i in 0 until sidebar.childCount) {
            val v = sidebar.getChildAt(i)
            if (v is TextView) v.setTextColor(text)
            if (v is LinearLayout) for (j in 0 until v.childCount) {
                val c = v.getChildAt(j)
                if (c is TextView && c.text != "▶") c.setTextColor(text)
            }
        }
        theme.text = if (dark) "☀" else "☾"
        refreshNav()
        if (reload && web.url?.startsWith("https://c16.local/") == true) when(section) { "home" -> showHome(); "history" -> showHistory(); "favorites" -> showFavorites(); "settings" -> showSettings() }
    }

    private fun refreshNav() {
        val normal = currentText()
        for (i in 0 until sidebar.childCount) {
            val v = sidebar.getChildAt(i)
            if (v is TextView && v.tag is String) {
                val on = v.tag == section
                v.setTypeface(v.typeface, if (on) Typeface.BOLD else Typeface.NORMAL)
                v.setTextColor(if (on) Color.WHITE else normal)
                v.background = if (on) rounded(Color.rgb(166, 58, 72), 18f) else transparent()
            }
        }
    }

    private fun currentText() = if (dark) Color.rgb(244,247,251) else Color.rgb(22,29,37)
    private fun rounded(color: Int, radius: Float) = GradientDrawable().apply { setColor(color); cornerRadius = radius }
    private fun transparent() = GradientDrawable().apply { setColor(Color.TRANSPARENT) }
    private fun escape(s: String) = s.replace("&","&amp;").replace("'","&#39;").replace("\"","&quot;").replace("<","&lt;").replace(">","&gt;")

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (customView != null) web.webChromeClient?.onHideCustomView()
        else if (web.canGoBack()) web.goBack()
        else if (section != "home") showHome()
        else super.onBackPressed()
    }

    override fun onDestroy() { web.destroy(); super.onDestroy() }
}
