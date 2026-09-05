from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V5.4: keep the proven player untouched. Remove artificial data caps and add user-driven pagination.
# V5.3 fetched at most four subscription pages; allow up to 100 pages (5000 channels) while still
# keeping a defensive guard against a broken/repeated nextPageToken.
s=s.replace('}while(token.isNotBlank() && guard<4)','}while(token.isNotBlank() && guard<100)',1)

# Route account/video collections through V5.4 paged loaders.
repls={
    '"search"->showSearch(u.getQueryParameter("q").orEmpty());':'"search"->showSearch54(u.getQueryParameter("q").orEmpty());"searchmore"->loadSearchMore54(u.getQueryParameter("q").orEmpty(),u.getQueryParameter("token").orEmpty());',
    '"likes"->showLikedVideos();':'"likes"->showLikedVideos54();"likesmore"->loadLikesMore54(u.getQueryParameter("token").orEmpty());',
    '"playlists"->showPlaylists();':'"playlists"->showPlaylists54();"playlistsmore"->loadPlaylistsMore54(u.getQueryParameter("token").orEmpty());',
    '"playlist"->showPlaylist(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty());':'"playlist"->showPlaylist54(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty());"playlistmore"->loadPlaylistMore54(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("token").orEmpty());',
    '"channel"->showChannel51(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("tab").orEmpty());':'"channel"->showChannel54(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("tab").orEmpty());"channelmore"->loadChannelMore54(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("uploads").orEmpty(),u.getQueryParameter("token").orEmpty());'
}
for old,new in repls.items():
    if old not in s: raise SystemExit('v5.4 route anchor missing: '+old[:40])
    s=s.replace(old,new,1)

css=r'''
/* V5.4 large collections: fetch 50 at a time, render incrementally instead of loading hundreds at once. */
.moreWrap54{display:flex;align-items:center;justify-content:center;gap:14px;margin:30px 0 8px}.more54{display:inline-flex;align-items:center;justify-content:center;min-width:190px;height:50px;padding:0 22px;border-radius:25px;background:$text;color:$bg;font-size:16px;font-weight:680;border:0}.more54.disabled{background:$p2;color:$sub}.loaded54{font-size:14px;color:$sub}.collectionNote54{padding:13px 17px;margin-bottom:18px;border-radius:17px;background:$panel;border:1px solid $border;color:$sub;font-size:14px}.channelVideoHead54{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-bottom:18px}.channelVideoHead54 h1{font-size:31px;margin:0}.channelVideoHead54 p{color:$sub;margin:6px 0 0;font-size:14px}.playlistGrid54{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:22px 17px}
@media(max-width:1700px){.playlistGrid54{grid-template-columns:repeat(4,minmax(0,1fr))}}
'''
if 'V5.4 large collections' not in s:s=s.replace('</style>',css+'</style>',1)

