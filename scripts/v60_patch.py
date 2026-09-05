from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V6.0: fix the concrete screen issues reported from V5.9.
# Keep the proven WebView/IFrame/Media Integrity playback stack untouched.

# 1) Home: remove the large account-refresh banner completely and move refresh to the top toolbar.
# The V5.1 banner survives V5.7 because it is a manageBar51 block, so hide only the one inside homeRoot.
css=r'''
/* V6.0 C16 browse/scroll fixes */
#homeRoot>.manageBar51{display:none!important}
.content{height:calc(100vh - 90px)!important;min-height:0!important;overflow-y:scroll!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important;overscroll-behavior-y:contain!important;touch-action:pan-y!important}
.rail,.channelRail56{touch-action:pan-x pan-y!important;overscroll-behavior-x:contain!important}
.subGrid53{grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:16px!important}.subCard53{min-height:108px!important;padding:14px!important}.subPager53{margin-top:20px!important}
.channelGrid60{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:28px 18px;padding-bottom:10px}.channelGrid60 .card{min-width:0}.channelGrid60 .ctitle{height:auto;min-height:52px}.channelAllHint60{display:flex;align-items:center;justify-content:space-between;gap:16px;margin:14px 0 18px;padding:14px 17px;border-radius:18px;background:$panel;border:1px solid $border;color:$sub}.channelAllHint60 b{font-size:17px;color:$text}.channelHomeMore60{display:flex;align-items:center;justify-content:center;gap:14px;margin:18px 0 8px}.channelHomeMore60 .more54{min-width:220px}.refresh60{font-size:27px!important;font-weight:500!important}
@media(max-width:1700px){.subGrid53{grid-template-columns:repeat(4,minmax(0,1fr))!important}.channelGrid60{grid-template-columns:repeat(3,minmax(0,1fr))}}
'''
if 'V6.0 C16 browse/scroll fixes' not in s:
    if '</style>' not in s: raise SystemExit('v6.0 style anchor missing')
    s=s.replace('</style>',css+'</style>',1)

# Top toolbar refresh, immediately next to the theme button.
old_top='''<a class='round' href='c16://favorites'>♡</a><a class='round' href='c16://theme'>${if(dark)"☀" else "☾"}</a>'''
new_top='''<a class='round' href='c16://favorites'>♡</a><a class='round refresh60' href='c16://homesync' title='刷新账号内容'>↻</a><a class='round' href='c16://theme'>${if(dark)"☀" else "☾"}</a>'''
if old_top not in s: raise SystemExit('v6.0 top toolbar anchor missing')
s=s.replace(old_top,new_top,1)

# 2) Subscription gallery: fill a 5-column page (20 = 5 x 4) instead of 18 cards.
s=s.replace('''                    val pageSize=18''','''                    val pageSize=20''',1)

# 3) Channel homepage: retain the first 50 but expose the nextPageToken directly on the same
# horizontal shelf, so the user can continue loading 50-by-50 without a 50-video ceiling.
old_latest='''                    val latest=if(uploads.isBlank())emptyList() else apiVideoList(apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=50"),true)
                    latest.forEach{dynamicVideoChannelIds[it.id]=id}'''
new_latest='''                    val latestPage60=if(uploads.isBlank())JSONObject() else apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=50")
                    val latest=if(uploads.isBlank())emptyList() else apiVideoList(latestPage60,true)
                    val latestNext60=latestPage60.optString("nextPageToken","")
                    latest.forEach{dynamicVideoChannelIds[it.id]=id}'''
if old_latest not in s: raise SystemExit('v6.0 channel latest anchor missing')
s=s.replace(old_latest,new_latest,1)

old_home='''                            val homeVideos=if(latest.isEmpty())"" else rail("最新视频","左右滑动查看更多 · 已读取 ${latest.size} 个",latest)+"<div class='channelMore56'><a class='more54' href='c16://channel?id=${Uri.encode(id)}&title=${Uri.encode(channelTitle)}&tab=videos'>查看频道全部视频</a><span>进入后每次继续加载 50 个，直到该频道全部视频加载完成</span></div>"'''
new_home='''                            val homeVideos=if(latest.isEmpty())"" else channelHomeRail60(id,channelTitle,uploads,latestNext60,latest)'''
if old_home not in s: raise SystemExit('v6.0 channel home anchor missing')
s=s.replace(old_home,new_home,1)

