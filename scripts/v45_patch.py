from pathlib import Path

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

old = '''"subscriptions"->showSimple("订阅","V4.4 已恢复账号授权入口；订阅频道同步将在授权后继续接入。");"local"'''
new = '''"subscriptions"->showSubscriptions();"likes"->showLikedVideos();"playlists"->showPlaylists();"playlist"->showPlaylist(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty());"channel"->showChannel(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty());"local"'''
if old not in s: raise SystemExit('v4.5 route subscriptions target missing')
s = s.replace(old,new,1)

s = s.replace('C16 YouTube · V4.4</p>', 'C16 YouTube · V4.5</p>', 1)

old_comments = '''val comments="<div class='comments'><h2>评论</h2><div class='comment'><div class='commentAvatar'></div><div><b>C16 YouTube</b><p>评论区保留；真实评论仍需 YouTube Data API 对应权限，未授权时不伪造评论数据。</p></div></div></div>"'''
new_comments = '''val comments="<div class='comments'><h2>评论</h2><div id='commentsBody'><div class='comment'><div class='commentAvatar'></div><div><b>YouTube</b><p>正在读取真实评论…</p></div></div></div></div>"'''
if old_comments not in s: raise SystemExit('v4.5 comments target missing')
s = s.replace(old_comments,new_comments,1)

old_channel = '''<a class='channelText' href='c16://category?name=${Uri.encode(v.category)}'><b>${esc(v.channel)}</b><span>点击查看更多相关内容</span></a>'''
new_channel = '''<a class='channelText' href='c16://search?q=${Uri.encode(v.channel)}'><b>${esc(v.channel)}</b><span>点击搜索频道相关内容</span></a>'''
if old_channel in s: s = s.replace(old_channel,new_channel,1)

old_end = '''</aside></div>""";load(shell("",body,true))
    }
'''
new_end = '''</aside></div>""";load(shell("",body,true));fetchCommentsAsync(id)
    }
'''
if old_end not in s: raise SystemExit('v4.5 player load target missing')
s = s.replace(old_end,new_end,1)

old_account = '''    private fun showAccountCenter(){
        currentVideoId=null
        val body="""<div class='simple' style='max-width:1080px;margin:0 auto'><div style='display:flex;align-items:center;gap:22px'><div class='avatar' style='width:82px;height:82px'></div><div><h1 style='margin:0'>YouTube 账号已连接</h1><p style='margin:8px 0 0'>V4.4 已保存授权令牌，可继续接入订阅、点赞、播放列表和公开评论。</p></div></div><div style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:28px'><a class='chip' href='c16://subscriptions'>订阅</a><a class='chip' href='c16://history'>观看历史</a><a class='chip' href='c16://favorites'>车机收藏</a></div><div style='margin-top:28px'><a class='chip' href='c16://logout'>退出账号</a></div></div>"""
        load(shell("",body))
    }
'''
new_account = '''    private fun showAccountCenter(){
        currentVideoId=null
        val body="""<div class='simple' style='max-width:1120px;margin:0 auto'><div id='accountProfile' style='display:flex;align-items:center;gap:22px'><div class='avatar' style='width:82px;height:82px'></div><div><h1 style='margin:0'>YouTube 账号已连接</h1><p style='margin:8px 0 0'>正在同步你的 YouTube 账号资料…</p></div></div><div style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:28px'><a class='chip' href='c16://subscriptions'>订阅频道</a><a class='chip' href='c16://likes'>点赞视频</a><a class='chip' href='c16://playlists'>播放列表</a><a class='chip' href='c16://history'>车机历史</a><a class='chip' href='c16://favorites'>车机收藏</a><a class='chip' href='c16://settings'>设置</a></div><div style='margin-top:28px'><a class='chip' href='c16://logout'>退出账号</a></div></div>"""
        load(shell("",body));fetchAccountProfileAsync()
    }
'''
if old_account not in s: raise SystemExit('v4.5 account center target missing')
s = s.replace(old_account,new_account,1)