marker='''    private fun accountPill51():String{'''
methods=r'''    private fun appendHtml54(target:String,html:String){
        val js="var e=document.getElementById("+JSONObject.quote(target)+");if(e)e.insertAdjacentHTML('beforeend',"+JSONObject.quote(html)+");"
        web.evaluateJavascript(js,null)
    }
    private fun setMore54(target:String,html:String){
        val js="var e=document.getElementById("+JSONObject.quote(target)+");if(e)e.innerHTML="+JSONObject.quote(html)+";"
        web.evaluateJavascript(js,null)
    }
    private fun videoMoreButton54(host:String,params:String,token:String,loaded:Int):String{
        return if(token.isBlank())"<div class='moreWrap54'><span class='more54 disabled'>已加载全部</span><span class='loaded54'>已显示 $loaded 个</span></div>"
        else "<div class='moreWrap54'><a class='more54' href='c16://$host?$params&token=${Uri.encode(token)}'>加载更多 50 个</a><span class='loaded54'>当前已显示 $loaded 个</span></div>"
    }
    private fun showSearch54(q:String){
        val query=q.trim();currentVideoId=null
        if(query.isBlank()){showSearch("");return}
        if(prefs.getString("access_token","").orEmpty().isBlank()){showSearch(query);return}
        val body="<div class='collectionNote54'>YouTube 搜索 · 每次加载最多 50 个结果，继续点击“加载更多”即可读取下一页。</div><div class='sectionHead'><h2>搜索：${esc(query)}</h2><span id='searchCount54'>正在加载…</span></div><div id='searchGrid54' class='grid'></div><div id='searchMore54'></div>"
        load(shell("search",body));fetchSearchPage54(query,"",false)
    }
    private fun loadSearchMore54(q:String,token:String){if(q.isNotBlank()&&token.isNotBlank())fetchSearchPage54(q,token,true)}
    private fun fetchSearchPage54(q:String,token:String,append:Boolean){
        Thread{try{
            val suffix=if(token.isBlank())"" else "&pageToken=${Uri.encode(token)}"
            val j=apiGet("search?part=snippet&type=video&videoEmbeddable=true&maxResults=50&relevanceLanguage=zh-Hans&q=${Uri.encode(q)}$suffix")
            val list=apiSearchVideos(j);val next=j.optString("nextPageToken","")
            val html=list.joinToString(""){card(it)}
            main.post{
                if(append)appendHtml54("searchGrid54",html) else setMore54("searchGrid54",html)
                val current="document.getElementById('searchGrid54')?document.getElementById('searchGrid54').children.length:0"
                web.evaluateJavascript("var n=$current;var c=document.getElementById('searchCount54');if(c)c.textContent=n+' 个已加载';var m=document.getElementById('searchMore54');if(m)m.innerHTML="+JSONObject.quote(videoMoreButton54("searchmore","q=${Uri.encode(q)}",next,0))+".replace('当前已显示 0 个','继续加载下一页');",null)
            }
        }catch(e:Exception){main.post{setMore54("searchMore54","<div class='searchNotice'>加载更多失败：${esc((e.message?:"请求失败").take(150))}</div>")}}}.start()
    }
    private fun showLikedVideos54(){
        currentVideoId=null;requireLoginOr{
            load(shell("","<div class='collectionNote54'>点赞视频 · 每次读取 50 个，不再只显示前几十个。</div><div class='sectionHead'><h2>点赞视频</h2><span id='likesCount54'>正在加载…</span></div><div id='likesGrid54' class='grid'></div><div id='likesMore54'></div>"));fetchLikesPage54("",false)
        }
    }
    private fun loadLikesMore54(token:String){if(token.isNotBlank())fetchLikesPage54(token,true)}
    private fun fetchLikesPage54(token:String,append:Boolean){
        Thread{try{
            val suffix=if(token.isBlank())"" else "&pageToken=${Uri.encode(token)}"
            val j=apiGet("videos?part=snippet&myRating=like&maxResults=50$suffix");val list=apiVideoList(j);val next=j.optString("nextPageToken","");val html=list.joinToString(""){card(it)}
            main.post{if(append)appendHtml54("likesGrid54",html) else setMore54("likesGrid54",html);web.evaluateJavascript("var n=document.getElementById('likesGrid54')?document.getElementById('likesGrid54').children.length:0;var c=document.getElementById('likesCount54');if(c)c.textContent=n+' 个已加载';var m=document.getElementById('likesMore54');if(m)m.innerHTML="+JSONObject.quote(videoMoreButton54("likesmore","from=likes",next,0))+".replace('当前已显示 0 个','继续加载下一页');",null)}
        }catch(e:Exception){main.post{setMore54("likesMore54","<div class='searchNotice'>点赞视频加载失败：${esc((e.message?:"请求失败").take(150))}</div>")}}}.start()
    }
    private fun showPlaylists54(){
        currentVideoId=null;requireLoginOr{
            load(shell("","<div class='collectionNote54'>我的播放列表 · 每次读取 50 个。</div><div class='sectionHead'><h2>播放列表</h2><span id='plCount54'>正在加载…</span></div><div id='plGrid54' class='playlistGrid54'></div><div id='plMore54'></div>"));fetchPlaylistsPage54("",false)
        }
    }
    private fun loadPlaylistsMore54(token:String){if(token.isNotBlank())fetchPlaylistsPage54(token,true)}
    private fun fetchPlaylistsPage54(token:String,append:Boolean){
        Thread{try{
            val suffix=if(token.isBlank())"" else "&pageToken=${Uri.encode(token)}";val j=apiGet("playlists?part=snippet&mine=true&maxResults=50$suffix");val arr=j.optJSONArray("items");val b=StringBuilder()
            if(arr!=null)for(i in 0 until arr.length()){val item=arr.optJSONObject(i)?:continue;val id=item.optString("id");val sn=item.optJSONObject("snippet")?:continue;val title=sn.optString("title","播放列表");val img=sn.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url",sn.optJSONObject("thumbnails")?.optJSONObject("default")?.optString("url").orEmpty()).orEmpty();b.append("<a class='card' href='c16://playlist?id=${Uri.encode(id)}&title=${Uri.encode(title)}'><div class='thumb'><img src='${esc(img)}'></div><div class='ctitle'>${esc(title)}</div><div class='cmeta'>播放列表 · 点击打开</div></a>")}
            val next=j.optString("nextPageToken","");main.post{if(append)appendHtml54("plGrid54",b.toString()) else setMore54("plGrid54",b.toString());web.evaluateJavascript("var n=document.getElementById('plGrid54')?document.getElementById('plGrid54').children.length:0;var c=document.getElementById('plCount54');if(c)c.textContent=n+' 个已加载';var m=document.getElementById('plMore54');if(m)m.innerHTML="+JSONObject.quote(videoMoreButton54("playlistsmore","from=playlists",next,0))+".replace('当前已显示 0 个','继续加载下一页');",null)}
        }catch(e:Exception){main.post{setMore54("plMore54","<div class='searchNotice'>播放列表加载失败：${esc((e.message?:"请求失败").take(150))}</div>")}}}.start()
    }
    private fun showPlaylist54(id:String,title:String){
        currentVideoId=null;if(id.isBlank())return;requireLoginOr{
            val t=title.ifBlank{"播放列表"};load(shell("","<div class='collectionNote54'>播放列表视频 · 每次读取 50 个，按需继续加载。</div><div class='sectionHead'><h2>${esc(t)}</h2><span id='pliCount54'>正在加载…</span></div><div id='pliGrid54' class='grid'></div><div id='pliMore54'></div>"));fetchPlaylistPage54(id,t,"",false)
        }
    }
    private fun loadPlaylistMore54(id:String,title:String,token:String){if(id.isNotBlank()&&token.isNotBlank())fetchPlaylistPage54(id,title,token,true)}
    private fun fetchPlaylistPage54(id:String,title:String,token:String,append:Boolean){
        Thread{try{val suffix=if(token.isBlank())"" else "&pageToken=${Uri.encode(token)}";val j=apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(id)}&maxResults=50$suffix");val list=apiVideoList(j,true);val next=j.optString("nextPageToken","");val html=list.joinToString(""){card(it)};main.post{if(append)appendHtml54("pliGrid54",html) else setMore54("pliGrid54",html);web.evaluateJavascript("var n=document.getElementById('pliGrid54')?document.getElementById('pliGrid54').children.length:0;var c=document.getElementById('pliCount54');if(c)c.textContent=n+' 个已加载';var m=document.getElementById('pliMore54');if(m)m.innerHTML="+JSONObject.quote(videoMoreButton54("playlistmore","id=${Uri.encode(id)}&title=${Uri.encode(title)}",next,0))+".replace('当前已显示 0 个','继续加载下一页');",null)}}catch(e:Exception){main.post{setMore54("pliMore54","<div class='searchNotice'>视频加载失败：${esc((e.message?:"请求失败").take(150))}</div>")}}}.start()
    }
    private fun showChannel54(id:String,title:String,tabRaw:String){
        if(tabRaw!="videos"){showChannel51(id,title,tabRaw);return};currentVideoId=null;if(id.isBlank())return
        requireLoginOr{Thread{try{val cj=apiGet("channels?part=snippet,contentDetails&id=${Uri.encode(id)}");val item=cj.optJSONArray("items")?.optJSONObject(0)?:throw IllegalStateException("没有找到频道");val sn=item.optJSONObject("snippet")?:JSONObject();val t=sn.optString("title",title.ifBlank{"YouTube 频道"});val uploads=item.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")?.optString("uploads").orEmpty();if(uploads.isBlank())throw IllegalStateException("没有找到频道上传列表");val html="<div class='channelVideoHead54'><div><h1>${esc(t)}</h1><p>频道全部视频 · 每次读取 50 个</p></div><a class='chip' href='c16://channel?id=${Uri.encode(id)}&title=${Uri.encode(t)}&tab=home'>返回频道主页</a></div><div class='channelTabs51'><a class='channelTab51' href='c16://channel?id=${Uri.encode(id)}&title=${Uri.encode(t)}&tab=home'>主页</a><a class='channelTab51 on' href='c16://channel?id=${Uri.encode(id)}&title=${Uri.encode(t)}&tab=videos'>视频</a><a class='channelTab51' href='c16://channel?id=${Uri.encode(id)}&title=${Uri.encode(t)}&tab=playlists'>播放列表</a></div><div id='chGrid54' class='grid'></div><div id='chMore54'></div>";main.post{load(shell("subscriptions",html));fetchChannelPage54(id,t,uploads,"",false)}}catch(e:Exception){main.post{showApiError("频道视频",e)}}}.start()}
    }
    private fun loadChannelMore54(id:String,title:String,uploads:String,token:String){if(uploads.isNotBlank()&&token.isNotBlank())fetchChannelPage54(id,title,uploads,token,true)}
    private fun fetchChannelPage54(id:String,title:String,uploads:String,token:String,append:Boolean){
        Thread{try{val suffix=if(token.isBlank())"" else "&pageToken=${Uri.encode(token)}";val j=apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=50$suffix");val list=apiVideoList(j,true);list.forEach{dynamicVideoChannelIds[it.id]=id};val next=j.optString("nextPageToken","");val html=list.joinToString(""){card(it)};main.post{if(append)appendHtml54("chGrid54",html) else setMore54("chGrid54",html);val more=videoMoreButton54("channelmore","id=${Uri.encode(id)}&title=${Uri.encode(title)}&uploads=${Uri.encode(uploads)}",next,0).replace("当前已显示 0 个","继续加载下一页");setMore54("chMore54",more)}}catch(e:Exception){main.post{setMore54("chMore54","<div class='searchNotice'>频道视频加载失败：${esc((e.message?:"请求失败").take(150))}</div>")}}}.start()
    }

'''
if marker not in s: raise SystemExit('v5.4 method marker missing')
s=s.replace(marker,methods+marker,1)

s=s.replace('C16 YouTube · V5.3','C16 YouTube · V5.4')
s=s.replace('"应用版本" to "5.3.40070"','"应用版本" to "5.4.40071"')
p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V5.4 full pagination and load-more')
