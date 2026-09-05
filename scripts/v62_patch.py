from pathlib import Path
import re

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V6.2: YouTube-web-style channel/player behavior + remove legacy demo content.
# Keep the proven V4.8+ WebView / IFrame / Media Integrity playback core untouched.

field='    private var currentVideoId: String? = null\n'
field_add='''    private var lastRoute62="c16://home"\n    private val legacyVideoIds62=setOf("M7lc1UVf-VE","jNQXAC9IVRw","linlz7-Pnvw","Scxs7L0vhZ4","kJQP7kiw5Fk","dQw4w9WgXcQ","9bZkp7q19f0","OPf0YbXqDm0","DsonSEllPmU","dXOdiF4wbNU","aqz-KE-bpKQ","ysz5S6PUM-U","L_jWHffIx5E")\n'''
if 'lastRoute62' not in s:
    if field not in s: raise SystemExit('v6.2 field anchor missing')
    s=s.replace(field,field+field_add,1)

oncreate='''configureWebView(); showHome()'''
if oncreate in s:
    s=s.replace(oncreate,'''configureWebView(); cleanupLegacy62(); showHome()''',1)

route_head='''    private fun route(u:Uri){when(u.host){'''
route_head_new='''    private fun route(u:Uri){\n        val host62=u.host.orEmpty()\n        if(host62 !in setOf("refresh62","theme","sidebar","favorite","later","laterremove","playersub62","subtoggle","comments","homesync","playermode","playerreload")) lastRoute62=u.toString()\n        when(host62){'''
if route_head not in s: raise SystemExit('v6.2 route head missing')
s=s.replace(route_head,route_head_new,1)

home_case='''"home"->showHome();'''
home_case_new='''"home"->showHome();"refresh62"->refreshCurrent62();"playersub62"->togglePlayerSubscription62(u.getQueryParameter("video").orEmpty());"channelbyvideo62"->openPlayerChannel62(u.getQueryParameter("video").orEmpty());"channelmediamore62"->loadChannelMediaMore62(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("kind").orEmpty(),u.getQueryParameter("uploads").orEmpty(),u.getQueryParameter("token").orEmpty());'''
if home_case not in s: raise SystemExit('v6.2 home route missing')
s=s.replace(home_case,home_case_new,1)

old_channel_route='''"channel"->showChannel54(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("tab").orEmpty());'''
new_channel_route='''"channel"->showChannel62(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("tab").orEmpty());'''
if old_channel_route not in s: raise SystemExit('v6.2 channel route missing')
s=s.replace(old_channel_route,new_channel_route,1)

s=s.replace("href='c16://homesync' title='刷新账号内容'","href='c16://refresh62' title='刷新当前页面'",1)

old_nav='''${nav("sub","sub","订阅","subscriptions")}${nav("history","history","历史记录","history")}${nav("favorites","heart","我的收藏","favorites")}${nav("watchlater","history","稍后观看","watchlater")}${nav("likes","heart","点赞视频","likes")}${nav("playlists","sub","播放列表","playlists")}${nav("local","local","本地视频","local")}'''
new_nav='''${nav("sub","sub","订阅","subscriptions")}${nav("history","history","历史记录","history")}${nav("favorites","heart","我的收藏","favorites")}${nav("watchlater","clockplus","稍后观看","watchlater")}${nav("likes","thumb","点赞视频","likes")}${nav("playlists","playlist","播放列表","playlists")}${nav("local","local","本地视频","local")}'''
if old_nav not in s: raise SystemExit('v6.2 sidebar nav missing')
s=s.replace(old_nav,new_nav,1)
svg_anchor=''';"local"->"<svg viewBox='0 0 24 24'><rect x='3' y='5' width='18' height='14' rx='3'/><path d='m10 9 5 3-5 3z'/></svg>"'''
svg_add=''';"clockplus"->"<svg viewBox='0 0 24 24'><circle cx='11' cy='12' r='8'/><path d='M11 7v5l3 2M19 17v5m-2.5-2.5h5'/></svg>";"thumb"->"<svg viewBox='0 0 24 24'><path d='M7 10v10H3V10h4zm0 9h9.2a2 2 0 0 0 1.9-1.4l2.1-6.3A2 2 0 0 0 18.3 9H14l.6-3.2A2.4 2.4 0 0 0 12.2 3L7 10z'/></svg>";"playlist"->"<svg viewBox='0 0 24 24'><path d='M4 6h10M4 11h10M4 16h7'/><path d='m16 14 5 3-5 3z'/></svg>";"local"->"<svg viewBox='0 0 24 24'><rect x='3' y='5' width='18' height='14' rx='3'/><path d='m10 9 5 3-5 3z'/></svg>"'''
if svg_anchor not in s: raise SystemExit('v6.2 svg anchor missing')
s=s.replace(svg_anchor,svg_add,1)

