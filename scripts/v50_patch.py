from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V5.0 freezes the proven V4.8/V4.9 playback core and focuses on product functionality.
# Keep a channel-id map for API-loaded videos so search/channel navigation can be real.
field='    private val dynamicVideos=java.util.concurrent.ConcurrentHashMap<String,Video>()\n'
if 'dynamicVideoChannelIds' not in s:
    if field not in s: raise SystemExit('v5.0 dynamicVideos field missing')
    s=s.replace(field,field+'    private val dynamicVideoChannelIds=java.util.concurrent.ConcurrentHashMap<String,String>()\n',1)

# Routes: real Watch Later collection while preserving all existing player routes.
route_anchor='''"favorites"->showFavorites();'''
route_new='''"favorites"->showFavorites();"watchlater"->showWatchLater();"later"->toggleWatchLater(u.getQueryParameter("id").orEmpty());'''
if route_anchor not in s: raise SystemExit('v5.0 route favorites anchor missing')
s=s.replace(route_anchor,route_new,1)

# Top account button shows the synced channel name when available.
old_login='''<a class='pill' href='c16://login'>${if(prefs.getString("access_token","").orEmpty().isNotBlank())"账号" else "登录"}</a>'''
new_login='''<a class='pill' href='c16://login'>${if(prefs.getString("access_token","").orEmpty().isNotBlank())prefs.getString("account_title","账号").orEmpty().ifBlank{"账号"}.take(10) else "登录"}</a>'''
if old_login in s:
    s=s.replace(old_login,new_login,1)

# V5.0 UI additions for real search/channel pages. No player CSS is modified.
css_anchor='.emptyShelf{padding:24px;border:1px dashed $border;border-radius:18px;color:$sub;background:$panel;font-size:16px}'
css_add='''.emptyShelf{padding:24px;border:1px dashed $border;border-radius:18px;color:$sub;background:$panel;font-size:16px}.searchNotice{padding:16px 18px;border-radius:18px;background:$panel;border:1px solid $border;margin-bottom:18px;color:$sub;font-size:16px}.channelHero50{display:grid;grid-template-columns:120px 1fr auto;gap:22px;align-items:center;padding:26px;border-radius:24px;background:$panel;border:1px solid $border;margin-bottom:26px}.channelHero50 img{width:120px;height:120px;border-radius:50%;object-fit:cover;background:$p2}.channelHero50 h1{font-size:36px;margin:0 0 8px}.channelHero50 p{margin:6px 0;color:$sub;font-size:16px;line-height:1.5}.channelStats50{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px}.channelStats50 span{padding:7px 11px;border-radius:15px;background:$p2;font-size:14px;color:$text}.playlistMini50{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px}.playlistMini50 .thumb{position:relative}.playlistMini50 .thumb:after{content:'播放列表';position:absolute;right:8px;bottom:8px;padding:4px 8px;border-radius:10px;background:rgba(0,0,0,.72);color:#fff;font-size:12px}'''
if css_anchor not in s: raise SystemExit('v5.0 CSS anchor missing')
s=s.replace(css_anchor,css_add,1)

# Replace the static-only search with authenticated YouTube search, while retaining a useful
# local fallback when the user is not logged in. Search API is only called after an explicit query.
old_search='''    private fun showSearch(q:String){currentVideoId=null;val list=if(q.isBlank())videos else videos.filter{it.title.contains(q,true)||it.channel.contains(q,true)||it.category.contains(q,true)};val body="<div class='sectionHead'><h2>搜索${if(q.isBlank())"" else "：${esc(q)}"}</h2><span>${list.size} 个结果</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>";load(shell("search",body))}
'''
new_search='''    private fun showSearch(q:String){
        currentVideoId=null
        val query=q.trim()
        if(query.isBlank()){
            val body="<div class='sectionHead'><h2>探索</h2><span>选择分类或输入关键词</span></div><div class='chips'>${chips("推荐")}</div>${rail("热门内容","车机内置精选",videos.take(12))}"
            load(shell("search",body));return
        }
        val local=videos.filter{it.title.contains(query,true)||it.channel.contains(query,true)||it.category.contains(query,true)}
        if(prefs.getString("access_token","").orEmpty().isBlank()){
            val notice="<div class='searchNotice'>当前显示车机本地匹配结果。登录 YouTube 后可搜索真实 YouTube 视频。</div>"
            val body="$notice<div class='sectionHead'><h2>搜索：${esc(query)}</h2><span>${local.size} 个本地结果</span></div><div class='grid'>${local.joinToString(""){card(it)}}</div>"
            load(shell("search",body));return
        }
        load(shell("search","<div class='simple'><h1>搜索：${esc(query)}</h1><p>正在从 YouTube 获取结果…</p></div>"))
        Thread{
            try{
                val j=apiGet("search?part=snippet&type=video&maxResults=25&q=${Uri.encode(query)}")
                val list=apiSearchVideos(j)
                val html="<div class='searchNotice'>YouTube 搜索结果 · 点击视频直接进入 C16 播放页</div><div class='sectionHead'><h2>搜索：${esc(query)}</h2><span>${list.size} 个结果</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>"
                main.post{load(shell("search",html))}
            }catch(e:Exception){
                main.post{
                    val fallback="<div class='searchNotice'>YouTube 搜索暂不可用：${esc((e.message?:"请求失败").take(120))}。下面显示车机本地匹配。</div><div class='sectionHead'><h2>搜索：${esc(query)}</h2><span>${local.size} 个本地结果</span></div><div class='grid'>${local.joinToString(""){card(it)}}</div>"
                    load(shell("search",fallback))
                }
            }
        }.start()
    }
'''
if old_search not in s: raise SystemExit('v5.0 showSearch target missing')
s=s.replace(old_search,new_search,1)

