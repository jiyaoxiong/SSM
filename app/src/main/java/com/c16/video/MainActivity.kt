package com.android.printspooler

import android.app.Activity
import android.graphics.Color
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class MainActivity : Activity() {

    private lateinit var webView: WebView
    private lateinit var statusText: TextView
    private lateinit var root: FrameLayout
    private lateinit var content: LinearLayout

    private var customView: View? = null
    private var customViewCallback: WebChromeClient.CustomViewCallback? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.decorView.systemUiVisibility = (
            View.SYSTEM_UI_FLAG_FULLSCREEN or
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            )

        root = FrameLayout(this)
        root.setBackgroundColor(Color.rgb(14, 17, 22))
        setContentView(root)

        content = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(28, 28, 28, 28)
        }
        root.addView(
            content,
            FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
        )

        buildControlPanel()
        buildWebView()
    }

    private fun buildControlPanel() {
        val panel = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.TOP
            setPadding(10, 6, 24, 6)
        }
        content.addView(panel, LinearLayout.LayoutParams(620, ViewGroup.LayoutParams.MATCH_PARENT))

        val title = TextView(this).apply {
            text = "C16 VIDEO TEST"
            setTextColor(Color.WHITE)
            textSize = 34f
            gravity = Gravity.START
        }
        panel.addView(title, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 90))

        val info = TextView(this).apply {
            text = "零跑 C16 · Android 12 · SA8295P\n2560×1440 · WebView 126\n测试版 v0.2"
            setTextColor(Color.LTGRAY)
            textSize = 24f
            setLineSpacing(8f, 1f)
        }
        panel.addView(info, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 190))

        statusText = TextView(this).apply {
            text = "状态：等待测试"
            setTextColor(Color.rgb(120, 220, 160))
            textSize = 22f
            setPadding(0, 0, 0, 16)
        }
        panel.addView(statusText, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 90))

        panel.addView(makeButton("① 网络测试") { testNetwork() })
        panel.addView(makeButton("② 打开 YouTube 首页") {
            statusText.text = "状态：正在加载 YouTube 首页…"
            webView.loadUrl("https://www.youtube.com/")
        })
        panel.addView(makeButton("③ 播放测试视频") { loadYouTubeEmbed() })
        panel.addView(makeButton("④ 重新加载") { webView.reload() })
        panel.addView(makeButton("⑤ 清空页面") {
            webView.loadUrl("about:blank")
            statusText.text = "状态：页面已清空"
        })
    }

    private fun makeButton(text: String, action: () -> Unit): Button {
        return Button(this).apply {
            this.text = text
            textSize = 24f
            isAllCaps = false
            setOnClickListener { action() }
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                105
            ).apply { setMargins(0, 0, 0, 18) }
        }
    }

    private fun buildWebView() {
        webView = WebView(this).apply {
            setBackgroundColor(Color.BLACK)
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.mediaPlaybackRequiresUserGesture = false
            settings.loadsImagesAutomatically = true
            settings.useWideViewPort = true
            settings.loadWithOverviewMode = true
            settings.allowContentAccess = true
            settings.allowFileAccess = false

            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                    return false
                }

                override fun onPageFinished(view: WebView?, url: String?) {
                    statusText.text = "状态：页面已加载"
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
                    content.visibility = View.GONE
                    root.addView(
                        view,
                        FrameLayout.LayoutParams(
                            FrameLayout.LayoutParams.MATCH_PARENT,
                            FrameLayout.LayoutParams.MATCH_PARENT
                        )
                    )
                }

                override fun onHideCustomView() {
                    val view = customView ?: return
                    root.removeView(view)
                    customView = null
                    customViewCallback?.onCustomViewHidden()
                    customViewCallback = null
                    content.visibility = View.VISIBLE
                }
            }
        }

        content.addView(webView, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f))
    }

    private fun loadYouTubeEmbed() {
        statusText.text = "状态：正在加载 YouTube 嵌入播放器…"
        val url = "https://www.youtube.com/embed/M7lc1UVf-VE?playsinline=1&rel=0&autoplay=0"
        val headers = mapOf("Referer" to "https://www.youtube.com/")
        webView.loadUrl(url, headers)
    }

    private fun testNetwork() {
        val cm = getSystemService(CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork
        val caps = cm.getNetworkCapabilities(network)
        val online = caps?.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) == true
        statusText.text = if (online) "状态：系统网络可用，正在测试 YouTube…" else "状态：没有可用网络"

        if (!online) return

        thread {
            try {
                val connection = URL("https://www.youtube.com/").openConnection() as HttpURLConnection
                connection.connectTimeout = 7000
                connection.readTimeout = 7000
                connection.instanceFollowRedirects = true
                connection.requestMethod = "GET"
                val code = connection.responseCode
                connection.disconnect()
                runOnUiThread {
                    statusText.text = "状态：YouTube 网络响应 HTTP $code"
                }
            } catch (e: Exception) {
                runOnUiThread {
                    statusText.text = "状态：访问 YouTube 失败：${e.javaClass.simpleName}"
                }
            }
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (customView != null) {
            webView.webChromeClient?.onHideCustomView()
        } else if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