old_player_channel='''<div class='channel'><div class='avatar'></div><a class='channelText' href='c16://category?name=${Uri.encode(v.category)}'><b>${esc(v.channel)}</b><span>点击查看更多相关内容</span></a><a class='subscribe' href='c16://subscriptions'>订阅</a></div>'''
new_player_channel='''<div class='channel'><div id='playerAvatar62' class='avatar playerAvatar62'></div><a id='playerChannelLink62' class='channelText' href='c16://channelbyvideo62?video=${Uri.encode(v.id)}'><b id='playerChannelName62'>${esc(v.channel)}</b><span>查看频道</span></a><a id='playerSub62' class='subscribe playerSub62' href='c16://playersub62?video=${Uri.encode(v.id)}'>订阅</a></div>'''
if old_player_channel not in s: raise SystemExit('v6.2 player channel row missing')
s=s.replace(old_player_channel,new_player_channel,1)

player_tail='''load(shell("",body,true));fetchCommentsAsync(id)'''
if player_tail not in s: raise SystemExit('v6.2 player tail missing')
s=s.replace(player_tail,'''load(shell("",body,true));loadPlayerChannelUi62(id);fetchCommentsAsync(id)''',1)

s=s.replace('''val pool=(videos+dynamicVideos.values).distinctBy{it.id}''','''val pool=dynamicVideos.values.distinctBy{it.id}.filterNot{legacyVideoIds62.contains(it.id)}''',1)
s=s.replace('''dynamicVideos[id]?:videos.firstOrNull{it.id==id}?:meta.optJSONObject(id)?.let''','''dynamicVideos[id]?:meta.optJSONObject(id)?.let''',1)
s=s.replace('''val v=dynamicVideos[id]?:videos.firstOrNull{it.id==id}?:return''','''val v=dynamicVideos[id]?:return''',1)
s=s.replace('''        videos.firstOrNull{it.id==id}?.let{return it}\n''','''        if(legacyVideoIds62.contains(id))return null\n''',1)
s=s.replace('''val v=videos.firstOrNull{it.id==id}?:dynamicVideos[id]?:Video(id,"YouTube 视频","YouTube","正在播放","推荐")''','''val v=dynamicVideos[id]?:Video(id,"YouTube 视频","YouTube","正在播放","推荐")''',1)

s=s.replace('''val local=videos.filter{it.title.contains(query,true)||it.channel.contains(query,true)||it.category.contains(query,true)}''','''val local=dynamicVideos.values.filterNot{legacyVideoIds62.contains(it.id)}.filter{it.title.contains(query,true)||it.channel.contains(query,true)||it.category.contains(query,true)}''',1)
s=s.replace('''val local=videos.filter{it.category==name || (name=="科技AI"&&it.category=="科技")}''','''val local=dynamicVideos.values.filterNot{legacyVideoIds62.contains(it.id)}.filter{it.category==name || (name=="科技AI"&&it.category=="科技")}''',1)
s=s.replace('''rail("热门内容","车机内置精选",videos.take(12))''','''rail("热门内容","已加载的 YouTube 内容",dynamicVideos.values.filterNot{legacyVideoIds62.contains(it.id)}.take(12))''',1)

old_drive='''        val next=history.firstOrNull()?:homeSubscriptionFeed.firstOrNull()?:videos.first()'''
new_drive='''        val next=history.firstOrNull()?:homeSubscriptionFeed.firstOrNull()?:homeLikedFeed.firstOrNull()?:dynamicVideos.values.firstOrNull{!legacyVideoIds62.contains(it.id)}\n        if(next==null){load(shell("drive","<div class='simple'><h1>暂无可播放内容</h1><p>登录 YouTube 或先浏览一个频道后，这里会显示真实视频。</p><a class='chip' href='c16://home'>返回首页</a></div>"));return}'''
s=s.replace(old_drive,new_drive)

