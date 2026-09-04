from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V4.9 focuses on the home/data layer now that V4.8 playback works.
field='    private val dynamicVideos=java.util.concurrent.ConcurrentHashMap<String,Video>()\n'
add='''    private val homeSubscriptionFeed=java.util.concurrent.CopyOnWriteArrayList<Video>()
    private val homeLikedFeed=java.util.concurrent.CopyOnWriteArrayList<Video>()
    @Volatile private var homeSyncing=false
    @Volatile private var homeSyncError=""
    @Volatile private var homeSyncedAt=0L
'''
if 'homeSubscriptionFeed' not in s:
    if field not in s: raise SystemExit('v4.9 dynamicVideos field missing')
    s=s.replace(field,field+add,1)

# Give Driving Mode its own route instead of routing back to ordinary home.
route_old='''"home"->showHome();"watch"'''
route_new='''"home"->showHome();"drivehome"->showDriveHome();"watch"'''
if route_old not in s: raise SystemExit('v4.9 home route target missing')
s=s.replace(route_old,route_new,1)

nav_old='''${nav("home","home","首页","home")}${nav("drive","drive","驾驶模式","home")}'''
nav_new='''${nav("home","home","首页","home")}${nav("drive","drive","驾驶模式","drivehome")}'''
if nav_old not in s: raise SystemExit('v4.9 drive nav target missing')
s=s.replace(nav_old,nav_new,1)

# Home-specific CSS: denser TV/car shelves and clear account-sync states.
css_anchor='.section{margin-top:28px}'
css_add='''.section{margin-top:28px}.homeSync{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:15px 18px;margin:0 0 18px;border-radius:18px;background:$panel;border:1px solid $border}.homeSync strong{font-size:18px}.homeSync span{font-size:15px;color:$sub}.homeCta{display:flex;align-items:center;justify-content:space-between;gap:22px;padding:22px 24px;border-radius:22px;background:linear-gradient(115deg,${if(dark)"#201316,#141414" else "#fff1f3,#ffffff"});border:1px solid $border;margin-top:26px}.homeCta h3{font-size:25px;margin:0 0 7px}.homeCta p{margin:0;color:$sub;font-size:16px}.homeCta .btn{white-space:nowrap;background:#ff0033;color:#fff}.driveGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;margin-top:18px}.driveTile{min-height:180px;border-radius:24px;padding:24px;background:$panel;border:1px solid $border;display:flex;flex-direction:column;justify-content:space-between}.driveTile b{font-size:27px}.driveTile span{font-size:16px;color:$sub}.driveHero{padding:30px 32px;border-radius:28px;background:linear-gradient(120deg,#0b1118,#192a3b);color:#fff;min-height:250px;display:flex;flex-direction:column;justify-content:flex-end}.driveHero h1{font-size:43px;margin:0 0 10px}.driveHero p{font-size:18px;color:#d8e2ec;margin:0 0 20px}.emptyShelf{padding:24px;border:1px dashed $border;border-radius:18px;color:$sub;background:$panel;font-size:16px}'''
if css_anchor not in s: raise SystemExit('v4.9 CSS anchor missing')
s=s.replace(css_anchor,css_add,1)

