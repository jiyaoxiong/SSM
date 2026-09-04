from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# AndroidX WebKit APIs let us explicitly enable/query WebView Media Integrity when the
# installed WebView implementation supports it. YouTube documents this as relevant to
# embedded playback in Android WebView.
if 'import androidx.webkit.WebSettingsCompat' not in s:
    anchor='import android.widget.FrameLayout\n'
    imports='''import androidx.webkit.WebSettingsCompat\nimport androidx.webkit.WebViewFeature\nimport androidx.webkit.WebViewMediaIntegrityApiStatusConfig\n'''
    if anchor not in s: raise SystemExit('v4.8 import anchor missing')
    s=s.replace(anchor,anchor+imports,1)

# Explicitly enable Media Integrity with app identity when supported by the installed WebView.
old='''        web.settings.apply{javaScriptEnabled=true;javaScriptCanOpenWindowsAutomatically=true;domStorageEnabled=true;databaseEnabled=true;mediaPlaybackRequiresUserGesture=false;useWideViewPort=true;loadWithOverviewMode=true;setSupportZoom(false);mixedContentMode=WebSettings.MIXED_CONTENT_ALWAYS_ALLOW;cacheMode=WebSettings.LOAD_DEFAULT;userAgentString=WebSettings.getDefaultUserAgent(this@MainActivity)}\n        CookieManager.getInstance().apply{setAcceptCookie(true);setAcceptThirdPartyCookies(web,true);flush()}\n'''
new='''        web.settings.apply{javaScriptEnabled=true;javaScriptCanOpenWindowsAutomatically=true;domStorageEnabled=true;databaseEnabled=true;mediaPlaybackRequiresUserGesture=false;useWideViewPort=true;loadWithOverviewMode=true;setSupportZoom(false);mixedContentMode=WebSettings.MIXED_CONTENT_ALWAYS_ALLOW;cacheMode=WebSettings.LOAD_DEFAULT;userAgentString=WebSettings.getDefaultUserAgent(this@MainActivity)}\n        try{\n            if(WebViewFeature.isFeatureSupported(WebViewFeature.WEBVIEW_MEDIA_INTEGRITY_API_STATUS)){\n                val integrityConfig=WebViewMediaIntegrityApiStatusConfig.Builder(WebViewMediaIntegrityApiStatusConfig.WEBVIEW_MEDIA_INTEGRITY_API_ENABLED).build()\n                WebSettingsCompat.setWebViewMediaIntegrityApiStatus(web.settings,integrityConfig)\n            }\n        }catch(_:Throwable){}\n        CookieManager.getInstance().apply{setAcceptCookie(true);setAcceptThirdPartyCookies(web,true);flush()}\n'''
if old not in s: raise SystemExit('v4.8 WebView settings target missing')
s=s.replace(old,new,1)

# Player diagnostics and persisted preferred playback mode.
route_old='''"watch"->showPlayer(u.getQueryParameter("id").orEmpty());"playerreload"->{web.clearCache(false);showPlayer(u.getQueryParameter("id").orEmpty())};"watchweb"->showYouTubeWeb(u.getQueryParameter("id").orEmpty());"category"'''
route_new='''"watch"->showPlayer(u.getQueryParameter("id").orEmpty());"playerreload"->{web.clearCache(false);showPlayer(u.getQueryParameter("id").orEmpty())};"watchweb"->showYouTubeWeb(u.getQueryParameter("id").orEmpty());"diagnostics"->showPlaybackDiagnostics();"playermode"->{val m=u.getQueryParameter("mode").orEmpty();if(m=="auto"||m=="web")prefs.edit().putString("player_mode",m).apply();showSettings()};"category"'''
if route_old not in s: raise SystemExit('v4.8 route target missing')
s=s.replace(route_old,route_new,1)

# When the user deliberately chooses Web mode, skip the embedded player entirely.
player_start='''    private fun showPlayer(id:String){\n        val v=videos.firstOrNull{it.id==id}?:dynamicVideos[id]?:Video(id,"YouTube 视频","YouTube","正在播放","推荐");currentVideoId=id\n'''
player_new='''    private fun showPlayer(id:String){\n        if(prefs.getString("player_mode","auto")=="web"){showYouTubeWeb(id);return}\n        val v=videos.firstOrNull{it.id==id}?:dynamicVideos[id]?:Video(id,"YouTube 视频","YouTube","正在播放","推荐");currentVideoId=id\n'''
if player_start not in s: raise SystemExit('v4.8 player start target missing')
s=s.replace(player_start,player_new,1)

