from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V6.3: finish the V6.2 UX work and classify portrait/Shorts content separately.
# Playback/WebView/IFrame/Media Integrity core remains untouched.

# 1) Add a YouTube-style Shorts entry to the left rail, directly after Home.
nav_anchor='''${nav("home","home","首页","home")}${nav("drive","drive","驾驶模式","drive59")}'''
nav_new='''${nav("home","home","首页","home")}${nav("shorts63","shorts63","Shorts","shorts63")}${nav("drive","drive","驾驶模式","drive59")}'''
if nav_anchor not in s: raise SystemExit('v6.3 sidebar home/drive anchor missing')
s=s.replace(nav_anchor,nav_new,1)

# Shorts icon.
svg_anchor='''"home"->"<svg viewBox='0 0 24 24'><path d='M3 11.2 12 4l9 7.2v8.3a1.5 1.5 0 0 1-1.5 1.5h-5v-6h-5v6h-5A1.5 1.5 0 0 1 3 19.5z'/></svg>";"drive"'''
svg_new='''"home"->"<svg viewBox='0 0 24 24'><path d='M3 11.2 12 4l9 7.2v8.3a1.5 1.5 0 0 1-1.5 1.5h-5v-6h-5v6h-5A1.5 1.5 0 0 1 3 19.5z'/></svg>";"shorts63"->"<svg viewBox='0 0 24 24'><path d='m14.7 3-6.2 3.6a2.2 2.2 0 0 0 .1 3.9l2 1-2.5 1.5a2.2 2.2 0 0 0 .1 3.9L12 19l5.9-3.4a2.2 2.2 0 0 0-.1-3.9l-2-1 2.6-1.5a2.2 2.2 0 0 0-.2-3.9L14.7 3z'/><path d='m11 9 4 3-4 3z'/></svg>";"drive"'''
if svg_anchor not in s: raise SystemExit('v6.3 svg anchor missing')
s=s.replace(svg_anchor,svg_new,1)

# 2) Global Shorts routes.
home_route='''"home"->showHome();"refresh62"'''
home_route_new='''"home"->showHome();"shorts63"->showShorts63();"shortsmore63"->loadShortsMore63(u.getQueryParameter("token").orEmpty());"refresh62"'''
if home_route not in s: raise SystemExit('v6.3 route anchor missing')
s=s.replace(home_route,home_route_new,1)

# 3) Upgrade channel split: portrait thumbnail metadata and explicit Shorts markers count as Shorts.
old_details='''            val ids=list.map{it.id}.filter{it.isNotBlank()};val secs=mutableMapOf<String,Long>()
            if(ids.isNotEmpty()){
                val dj=apiGet("videos?part=contentDetails&id=${ids.joinToString(",")}");val da=dj.optJSONArray("items")
                if(da!=null)for(i in 0 until da.length()){val x=da.optJSONObject(i)?:continue;val raw=x.optJSONObject("contentDetails")?.optString("duration").orEmpty();val sec=try{java.time.Duration.parse(raw).seconds}catch(_:Exception){Long.MAX_VALUE};secs[x.optString("id","")]=sec}
            }
            val filtered=list.filter{v->val sec=secs[v.id]?:Long.MAX_VALUE;if(kind=="shorts")sec<=180 else sec>180}.filterNot{legacyVideoIds62.contains(it.id)}'''
new_details='''            val ids=list.map{it.id}.filter{it.isNotBlank()};val shortFlags63=mutableMapOf<String,Boolean>()
            if(ids.isNotEmpty()){
                val dj=apiGet("videos?part=snippet,contentDetails&id=${ids.joinToString(",")}");val da=dj.optJSONArray("items")
                if(da!=null)for(i in 0 until da.length()){
                    val x=da.optJSONObject(i)?:continue;val vid=x.optString("id","");val cd=x.optJSONObject("contentDetails")?:JSONObject();val sn=x.optJSONObject("snippet")?:JSONObject()
                    val raw=cd.optString("duration","");val sec=try{java.time.Duration.parse(raw).seconds}catch(_:Exception){Long.MAX_VALUE}
                    shortFlags63[vid]=isShortVideo63(sn,sec)
                }
            }
            val filtered=list.filter{v->val sh=shortFlags63[v.id]?:looksShortByTitle63(v.title);if(kind=="shorts")sh else !sh}.filterNot{legacyVideoIds62.contains(it.id)}'''
