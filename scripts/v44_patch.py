from pathlib import Path

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

imports = '''import android.os.Handler
import android.os.Looper
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.util.concurrent.atomic.AtomicBoolean
'''
anchor = 'import android.os.Bundle\n'
if 'import android.os.Handler' not in s:
    if anchor not in s: raise SystemExit('v4.4 imports anchor missing')
    s = s.replace(anchor, anchor + imports, 1)

field_anchor = '    private lateinit var web: WebView\n'
field_add = '''    private val main = Handler(Looper.getMainLooper())
    private val loginPolling = AtomicBoolean(false)
'''
if 'private val loginPolling' not in s:
    s = s.replace(field_anchor, field_anchor + field_add, 1)

old_route = '''    private fun route(u:Uri){when(u.host){"home"->showHome();"watch"->showPlayer(u.getQueryParameter("id").orEmpty());"category"->showCategory(u.getQueryParameter("name").orEmpty());"search"->showSearch(u.getQueryParameter("q").orEmpty());"theme"->{dark=!dark;prefs.edit().putBoolean("dark",dark).apply();rerender()};"sidebar"->{collapsed=!collapsed;prefs.edit().putBoolean("collapsed",collapsed).apply();rerender()};"history"->showSimple("历史记录","这里会显示在车机内打开过的视频。");"favorites"->showSimple("我的收藏","收藏的视频会集中显示在这里。");"subscriptions"->showSimple("订阅","登录后显示订阅频道更新。");"local"->showSimple("本地视频","后续可接入车机本地媒体库。");"settings"->showSimple("设置","C16 YouTube · V4.3 播放兼容性修复版");"login"->showSimple("YouTube 登录","手机授权入口将在下一步继续接回现有 OAuth 登录模块。")}}
'''
new_route = '''    private fun route(u:Uri){when(u.host){"home"->showHome();"watch"->showPlayer(u.getQueryParameter("id").orEmpty());"category"->showCategory(u.getQueryParameter("name").orEmpty());"search"->showSearch(u.getQueryParameter("q").orEmpty());"theme"->{dark=!dark;prefs.edit().putBoolean("dark",dark).apply();rerender()};"sidebar"->{collapsed=!collapsed;prefs.edit().putBoolean("collapsed",collapsed).apply();rerender()};"history"->showHistory();"favorites"->showFavorites();"favorite"->toggleFavorite(u.getQueryParameter("id").orEmpty());"subscriptions"->showSimple("订阅","V4.4 已恢复账号授权入口；订阅频道同步将在授权后继续接入。");"local"->showSimple("本地视频","后续可接入车机本地媒体库。");"settings"->showSettings();"login"->showLoginCenter();"oauthsave"->{val client=u.getQueryParameter("client").orEmpty();val secret=u.getQueryParameter("secret").orEmpty();prefs.edit().putString("oauth_client_id",client).putString("oauth_client_secret",secret).apply();startDeviceLogin(client,secret)};"startQr"->startDeviceLogin(prefs.getString("oauth_client_id","").orEmpty(),prefs.getString("oauth_client_secret","").orEmpty());"logout"->logout()}}
'''
if old_route not in s: raise SystemExit('v4.4 route target missing')
s = s.replace(old_route, new_route, 1)

s = s.replace("<a class='pill' href='c16://login'>登录</a>", """<a class='pill' href='c16://login'>${if(prefs.getString("access_token","").orEmpty().isNotBlank())"账号" else "登录"}</a>""", 1)