# Add a diagnostics action to the embed recovery UI.
old_err_actions='''<div class='errActions'><a href='c16://playerreload?id=${Uri.encode(id)}'>重试</a><a href='c16://watchweb?id=${Uri.encode(id)}'>在 YouTube 网页播放</a></div>'''
new_err_actions='''<div class='errActions'><a href='c16://playerreload?id=${Uri.encode(id)}'>重试</a><a href='c16://watchweb?id=${Uri.encode(id)}'>YouTube 网页播放</a><a href='c16://diagnostics'>播放诊断</a></div>'''
if old_err_actions not in s: raise SystemExit('v4.8 error actions target missing')
s=s.replace(old_err_actions,new_err_actions,1)

# Make the slow-player recovery bar include diagnostics as well.
old_fallback='''<div class='playerFallback'><a href='c16://playerreload?id=${Uri.encode(id)}'>重新加载</a><a href='c16://watchweb?id=${Uri.encode(id)}'>YouTube 网页模式</a></div>'''
new_fallback='''<div class='playerFallback'><a href='c16://playerreload?id=${Uri.encode(id)}'>重新加载</a><a href='c16://watchweb?id=${Uri.encode(id)}'>YouTube 网页模式</a><a href='c16://diagnostics'>播放诊断</a></div>'''
if old_fallback not in s: raise SystemExit('v4.8 fallback target missing')
s=s.replace(old_fallback,new_fallback,1)

# Improve error copy: internal YouTube UI errors such as 152-4 are not part of the public
# IFrame API error-code list, so don't misclassify them. Public codes stay explicit.
old_error_js="""if(code==101||code==150)m='视频作者不允许第三方嵌入播放。';else if(code==153)m='播放器请求缺少 YouTube 要求的来源标识。';else if(code==5)m='当前 WebView 无法播放这个 HTML5 视频。';if(t)t.innerText=m+' 可以改用 YouTube 网页模式。'}"""
new_error_js="""if(code==101||code==150)m='视频作者不允许第三方嵌入播放。';else if(code==153)m='播放器请求缺少 YouTube 要求的来源标识或客户端身份。';else if(code==5)m='当前 WebView 无法播放这个 HTML5 视频。';if(t)t.innerText=m+' 可尝试网页模式，或打开播放诊断查看 WebView / Media Integrity 状态。'}"""
if old_error_js not in s: raise SystemExit('v4.8 error JS target missing')
s=s.replace(old_error_js,new_error_js,1)

# Settings gets an explicit player-mode control and diagnostics entry.
old_settings='''        val signed=prefs.getString("access_token","").orEmpty().isNotBlank()\n        val body="""<div class='simple'><h1>设置</h1><p>C16 YouTube · V4.7</p><div style='display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:24px'><a class='chip' href='c16://theme'>${if(dark)"☀ 切换浅色模式" else "☾ 切换深色模式"}</a><a class='chip' href='c16://login'>${if(signed)"YouTube 账号中心" else "手机扫码登录 YouTube"}</a><a class='chip' href='c16://history'>观看历史</a><a class='chip' href='c16://favorites'>我的收藏</a></div></div>"""\n'''
new_settings='''        val signed=prefs.getString("access_token","").orEmpty().isNotBlank()\n        val playerMode=prefs.getString("player_mode","auto").orEmpty()\n        val body="""<div class='simple'><h1>设置</h1><p>C16 YouTube · V4.8</p><div style='display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:24px'><a class='chip' href='c16://theme'>${if(dark)"☀ 切换浅色模式" else "☾ 切换深色模式"}</a><a class='chip' href='c16://login'>${if(signed)"YouTube 账号中心" else "手机扫码登录 YouTube"}</a><a class='chip' href='c16://history'>观看历史</a><a class='chip' href='c16://favorites'>我的收藏</a><a class='chip' href='c16://playermode?mode=${if(playerMode=="web")"auto" else "web"}'>播放模式：${if(playerMode=="web")"YouTube 网页" else "自动嵌入"}</a><a class='chip' href='c16://diagnostics'>播放诊断</a></div><p style='font-size:16px;margin-top:20px'>如果车机持续出现 YouTube 嵌入播放错误，可切换到 YouTube 网页模式；不会提取或绕过 YouTube 视频流。</p></div>"""\n'''
if old_settings not in s: raise SystemExit('v4.8 settings target missing')
s=s.replace(old_settings,new_settings,1)

