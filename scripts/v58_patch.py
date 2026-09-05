from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V5.8: car-navigation/library polish. Keep the proven player/WebView core untouched.

# Add direct library entries to the left sidebar. These routes already exist from V5.0/V5.4.
old_nav='''${nav("sub","sub","订阅","subscriptions")}${nav("history","history","历史记录","history")}${nav("favorites","heart","我的收藏","favorites")}${nav("local","local","本地视频","local")}'''
new_nav='''${nav("sub","sub","订阅","subscriptions")}${nav("history","history","历史记录","history")}${nav("favorites","heart","我的收藏","favorites")}${nav("watchlater","history","稍后观看","watchlater")}${nav("likes","heart","点赞视频","likes")}${nav("playlists","sub","播放列表","playlists")}${nav("local","local","本地视频","local")}'''
if old_nav not in s: raise SystemExit('v5.8 sidebar nav anchor missing')
s=s.replace(old_nav,new_nav,1)

# Give every horizontal shelf two-way controls instead of only a right arrow.
old_rail='''    private fun rail(title:String,note:String,list:List<Video>)="<div class='section'><div class='sectionHead'><h2>$title</h2><span>$note</span></div><div class='railWrap'><div class='rail'>${list.joinToString(""){card(it)}}</div><button class='arrow' onclick=\\"this.previousElementSibling.scrollBy({left:900,behavior:'smooth'})\\">›</button></div></div>"'''
new_rail='''    private fun rail(title:String,note:String,list:List<Video>)="<div class='section'><div class='sectionHead'><h2>$title</h2><span>$note</span></div><div class='railWrap'><button class='arrow arrowLeft58' onclick=\\"var r=this.nextElementSibling;r.scrollBy({left:-r.clientWidth*.88,behavior:'smooth'})\\">‹</button><div class='rail'>${list.joinToString(""){card(it)}}</div><button class='arrow' onclick=\\"var r=this.previousElementSibling;r.scrollBy({left:r.clientWidth*.88,behavior:'smooth'})\\">›</button></div></div>"'''
if old_rail not in s: raise SystemExit('v5.8 rail helper anchor missing')
s=s.replace(old_rail,new_rail,1)

# Keep more real history visible on the home shelf.
s=s.replace('rail("继续观看","来自这台 C16 的真实观看记录",history.take(12))','rail("继续观看","来自这台 C16 的真实观看记录",history.take(30))',1)

# Library pages should highlight their sidebar entry.
s=s.replace('load(shell("","<div class=\'collectionNote54\'>点赞视频', 'load(shell("likes","<div class=\'collectionNote54\'>点赞视频',1)
s=s.replace('load(shell("","<div class=\'collectionNote54\'>我的播放列表', 'load(shell("playlists","<div class=\'collectionNote54\'>我的播放列表',1)
s=s.replace('load(shell("","<div class=\'simple\'><h1>稍后观看</h1>', 'load(shell("watchlater","<div class=\'simple\'><h1>稍后观看</h1>',1)
s=s.replace('load(shell("",head+"<div class=\'grid\'>$cards</div><div style=\'height:36px\'></div>"))', 'load(shell("watchlater",head+"<div class=\'grid\'>$cards</div><div style=\'height:36px\'></div>"))',1)

# Favorites/watch-later need to survive an app restart for API-loaded videos. V5.6 already persists
# metadata for watched dynamic videos; reuse that metadata as the local library source of truth.
s=s.replace('''"favorites"->showFavorites();''','''"favorites"->showFavorites58();''',1)
s=s.replace('''    private fun watchLaterVideos():List<Video> = watchLaterIds().mapNotNull{id->videos.firstOrNull{it.id==id}?:dynamicVideos[id]}.take(40)''','''    private fun watchLaterVideos():List<Video> = watchLaterIds().mapNotNull{id->resolveStoredVideo58(id)}.take(100)''',1)

marker='''    private fun accountPill51():String{'''
methods=r'''    private fun resolveStoredVideo58(id:String):Video?{
        dynamicVideos[id]?.let{return it}
        videos.firstOrNull{it.id==id}?.let{return it}
        val j=historyMeta56().optJSONObject(id)?:return null
        return Video(id,j.optString("title","YouTube 视频"),j.optString("channel","YouTube"),j.optString("meta","本地记录"),j.optString("category","推荐"))
    }
    private fun showFavorites58(){
        currentVideoId=null
        val ids=prefs.getStringSet("favorites",emptySet()).orEmpty().toList()
        val list=ids.mapNotNull{resolveStoredVideo58(it)}
        val inner=if(list.isEmpty())"<div class='simple'><h1>我的收藏</h1><p>播放视频时点击“收藏”，视频会保存在这里。</p></div>" else "<div class='sectionHead'><h2>我的收藏</h2><span>${list.size} 个视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div><div style='height:36px'></div>"
        load(shell("favorites",inner))
    }
'''
if marker not in s: raise SystemExit('v5.8 helper insertion anchor missing')
s=s.replace(marker,methods+marker,1)

css=r'''
/* V5.8 car navigation + shelf controls */
.arrowLeft58{left:8px!important;right:auto!important}.railWrap:before,.railWrap:after{content:'';position:absolute;top:0;bottom:8px;width:42px;z-index:3;pointer-events:none}.railWrap:before{left:0;background:linear-gradient(90deg,$bg,transparent)}.railWrap:after{right:0;background:linear-gradient(270deg,$bg,transparent)}.railWrap .arrow{z-index:8!important}
.sidebar .nav{flex-shrink:0}.sidebar{overflow-y:auto!important;overflow-x:visible!important}.sidebar::-webkit-scrollbar{display:none}
#homeRoot .rail{scroll-padding-left:12px!important;scroll-padding-right:12px!important}
@media(max-height:1050px){.sidebar .nav{height:58px!important;margin:2px 0!important}.sidebar .brand{height:58px!important;margin-bottom:10px!important}}
'''
if 'V5.8 car navigation + shelf controls' not in s:s=s.replace('</style>',css+'</style>',1)

s=s.replace('C16 YouTube · V5.7','C16 YouTube · V5.8')
s=s.replace('"应用版本" to "5.7.40074"','"应用版本" to "5.8.40075"')

p.write_text(s,encoding='utf-8')
print('Applied V5.8 sidebar library shortcuts, two-way shelves and persistent dynamic library metadata')