old_home = '''    private fun showHome(){currentVideoId=null;val hero=videos.first();val body="""<div class='chips'>${chips("推荐")}</div><div class='hero'><img src='${thumb(hero)}'><div class='shade'></div><div class='heroCopy'><small>为你精选</small><h1>${esc(hero.title)}</h1><p>来自你的观看、订阅与近期内容。</p><div class='heroBtns'><a class='btn' href='c16://watch?id=${hero.id}'>▶ 立即播放</a><a class='btn alt' href='c16://category?name=科技AI'>探索更多</a></div></div></div>${rail("继续观看","你的车机观看记录",videos.take(8))}${rail("订阅频道更新","来自你订阅的频道",videos.drop(3).take(9))}${rail("猜你喜欢","向右查看更多",videos.reversed())}<div style='height:30px'></div>""";load(shell("home",body))}
'''
new_home = '''    private fun showHome(){currentVideoId=null;val hero=videos.first();val history=historyVideos();val continueList=if(history.isEmpty())videos.take(8) else history;val body="""<div class='chips'>${chips("推荐")}</div><div class='hero'><img src='${thumb(hero)}'><div class='shade'></div><div class='heroCopy'><small>为你精选</small><h1>${esc(hero.title)}</h1><p>适配 C16 14.6 英寸横屏的大屏 YouTube 首页。</p><div class='heroBtns'><a class='btn' href='c16://watch?id=${hero.id}'>▶ 立即播放</a><a class='btn alt' href='c16://category?name=科技AI'>探索更多</a></div></div></div>${rail("继续观看",if(history.isEmpty())"开始播放后自动记录" else "你的真实车机观看记录",continueList)}${rail("订阅频道更新","登录后逐步同步 YouTube 账号内容",videos.drop(3).take(9))}${rail("猜你喜欢","向右查看更多",videos.reversed())}<div style='height:30px'></div>""";load(shell("home",body))}
'''
if old_home not in s: raise SystemExit('v4.4 home target missing')
s = s.replace(old_home, new_home, 1)

player_anchor = '        val v=videos.firstOrNull{it.id==id}?:Video(id,"YouTube 视频","YouTube","正在播放","推荐");currentVideoId=id\n'
if player_anchor not in s: raise SystemExit('v4.4 player anchor missing')
s = s.replace(player_anchor, player_anchor + '        addHistory(id)\n        val fav=prefs.getStringSet("favorites",emptySet()).orEmpty().contains(id)\n', 1)

old_actions = """<div class='actions'><a class='action' href='c16://favorites'>♡ 收藏</a><a class='action' href='c16://category?name=${Uri.encode(v.category)}'>▤ 推荐</a><a class='action' href='c16://sidebar'>☰ 侧栏</a></div>"""
new_actions = """<div class='actions'><a class='action' href='c16://favorite?id=${Uri.encode(v.id)}'>${if(fav)"♥ 已收藏" else "♡ 收藏"}</a><a class='action' href='c16://category?name=${Uri.encode(v.category)}'>▤ 推荐</a><a class='action' href='c16://sidebar'>☰ 侧栏</a></div>"""
if old_actions not in s: raise SystemExit('v4.4 player actions target missing')
s = s.replace(old_actions, new_actions, 1)