pattern=r'''    private fun homeBody\(\):String\{.*?\n    \}\n    private fun maybeSyncHomeFeed\(\)\{'''
replacement=r'''    private fun homeBody():String{
        val signed=prefs.getString("access_token","").orEmpty().isNotBlank()
        val history=historyVideos().filterNot{legacyVideoIds62.contains(it.id)}
        val subs=homeSubscriptionFeed.toList().distinctBy{it.id}.filterNot{legacyVideoIds62.contains(it.id)}
        val likes=homeLikedFeed.toList().distinctBy{it.id}.filterNot{legacyVideoIds62.contains(it.id)}
        val later=watchLaterVideos().filterNot{legacyVideoIds62.contains(it.id)}
        val pool=(subs+likes+history+later+dynamicVideos.values).distinctBy{it.id}.filterNot{legacyVideoIds62.contains(it.id)}
        val hero=subs.firstOrNull()?:history.firstOrNull()?:likes.firstOrNull()?:later.firstOrNull()?:pool.firstOrNull()
        val chipsHtml="<div class='chips'>${chips("推荐")}</div>"
        if(hero==null){
            val state=if(signed)"正在同步你的真实 YouTube 内容。" else "登录 YouTube 后显示订阅、点赞、历史与推荐内容。"
            val action=if(signed)"<a class='btn' href='c16://refresh62'>刷新当前页面</a>" else "<a class='btn' href='c16://login'>登录 YouTube</a>"
            return chipsHtml+"<div class='homeCta'><div><h3>首页暂无真实视频</h3><p>$state</p></div>$action</div><div style='height:34px'></div>"
        }
        val recommend=pool.filter{it.id!=hero.id}.take(80)
        val continueSection=if(history.isEmpty())"" else rail("继续观看","来自这台 C16 的真实观看记录",history.take(40))
        val subscriptionSection=if(subs.isEmpty())"" else rail("订阅频道更新","来自你订阅频道的最新视频",subs)
        val likedSection=if(likes.isEmpty())"" else rail("点赞回看","你的 YouTube 点赞视频",likes.take(50))
        val laterSection=if(later.isEmpty())"" else rail("稍后观看","保存在这台 C16 上",later.take(50))
        val recommendSection=if(recommend.isEmpty())"" else rail("为你推荐","基于真实账号与浏览数据",recommend)
        val loginCta=if(signed)"" else "<div class='homeCta'><div><h3>登录 YouTube 获取完整首页</h3><p>同步订阅频道、点赞与账号内容。</p></div><a class='btn' href='c16://login'>手机扫码登录</a></div>"
        return """$chipsHtml<div class='hero'><img src='${thumb(hero)}'><div class='shade'></div><div class='heroCopy'><small>${if(subs.any{it.id==hero.id})"来自你的订阅" else if(history.any{it.id==hero.id})"继续观看" else "为你精选"}</small><h1>${esc(hero.title)}</h1><p>${esc(hero.channel)} · YouTube</p><div class='heroBtns'><a class='btn' href='c16://watch?id=${hero.id}'>▶ 立即播放</a><a class='btn alt' href='c16://drive59'>驾驶模式</a></div></div></div>$continueSection$subscriptionSection$likedSection$laterSection$recommendSection$loginCta<div style='height:34px'></div>"""
    }
    private fun maybeSyncHomeFeed(){'''
s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('v6.2 homeBody replacement failed')
s=s2

old_tabs='''val tabs="<div class='channelTabs51'>${tabLink("home","主页")}${tabLink("videos","视频")}${tabLink("playlists","播放列表")}</div>"'''
new_tabs='''val tabs="<div class='channelTabs51'>${tabLink("home","主页")}${tabLink("videos","视频")}${tabLink("shorts","Shorts")}${tabLink("playlists","播放列表")}</div>"'''
if old_tabs not in s: raise SystemExit('v6.2 channel tabs anchor missing')
s=s.replace(old_tabs,new_tabs,1)

