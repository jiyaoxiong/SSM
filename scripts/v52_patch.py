from pathlib import Path
import re

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

ui_css=r'''
/* V5.2 - restore the pre-data-rework C16 large-screen visual system */
html,body{font-family:Roboto,'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif!important;font-size:16px!important;font-weight:400!important}
.main{grid-template-rows:82px 1fr!important}.top{padding:12px 24px!important;gap:10px!important}
.search{height:50px!important;max-width:760px!important}.search input{font-size:17px!important;font-weight:400!important}
.pill{height:46px!important;font-size:16px!important;font-weight:650!important}.round{width:46px!important;height:46px!important}
.content{padding:22px 28px 72px!important}.chip{font-size:16px!important;font-weight:650!important;padding:9px 16px!important}
.sectionHead h2{font-size:28px!important;font-weight:700!important}.sectionHead span{font-size:15px!important}
.ctitle{font-size:18px!important;font-weight:650!important;line-height:1.35!important;height:49px!important}.cmeta{font-size:14px!important;line-height:1.45!important}
.grid{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:28px 18px!important}
.hero{height:312px!important}.heroCopy{width:46%!important;top:28px!important}.heroCopy h1{font-size:40px!important;font-weight:700!important;line-height:1.08!important}.heroCopy p{font-size:17px!important}
.btn,.action,.subscribe{font-weight:650!important}.pTitle{font-size:34px!important;font-weight:700!important;line-height:1.22!important}.pMeta{font-size:17px!important}
.channelText b{font-size:22px!important;font-weight:700!important}.channelText span{font-size:15px!important}
.recommend{padding:16px!important}.rec{grid-template-columns:176px minmax(0,1fr)!important;gap:13px!important}.rec img{width:176px!important}
.rec b,.recTitle{font-size:16px!important;font-weight:650!important;line-height:1.35!important}.rec span,.recMeta{font-size:13px!important}
.comments{padding:20px 22px!important}.comments h2{font-size:25px!important;font-weight:700!important}.comment b{font-size:15px!important;font-weight:650!important}.comment p{font-size:15px!important;line-height:1.55!important}
.simple h1{font-size:32px!important;font-weight:700!important}.simple p{font-size:17px!important}
.channelHero50 h1{font-size:32px!important;font-weight:700!important}.channelHero50 p{font-size:15px!important}
.manageBar51 b{font-size:17px!important;font-weight:700!important}.manageBar51 span{font-size:14px!important}
.accountPill51 span{font-size:15px!important;font-weight:650!important}.channelTab51,.subButton51{font-size:15px!important;font-weight:650!important}
.commentHead52{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:8px}.commentTools52{display:flex;gap:8px}
.commentTools52 a{padding:8px 13px;border-radius:18px;background:$p2;border:1px solid $border;font-size:14px;font-weight:650}.commentTools52 a.on{background:$text;color:$bg}
.commentStats52{font-size:13px;color:$sub;margin-top:4px}.categoryState52{padding:18px 20px;border-radius:18px;background:$panel;border:1px solid $border;color:$sub;font-size:16px;margin-bottom:18px}
@media(max-width:1700px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))!important}.pTitle{font-size:31px!important}.rec{grid-template-columns:154px minmax(0,1fr)!important}.rec img{width:154px!important}}
'''
if 'V5.2 - restore the pre-data-rework' not in s:
    if '</style>' not in s: raise SystemExit('v5.2 style close missing')
    s=s.replace('</style>',ui_css+'</style>',1)