# Store channel ids for API video lists as well.
api_line='''val v=Video(id,sn.optString("title","YouTube 视频"),sn.optString("channelTitle","YouTube"),"YouTube · 账号内容","推荐");dynamicVideos[id]=v;out+=v'''
api_line_new='''val v=Video(id,sn.optString("title","YouTube 视频"),sn.optString("channelTitle","YouTube"),"YouTube · 账号内容","推荐");dynamicVideos[id]=v;val channelId=sn.optString("channelId",sn.optString("videoOwnerChannelId",""));if(channelId.isNotBlank())dynamicVideoChannelIds[id]=channelId;out+=v'''
if api_line not in s: raise SystemExit('v5.0 apiVideoList target missing')
s=s.replace(api_line,api_line_new,1)

# Parse search.list responses whose id is an object rather than a string.
method_marker='''    private fun requireLoginOr(action:()->Unit)'''
search_parser='''    private fun apiSearchVideos(j:JSONObject):List<Video>{
        val arr=j.optJSONArray("items")?:return emptyList()
        val out=mutableListOf<Video>()
        for(i in 0 until arr.length()){
            val item=arr.optJSONObject(i)?:continue
            val id=item.optJSONObject("id")?.optString("videoId").orEmpty()
            val sn=item.optJSONObject("snippet")?:continue
            if(id.isBlank())continue
            val v=Video(id,sn.optString("title","YouTube 视频"),sn.optString("channelTitle","YouTube"),"YouTube · 搜索结果","推荐")
            dynamicVideos[id]=v
            val channelId=sn.optString("channelId","")
            if(channelId.isNotBlank())dynamicVideoChannelIds[id]=channelId
            out+=v
        }
        return out
    }
'''
if 'private fun apiSearchVideos(' not in s:
    if method_marker not in s: raise SystemExit('v5.0 search parser marker missing')
    s=s.replace(method_marker,search_parser+method_marker,1)