old_home='''    private fun showHome(){currentVideoId=null;val hero=videos.first();val history=historyVideos();val continueList=if(history.isEmpty())videos.take(8) else history;val body="""<div class='chips'>${chips("推荐")}</div><div class='hero'><img src='${thumb(hero)}'><div class='shade'></div><div class='heroCopy'><small>为你精选</small><h1>${esc(hero.title)}</h1><p>适配 C16 14.6 英寸横屏的大屏 YouTube 首页。</p><div class='heroBtns'><a class='btn' href='c16://watch?id=${hero.id}'>▶ 立即播放</a><a class='btn alt' href='c16://category?name=科技AI'>探索更多</a></div></div></div>${rail("继续观看",if(history.isEmpty())"开始播放后自动记录" else "你的真实车机观看记录",continueList)}${rail("订阅频道更新","登录后逐步同步 YouTube 账号内容",videos.drop(3).take(9))}${rail("猜你喜欢","向右查看更多",videos.reversed())}<div style='height:30px'></div>""";load(shell("home",body))}
'''
new_home='''    private fun showHome(){
        currentVideoId=null
        load(shell("home","<div id='homeRoot'>${homeBody()}</div>"))
        maybeSyncHomeFeed()
    }
    private fun homeBody():String{
        val history=historyVideos()
        val signed=prefs.getString("access_token","").orEmpty().isNotBlank()
        val subs=homeSubscriptionFeed.toList().distinctBy{it.id}.take(15)
        val likes=homeLikedFeed.toList().distinctBy{it.id}.take(12)
        val hero=(subs.firstOrNull()?:history.firstOrNull()?:likes.firstOrNull()?:videos.first())
        val preferred=history.groupingBy{it.category}.eachCount().entries.sortedByDescending{it.value}.map{it.key}
        val preferredStatic=(preferred.flatMap{cat->videos.filter{it.category==cat}}+videos).distinctBy{it.id}
        val recommend=(likes+subs+history+preferredStatic).distinctBy{it.id}.filter{it.id!=hero.id}.take(15)
        val syncLine=when{
            !signed->"<div class='homeSync'><strong>个性化首页</strong><span>登录 YouTube 后同步订阅频道、点赞与账号内容</span></div>"
            homeSyncing->"<div class='homeSync'><strong>正在同步你的 YouTube 首页</strong><span>订阅 · 点赞 · 最近内容</span></div>"
            homeSyncError.isNotBlank()->"<div class='homeSync'><strong>账号内容暂未同步</strong><span>${esc(homeSyncError)}</span></div>"
            subs.isNotEmpty()||likes.isNotEmpty()->"<div class='homeSync'><strong>已同步 YouTube 账号内容</strong><span>${subs.size} 个订阅更新 · ${likes.size} 个点赞视频</span></div>"
            else->"<div class='homeSync'><strong>YouTube 账号已连接</strong><span>正在等待账号首页内容</span></div>"
        }
        val continueSection=if(history.isEmpty())"" else rail("继续观看","来自这台 C16 的真实观看记录",history.take(12))
        val subscriptionSection=if(subs.isEmpty())"" else rail("订阅频道更新","来自你订阅频道的最新视频",subs)
        val likedSection=if(likes.isEmpty())"" else rail("点赞回看","你的 YouTube 点赞视频",likes)
        val loginCta=if(signed)"" else "<div class='homeCta'><div><h3>把你的 YouTube 带到 C16</h3><p>登录后首页自动显示订阅更新、点赞视频和你的账号内容。</p></div><a class='btn' href='c16://login'>手机扫码登录</a></div>"
        return """$syncLine<div class='chips'>${chips("推荐")}</div><div class='hero'><img src='${thumb(hero)}'><div class='shade'></div><div class='heroCopy'><small>${if(subs.any{it.id==hero.id})"来自你的订阅" else if(history.any{it.id==hero.id})"继续观看" else "为你精选"}</small><h1>${esc(hero.title)}</h1><p>${esc(hero.channel)} · C16 大屏首页</p><div class='heroBtns'><a class='btn' href='c16://watch?id=${hero.id}'>▶ 立即播放</a><a class='btn alt' href='c16://drivehome'>驾驶模式</a></div></div></div>$continueSection$subscriptionSection$likedSection${rail("为你推荐","结合观看记录、订阅与点赞",recommend)}${rail("音乐与氛围","适合车内大屏播放",videos.filter{it.category=="音乐"}.take(10))}${rail("旅行与 4K","大屏风景内容",videos.filter{it.category=="旅行"}.take(10))}$loginCta<div style='height:34px'></div>"""
    }
    private fun maybeSyncHomeFeed(){
        if(prefs.getString("access_token","").orEmpty().isBlank())return
        if(homeSyncing)return
        if((homeSubscriptionFeed.isNotEmpty()||homeLikedFeed.isNotEmpty())&&System.currentTimeMillis()-homeSyncedAt<15*60*1000L)return
        homeSyncing=true;homeSyncError=""
        updateHomeDom()
        Thread{
            try{
                val likes=apiVideoList(apiGet("videos?part=snippet&myRating=like&maxResults=20"))
                val sj=apiGet("subscriptions?part=snippet&mine=true&maxResults=12")
                val sa=sj.optJSONArray("items")
                val channelIds=mutableListOf<String>()
                if(sa!=null)for(i in 0 until sa.length()){
                    val id=sa.optJSONObject(i)?.optJSONObject("snippet")?.optJSONObject("resourceId")?.optString("channelId").orEmpty()
                    if(id.isNotBlank())channelIds+=id
                }
                val recent=mutableListOf<Video>()
                if(channelIds.isNotEmpty()){
                    val cj=apiGet("channels?part=contentDetails&id=${channelIds.take(8).joinToString(",")}")
                    val ca=cj.optJSONArray("items")
                    if(ca!=null)for(i in 0 until ca.length()){
                        val uploads=ca.optJSONObject(i)?.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")?.optString("uploads").orEmpty()
                        if(uploads.isBlank())continue
                        try{recent+=apiVideoList(apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=3"),true)}catch(_:Exception){}
                    }
                }
                homeLikedFeed.clear();homeLikedFeed.addAll(likes)
                homeSubscriptionFeed.clear();homeSubscriptionFeed.addAll(recent.distinctBy{it.id})
                homeSyncedAt=System.currentTimeMillis();homeSyncError=""
            }catch(e:Exception){homeSyncError=(e.message?:"YouTube 账号同步失败").take(140)}
            finally{homeSyncing=false;main.post{updateHomeDom()}}
        }.start()
    }
    private fun updateHomeDom(){
        main.post{
            val html=homeBody()
            web.evaluateJavascript("var r=document.getElementById('homeRoot');if(r)r.innerHTML="+JSONObject.quote(html),null)
        }
    }
    private fun showDriveHome(){
        currentVideoId=null
        val history=historyVideos()
        val next=history.firstOrNull()?:homeSubscriptionFeed.firstOrNull()?:videos.first()
        val body="""<div class='driveHero'><small style='font-weight:900;letter-spacing:3px;color:#7ac7ff'>C16 DRIVE</small><h1>大屏娱乐中心</h1><p>更少菜单、更大按钮，适合 14.6 英寸横屏操作。</p><div class='heroBtns'><a class='btn' href='c16://watch?id=${next.id}'>▶ ${if(history.isEmpty())"开始播放" else "继续观看"}</a><a class='btn alt' href='c16://home'>标准首页</a></div></div><div class='driveGrid'><a class='driveTile' href='c16://category?name=音乐'><b>音乐</b><span>车内氛围与热门音乐</span></a><a class='driveTile' href='c16://history'><b>最近播放</b><span>${history.size} 个车机观看记录</span></a><a class='driveTile' href='c16://favorites'><b>收藏</b><span>快速打开车机收藏</span></a><a class='driveTile' href='c16://subscriptions'><b>订阅</b><span>查看 YouTube 订阅频道</span></a></div>${if(history.isEmpty())"" else rail("继续观看","驾驶模式快捷入口",history.take(10))}<div style='height:30px'></div>"""
        load(shell("drive",body))
    }
'''
if old_home not in s: raise SystemExit('v4.9 showHome target missing')
s=s.replace(old_home,new_home,1)