# Channel videos tab: use an explicitly vertical-scroll-friendly grid and clearer unlimited wording.
s=s.replace("<div id='chGrid54' class='channelRail56'></div>","<div id='chGrid54' class='channelGrid60'></div>",1)
s=s.replace("频道全部视频 · 左右滑动浏览 · 可继续读取更多","频道全部视频 · 上下滑动浏览 · 每次继续读取 50 个",1)

# Route for loading more directly into the channel-home horizontal rail.
route_anchor='''"channelmore"->loadChannelMore54(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("uploads").orEmpty(),u.getQueryParameter("token").orEmpty());'''
route_new='''"channelmore"->loadChannelMore54(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("uploads").orEmpty(),u.getQueryParameter("token").orEmpty());"channelhomemore60"->loadChannelHomeMore60(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("uploads").orEmpty(),u.getQueryParameter("token").orEmpty());'''
if route_anchor not in s: raise SystemExit('v6.0 channelmore route anchor missing')
s=s.replace(route_anchor,route_new,1)

marker='''    private fun accountPill51():String{'''
methods=r'''    private fun channelHomeRail60(channelId:String,title:String,uploads:String,nextToken:String,list:List<Video>):String{
        val cards=list.joinToString(""){card(it)}
        val more=if(nextToken.isBlank())"<span class='more54 disabled'>已读取频道全部视频</span>" else "<a class='more54' href='c16://channelhomemore60?id=${Uri.encode(channelId)}&title=${Uri.encode(title)}&uploads=${Uri.encode(uploads)}&token=${Uri.encode(nextToken)}'>继续读取更多视频</a>"
        return "<div class='section'><div class='sectionHead'><h2>最新视频</h2><span id='channelHomeCount60'>已读取 ${list.size} 个 · 左右滑动查看更多</span></div><div class='railWrap'><button class='arrow arrowLeft58' onclick=\"var r=this.nextElementSibling;r.scrollBy({left:-r.clientWidth*.88,behavior:'smooth'})\">‹</button><div id='channelHomeRail60' class='rail'>$cards</div><button class='arrow' onclick=\"var r=this.previousElementSibling;r.scrollBy({left:r.clientWidth*.88,behavior:'smooth'})\">›</button></div><div id='channelHomeMore60' class='channelHomeMore60'>$more<a class='chip' href='c16://channel?id=${Uri.encode(channelId)}&title=${Uri.encode(title)}&tab=videos'>进入全部视频页</a></div></div>"
    }
    private fun loadChannelHomeMore60(channelId:String,title:String,uploads:String,token:String){
        if(channelId.isBlank()||uploads.isBlank()||token.isBlank())return
        Thread{
            try{
                val j=apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=50&pageToken=${Uri.encode(token)}")
                val list=apiVideoList(j,true);list.forEach{dynamicVideoChannelIds[it.id]=channelId}
                val next=j.optString("nextPageToken","");val html=list.joinToString(""){card(it)}
                main.post{
                    appendHtml54("channelHomeRail60",html)
                    val more=if(next.isBlank())"<span class='more54 disabled'>已读取频道全部视频</span>" else "<a class='more54' href='c16://channelhomemore60?id=${Uri.encode(channelId)}&title=${Uri.encode(title)}&uploads=${Uri.encode(uploads)}&token=${Uri.encode(next)}'>继续读取更多视频</a>"
                    setMore54("channelHomeMore60",more+"<a class='chip' href='c16://channel?id=${Uri.encode(channelId)}&title=${Uri.encode(title)}&tab=videos'>进入全部视频页</a>")
                    web.evaluateJavascript("var n=document.getElementById('channelHomeRail60')?document.getElementById('channelHomeRail60').children.length:0;var c=document.getElementById('channelHomeCount60');if(c)c.textContent='已读取 '+n+' 个 · 左右滑动查看更多';",null)
                }
            }catch(e:Exception){main.post{setMore54("channelHomeMore60","<span class='searchNotice'>加载更多失败：${esc((e.message?:"请求失败").take(150))}</span>")}}
        }.start()
    }
'''
if marker not in s: raise SystemExit('v6.0 helper marker missing')
s=s.replace(marker,methods+marker,1)

s=s.replace('C16 YouTube · V5.9','C16 YouTube · V6.0')
s=s.replace('"应用版本" to "5.9.40076"','"应用版本" to "6.0.40077"')

p.write_text(s,encoding='utf-8')
print('Applied V6.0: home refresh relocation, full 20-channel pages, vertical video scrolling and >50 channel loading')