# Upgrade channel pages: real profile, statistics, latest uploads and public playlists.
old_channel='''    private fun showChannel(id:String,title:String){
        currentVideoId=null;requireLoginOr{
            load(shell("subscriptions","<div class='simple'><h1>${esc(title.ifBlank{"频道"})}</h1><p>正在读取频道最新视频…</p></div>"))
            Thread{try{val cj=apiGet("channels?part=contentDetails&id=${Uri.encode(id)}");val uploads=cj.optJSONArray("items")?.optJSONObject(0)?.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")?.optString("uploads").orEmpty();if(uploads.isBlank())throw IllegalStateException("没有找到频道上传列表");val list=apiVideoList(apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=40"),true);val html="<div class='sectionHead'><h2>${esc(title.ifBlank{"频道"})}</h2><span>${list.size} 个最新视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>";main.post{load(shell("subscriptions",html))}}catch(e:Exception){main.post{showApiError("频道",e)}}}.start()
        }
    }
'''
new_channel='''    private fun showChannel(id:String,title:String){
        currentVideoId=null;requireLoginOr{
            load(shell("subscriptions","<div class='simple'><h1>${esc(title.ifBlank{"频道"})}</h1><p>正在读取频道主页…</p></div>"))
            Thread{
                try{
                    val cj=apiGet("channels?part=snippet,statistics,contentDetails&id=${Uri.encode(id)}")
                    val item=cj.optJSONArray("items")?.optJSONObject(0)?:throw IllegalStateException("没有找到这个频道")
                    val sn=item.optJSONObject("snippet")?:JSONObject()
                    val st=item.optJSONObject("statistics")?:JSONObject()
                    val channelTitle=sn.optString("title",title.ifBlank{"YouTube 频道"})
                    val avatar=sn.optJSONObject("thumbnails")?.optJSONObject("high")?.optString("url",sn.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url").orEmpty()).orEmpty()
                    val desc=sn.optString("description","").lineSequence().firstOrNull().orEmpty().take(180)
                    val subs=st.optString("subscriberCount","")
                    val views=st.optString("viewCount","")
                    val count=st.optString("videoCount","")
                    val uploads=item.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")?.optString("uploads").orEmpty()
                    val latest=if(uploads.isBlank())emptyList() else apiVideoList(apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=30"),true)
                    val pj=apiGet("playlists?part=snippet&channelId=${Uri.encode(id)}&maxResults=10")
                    val pa=pj.optJSONArray("items")
                    val playlists=StringBuilder()
                    if(pa!=null)for(i in 0 until pa.length()){
                        val pi=pa.optJSONObject(i)?:continue;val pid=pi.optString("id");val ps=pi.optJSONObject("snippet")?:continue;val pt=ps.optString("title","播放列表");val img=ps.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url").orEmpty()
                        playlists.append("<a class='card' href='c16://playlist?id=${Uri.encode(pid)}&title=${Uri.encode(pt)}'><div class='thumb'><img src='${esc(img)}'></div><div class='ctitle'>${esc(pt)}</div><div class='cmeta'>${esc(channelTitle)} · 播放列表</div></a>")
                    }
                    val hero="<div class='channelHero50'><img src='${esc(avatar)}'><div><h1>${esc(channelTitle)}</h1><p>${esc(desc)}</p><div class='channelStats50'>${if(subs.isNotBlank())"<span>$subs 位订阅者</span>" else ""}${if(count.isNotBlank())"<span>$count 个视频</span>" else ""}${if(views.isNotBlank())"<span>$views 次观看</span>" else ""}</div></div><a class='chip' href='c16://subscriptions'>我的订阅</a></div>"
                    val videoSection="<div class='sectionHead'><h2>最新视频</h2><span>${latest.size} 个</span></div><div class='grid'>${latest.joinToString(""){card(it)}}</div>"
                    val playlistSection=if(playlists.isEmpty())"" else "<div class='section' style='margin-top:32px'><div class='sectionHead'><h2>播放列表</h2><span>公开列表</span></div><div class='playlistMini50'>$playlists</div></div>"
                    main.post{load(shell("subscriptions",hero+videoSection+playlistSection+"<div style='height:40px'></div>"))}
                }catch(e:Exception){main.post{showApiError("频道",e)}}
            }.start()
        }
    }
'''
if old_channel not in s: raise SystemExit('v5.0 showChannel target missing')
s=s.replace(old_channel,new_channel,1)

# Persist account profile so the header account button can identify the signed-in channel.
profile_anchor='''val title=sn.optString("title","YouTube");val img=sn.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url").orEmpty();val subs=st?.optString("subscriberCount","").orEmpty();val html='''
profile_new='''val title=sn.optString("title","YouTube");val img=sn.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url").orEmpty();val subs=st?.optString("subscriberCount","").orEmpty();prefs.edit().putString("account_title",title).putString("account_avatar",img).putString("account_channel_id",item.optString("id","")).apply();val html='''
if profile_anchor not in s: raise SystemExit('v5.0 account profile anchor missing')
s=s.replace(profile_anchor,profile_new,1)

# Watch Later: local, reliable, and independent from YouTube's private Watch Later playlist.
watch_methods='''    private fun watchLaterIds():List<String> = prefs.getString("watch_later_ids","").orEmpty().split(",").filter{it.isNotBlank()}
    private fun watchLaterVideos():List<Video> = watchLaterIds().mapNotNull{id->videos.firstOrNull{it.id==id}?:dynamicVideos[id]}.take(40)
    private fun toggleWatchLater(id:String){
        if(id.isBlank())return
        val ids=watchLaterIds().toMutableList()
        if(id in ids)ids.remove(id) else ids.add(0,id)
        prefs.edit().putString("watch_later_ids",ids.distinct().take(60).joinToString(",")).apply()
        showPlayer(id)
    }
    private fun showWatchLater(){
        currentVideoId=null
        val list=watchLaterVideos()
        val inner=if(list.isEmpty())"<div class='simple'><h1>稍后观看</h1><p>在播放页点击“稍后观看”，视频会保存在这台 C16 上。</p></div>" else "<div class='sectionHead'><h2>稍后观看</h2><span>${list.size} 个视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>"
        load(shell("",inner))
    }
'''
marker='''    private fun showSettings(){'''
if 'private fun showWatchLater()' not in s:
    if marker not in s: raise SystemExit('v5.0 watch later marker missing')
    s=s.replace(marker,watch_methods+marker,1)

