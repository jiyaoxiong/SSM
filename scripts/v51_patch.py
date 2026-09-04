from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V5.1 deliberately leaves the proven V4.8/V4.9/V5.0 playback core untouched.
# This patch only improves account/channel/subscription/home/watch-later/car UX.

# Routes: channel tabs + real subscribe/unsubscribe + manual home refresh + Watch Later management.
channel_route='''"channel"->showChannel(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty());"local"'''
channel_route_new='''"channel"->showChannel51(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("tab").orEmpty());"subtoggle"->toggleSubscription51(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("subid").orEmpty());"local"'''
if channel_route not in s: raise SystemExit('v5.1 channel route anchor missing')
s=s.replace(channel_route,channel_route_new,1)

watch_route='''"watchlater"->showWatchLater();"later"->toggleWatchLater(u.getQueryParameter("id").orEmpty());'''
watch_route_new='''"watchlater"->showWatchLater51();"later"->toggleWatchLater(u.getQueryParameter("id").orEmpty());"laterremove"->removeWatchLater51(u.getQueryParameter("id").orEmpty());"clearwatchlater"->{prefs.edit().remove("watch_later_ids").apply();showWatchLater51()};'''
if watch_route not in s: raise SystemExit('v5.1 watch later route anchor missing')
s=s.replace(watch_route,watch_route_new,1)

home_route='''"home"->showHome();"drivehome"->showDriveHome();'''
home_route_new='''"home"->showHome();"homesync"->{homeSyncedAt=0L;homeSyncError="";homeSubscriptionFeed.clear();homeLikedFeed.clear();showHome()};"drivehome"->showDriveHome();'''
if home_route not in s: raise SystemExit('v5.1 home route anchor missing')
s=s.replace(home_route,home_route_new,1)

# Header account pill now shows the saved YouTube channel avatar + title when available.
old_account_pill='''<a class='pill' href='c16://login'>${if(prefs.getString("access_token","").orEmpty().isNotBlank())prefs.getString("account_title","账号").orEmpty().ifBlank{"账号"}.take(10) else "登录"}</a>'''
new_account_pill='''<a class='pill accountPill51' href='c16://login'>${accountPill51()}</a>'''
if old_account_pill not in s: raise SystemExit('v5.1 account pill anchor missing')
s=s.replace(old_account_pill,new_account_pill,1)

