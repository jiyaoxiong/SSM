from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# Native WebView fullscreen support for HTML5/YouTube video.
if 'import android.view.ViewGroup' not in s:
    s=s.replace('import android.view.View\n','import android.view.View\nimport android.view.ViewGroup\nimport android.webkit.WebChromeClient.CustomViewCallback\n',1)

field='    private lateinit var web: WebView\n'
if 'private var fullscreenView' not in s:
    s=s.replace(field,field+'    private var fullscreenView: View? = null\n    private var fullscreenCallback: CustomViewCallback? = null\n',1)

old='''        WebView.setWebContentsDebuggingEnabled(true); web.setBackgroundColor(Color.BLACK)
        web.settings.apply{javaScriptEnabled=true;domStorageEnabled=true;databaseEnabled=true;mediaPlaybackRequiresUserGesture=false;useWideViewPort=true;loadWithOverviewMode=true;setSupportZoom(false);mixedContentMode=WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE;cacheMode=WebSettings.LOAD_DEFAULT;userAgentString="Mozilla/5.0 (Linux; Android 12; C16) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
        CookieManager.getInstance().apply{setAcceptCookie(true);setAcceptThirdPartyCookies(web,true)}
        web.webChromeClient=WebChromeClient(); web.webViewClient=object:WebViewClient(){override fun shouldOverrideUrlLoading(view:WebView?,request:WebResourceRequest?):Boolean{val u=request?.url?:return false;if(u.scheme=="c16"){route(u);return true};return false}}
'''
new='''        WebView.setWebContentsDebuggingEnabled(true); web.setBackgroundColor(Color.BLACK);web.setLayerType(View.LAYER_TYPE_HARDWARE,null)
        web.settings.apply{javaScriptEnabled=true;javaScriptCanOpenWindowsAutomatically=true;domStorageEnabled=true;databaseEnabled=true;mediaPlaybackRequiresUserGesture=false;useWideViewPort=true;loadWithOverviewMode=true;setSupportZoom(false);mixedContentMode=WebSettings.MIXED_CONTENT_ALWAYS_ALLOW;cacheMode=WebSettings.LOAD_DEFAULT;userAgentString="Mozilla/5.0 (Linux; Android 12; C16) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
        CookieManager.getInstance().apply{setAcceptCookie(true);setAcceptThirdPartyCookies(web,true);flush()}
        web.webChromeClient=object:WebChromeClient(){
            override fun onShowCustomView(view:View?,callback:CustomViewCallback?){
                if(view==null){callback?.onCustomViewHidden();return}
                if(fullscreenView!=null){callback?.onCustomViewHidden();return}
                fullscreenView=view;fullscreenCallback=callback
                val decor=window.decorView as ViewGroup
                decor.addView(view,ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT));web.visibility=View.GONE
                window.decorView.systemUiVisibility=View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            }
            override fun onHideCustomView(){hideVideoFullscreen()}
        }
        web.webViewClient=object:WebViewClient(){override fun shouldOverrideUrlLoading(view:WebView?,request:WebResourceRequest?):Boolean{val u=request?.url?:return false;if(u.scheme=="c16"){route(u);return true};return false}}
'''
if old not in s: raise SystemExit('v4.6 configureWebView target missing')
s=s.replace(old,new,1)

# Add reliable back handling for native video fullscreen / YouTube web fallback.
marker='    private fun route(u:Uri){'
helper='''    private fun hideVideoFullscreen(){
        val v=fullscreenView?:return
        (v.parent as? ViewGroup)?.removeView(v);fullscreenView=null;web.visibility=View.VISIBLE;fullscreenCallback?.onCustomViewHidden();fullscreenCallback=null
        window.decorView.systemUiVisibility=View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
    }
    @Deprecated("Deprecated in Java")
    override fun onBackPressed(){
        if(fullscreenView!=null){hideVideoFullscreen();return}
        if(web.canGoBack()){web.goBack();return}
        super.onBackPressed()
    }
'''
if 'private fun hideVideoFullscreen()' not in s:
    s=s.replace(marker,helper+marker,1)

# Player routes: reload custom player and same-WebView YouTube watch-page fallback.
route_old='''"watch"->showPlayer(u.getQueryParameter("id").orEmpty());"category"'''
route_new='''"watch"->showPlayer(u.getQueryParameter("id").orEmpty());"playerreload"->{web.clearCache(false);showPlayer(u.getQueryParameter("id").orEmpty())};"watchweb"->showYouTubeWeb(u.getQueryParameter("id").orEmpty());"category"'''
if route_old not in s: raise SystemExit('v4.6 route watch target missing')
s=s.replace(route_old,route_new,1)

# Cleaner SVG chevron for compact sidebar, replacing the ugly text arrow.
s=s.replace('val menu=if(c)"›" else "‹"','val menu=if(c)"<svg viewBox=\'0 0 24 24\'><path d=\'m9 5 7 7-7 7\'/></svg>" else "<svg viewBox=\'0 0 24 24\'><path d=\'m15 5-7 7 7 7\'/></svg>"',1)
s=s.replace("font-size:32px;z-index:30;box-shadow:0 6px 20px rgba(0,0,0,.12)}", "font-size:32px;z-index:30;box-shadow:0 6px 20px rgba(0,0,0,.12)}.collapse svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}",1)