if old_details not in s: raise SystemExit('v6.3 channel classifier anchor missing')
s=s.replace(old_details,new_details,1)

# Render Shorts as portrait cards instead of landscape video cards.
old_html='''            val next=pj.optString("nextPageToken","");val html=filtered.joinToString(""){card(it)}'''
new_html='''            val next=pj.optString("nextPageToken","");val html=filtered.joinToString(""){if(kind=="shorts")shortCard63(it) else card(it)}'''
if old_html not in s: raise SystemExit('v6.3 channel card anchor missing')
s=s.replace(old_html,new_html,1)

# More accurate UI copy.
s=s.replace('''按时长不超过 3 分钟归入 Shorts 区域''','''竖屏、Shorts 标记及短时长内容归入 Shorts''',1)
s=s.replace('''仅显示超过 3 分钟的常规视频''','''过滤 Shorts 后显示常规长视频''',1)

# 4) Helpers and global Shorts browser.
marker='''    private fun accountPill51():String{'''
methods=r'''    private fun looksShortByTitle63(title:String):Boolean{
        val t=title.lowercase()
        return t.contains("#shorts")||t.contains("#short")||t.contains("#shortvideo")||t.contains("#短视频")||t.contains(" shorts ")
    }
    private fun isShortVideo63(sn:JSONObject,sec:Long):Boolean{
        val title=sn.optString("title","")
        var explicit=looksShortByTitle63(title)
        val tags=sn.optJSONArray("tags")
        if(tags!=null)for(i in 0 until tags.length()){
            val t=tags.optString(i,"").lowercase()
            if(t=="shorts"||t=="short"||t.contains("shortvideo")||t.contains("短视频")){explicit=true;break}
        }
        var portrait=false
        val thumbs=sn.optJSONObject("thumbnails")
        if(thumbs!=null){
            for(k in listOf("maxres","standard","high","medium","default")){
                val th=thumbs.optJSONObject(k)?:continue
                val w=th.optInt("width",0);val h=th.optInt("height",0)
                if(w>0&&h>0){portrait=h>w;break}
            }
        }
        // YouTube Data API does not expose the encoded frame orientation directly for every video.
        // Portrait thumbnail metadata and Shorts markers are strongest; <=3 minutes is a fallback
        // so actual Shorts without an explicit hashtag still land in the Shorts tab.
        return portrait||explicit||sec<=180
    }
    private fun shortCard63(v:Video):String{
        return "<a class='card shortCard63' href='c16://watch?id=${Uri.encode(v.id)}'><div class='thumb shortThumb63'><img loading='lazy' src='${thumb(v)}'><span class='shortBadge63'>Shorts</span></div><div class='ctitle'>${esc(v.title)}</div><div class='cmeta'>${esc(v.channel)}</div></a>"
    }
    private fun showShorts63(){
        currentVideoId=null
        val signed=prefs.getString("access_token","").orEmpty().isNotBlank()
        if(!signed){
            val local=dynamicVideos.values.filter{looksShortByTitle63(it.title)}.filterNot{legacyVideoIds62.contains(it.id)}
            val body="<div class='sectionHead shortsHead63'><h2>Shorts</h2><span>登录 YouTube 后可继续获取更多</span></div>"+
                if(local.isEmpty())"<div class='simple'><h1>Shorts</h1><p>登录 YouTube 后，这里会显示竖屏与短视频内容。</p><a class='chip' href='c16://login'>登录 YouTube</a></div>" else "<div class='shortsGrid63'>${local.joinToString(""){shortCard63(it)}}</div>"
            load(shell("shorts63",body));return
        }
        val body="<div class='sectionHead shortsHead63'><h2>Shorts</h2><span id='shortsCount63'>正在加载…</span></div><div id='shortsGrid63' class='shortsGrid63'></div><div id='shortsMore63'></div>"
        load(shell("shorts63",body));fetchShortsPage63("",false)
    }
    private fun loadShortsMore63(token:String){if(token.isNotBlank())fetchShortsPage63(token,true)}
    private fun fetchShortsPage63(token:String,append:Boolean){
        Thread{try{
            val suffix=if(token.isBlank())"" else "&pageToken=${Uri.encode(token)}"
            val sj=apiGet("search?part=snippet&type=video&videoEmbeddable=true&videoDuration=short&maxResults=50&q=${Uri.encode("#shorts")}$suffix")
            val candidates=apiSearchVideos(sj).filterNot{legacyVideoIds62.contains(it.id)}
            val ids=candidates.map{it.id}.filter{it.isNotBlank()}
            val flags=mutableMapOf<String,Boolean>()
            if(ids.isNotEmpty()){
                val dj=apiGet("videos?part=snippet,contentDetails&id=${ids.joinToString(",")}");val da=dj.optJSONArray("items")
                if(da!=null)for(i in 0 until da.length()){
                    val x=da.optJSONObject(i)?:continue;val raw=x.optJSONObject("contentDetails")?.optString("duration").orEmpty();val sec=try{java.time.Duration.parse(raw).seconds}catch(_:Exception){Long.MAX_VALUE};flags[x.optString("id","")]=isShortVideo63(x.optJSONObject("snippet")?:JSONObject(),sec)
                }
            }
            val list=candidates.filter{flags[it.id]?:looksShortByTitle63(it.title)}
            val html=list.joinToString(""){shortCard63(it)};val next=sj.optString("nextPageToken","")
            main.post{
                if(append)appendHtml54("shortsGrid63",html) else setMore54("shortsGrid63",html)
                val more=videoMoreButton54("shortsmore63","from=shorts",next,0).replace("class='more54'","class='more54 autoMore61'").replace("当前已显示 0 个","继续向下自动加载")
                setMore54("shortsMore63",more)
                web.evaluateJavascript("var n=document.getElementById('shortsGrid63')?document.getElementById('shortsGrid63').children.length:0;var c=document.getElementById('shortsCount63');if(c)c.textContent=n+' 个已加载';",null)
            }
        }catch(e:Exception){main.post{setMore54("shortsMore63","<div class='searchNotice'>Shorts 加载失败：${esc((e.message?:"请求失败").take(150))}</div>")}}}.start()
    }
'''
if marker not in s: raise SystemExit('v6.3 helper marker missing')
s=s.replace(marker,methods+marker,1)