# Account center: returning from login should immediately allow home sync to refresh.
old_account_load='''        load(shell("",body));fetchAccountProfileAsync()\n'''
new_account_load='''        load(shell("",body));fetchAccountProfileAsync();homeSyncedAt=0L\n'''
if old_account_load in s:
    s=s.replace(old_account_load,new_account_load,1)

# Logout should clear account-derived home data, while preserving local history/favorites.
old_logout='''        loginPolling.set(false)\n        prefs.edit().remove("access_token").remove("refresh_token").remove("token_expires_at").apply()\n        showLoginCenter()\n'''
new_logout='''        loginPolling.set(false)\n        prefs.edit().remove("access_token").remove("refresh_token").remove("token_expires_at").apply()\n        homeSubscriptionFeed.clear();homeLikedFeed.clear();homeSyncedAt=0L;homeSyncError=""\n        showLoginCenter()\n'''
if old_logout not in s: raise SystemExit('v4.9 logout target missing')
s=s.replace(old_logout,new_logout,1)

# Visible version labels, including the diagnostics page introduced in V4.8.
s=s.replace('C16 YouTube · V4.8','C16 YouTube · V4.9')
s=s.replace('"应用版本" to "4.8.40065"','"应用版本" to "4.9.40066"')

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V4.9 dynamic account home / driving home patch')