old_category='''    private fun showCategory(name:String){currentVideoId=null;val list=if(name=="推荐")videos else videos.filter{it.category==name || (name=="科技AI"&&it.category=="科技")};val body="<div class='chips'>${chips(name)}</div><div class='sectionHead'><h2>${esc(name)}</h2><span>${list.size} 个视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div>";load(shell("home",body))}'''
new_category=r'''    private fun showCategory(name:String){
        currentVideoId=null
        if(name.isBlank()||name=="推荐"){showHome();return}
        val query=when(name){"科技AI"->"人工智能 AI 科技";"汽车"->"汽车 新能源 智能驾驶";"音乐"->"音乐";"旅行"->"旅行 4K 风景";"电影"->"电影 影视";"哲学"->"哲学 思想";else->name}
        val local=videos.filter{it.category==name || (name=="科技AI"&&it.category=="科技")}
        if(prefs.getString("access_token","").orEmpty().isBlank()){
            val body="<div class='chips'>${chips(name)}</div><div class='categoryState52'>登录 YouTube 后可加载与“${esc(name)}”严格对应的真实内容；当前仅显示本地匹配。</div><div class='sectionHead'><h2>${esc(name)}</h2><span>${local.size} 个本地视频</span></div><div class='grid'>${local.joinToString(""){card(it)}}</div>"
            load(shell("home",body));return
        }
        load(shell("home","<div class='chips'>${chips(name)}</div><div class='categoryState52'>正在从 YouTube 加载“${esc(name)}”内容…</div>"))
        Thread{
            try{
                val j=apiGet("search?part=snippet&type=video&videoEmbeddable=true&maxResults=50&relevanceLanguage=zh-Hans&q=${Uri.encode(query)}")
                val arr=j.optJSONArray("items");val list=mutableListOf<Video>()
                if(arr!=null)for(i in 0 until arr.length()){
                    val item=arr.optJSONObject(i)?:continue
                    val id=item.optJSONObject("id")?.optString("videoId").orEmpty()
                    val sn=item.optJSONObject("snippet")?:continue
                    if(id.isBlank())continue
                    val v=Video(id,sn.optString("title","YouTube 视频"),sn.optString("channelTitle","YouTube"),"YouTube · ${name}",name)
                    dynamicVideos[id]=v
                    val cid=sn.optString("channelId","");if(cid.isNotBlank())dynamicVideoChannelIds[id]=cid
                    list+=v
                }
                val html="<div class='chips'>${chips(name)}</div><div class='sectionHead'><h2>${esc(name)}</h2><span>${list.size} 个 YouTube 视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div><div style='height:36px'></div>"
                main.post{load(shell("home",html))}
            }catch(e:Exception){
                val html="<div class='chips'>${chips(name)}</div><div class='categoryState52'>YouTube 分类加载失败：${esc((e.message?:"请求失败").take(120))}</div><div class='grid'>${local.joinToString(""){card(it)}}</div>"
                main.post{load(shell("home",html))}
            }
        }.start()
    }'''
if old_category not in s: raise SystemExit('v5.2 showCategory anchor missing')
s=s.replace(old_category,new_category,1)

s=s.replace('maxResults=30','maxResults=50')
s=s.replace('maxResults=40','maxResults=50')
s=s.replace('homeSubscriptionFeed.toList().distinctBy{it.id}.take(15)','homeSubscriptionFeed.toList().distinctBy{it.id}.take(30)')
s=s.replace('homeLikedFeed.toList().distinctBy{it.id}.take(12)','homeLikedFeed.toList().distinctBy{it.id}.take(30)')
s=s.replace(').distinctBy{it.id}.filter{it.id!=hero.id}.take(15)',').distinctBy{it.id}.filter{it.id!=hero.id}.take(30)')
s=s.replace('channelIds.take(8).joinToString(",")','channelIds.take(20).joinToString(",")')

old_comments='''val comments="<div class='comments'><h2>评论</h2><div id='commentsBody'><div class='comment'><div class='commentAvatar'></div><div><b>YouTube</b><p>正在读取真实评论…</p></div></div></div></div>"'''
new_comments='''val comments="<div class='comments'><div class='commentHead52'><div><h2>评论</h2><div class='commentStats52'>真实 YouTube 评论 · 最多显示 50 条</div></div><div class='commentTools52'><a class='on' href='c16://comments?id=${Uri.encode(id)}&order=relevance'>热门</a><a href='c16://comments?id=${Uri.encode(id)}&order=time'>最新</a></div></div><div id='commentsBody'><div class='comment'><div class='commentAvatar'></div><div><b>YouTube</b><p>正在读取真实评论…</p></div></div></div></div>"'''
if old_comments not in s: raise SystemExit('v5.2 comments html anchor missing')
s=s.replace(old_comments,new_comments,1)