marker='''    private fun accountPill51():String{'''
methods=r'''    private fun cleanupLegacy62(){
        val history=prefs.getString("history_ids","").orEmpty().split(",").filter{it.isNotBlank()&&!legacyVideoIds62.contains(it)}
        val later=prefs.getString("watch_later_ids","").orEmpty().split(",").filter{it.isNotBlank()&&!legacyVideoIds62.contains(it)}
        val fav=prefs.getStringSet("favorites",emptySet()).orEmpty().filterNot{legacyVideoIds62.contains(it)}.toSet()
        prefs.edit().putString("history_ids",history.joinToString(",")).putString("watch_later_ids",later.joinToString(",")).putStringSet("favorites",fav).apply()
    }
    private fun refreshCurrent62(){
        val target=lastRoute62.ifBlank{"c16://home"}
        if(target=="c16://home"){homeSyncedAt=0L;homeSyncError="";homeSubscriptionFeed.clear();homeLikedFeed.clear()}
        route(Uri.parse(target))
    }
    private fun ensureVideoChannel62(videoId:String):Pair<String,String>{
        val cached=dynamicVideoChannelIds[videoId].orEmpty();val cachedTitle=dynamicVideos[videoId]?.channel.orEmpty()
        if(cached.isNotBlank())return cached to cachedTitle
        val j=apiGet("videos?part=snippet&id=${Uri.encode(videoId)}&maxResults=1");val item=j.optJSONArray("items")?.optJSONObject(0)?:return "" to cachedTitle
        val sn=item.optJSONObject("snippet")?:JSONObject();val cid=sn.optString("channelId","");val title=sn.optString("channelTitle",cachedTitle)
        if(cid.isNotBlank())dynamicVideoChannelIds[videoId]=cid
        dynamicVideos[videoId]?.let{v->dynamicVideos[videoId]=Video(v.id,v.title,title.ifBlank{v.channel},v.meta,v.category)}
        return cid to title
    }
    private fun playerChannelData62(videoId:String):Array<String>{
        val pair=ensureVideoChannel62(videoId);val cid=pair.first;if(cid.isBlank())return arrayOf("",pair.second,"","false")
        val cj=apiGet("channels?part=snippet&id=${Uri.encode(cid)}");val sn=cj.optJSONArray("items")?.optJSONObject(0)?.optJSONObject("snippet")?:JSONObject()
        val title=sn.optString("title",pair.second.ifBlank{"YouTube 频道"});val th=sn.optJSONObject("thumbnails");val avatar=th?.optJSONObject("high")?.optString("url",th.optJSONObject("medium")?.optString("url",th.optJSONObject("default")?.optString("url").orEmpty()).orEmpty()).orEmpty()
        val subscribed=if(prefs.getString("access_token","").orEmpty().isBlank())false else subscriptionId51(cid).isNotBlank()
        return arrayOf(cid,title,avatar,subscribed.toString())
    }
    private fun loadPlayerChannelUi62(videoId:String){
        if(videoId.isBlank())return
        Thread{try{
            val d=playerChannelData62(videoId);if(d[0].isBlank())return@Thread
            val cid=d[0];val title=d[1];val avatar=d[2];val subscribed=d[3].toBoolean()
            main.post{
                val js="(function(){var a=document.getElementById('playerAvatar62');if(a&&"+JSONObject.quote(avatar)+".length)a.innerHTML='<img src='+"+JSONObject.quote(avatar)+"+'>';var n=document.getElementById('playerChannelName62');if(n)n.textContent="+JSONObject.quote(title)+";var l=document.getElementById('playerChannelLink62');if(l)l.href='c16://channel?id='+encodeURIComponent("+JSONObject.quote(cid)+")+'&title='+encodeURIComponent("+JSONObject.quote(title)+")+'&tab=home';var b=document.getElementById('playerSub62');if(b){b.textContent="+JSONObject.quote(if(subscribed)"✓ 已订阅" else "订阅")+";b.classList.toggle('on',"+subscribed+");}})()"
                web.evaluateJavascript(js,null)
            }
        }catch(_:Exception){}}.start()
    }
    private fun togglePlayerSubscription62(videoId:String){
        if(videoId.isBlank())return
        if(prefs.getString("access_token","").orEmpty().isBlank()){web.evaluateJavascript("alert('请先登录 YouTube 后再订阅频道')",null);return}
        web.evaluateJavascript("var b=document.getElementById('playerSub62');if(b)b.textContent='处理中…';",null)
        Thread{try{
            val pair=ensureVideoChannel62(videoId);val cid=pair.first;if(cid.isBlank())throw IllegalStateException("无法识别频道")
            val sid=subscriptionId51(cid)
            if(sid.isBlank()){
                val resource=JSONObject().put("kind","youtube#channel").put("channelId",cid)
                apiWrite51("subscriptions?part=snippet","POST",JSONObject().put("snippet",JSONObject().put("resourceId",resource)))
            }else apiWrite51("subscriptions?id=${Uri.encode(sid)}","DELETE",null)
            homeSyncedAt=0L;homeSubscriptionFeed.clear();homeSyncError="";main.post{loadPlayerChannelUi62(videoId)}
        }catch(e:Exception){main.post{web.evaluateJavascript("var b=document.getElementById('playerSub62');if(b)b.textContent='订阅失败';alert("+JSONObject.quote((e.message?:"订阅操作失败").take(140))+ ")",null)}}}.start()
    }
    private fun openPlayerChannel62(videoId:String){
        if(videoId.isBlank())return
        Thread{try{val p=ensureVideoChannel62(videoId);if(p.first.isBlank())throw IllegalStateException("无法识别频道");main.post{showChannel62(p.first,p.second,"home")}}catch(e:Exception){main.post{showApiError("频道",e)}}}.start()
    }
    private fun showChannel62(id:String,title:String,tabRaw:String){
        val tab=tabRaw.ifBlank{"home"};if(tab=="videos"||tab=="shorts")showChannelMedia62(id,title,tab) else showChannel51(id,title,tab)
    }
    private fun showChannelMedia62(id:String,title:String,kind:String){
        currentVideoId=null;if(id.isBlank())return
        requireLoginOr{
            load(shell("subscriptions","<div class='simple'><h1>${esc(title.ifBlank{"频道"})}</h1><p>正在读取频道${if(kind=="shorts")" Shorts" else "视频"}…</p></div>"))
            Thread{try{
                val cj=apiGet("channels?part=snippet,statistics,contentDetails&id=${Uri.encode(id)}");val item=cj.optJSONArray("items")?.optJSONObject(0)?:throw IllegalStateException("没有找到频道")
                val sn=item.optJSONObject("snippet")?:JSONObject();val st=item.optJSONObject("statistics")?:JSONObject();val t=sn.optString("title",title.ifBlank{"YouTube 频道"});val uploads=item.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")?.optString("uploads").orEmpty();if(uploads.isBlank())throw IllegalStateException("没有找到频道上传列表")
                val th=sn.optJSONObject("thumbnails");val avatar=th?.optJSONObject("high")?.optString("url",th.optJSONObject("medium")?.optString("url").orEmpty()).orEmpty();val subId=subscriptionId51(id);val subHref="c16://subtoggle?id=${Uri.encode(id)}&title=${Uri.encode(t)}&subid=${Uri.encode(subId)}"
                val hero="<div class='channelHero50'><img src='${esc(avatar)}'><div><h1>${esc(t)}</h1><p>${if(kind=="shorts")"Shorts 与短视频" else "长视频与常规视频"} · ${st.optString("subscriberCount","")} 位订阅者</p></div><a class='subButton51 ${if(subId.isNotBlank())"on" else ""}' href='$subHref'>${if(subId.isNotBlank())"✓ 已订阅" else "订阅"}</a></div>"
                fun tabLink(k:String,l:String)="<a class='channelTab51 ${if(kind==k)"on" else ""}' href='c16://channel?id=${Uri.encode(id)}&title=${Uri.encode(t)}&tab=$k'>$l</a>"
                val tabs="<div class='channelTabs51 ytChannelTabs62'>${tabLink("home","主页")}${tabLink("videos","视频")}${tabLink("shorts","Shorts")}${tabLink("playlists","播放列表")}</div>"
                val label=if(kind=="shorts")"Shorts" else "视频"
                val body=hero+tabs+"<div class='channelVideoHead54'><div><h1>$label</h1><p>${if(kind=="shorts")"按时长不超过 3 分钟归入 Shorts 区域" else "仅显示超过 3 分钟的常规视频"} · 向下自动继续加载</p></div></div><div id='chMediaGrid62' class='channelGrid60 ${if(kind=="shorts")"shortsGrid62" else ""}'></div><div id='chMediaMore62'></div>"
                main.post{load(shell("subscriptions",body));fetchChannelMediaPage62(id,t,kind,uploads,"",false)}
            }catch(e:Exception){main.post{showApiError("频道",e)}}}.start()
        }
    }
    private fun loadChannelMediaMore62(id:String,title:String,kind:String,uploads:String,token:String){if(id.isNotBlank()&&uploads.isNotBlank()&&token.isNotBlank())fetchChannelMediaPage62(id,title,kind,uploads,token,true)}
    private fun fetchChannelMediaPage62(id:String,title:String,kind:String,uploads:String,token:String,append:Boolean){
        Thread{try{
            val suffix=if(token.isBlank())"" else "&pageToken=${Uri.encode(token)}";val pj=apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=50$suffix");val list=apiVideoList(pj,true);list.forEach{dynamicVideoChannelIds[it.id]=id}
            val ids=list.map{it.id}.filter{it.isNotBlank()};val secs=mutableMapOf<String,Long>()
            if(ids.isNotEmpty()){
                val dj=apiGet("videos?part=contentDetails&id=${ids.joinToString(",")}");val da=dj.optJSONArray("items")
                if(da!=null)for(i in 0 until da.length()){val x=da.optJSONObject(i)?:continue;val raw=x.optJSONObject("contentDetails")?.optString("duration").orEmpty();val sec=try{java.time.Duration.parse(raw).seconds}catch(_:Exception){Long.MAX_VALUE};secs[x.optString("id","")]=sec}
            }
            val filtered=list.filter{v->val sec=secs[v.id]?:Long.MAX_VALUE;if(kind=="shorts")sec<=180 else sec>180}.filterNot{legacyVideoIds62.contains(it.id)}
            val next=pj.optString("nextPageToken","");val html=filtered.joinToString(""){card(it)}
            main.post{
                if(append)appendHtml54("chMediaGrid62",html) else setMore54("chMediaGrid62",html)
                val more=if(next.isBlank())"<div class='moreWrap54'><span class='more54 disabled'>已读取频道全部内容</span></div>" else "<div class='moreWrap54'><a class='more54 autoMore61' href='c16://channelmediamore62?id=${Uri.encode(id)}&title=${Uri.encode(title)}&kind=${Uri.encode(kind)}&uploads=${Uri.encode(uploads)}&token=${Uri.encode(next)}'>继续加载</a><span class='loaded54'>继续向下自动加载</span></div>"
                setMore54("chMediaMore62",more)
            }
        }catch(e:Exception){main.post{setMore54("chMediaMore62","<div class='searchNotice'>频道内容加载失败：${esc((e.message?:"请求失败").take(150))}</div>")}}}.start()
    }
'''
if marker not in s: raise SystemExit('v6.2 helper marker missing')
s=s.replace(marker,methods+marker,1)