# Add Watch Later to player actions without touching IFrame / Media Integrity / playback configuration.
fav_line='''        val fav=prefs.getStringSet("favorites",emptySet()).orEmpty().contains(id)
'''
if 'val later=prefs.getString("watch_later_ids"' not in s:
    if fav_line not in s: raise SystemExit('v5.0 favorite line missing')
    s=s.replace(fav_line,fav_line+'        val later=prefs.getString("watch_later_ids","").orEmpty().split(",").contains(id)\n',1)

action_old='''<a class='action' href='c16://favorite?id=${Uri.encode(v.id)}'>${if(fav)"♥ 已收藏" else "♡ 收藏"}</a><a class='action' href='c16://category?name=${Uri.encode(v.category)}'>▤ 推荐</a>'''
action_new='''<a class='action' href='c16://favorite?id=${Uri.encode(v.id)}'>${if(fav)"♥ 已收藏" else "♡ 收藏"}</a><a class='action' href='c16://later?id=${Uri.encode(v.id)}'>${if(later)"✓ 已加入稍后观看" else "＋ 稍后观看"}</a><a class='action' href='c16://category?name=${Uri.encode(v.category)}'>▤ 推荐</a>'''
if action_old not in s: raise SystemExit('v5.0 player action anchor missing')
s=s.replace(action_old,action_new,1)

# Home gets a real Watch Later shelf when the user has added items.
home_likes='''        val likes=homeLikedFeed.toList().distinctBy{it.id}.take(12)
'''
if 'val later=watchLaterVideos()' not in s:
    if home_likes not in s: raise SystemExit('v5.0 home likes anchor missing')
    s=s.replace(home_likes,home_likes+'        val later=watchLaterVideos()\n',1)

home_sections='''        val likedSection=if(likes.isEmpty())"" else rail("点赞回看","你的 YouTube 点赞视频",likes)
'''
if '稍后观看","保存在这台 C16' not in s:
    if home_sections not in s: raise SystemExit('v5.0 home section anchor missing')
    s=s.replace(home_sections,home_sections+'        val laterSection=if(later.isEmpty())"" else rail("稍后观看","保存在这台 C16 上",later.take(12))\n',1)

home_return='$continueSection$subscriptionSection$likedSection${rail("为你推荐"'
if home_return not in s: raise SystemExit('v5.0 home return target missing')
s=s.replace(home_return,'$continueSection$subscriptionSection$likedSection$laterSection${rail("为你推荐"',1)

# Account center exposes Watch Later alongside history/favorites.
account_grid='''<a class='chip' href='c16://history'>车机历史</a><a class='chip' href='c16://favorites'>车机收藏</a><a class='chip' href='c16://settings'>设置</a>'''
account_grid_new='''<a class='chip' href='c16://history'>车机历史</a><a class='chip' href='c16://favorites'>车机收藏</a><a class='chip' href='c16://watchlater'>稍后观看</a><a class='chip' href='c16://settings'>设置</a>'''
if account_grid in s:
    s=s.replace(account_grid,account_grid_new,1)

# Drive mode exposes Watch Later as a large tile by replacing the less-useful subscription shortcut.
drive_tile='''<a class='driveTile' href='c16://subscriptions'><b>订阅</b><span>查看 YouTube 订阅频道</span></a>'''
drive_tile_new='''<a class='driveTile' href='c16://watchlater'><b>稍后观看</b><span>一键打开待看视频</span></a>'''
if drive_tile in s:
    s=s.replace(drive_tile,drive_tile_new,1)

# Clear only account identity metadata on logout; local history/favorites/watch-later remain.
logout_anchor='''homeSubscriptionFeed.clear();homeLikedFeed.clear();homeSyncedAt=0L;homeSyncError=""
'''
if logout_anchor in s:
    s=s.replace(logout_anchor,logout_anchor+'        prefs.edit().remove("account_title").remove("account_avatar").remove("account_channel_id").apply()\n',1)

# Visible version labels and diagnostics.
s=s.replace('C16 YouTube · V4.9','C16 YouTube · V5.0')
s=s.replace('"应用版本" to "4.9.40066"','"应用版本" to "5.0.40067"')

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V5.0 search/channel/watch-later/product-completion patch; playback core unchanged')