css=r'''
/* V6.3 portrait Shorts / YouTube-style browsing */
.shortsGrid63,.shortsGrid62{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:26px 18px!important;align-items:start}.shortCard63{min-width:0}.shortThumb63,.shortsGrid62 .thumb{aspect-ratio:9/16!important;border-radius:18px!important;position:relative!important;background:#111!important}.shortThumb63 img,.shortsGrid62 .thumb img{width:100%!important;height:100%!important;object-fit:cover!important}.shortBadge63{position:absolute;left:10px;bottom:10px;padding:5px 9px;border-radius:10px;background:rgba(0,0,0,.72);color:#fff;font-size:12px;font-weight:800}.shortCard63 .ctitle,.shortsGrid62 .ctitle{height:auto!important;min-height:52px!important;font-size:18px!important;line-height:1.35!important}.shortCard63 .cmeta{font-size:15px!important}.shortsHead63{margin-bottom:18px!important}.shortsHead63 h2{display:flex;align-items:center;gap:10px}.shortsHead63 h2:before{content:'▶';display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:11px;background:#ff0033;color:#fff;font-size:15px}.sidebar .nav.on[href='c16://shorts63']{background:$activeBg!important}
@media(max-width:1800px){.shortsGrid63,.shortsGrid62{grid-template-columns:repeat(4,minmax(0,1fr))!important}}@media(max-width:1450px){.shortsGrid63,.shortsGrid62{grid-template-columns:repeat(3,minmax(0,1fr))!important}}
'''
if 'V6.3 portrait Shorts / YouTube-style browsing' not in s:s=s.replace('</style>',css+'</style>',1)

s=s.replace('C16 YouTube · V6.2','C16 YouTube · V6.3')
s=s.replace('"应用版本" to "6.2.40079"','"应用版本" to "6.3.40080"')

p.write_text(s,encoding='utf-8')
print('Applied V6.3 portrait Shorts classification, global Shorts entry and portrait cards; playback core untouched')