# Player CSS: larger video, resilient loading overlay, compact controls, less intrusive right rail.
css_anchor='.playerBox iframe{width:100%;height:100%;border:0;display:block;position:relative;z-index:1}'
css_add=""".playerBox iframe{width:100%;height:100%;border:0;display:block;position:relative;z-index:2;background:#000}.playerFallback{position:absolute;left:18px;right:18px;bottom:18px;z-index:4;display:flex;justify-content:center;gap:10px;opacity:0;pointer-events:none;transition:.25s}.playerBox.playerSlow .playerFallback{opacity:1;pointer-events:auto}.playerFallback a{padding:11px 17px;border-radius:22px;background:rgba(20,20,20,.88);border:1px solid rgba(255,255,255,.25);color:#fff;font-size:16px;font-weight:800;backdrop-filter:blur(10px)}.playerBox iframe.playerReady+.loading{display:none}.playerStatus{font-size:15px;color:rgba(255,255,255,.75)}"""
if css_anchor not in s: raise SystemExit('v4.6 player css target missing')
s=s.replace(css_anchor,css_add,1)

# Replace iframe URL with a simpler official embed URL and a JS-assisted load/fallback UI.
old_embed='''        val embed="https://www.youtube.com/embed/${Uri.encode(id)}?autoplay=1&playsinline=1&rel=0&modestbranding=1&enablejsapi=1&origin=https%3A%2F%2Fwww.youtube.com"
'''
new_embed='''        val embed="https://www.youtube.com/embed/${Uri.encode(id)}?autoplay=1&playsinline=1&rel=0&enablejsapi=1&fs=1&origin=https%3A%2F%2Fwww.youtube.com&widget_referrer=https%3A%2F%2Fwww.youtube.com%2F"
'''
if old_embed not in s: raise SystemExit('v4.6 embed target missing')
s=s.replace(old_embed,new_embed,1)

old_box='''<div class='playerBox'><div class='loading'><div class='spinner'></div><b style='font-size:22px'>正在准备 YouTube 播放器</b><span>如果仍无法播放，请检查代理与 YouTube 登录状态</span></div><iframe src='$embed' allow='autoplay; encrypted-media; picture-in-picture; fullscreen' allowfullscreen referrerpolicy='strict-origin-when-cross-origin'></iframe></div>'''
new_box='''<div class='playerBox' id='playerBox'><iframe id='ytFrame' src='$embed' allow='autoplay; encrypted-media; picture-in-picture; fullscreen' allowfullscreen referrerpolicy='strict-origin-when-cross-origin' onload="this.classList.add('playerReady');document.getElementById('loadState').innerText='播放器已连接'"></iframe><div class='loading'><div class='spinner'></div><b style='font-size:22px'>正在连接 YouTube</b><span class='playerStatus' id='loadState'>正在加载官方嵌入播放器…</span></div><div class='playerFallback'><a href='c16://playerreload?id=${Uri.encode(id)}'>重新加载</a><a href='c16://watchweb?id=${Uri.encode(id)}'>YouTube 网页模式</a></div></div>'''
if old_box not in s: raise SystemExit('v4.6 player box target missing')
s=s.replace(old_box,new_box,1)

# Replace ugly hamburger action with a clean text control; sidebar itself uses SVG.
s=s.replace("<a class='action' href='c16://sidebar'>☰ 侧栏</a>","<a class='action' href='c16://sidebar'>侧栏显示</a>",1)

# Inject timeout script into player page: show recovery controls if embed takes too long.
old_load='''</aside></div>""";load(shell("",body,true));fetchCommentsAsync(id)
'''
new_load='''</aside></div><script>setTimeout(function(){var b=document.getElementById('playerBox');if(b)b.classList.add('playerSlow')},8000);window.addEventListener('message',function(e){if(typeof e.data==='string'&&e.data.indexOf('onStateChange')>=0){var l=document.querySelector('.loading');if(l)l.style.display='none'}});</script>""";load(shell("",body,true));fetchCommentsAsync(id)
'''
if old_load not in s: raise SystemExit('v4.6 player ending target missing')
s=s.replace(old_load,new_load,1)

# Same-WebView official YouTube page fallback. This does not extract streams or bypass YouTube protections.
method_marker='    private fun showSimple(title:String,copy:String)'
method='''    private fun showYouTubeWeb(id:String){
        if(id.isBlank())return
        currentVideoId=id
        web.loadUrl("https://www.youtube.com/watch?v=${Uri.encode(id)}")
    }
'''
if 'private fun showYouTubeWeb(' not in s:
    if method_marker not in s: raise SystemExit('v4.6 method marker missing')
    s=s.replace(method_marker,method+method_marker,1)

# Visible version label from v4.5 account patch.
s=s.replace('C16 YouTube · V4.5</p>','C16 YouTube · V4.6</p>',1)

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V4.6 player reliability/fullscreen patch')