methods = r'''    private fun historyIds():List<String> = prefs.getString("history_ids","").orEmpty().split(",").filter{it.isNotBlank()}
    private fun historyVideos():List<Video> = historyIds().mapNotNull{id->videos.firstOrNull{it.id==id}}.take(20)
    private fun addHistory(id:String){
        if(id.isBlank())return
        val ids=(listOf(id)+historyIds().filter{it!=id}).take(30)
        prefs.edit().putString("history_ids",ids.joinToString(",")).apply()
    }
    private fun showHistory(){
        currentVideoId=null
        val list=historyVideos()
        val inner=if(list.isEmpty())"<div class='simple'><h1>历史记录</h1><p>你在车机里播放过的视频会自动出现在这里。</p></div>" else "<div class='sectionHead'><h2>历史记录</h2><span>${list.size} 个视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>"
        load(shell("history",inner))
    }
    private fun showFavorites(){
        currentVideoId=null
        val ids=prefs.getStringSet("favorites",emptySet()).orEmpty()
        val list=videos.filter{it.id in ids}
        val inner=if(list.isEmpty())"<div class='simple'><h1>我的收藏</h1><p>播放视频时点击“收藏”，视频就会保存在这里。</p></div>" else "<div class='sectionHead'><h2>我的收藏</h2><span>${list.size} 个视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>"
        load(shell("favorites",inner))
    }
    private fun toggleFavorite(id:String){
        if(id.isBlank())return
        val set=prefs.getStringSet("favorites",emptySet()).orEmpty().toMutableSet()
        if(!set.add(id))set.remove(id)
        prefs.edit().putStringSet("favorites",set).apply()
        showPlayer(id)
    }
    private fun showSettings(){
        currentVideoId=null
        val signed=prefs.getString("access_token","").orEmpty().isNotBlank()
        val body="""<div class='simple'><h1>设置</h1><p>C16 YouTube · V4.4</p><div style='display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:24px'><a class='chip' href='c16://theme'>${if(dark)"☀ 切换浅色模式" else "☾ 切换深色模式"}</a><a class='chip' href='c16://login'>${if(signed)"YouTube 账号中心" else "手机扫码登录 YouTube"}</a><a class='chip' href='c16://history'>观看历史</a><a class='chip' href='c16://favorites'>我的收藏</a></div></div>"""
        load(shell("settings",body))
    }
    private fun showLoginCenter(){
        currentVideoId=null
        if(prefs.getString("access_token","").orEmpty().isNotBlank()){showAccountCenter();return}
        val client=esc(prefs.getString("oauth_client_id","").orEmpty())
        val secret=esc(prefs.getString("oauth_client_secret","").orEmpty())
        if(client.isNotBlank()&&secret.isNotBlank()){
            val body="""<div class='simple' style='max-width:980px;margin:0 auto'><h1>手机扫码登录 YouTube</h1><p>OAuth 客户端已保存在本机。点击下面按钮生成新的 Google 设备授权二维码。</p><a class='btn' href='c16://startQr'>生成登录二维码</a><p style='margin-top:28px;font-size:16px'>使用 Google Cloud 中 TVs and Limited Input devices 类型的 OAuth 客户端。</p></div>"""
            load(shell("",body));return
        }
        val body="""<div class='simple' style='max-width:1050px;margin:0 auto'><h1>首次设置 YouTube 登录</h1><p>只需设置一次。Client ID 与 Client Secret 仅保存在这台车机应用本地。</p><div style='display:grid;gap:14px;margin:24px 0'><input id='client' value='$client' placeholder='OAuth Client ID' style='height:58px;border-radius:16px;border:1px solid #888;padding:0 18px;font-size:18px'><input id='secret' value='$secret' placeholder='OAuth Client Secret' type='password' style='height:58px;border-radius:16px;border:1px solid #888;padding:0 18px;font-size:18px'><button onclick="location.href='c16://oauthsave?client='+encodeURIComponent(document.getElementById('client').value)+'&secret='+encodeURIComponent(document.getElementById('secret').value)" style='height:58px;border:0;border-radius:18px;background:#ff0033;color:white;font-size:19px;font-weight:800'>保存并生成二维码</button></div><p style='font-size:16px'>需要在 Google Cloud 启用 YouTube Data API v3，并创建 TVs and Limited Input devices 类型 OAuth 客户端。</p></div>"""
        load(shell("",body))
    }
    private fun startDeviceLogin(client:String,secret:String){
        if(client.isBlank()||secret.isBlank()){showLoginCenter();return}
        loginPolling.set(false)
        Thread{
            try{
                val (_,text)=postForm("https://oauth2.googleapis.com/device/code",mapOf("client_id" to client,"scope" to "https://www.googleapis.com/auth/youtube"))
                val j=JSONObject(text)
                if(!j.has("device_code"))throw IllegalStateException(j.optString("error_description",j.optString("error","无法生成设备授权码")))
                val device=j.getString("device_code");val user=j.getString("user_code");val verify=j.getString("verification_url");val expires=j.optInt("expires_in",1800);val interval=j.optInt("interval",5)
                loginPolling.set(true)
                main.post{showDeviceCode(verify,user)}
                pollDeviceToken(client,secret,device,expires,interval)
            }catch(e:Exception){main.post{showLoginError(e.message?:"登录初始化失败")}}
        }.start()
    }
    private fun showDeviceCode(url:String,code:String){
        val qr="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${Uri.encode(url)}"
        val body="""<div class='simple' style='max-width:1080px;margin:0 auto;text-align:center'><h1>用手机完成 YouTube 授权</h1><p>扫描二维码打开 Google 设备授权页，然后输入下面的代码。</p><div style='display:flex;justify-content:center;gap:48px;align-items:center;margin-top:24px'><img src='$qr' style='width:300px;height:300px;background:white;padding:12px;border-radius:22px'><div style='text-align:left'><div style='font-size:18px;opacity:.7'>设备代码</div><div style='font-size:46px;font-weight:900;letter-spacing:5px;margin:10px 0 24px'>$code</div><div style='font-size:20px'>$url</div><p style='font-size:16px'>授权完成后，车机会自动进入账号中心，无需手动刷新。</p></div></div></div>"""
        load(shell("",body))
    }
    private fun pollDeviceToken(client:String,secret:String,device:String,expires:Int,startInterval:Int){
        var interval=startInterval.coerceAtLeast(5)
        val end=System.currentTimeMillis()+expires*1000L
        while(loginPolling.get()&&System.currentTimeMillis()<end){
            Thread.sleep(interval*1000L)
            val (status,text)=postForm("https://oauth2.googleapis.com/token",mapOf("client_id" to client,"client_secret" to secret,"device_code" to device,"grant_type" to "urn:ietf:params:oauth:grant-type:device_code"))
            val j=JSONObject(text)
            if(status in 200..299&&j.has("access_token")){
                prefs.edit().putString("access_token",j.getString("access_token")).putString("refresh_token",j.optString("refresh_token")).putLong("token_expires_at",System.currentTimeMillis()+j.optLong("expires_in",3600)*1000L).apply()
                loginPolling.set(false);main.post{showAccountCenter()};return
            }
            when(j.optString("error")){
                "authorization_pending"->{}
                "slow_down"->interval+=5
                "access_denied"->{loginPolling.set(false);main.post{showLoginError("你取消了本次授权。")};return}
                "expired_token"->{loginPolling.set(false);main.post{showLoginError("二维码已过期，请重新生成。")};return}
                else->{if(status!=428){loginPolling.set(false);main.post{showLoginError(j.optString("error_description","授权失败"))};return}}
            }
        }
        if(loginPolling.getAndSet(false))main.post{showLoginError("二维码已过期，请重新生成。")}
    }
    private fun showAccountCenter(){
        currentVideoId=null
        val body="""<div class='simple' style='max-width:1080px;margin:0 auto'><div style='display:flex;align-items:center;gap:22px'><div class='avatar' style='width:82px;height:82px'></div><div><h1 style='margin:0'>YouTube 账号已连接</h1><p style='margin:8px 0 0'>V4.4 已保存授权令牌，可继续接入订阅、点赞、播放列表和公开评论。</p></div></div><div style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:28px'><a class='chip' href='c16://subscriptions'>订阅</a><a class='chip' href='c16://history'>观看历史</a><a class='chip' href='c16://favorites'>车机收藏</a></div><div style='margin-top:28px'><a class='chip' href='c16://logout'>退出账号</a></div></div>"""
        load(shell("",body))
    }
    private fun logout(){
        loginPolling.set(false)
        prefs.edit().remove("access_token").remove("refresh_token").remove("token_expires_at").apply()
        showLoginCenter()
    }
    private fun showLoginError(msg:String){
        currentVideoId=null
        val body="""<div class='simple' style='max-width:900px;margin:0 auto'><h1>登录未完成</h1><p>${esc(msg)}</p><a class='chip' href='c16://login'>返回登录</a></div>"""
        load(shell("",body))
    }
    private fun postForm(url:String,params:Map<String,String>):Pair<Int,String>{
        val body=params.entries.joinToString("&"){URLEncoder.encode(it.key,"UTF-8")+"="+URLEncoder.encode(it.value,"UTF-8")}
        val c=URL(url).openConnection() as HttpURLConnection
        c.requestMethod="POST";c.doOutput=true;c.connectTimeout=15000;c.readTimeout=15000
        c.setRequestProperty("Content-Type","application/x-www-form-urlencoded")
        c.outputStream.use{it.write(body.toByteArray(StandardCharsets.UTF_8))}
        val code=c.responseCode
        val stream=if(code in 200..299)c.inputStream else c.errorStream
        val text=stream?.bufferedReader()?.use{it.readText()}.orEmpty()
        c.disconnect()
        return code to text
    }

'''
marker = '    private fun showSimple(title:String,copy:String)'
if 'private fun showLoginCenter()' not in s:
    if marker not in s: raise SystemExit('v4.4 methods marker missing')
    s = s.replace(marker, methods + marker, 1)

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube V4.4 account/login/history/favorites upgrade')