css=r'''
/* V6.2 YouTube-style channel/player polish */
.playerAvatar62{overflow:hidden!important;background:$p2!important}.playerAvatar62 img{width:100%;height:100%;object-fit:cover;display:block}.playerSub62.on{background:$p2!important;color:$text!important;border:1px solid $border!important}.ytChannelTabs62{border-bottom:1px solid $border;padding-bottom:10px!important;margin-bottom:22px!important}.ytChannelTabs62 .channelTab51{border:0!important;border-radius:0!important;background:transparent!important;padding:12px 16px!important}.ytChannelTabs62 .channelTab51.on{color:$text!important;border-bottom:3px solid $text!important}.shortsGrid62 .thumb img{object-fit:cover!important}.shortsGrid62 .ctitle{min-height:54px!important}.refresh60{cursor:pointer}
'''
if 'V6.2 YouTube-style channel/player polish' not in s:s=s.replace('</style>',css+'</style>',1)

s=s.replace('C16 YouTube · V6.1','C16 YouTube · V6.2')
s=s.replace('"应用版本" to "6.1.40078"','"应用版本" to "6.2.40079"')

p.write_text(s,encoding='utf-8')
print('Applied V6.2 current-page refresh, real player subscription/avatar, no legacy demos, unique sidebar icons and channel Videos/Shorts split')
