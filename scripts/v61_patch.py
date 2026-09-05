from pathlib import Path
import re

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V6.1: data completeness. Do not touch the proven WebView/IFrame/Media Integrity player core.
# Goals: no artificial 50-video ceiling, auto-continue pagination on collection pages,
# category pagination, complete subscription traversal, and home subscription sync across all channels.

# 1) Category pages become paged instead of a single search.list page.
old_route='''"category"->showCategory(u.getQueryParameter("name").orEmpty());'''
new_route='''"category"->showCategory61(u.getQueryParameter("name").orEmpty());"categorymore61"->loadCategoryMore61(u.getQueryParameter("name").orEmpty(),u.getQueryParameter("q").orEmpty(),u.getQueryParameter("token").orEmpty());'''
if old_route not in s: raise SystemExit('v6.1 category route anchor missing')
s=s.replace(old_route,new_route,1)

# 2) Existing V5.4 collection buttons are auto-pagination sentinels as well as manual buttons.
old_more="else \"<div class='moreWrap54'><a class='more54' href='c16://$host?$params&token=${Uri.encode(token)}'>加载更多 50 个</a><span class='loaded54'>当前已显示 $loaded 个</span></div>\""
new_more="else \"<div class='moreWrap54'><a class='more54 autoMore61' href='c16://$host?$params&token=${Uri.encode(token)}'>继续加载更多</a><span class='loaded54'>当前已显示 $loaded 个</span></div>\""
if old_more not in s: raise SystemExit('v6.1 videoMoreButton54 anchor missing')
s=s.replace(old_more,new_more,1)

# V6.0 channel-home load-more also participates in auto paging.
s=s.replace("<a class='more54' href='c16://channelhomemore60?", "<a class='more54 autoMore61' href='c16://channelhomemore60?", 2)

# 3) Subscription traversal should stop only when YouTube says there is no nextPageToken.
# Also protect against a malformed repeated token without imposing a page-count ceiling.
sub_head='''                    var token=""
                    var guard=0
                    do{'''
sub_head_new='''                    var token=""
                    var guard=0
                    val seenTokens61=mutableSetOf<String>()
                    do{'''
if sub_head not in s: raise SystemExit('v6.1 subscription loop head missing')
s=s.replace(sub_head,sub_head_new,1)
sub_tail='''                        token=j.optString("nextPageToken","")
                        guard++
                    }while(token.isNotBlank() && guard<100)'''
sub_tail_new='''                        val next61=j.optString("nextPageToken","")
                        token=if(next61.isNotBlank() && seenTokens61.add(next61)) next61 else ""
                        guard++
                    }while(token.isNotBlank())'''
if sub_tail not in s: raise SystemExit('v6.1 subscription loop tail missing')
s=s.replace(sub_tail,sub_tail_new,1)

# 4) Hydrate cached home account data before painting, then sync all subscribed channels.
s=s.replace('''        load(shell("home","<div id='homeRoot'>${homeBody()}</div>"))
        maybeSyncHomeFeed()''','''        hydrateHomeCache61()
        load(shell("home","<div id='homeRoot'>${homeBody()}</div>"))
        maybeSyncHomeFeed61()''',1)
# Show one latest upload from every subscribed channel on the home subscription rail.
s=s.replace('''val subs=homeSubscriptionFeed.toList().distinctBy{it.id}.take(30)''','''val subs=homeSubscriptionFeed.toList().distinctBy{it.id}''',1)

# 5) Generic auto-load observer. It clicks the next-page link only when the user scrolls near it.
# MutationObserver re-binds when the load-more HTML is replaced after each API page.
auto_js=r'''<script>
(function(){
  var busy=false;
  function bind(){
    document.querySelectorAll('a.autoMore61:not([data-auto61])').forEach(function(a){
      a.setAttribute('data-auto61','1');
      var io=new IntersectionObserver(function(es){
        es.forEach(function(e){if(e.isIntersecting&&!busy){busy=true;io.disconnect();setTimeout(function(){a.click();setTimeout(function(){busy=false},900)},180)}})
      },{root:document.querySelector('.content'),rootMargin:'0px 0px 480px 0px',threshold:0.01});
      io.observe(a);
    });
  }
  bind(); new MutationObserver(bind).observe(document.body,{childList:true,subtree:true});
})();
</script>'''
if 'data-auto61' not in s:
    if '</body></html>' not in s: raise SystemExit('v6.1 body close missing')
    s=s.replace('</body></html>',auto_js+'</body></html>',1)