route_anchor='''"channel"->showChannel51(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("tab").orEmpty());"subtoggle"'''
route_new='''"channel"->showChannel51(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("title").orEmpty(),u.getQueryParameter("tab").orEmpty());"comments"->fetchCommentsAsync(u.getQueryParameter("id").orEmpty(),u.getQueryParameter("order").orEmpty().ifBlank{"relevance"});"subtoggle"'''
if route_anchor not in s: raise SystemExit('v5.2 comments route anchor missing')
s=s.replace(route_anchor,route_new,1)

pattern=r'''    private fun fetchCommentsAsync\(videoId:String\)\{\n.*?\n    \}\n    private fun showApiError'''
replacement=r'''    private fun fetchCommentsAsync(videoId:String,order:String="relevance"){
        if(videoId.isBlank())return
        if(prefs.getString("access_token","").orEmpty().isBlank()){
            val html="<div class='comment'><div><b>需要登录</b><p>登录 YouTube 后即可读取真实评论。</p></div></div>"
            main.post{web.evaluateJavascript("document.getElementById('commentsBody')&& (document.getElementById('commentsBody').innerHTML="+JSONObject.quote(html)+")",null)}
            return
        }
        main.post{web.evaluateJavascript("var c=document.getElementById('commentsBody');if(c)c.innerHTML='<div class=\"comment\"><div><b>YouTube</b><p>正在刷新评论…</p></div></div>'",null)}
        Thread{
            try{
                val sort=if(order=="time")"time" else "relevance"
                val j=apiGet("commentThreads?part=snippet,replies&videoId=${Uri.encode(videoId)}&maxResults=50&order=$sort&textFormat=plainText")
                val arr=j.optJSONArray("items");val b=StringBuilder()
                if(arr!=null)for(i in 0 until arr.length()){
                    val thread=arr.optJSONObject(i)?:continue
                    val ts=thread.optJSONObject("snippet")?:continue
                    val topObj=ts.optJSONObject("topLevelComment")?:continue
                    val top=topObj.optJSONObject("snippet")?:continue
                    val author=top.optString("authorDisplayName","YouTube 用户")
                    val text=top.optString("textDisplay","")
                    val avatar=top.optString("authorProfileImageUrl","")
                    val likes=top.optInt("likeCount",0);val replies=ts.optInt("totalReplyCount",0)
                    b.append("<div class='comment'><div class='commentAvatar' style=\"background-image:url('${esc(avatar)}');background-size:cover;background-position:center\"></div><div><b>${esc(author)}</b><p>${esc(text)}</p><div class='commentStats52'>${if(likes>0)"👍 $likes" else ""}${if(replies>0)" · $replies 条回复" else ""}</div></div></div>")
                }
                val html=if(b.isEmpty())"<div class='comment'><div><p>这个视频暂时没有可显示的评论。</p></div></div>" else b.toString()
                main.post{web.evaluateJavascript("document.getElementById('commentsBody')&& (document.getElementById('commentsBody').innerHTML="+JSONObject.quote(html)+")",null)}
            }catch(e:Exception){
                val raw=e.message?:"YouTube API 错误"
                val msg=if(raw.contains("disabled",true)||raw.contains("commentsDisabled",true))"该视频已关闭评论。" else "评论暂时无法读取：${esc(raw.take(160))}"
                val html="<div class='comment'><div><b>YouTube</b><p>$msg</p></div></div>"
                main.post{web.evaluateJavascript("document.getElementById('commentsBody')&& (document.getElementById('commentsBody').innerHTML="+JSONObject.quote(html)+")",null)}
            }
        }.start()
    }
    private fun showApiError'''
s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('v5.2 fetchCommentsAsync anchor missing')
s=s2

s=s.replace('C16 YouTube · V5.1','C16 YouTube · V5.2')
s=s.replace('"应用版本" to "5.1.40068"','"应用版本" to "5.2.40069"')

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V5.2 UI restore, accurate categories, full page data and comments')