# Product/UI CSS only. No player or WebView playback CSS/settings are changed.
css_anchor=".playlistMini50 .thumb:after{content:'播放列表';position:absolute;right:8px;bottom:8px;padding:4px 8px;border-radius:10px;background:rgba(0,0,0,.72);color:#fff;font-size:12px}"
css_add=""".playlistMini50 .thumb:after{content:'播放列表';position:absolute;right:8px;bottom:8px;padding:4px 8px;border-radius:10px;background:rgba(0,0,0,.72);color:#fff;font-size:12px}.accountPill51{gap:9px;max-width:220px}.accountPill51 img{width:34px;height:34px;border-radius:50%;object-fit:cover}.accountPill51 span{max-width:145px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.channelTabs51{display:flex;gap:10px;margin:-8px 0 24px;padding-bottom:4px;overflow-x:auto}.channelTabs51::-webkit-scrollbar{display:none}.channelTab51{padding:11px 18px;border-radius:20px;background:$panel;border:1px solid $border;font-size:16px;font-weight:800}.channelTab51.on{background:$text;color:$bg}.subButton51{display:inline-flex;align-items:center;justify-content:center;min-width:132px;padding:13px 20px;border-radius:23px;background:#ff0033;color:#fff;font-weight:900;border:0}.subButton51.on{background:$p2;color:$text;border:1px solid $border}.manageBar51{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:16px 18px;border-radius:18px;background:$panel;border:1px solid $border;margin-bottom:18px}.manageBar51 b{font-size:18px}.manageBar51 span{display:block;color:$sub;font-size:14px;margin-top:3px}.manageCard51{position:relative}.remove51{position:absolute;right:8px;top:8px;z-index:3;padding:7px 11px;border-radius:16px;background:rgba(10,10,10,.82);color:#fff;font-size:13px;font-weight:800}.channelEmpty51{padding:34px;border-radius:20px;background:$panel;border:1px dashed $border;color:$sub;text-align:center;font-size:17px}.driveQuick51{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}.driveQuick51 a{padding:10px 15px;border-radius:18px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);color:#fff;font-weight:800}"
if css_anchor not in s: raise SystemExit('v5.1 CSS anchor missing')
s=s.replace(css_anchor,css_add,1)

# Five large tiles fit the real C16 landscape display and restore a direct subscriptions shortcut.
drive_css='''.driveGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;margin-top:18px}'''
if drive_css in s:
    s=s.replace(drive_css,'''.driveGrid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px;margin-top:18px}''',1)

drive_watch='''<a class='driveTile' href='c16://watchlater'><b>稍后观看</b><span>一键打开待看视频</span></a>'''
if drive_watch in s:
    s=s.replace(drive_watch,drive_watch+'''<a class='driveTile' href='c16://subscriptions'><b>订阅</b><span>查看 YouTube 订阅频道</span></a>''',1)

# Home gets an explicit refresh control. This refreshes account-derived shelves only.
home_return='''        return """$syncLine<div class='chips'>'''
home_return_new='''        return """<div class='manageBar51'><div><b>V5.1 个性化首页</b><span>订阅、点赞、观看记录与稍后观看</span></div><a class='chip' href='c16://homesync'>刷新账号内容</a></div>$syncLine<div class='chips'>'''
if home_return not in s: raise SystemExit('v5.1 home refresh anchor missing')
s=s.replace(home_return,home_return_new,1)

# Helpers + channel/watch-later functionality. Uses existing OAuth token and YouTube Data API.
marker='''    private fun showSettings(){'''
methods=r'''    private fun accountPill51():String{
        if(prefs.getString("access_token","").orEmpty().isBlank())return "<span>登录</span>"
        val title=prefs.getString("account_title","账号").orEmpty().ifBlank{"账号"}.take(12)
        val img=prefs.getString("account_avatar","").orEmpty()
        return if(img.isBlank())"<span>${esc(title)}</span>" else "<img src='${esc(img)}'><span>${esc(title)}</span>"
    }
    private fun apiWrite51(path:String,method:String,body:JSONObject?=null):JSONObject{
        val token=ensureAccessToken()
        if(token.isBlank())throw IllegalStateException("请先登录 YouTube")
        val c=URL("https://www.googleapis.com/youtube/v3/$path").openConnection() as HttpURLConnection
        c.requestMethod=method;c.connectTimeout=15000;c.readTimeout=15000
        c.setRequestProperty("Authorization","Bearer $token");c.setRequestProperty("Accept","application/json")
        if(body!=null){
            c.doOutput=true;c.setRequestProperty("Content-Type","application/json; charset=utf-8")
            c.outputStream.use{it.write(body.toString().toByteArray(StandardCharsets.UTF_8))}
        }
        val code=c.responseCode
        val stream=if(code in 200..299)c.inputStream else c.errorStream
        val text=stream?.bufferedReader()?.use{it.readText()}.orEmpty();c.disconnect()
        if(code !in 200..299){
            val msg=try{JSONObject(text).optJSONObject("error")?.optString("message")?:text}catch(_:Exception){text}
            throw IllegalStateException(msg.ifBlank{"YouTube API 请求失败 ($code)"})
        }
        return if(text.isBlank())JSONObject() else JSONObject(text)
    }
    private fun subscriptionId51(channelId:String):String{
        if(channelId.isBlank())return ""
        return try{
            val j=apiGet("subscriptions?part=id&mine=true&forChannelId=${Uri.encode(channelId)}&maxResults=1")
            j.optJSONArray("items")?.optJSONObject(0)?.optString("id").orEmpty()
        }catch(_:Exception){""}
    }
    private fun showChannel51(id:String,title:String,tabRaw:String){
        currentVideoId=null
        if(id.isBlank()){showApiError("频道",IllegalStateException("缺少频道 ID"));return}
        requireLoginOr{
            val tab=when(tabRaw){"videos"->"videos";"playlists"->"playlists";else->"home"}
            load(shell("subscriptions","<div class='simple'><h1>${esc(title.ifBlank{"频道"})}</h1><p>正在读取频道主页…</p></div>"))
            Thread{
                try{
                    val cj=apiGet("channels?part=snippet,statistics,contentDetails&id=${Uri.encode(id)}")
                    val item=cj.optJSONArray("items")?.optJSONObject(0)?:throw IllegalStateException("没有找到这个频道")
                    val sn=item.optJSONObject("snippet")?:JSONObject();val st=item.optJSONObject("statistics")?:JSONObject()
                    val channelTitle=sn.optString("title",title.ifBlank{"YouTube 频道"})
                    val avatar=sn.optJSONObject("thumbnails")?.optJSONObject("high")?.optString("url",sn.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url").orEmpty()).orEmpty()
                    val desc=sn.optString("description","").lineSequence().firstOrNull().orEmpty().take(180)
                    val subs=st.optString("subscriberCount","");val views=st.optString("viewCount","");val count=st.optString("videoCount","")
                    val uploads=item.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")?.optString("uploads").orEmpty()
                    val latest=if(uploads.isBlank())emptyList() else apiVideoList(apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=40"),true)
                    latest.forEach{dynamicVideoChannelIds[it.id]=id}
                    val pj=apiGet("playlists?part=snippet&channelId=${Uri.encode(id)}&maxResults=20")
                    val pa=pj.optJSONArray("items");val playlistCards=StringBuilder()
                    if(pa!=null)for(i in 0 until pa.length()){
                        val pi=pa.optJSONObject(i)?:continue;val pid=pi.optString("id");val ps=pi.optJSONObject("snippet")?:continue
                        val pt=ps.optString("title","播放列表");val img=ps.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url").orEmpty()
                        playlistCards.append("<a class='card' href='c16://playlist?id=${Uri.encode(pid)}&title=${Uri.encode(pt)}'><div class='thumb'><img src='${esc(img)}'></div><div class='ctitle'>${esc(pt)}</div><div class='cmeta'>${esc(channelTitle)} · 播放列表</div></a>")
                    }
                    val subId=subscriptionId51(id);val subscribed=subId.isNotBlank()
                    val subHref="c16://subtoggle?id=${Uri.encode(id)}&title=${Uri.encode(channelTitle)}&subid=${Uri.encode(subId)}"
                    val hero="<div class='channelHero50'><img src='${esc(avatar)}'><div><h1>${esc(channelTitle)}</h1><p>${esc(desc)}</p><div class='channelStats50'>${if(subs.isNotBlank())"<span>$subs 位订阅者</span>" else ""}${if(count.isNotBlank())"<span>$count 个视频</span>" else ""}${if(views.isNotBlank())"<span>$views 次观看</span>" else ""}</div></div><a class='subButton51 ${if(subscribed)"on" else ""}' href='$subHref'>${if(subscribed)"✓ 已订阅" else "订阅频道"}</a></div>"
                    fun tabLink(key:String,label:String)="<a class='channelTab51 ${if(tab==key)"on" else ""}' href='c16://channel?id=${Uri.encode(id)}&title=${Uri.encode(channelTitle)}&tab=$key'>$label</a>"
                    val tabs="<div class='channelTabs51'>${tabLink("home","主页")}${tabLink("videos","视频")}${tabLink("playlists","播放列表")}</div>"
                    val videosHtml=if(latest.isEmpty())"<div class='channelEmpty51'>这个频道暂时没有可显示的视频。</div>" else "<div class='grid'>${latest.joinToString(""){card(it)}}</div>"
                    val playlistsHtml=if(playlistCards.isEmpty())"<div class='channelEmpty51'>这个频道暂时没有公开播放列表。</div>" else "<div class='playlistMini50'>$playlistCards</div>"
                    val content=when(tab){
                        "videos"->"<div class='sectionHead'><h2>全部视频</h2><span>${latest.size} 个最新视频</span></div>$videosHtml"
                        "playlists"->"<div class='sectionHead'><h2>播放列表</h2><span>${pa?.length()?:0} 个公开列表</span></div>$playlistsHtml"
                        else->{
                            val homeVideos=if(latest.isEmpty())"" else "<div class='sectionHead'><h2>最新视频</h2><span>${latest.size} 个</span></div><div class='grid'>${latest.take(12).joinToString(""){card(it)}}</div>"
                            val homeLists=if(playlistCards.isEmpty())"" else "<div class='section' style='margin-top:32px'><div class='sectionHead'><h2>播放列表</h2><span>公开列表</span></div><div class='playlistMini50'>$playlistCards</div></div>"
                            homeVideos+homeLists
                        }
                    }
                    main.post{load(shell("subscriptions",hero+tabs+content+"<div style='height:42px'></div>"))}
                }catch(e:Exception){main.post{showApiError("频道",e)}}
            }.start()
        }
    }
    private fun toggleSubscription51(channelId:String,title:String,subscriptionId:String){
        if(channelId.isBlank())return
        requireLoginOr{
            load(shell("subscriptions","<div class='simple'><h1>${if(subscriptionId.isBlank())"正在订阅" else "正在取消订阅"}</h1><p>${esc(title.ifBlank{"YouTube 频道"})}</p></div>"))
            Thread{
                try{
                    if(subscriptionId.isBlank()){
                        val resource=JSONObject().put("kind","youtube#channel").put("channelId",channelId)
                        val body=JSONObject().put("snippet",JSONObject().put("resourceId",resource))
                        apiWrite51("subscriptions?part=snippet","POST",body)
                    }else apiWrite51("subscriptions?id=${Uri.encode(subscriptionId)}","DELETE",null)
                    homeSyncedAt=0L;homeSubscriptionFeed.clear();homeSyncError=""
                    main.post{showChannel51(channelId,title,"home")}
                }catch(e:Exception){main.post{showApiError(if(subscriptionId.isBlank())"订阅频道" else "取消订阅",e)}}
            }.start()
        }
    }
    private fun removeWatchLater51(id:String){
        if(id.isBlank()){showWatchLater51();return}
        val ids=watchLaterIds().filter{it!=id}
        prefs.edit().putString("watch_later_ids",ids.joinToString(",")).apply();showWatchLater51()
    }
    private fun showWatchLater51(){
        currentVideoId=null
        val list=watchLaterVideos()
        if(list.isEmpty()){
            load(shell("","<div class='simple'><h1>稍后观看</h1><p>在播放页点击“稍后观看”，视频会保存在这台 C16 上。</p><a class='chip' href='c16://home'>返回首页</a></div>"));return
        }
        val cards=list.joinToString(""){v->"<div class='manageCard51'><a class='remove51' href='c16://laterremove?id=${Uri.encode(v.id)}'>移除</a>${card(v)}</div>"}
        val head="<div class='manageBar51'><div><b>稍后观看</b><span>${list.size} 个保存在这台 C16 上的视频</span></div><a class='chip' href='c16://clearwatchlater'>清空全部</a></div>"
        load(shell("",head+"<div class='grid'>$cards</div><div style='height:36px'></div>"))
    }

'''
if 'private fun showChannel51(' not in s:
    if marker not in s: raise SystemExit('v5.1 method marker missing')
    s=s.replace(marker,methods+marker,1)

# Account center wording + version labels.
s=s.replace('C16 YouTube · V5.0','C16 YouTube · V5.1')
s=s.replace('"应用版本" to "5.0.40067"','"应用版本" to "5.1.40068"')

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V5.1 channel tabs/subscription/account/home/watch-later UX; playback core unchanged')