# 6) Category and home-cache helpers.
marker='''    private fun accountPill51():String{'''
methods=r'''    private fun categoryQuery61(name:String)=when(name){
        "科技AI"->"人工智能 AI 科技";"汽车"->"汽车 新能源 智能驾驶";"音乐"->"音乐";"旅行"->"旅行 4K 风景";"电影"->"电影 影视";"哲学"->"哲学 思想";else->name
    }
    private fun showCategory61(nameRaw:String){
        val name=nameRaw.ifBlank{"推荐"};currentVideoId=null
        if(name=="推荐"){showHome();return}
        val q=categoryQuery61(name)
        if(prefs.getString("access_token","").orEmpty().isBlank()){showCategory(name);return}
        val body="<div class='chips'>${chips(name)}</div><div class='collectionNote54'>${esc(name)} · 向下浏览会自动继续读取后续 YouTube 结果，不限制为首批 50 个。</div><div class='sectionHead'><h2>${esc(name)}</h2><span id='catCount61'>正在加载…</span></div><div id='catGrid61' class='grid'></div><div id='catMore61'></div>"
        load(shell("home",body));fetchCategoryPage61(name,q,"",false)
    }
    private fun loadCategoryMore61(name:String,q:String,token:String){if(name.isNotBlank()&&q.isNotBlank()&&token.isNotBlank())fetchCategoryPage61(name,q,token,true)}
    private fun fetchCategoryPage61(name:String,q:String,token:String,append:Boolean){
        Thread{
            try{
                val suffix=if(token.isBlank())"" else "&pageToken=${Uri.encode(token)}"
                val j=apiGet("search?part=snippet&type=video&videoEmbeddable=true&maxResults=50&relevanceLanguage=zh-Hans&q=${Uri.encode(q)}$suffix")
                val list=apiSearchVideos(j);list.forEach{v->if(v.category!=name)dynamicVideos[v.id]=Video(v.id,v.title,v.channel,"YouTube · $name",name)}
                val next=j.optString("nextPageToken","");val html=list.joinToString(""){card(dynamicVideos[it.id]?:it)}
                main.post{
                    if(append)appendHtml54("catGrid61",html) else setMore54("catGrid61",html)
                    web.evaluateJavascript("var n=document.getElementById('catGrid61')?document.getElementById('catGrid61').children.length:0;var c=document.getElementById('catCount61');if(c)c.textContent=n+' 个已加载';var m=document.getElementById('catMore61');if(m)m.innerHTML="+JSONObject.quote(videoMoreButton54("categorymore61","name=${Uri.encode(name)}&q=${Uri.encode(q)}",next,0))+".replace('当前已显示 0 个','继续向下自动加载');",null)
                }
            }catch(e:Exception){main.post{setMore54("catMore61","<div class='searchNotice'>分类内容加载失败：${esc((e.message?:"请求失败").take(150))}</div>")}}
        }.start()
    }
    private fun videosToJson61(list:List<Video>):String{
        val a=JSONArray();list.distinctBy{it.id}.forEach{v->a.put(JSONObject().put("id",v.id).put("title",v.title).put("channel",v.channel).put("meta",v.meta).put("category",v.category))};return a.toString()
    }
    private fun videosFromJson61(raw:String):List<Video>{
        val out=mutableListOf<Video>();try{val a=JSONArray(raw);for(i in 0 until a.length()){val j=a.optJSONObject(i)?:continue;val id=j.optString("id","");if(id.isBlank())continue;val v=Video(id,j.optString("title","YouTube 视频"),j.optString("channel","YouTube"),j.optString("meta","账号缓存"),j.optString("category","推荐"));out+=v;dynamicVideos[id]=v}}catch(_:Exception){};return out
    }
    private fun hydrateHomeCache61(){
        if(homeSubscriptionFeed.isEmpty())homeSubscriptionFeed.addAll(videosFromJson61(prefs.getString("home_sub_cache_61","[]").orEmpty()))
        if(homeLikedFeed.isEmpty())homeLikedFeed.addAll(videosFromJson61(prefs.getString("home_like_cache_61","[]").orEmpty()))
    }
    private fun maybeSyncHomeFeed61(){
        if(prefs.getString("access_token","").orEmpty().isBlank())return
        if(homeSyncing)return
        if(homeSubscriptionFeed.isNotEmpty()&&System.currentTimeMillis()-homeSyncedAt<30*60*1000L)return
        homeSyncing=true;homeSyncError="";updateHomeDom()
        Thread{
            try{
                // Likes: follow pagination up to the API's useful recent-history range, rather than one 50-item page.
                val likes=mutableListOf<Video>();var likeToken="";val seenLike=mutableSetOf<String>()
                do{
                    val suffix=if(likeToken.isBlank())"" else "&pageToken=${Uri.encode(likeToken)}"
                    val j=apiGet("videos?part=snippet&myRating=like&maxResults=50$suffix");likes+=apiVideoList(j)
                    val n=j.optString("nextPageToken","");likeToken=if(n.isNotBlank()&&seenLike.add(n)&&likes.size<1000)n else ""
                }while(likeToken.isNotBlank())

                // Subscriptions: traverse every page returned by YouTube.
                val channelIds=mutableListOf<String>();var subToken="";val seenSub=mutableSetOf<String>()
                do{
                    val suffix=if(subToken.isBlank())"" else "&pageToken=${Uri.encode(subToken)}"
                    val j=apiGet("subscriptions?part=snippet&mine=true&maxResults=50&order=alphabetical$suffix");val a=j.optJSONArray("items")
                    if(a!=null)for(i in 0 until a.length()){val id=a.optJSONObject(i)?.optJSONObject("snippet")?.optJSONObject("resourceId")?.optString("channelId").orEmpty();if(id.isNotBlank())channelIds+=id}
                    val n=j.optString("nextPageToken","");subToken=if(n.isNotBlank()&&seenSub.add(n))n else ""
                }while(subToken.isNotBlank())

                // Resolve upload playlists in batches of 50 channel IDs.
                val uploads=mutableListOf<Pair<String,String>>()
                channelIds.distinct().chunked(50).forEach{chunk->
                    val cj=apiGet("channels?part=contentDetails&id=${chunk.joinToString(",")}");val ca=cj.optJSONArray("items")
                    if(ca!=null)for(i in 0 until ca.length()){val ci=ca.optJSONObject(i)?:continue;val cid=ci.optString("id","");val up=ci.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")?.optString("uploads").orEmpty();if(cid.isNotBlank()&&up.isNotBlank())uploads+=cid to up}
                }

                // One newest upload per subscribed channel, with bounded concurrency so 80+ subscriptions stay practical.
                val recent=java.util.Collections.synchronizedList(mutableListOf<Video>())
                val pool=java.util.concurrent.Executors.newFixedThreadPool(8)
                uploads.forEach{(cid,up)->pool.submit{try{val got=apiVideoList(apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(up)}&maxResults=1"),true);got.forEach{v->dynamicVideoChannelIds[v.id]=cid;recent.add(v)}}catch(_:Exception){}}}
                pool.shutdown();pool.awaitTermination(75,java.util.concurrent.TimeUnit.SECONDS)

                val subFeed=recent.distinctBy{it.id}
                val likeFeed=likes.distinctBy{it.id}
                homeSubscriptionFeed.clear();homeSubscriptionFeed.addAll(subFeed)
                homeLikedFeed.clear();homeLikedFeed.addAll(likeFeed)
                prefs.edit().putString("home_sub_cache_61",videosToJson61(subFeed)).putString("home_like_cache_61",videosToJson61(likeFeed)).apply()
                homeSyncedAt=System.currentTimeMillis();homeSyncError=""
            }catch(e:Exception){homeSyncError=(e.message?:"YouTube 账号同步失败").take(140)}
            finally{homeSyncing=false;main.post{updateHomeDom()}}
        }.start()
    }
'''
if marker not in s: raise SystemExit('v6.1 helper insertion anchor missing')
s=s.replace(marker,methods+marker,1)

css=r'''
/* V6.1 data-complete browsing */
.autoMore61{box-shadow:0 8px 22px rgba(0,0,0,.12)}
.collectionNote54{font-size:15px!important}.moreWrap54{min-height:66px}.moreWrap54 .loaded54{font-size:15px!important}
'''
if 'V6.1 data-complete browsing' not in s:s=s.replace('</style>',css+'</style>',1)

s=s.replace('C16 YouTube · V6.0','C16 YouTube · V6.1')
s=s.replace('"应用版本" to "6.0.40077"','"应用版本" to "6.1.40078"')

p.write_text(s,encoding='utf-8')
print('Applied V6.1 complete pagination, category continuation, all-subscription home sync and local home cache')