# Native diagnostics page. It intentionally reports environment capability instead of pretending
# that every device can produce a valid attestation token (real C16 may not include full GMS).
marker='''    private fun showYouTubeWeb(id:String){\n'''
method='''    private fun showPlaybackDiagnostics(){\n        currentVideoId=null\n        val webPkg=try{WebView.getCurrentWebViewPackage()}catch(_:Throwable){null}\n        val webName=webPkg?.packageName?:"未知"\n        val webVer=webPkg?.versionName?:"未知"\n        val integritySupported=try{WebViewFeature.isFeatureSupported(WebViewFeature.WEBVIEW_MEDIA_INTEGRITY_API_STATUS)}catch(_:Throwable){false}\n        val integrityStatus=if(integritySupported){\n            try{\n                when(WebSettingsCompat.getWebViewMediaIntegrityApiStatus(web.settings).defaultStatus){\n                    WebViewMediaIntegrityApiStatusConfig.WEBVIEW_MEDIA_INTEGRITY_API_ENABLED->"已启用（含应用身份）"\n                    WebViewMediaIntegrityApiStatusConfig.WEBVIEW_MEDIA_INTEGRITY_API_ENABLED_WITHOUT_APP_IDENTITY->"已启用（不含应用身份）"\n                    else->"已禁用"\n                }\n            }catch(_:Throwable){"支持，但读取状态失败"}\n        }else "当前 WebView 不支持"\n        val hasGms=try{packageManager.getPackageInfo("com.google.android.gms",0);true}catch(_:Throwable){false}\n        val ua=web.settings.userAgentString.orEmpty()\n        val mode=prefs.getString("player_mode","auto").orEmpty()\n        val rows=listOf(\n            "应用包名" to packageName,\n            "应用版本" to "4.8.40065",\n            "Android" to android.os.Build.VERSION.RELEASE,\n            "WebView 包" to webName,\n            "WebView 版本" to webVer,\n            "Media Integrity" to integrityStatus,\n            "Google Play 服务" to if(hasGms)"已安装" else "未检测到",\n            "页面 Origin" to "https://c16.local",\n            "播放器模式" to if(mode=="web")"YouTube 网页" else "自动嵌入"\n        )\n        val table=rows.joinToString(""){"<div style='display:grid;grid-template-columns:240px 1fr;gap:16px;padding:13px 0;border-bottom:1px solid rgba(128,128,128,.22)'><b>${esc(it.first)}</b><span>${esc(it.second)}</span></div>"}\n        val body="""<div class='simple' style='max-width:1180px;margin:0 auto'><h1>播放诊断</h1><p>用于判断 YouTube 嵌入播放器在当前 Android WebView 环境中的兼容性。</p>$table<div style='margin-top:22px'><b>User-Agent</b><p style='font-size:15px;word-break:break-all'>${esc(ua)}</p></div><div style='display:flex;gap:12px;flex-wrap:wrap;margin-top:24px'><a class='chip' href='c16://home'>返回首页</a><a class='chip' href='c16://playermode?mode=${if(mode=="web")"auto" else "web"}'>切换播放模式</a></div><p style='font-size:15px;margin-top:22px'>说明：YouTube 的 Android WebView 嵌入播放器可能使用 Media Integrity 验证应用与设备。这里显示“支持/已启用”并不等于设备一定能生成有效认证；认证还可能依赖 Google Play 服务与设备环境。</p></div>"""\n        load(shell("settings",body))\n    }\n'''
if 'private fun showPlaybackDiagnostics()' not in s:
    if marker not in s: raise SystemExit('v4.8 diagnostics marker missing')
    s=s.replace(marker,method+marker,1)

# Ensure any surviving visible label is V4.8.
s=s.replace('C16 YouTube · V4.7','C16 YouTube · V4.8')

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V4.8 Media Integrity diagnostics/player fallback patch')