methods = r'''    private fun ensureAccessToken():String{
        val token=prefs.getString("access_token","").orEmpty()
        val expires=prefs.getLong("token_expires_at",0L)
        if(token.isNotBlank() && System.currentTimeMillis()<expires-60000L)return token
        val refresh=prefs.getString("refresh_token","").orEmpty()
        val client=prefs.getString("oauth_client_id","").orEmpty()
        val secret=prefs.getString("oauth_client_secret","").orEmpty()
        if(refresh.isBlank()||client.isBlank()||secret.isBlank())return token
        return try{
            val (status,text)=postForm("https://oauth2.googleapis.com/token",mapOf("client_id" to client,"client_secret" to secret,"refresh_token" to refresh,"grant_type" to "refresh_token"))
            val j=JSONObject(text)
            if(status in 200..299&&j.has("access_token")){
                val fresh=j.getString("access_token")
                prefs.edit().putString("access_token",fresh).putLong("token_expires_at",System.currentTimeMillis()+j.optLong("expires_in",3600)*1000L).apply();fresh
            }else token
        }catch(_:Exception){token}
    }
    private fun apiGet(path:String):JSONObject{
        val token=ensureAccessToken()
        if(token.isBlank())throw IllegalStateException("请先登录 YouTube")
        val c=URL("https://www.googleapis.com/youtube/v3/$path").openConnection() as HttpURLConnection
        c.requestMethod="GET";c.connectTimeout=15000;c.readTimeout=15000;c.setRequestProperty("Authorization","Bearer $token");c.setRequestProperty("Accept","application/json")
        val code=c.responseCode;val stream=if(code in 200..299)c.inputStream else c.errorStream;val text=stream?.bufferedReader()?.use{it.readText()}.orEmpty();c.disconnect()
        if(code !in 200..299){val msg=try{JSONObject(text).optJSONObject("error")?.optString("message")?:text}catch(_:Exception){text};throw IllegalStateException(msg.ifBlank{"YouTube API 请求失败 ($code)"})}
        return JSONObject(text)
    }
    private fun apiVideoList(j:JSONObject,playlistItems:Boolean=false):List<Video>{
        val arr=j.optJSONArray("items")?:return emptyList();val out=mutableListOf<Video>()
        for(i in 0 until arr.length()){
            val item=arr.optJSONObject(i)?:continue;val sn=item.optJSONObject("snippet")?:continue
            val id=if(playlistItems)sn.optJSONObject("resourceId")?.optString("videoId").orEmpty() else item.optString("id")
            if(id.isBlank())continue
            out+=Video(id,sn.optString("title","YouTube 视频"),sn.optString("channelTitle","YouTube"),"YouTube · 账号内容","推荐")
        };return out
    }
    private fun requireLoginOr(action:()->Unit){if(prefs.getString("access_token","").orEmpty().isBlank())showLoginCenter() else action()}
    private fun showSubscriptions(){
        currentVideoId=null;requireLoginOr{
            load(shell("subscriptions","<div class='sectionHead'><h2>订阅频道</h2><span>正在同步 YouTube…</span></div><div class='simple'><p>正在读取你的真实订阅频道。</p></div>"))
            Thread{try{val j=apiGet("subscriptions?part=snippet&mine=true&maxResults=30");val arr=j.optJSONArray("items");val cards=StringBuilder();if(arr!=null)for(i in 0 until arr.length()){val sn=arr.optJSONObject(i)?.optJSONObject("snippet")?:continue;val rid=sn.optJSONObject("resourceId")?.optString("channelId").orEmpty();val title=sn.optString("title","YouTube 频道");val img=sn.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url").orEmpty();cards.append("<a class='card' href='c16://channel?id=${Uri.encode(rid)}&title=${Uri.encode(title)}'><div class='thumb'><img src='${esc(img)}'></div><div class='ctitle'>${esc(title)}</div><div class='cmeta'>订阅频道 · 查看最新视频</div></a>")};val html="<div class='sectionHead'><h2>订阅频道</h2><span>${arr?.length()?:0} 个频道</span></div><div class='grid'>$cards</div>";main.post{load(shell("subscriptions",html))}}catch(e:Exception){main.post{showApiError("订阅频道",e)}}}.start()
        }
    }
    private fun showLikedVideos(){
        currentVideoId=null;requireLoginOr{
            load(shell("","<div class='simple'><h1>点赞视频</h1><p>正在同步 YouTube…</p></div>"))
            Thread{try{val list=apiVideoList(apiGet("videos?part=snippet&myRating=like&maxResults=30"));val html="<div class='sectionHead'><h2>点赞视频</h2><span>${list.size} 个视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>";main.post{load(shell("",html))}}catch(e:Exception){main.post{showApiError("点赞视频",e)}}}.start()
        }
    }
    private fun showPlaylists(){
        currentVideoId=null;requireLoginOr{
            load(shell("","<div class='simple'><h1>播放列表</h1><p>正在同步 YouTube…</p></div>"))
            Thread{try{val j=apiGet("playlists?part=snippet&mine=true&maxResults=30");val arr=j.optJSONArray("items");val cards=StringBuilder();if(arr!=null)for(i in 0 until arr.length()){val item=arr.optJSONObject(i)?:continue;val id=item.optString("id");val sn=item.optJSONObject("snippet")?:continue;val title=sn.optString("title","播放列表");val img=sn.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url").orEmpty();cards.append("<a class='card' href='c16://playlist?id=${Uri.encode(id)}&title=${Uri.encode(title)}'><div class='thumb'><img src='${esc(img)}'></div><div class='ctitle'>${esc(title)}</div><div class='cmeta'>播放列表 · 点击打开</div></a>")};val html="<div class='sectionHead'><h2>播放列表</h2><span>${arr?.length()?:0} 个</span></div><div class='grid'>$cards</div>";main.post{load(shell("",html))}}catch(e:Exception){main.post{showApiError("播放列表",e)}}}.start()
        }
    }
    private fun showPlaylist(id:String,title:String){
        currentVideoId=null;requireLoginOr{
            load(shell("","<div class='simple'><h1>${esc(title.ifBlank{"播放列表"})}</h1><p>正在读取视频…</p></div>"))
            Thread{try{val list=apiVideoList(apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(id)}&maxResults=40"),true);val html="<div class='sectionHead'><h2>${esc(title.ifBlank{"播放列表"})}</h2><span>${list.size} 个视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>";main.post{load(shell("",html))}}catch(e:Exception){main.post{showApiError("播放列表",e)}}}.start()
        }
    }
    private fun showChannel(id:String,title:String){
        currentVideoId=null;requireLoginOr{
            load(shell("subscriptions","<div class='simple'><h1>${esc(title.ifBlank{"频道"})}</h1><p>正在读取频道最新视频…</p></div>"))
            Thread{try{val cj=apiGet("channels?part=contentDetails&id=${Uri.encode(id)}");val uploads=cj.optJSONArray("items")?.optJSONObject(0)?.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")?.optString("uploads").orEmpty();if(uploads.isBlank())throw IllegalStateException("没有找到频道上传列表");val list=apiVideoList(apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=40"),true);val html="<div class='sectionHead'><h2>${esc(title.ifBlank{"频道"})}</h2><span>${list.size} 个最新视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>";main.post{load(shell("subscriptions",html))}}catch(e:Exception){main.post{showApiError("频道",e)}}}.start()
        }
    }
    private fun fetchAccountProfileAsync(){
        Thread{try{val j=apiGet("channels?part=snippet,statistics&mine=true");val item=j.optJSONArray("items")?.optJSONObject(0)?:return@Thread;val sn=item.optJSONObject("snippet")?:return@Thread;val st=item.optJSONObject("statistics");val title=sn.optString("title","YouTube");val img=sn.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url").orEmpty();val subs=st?.optString("subscriberCount","").orEmpty();val html="<img src='${esc(img)}' style='width:82px;height:82px;border-radius:50%;object-fit:cover'><div><h1 style='margin:0'>${esc(title)}</h1><p style='margin:8px 0 0'>YouTube 账号已连接${if(subs.isNotBlank())" · $subs 位订阅者" else ""}</p></div>";main.post{web.evaluateJavascript("document.getElementById('accountProfile')&& (document.getElementById('accountProfile').innerHTML="+JSONObject.quote(html)+")",null)}}catch(_:Exception){}}.start()
    }
    private fun fetchCommentsAsync(videoId:String){
        if(prefs.getString("access_token","").orEmpty().isBlank())return
        Thread{try{val j=apiGet("commentThreads?part=snippet&videoId=${Uri.encode(videoId)}&maxResults=12&order=relevance&textFormat=plainText");val arr=j.optJSONArray("items");val b=StringBuilder();if(arr!=null)for(i in 0 until arr.length()){val top=arr.optJSONObject(i)?.optJSONObject("snippet")?.optJSONObject("topLevelComment")?.optJSONObject("snippet")?:continue;val author=top.optString("authorDisplayName","YouTube 用户");val text=top.optString("textDisplay","");val avatar=top.optString("authorProfileImageUrl","");b.append("<div class='comment'><div class='commentAvatar' style=\"background-image:url('${esc(avatar)}');background-size:cover\"></div><div><b>${esc(author)}</b><p>${esc(text)}</p></div></div>")};val html=if(b.isEmpty())"<div class='comment'><div><p>这个视频暂时没有可显示的评论。</p></div></div>" else b.toString();main.postDelayed({web.evaluateJavascript("document.getElementById('commentsBody')&& (document.getElementById('commentsBody').innerHTML="+JSONObject.quote(html)+")",null)},700)}catch(e:Exception){val msg=if((e.message?:"").contains("disabled",true))"该视频已关闭评论。" else "评论暂时无法读取：${esc(e.message?:"YouTube API 错误")}";main.postDelayed({web.evaluateJavascript("document.getElementById('commentsBody')&& (document.getElementById('commentsBody').innerHTML="+JSONObject.quote("<div class='comment'><div><p>$msg</p></div></div>")+")",null)},700)}}.start()
    }
    private fun showApiError(title:String,e:Exception){
        val body="<div class='simple'><h1>${esc(title)}</h1><p>${esc(e.message?:"YouTube API 暂时不可用")}</p><a class='chip' href='c16://login'>账号中心</a></div>";load(shell("",body))
    }

'''
marker='    private fun showSimple(title:String,copy:String)'
if 'private fun ensureAccessToken()' not in s:
    if marker not in s: raise SystemExit('v4.5 methods marker missing')
    s=s.replace(marker,methods+marker,1)

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V4.5 YouTube account data sync')
