from pathlib import Path
import re

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# Subscription route now supports explicit pages, so all channels are discoverable on the C16 screen.
route='''"subscriptions"->showSubscriptions();'''
route_new='''"subscriptions"->showSubscriptions53(u.getQueryParameter("page")?.toIntOrNull()?:1);'''
if route not in s: raise SystemExit('v5.3 subscriptions route anchor missing')
s=s.replace(route,route_new,1)

css=r'''
/* V5.3 C16 subscription gallery: compact channel-first design, 18 channels per screen. */
.subTop53{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin:0 0 22px}.subTop53 h1{font-size:32px;line-height:1.1;margin:0;font-weight:720}.subTop53 p{font-size:15px;color:$sub;margin:7px 0 0}.subCount53{font-size:15px;color:$sub;background:$panel;border:1px solid $border;border-radius:20px;padding:9px 14px;white-space:nowrap}
.subGrid53{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:18px}.subCard53{display:flex;align-items:center;gap:15px;min-height:112px;padding:16px;border-radius:20px;background:$panel;border:1px solid $border;transition:.16s ease;overflow:hidden}.subCard53:active{transform:scale(.985);background:$p2}.subAvatar53{width:78px;height:78px;min-width:78px;border-radius:50%;object-fit:cover;background:$p2}.subInfo53{min-width:0;flex:1}.subInfo53 b{display:block;font-size:17px;line-height:1.3;font-weight:680;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.subInfo53 span{display:block;margin-top:7px;font-size:13px;color:$sub}.subArrow53{font-size:21px;color:$sub;line-height:1}
.subPager53{display:flex;align-items:center;justify-content:center;gap:12px;margin:26px 0 4px}.subPager53 a,.subPager53 span{display:inline-flex;align-items:center;justify-content:center;height:44px;min-width:44px;padding:0 15px;border-radius:22px;background:$panel;border:1px solid $border;font-size:15px;font-weight:650}.subPager53 .on{background:$text;color:$bg}.subPager53 .disabled{opacity:.35}.subRange53{text-align:center;color:$sub;font-size:14px;margin-top:10px}
@media(max-width:1900px){.subGrid53{grid-template-columns:repeat(5,minmax(0,1fr))}}@media(max-width:1500px){.subGrid53{grid-template-columns:repeat(4,minmax(0,1fr))}}
'''
if 'V5.3 C16 subscription gallery' not in s:
    s=s.replace('</style>',css+'</style>',1)

# Insert a new implementation rather than touching the older account API method.
marker='''    private fun showLikedVideos(){'''
method=r'''    private fun showSubscriptions53(requestedPage:Int){
        currentVideoId=null
        requireLoginOr{
            load(shell("subscriptions","<div class='subTop53'><div><h1>订阅频道</h1><p>正在同步你的全部 YouTube 订阅…</p></div></div>"))
            Thread{
                try{
                    val all=mutableListOf<Array<String>>()
                    var token=""
                    var guard=0
                    do{
                        val suffix=if(token.isBlank())"" else "&pageToken=${Uri.encode(token)}"
                        val j=apiGet("subscriptions?part=snippet&mine=true&maxResults=50&order=alphabetical$suffix")
                        val arr=j.optJSONArray("items")
                        if(arr!=null)for(i in 0 until arr.length()){
                            val sn=arr.optJSONObject(i)?.optJSONObject("snippet")?:continue
                            val rid=sn.optJSONObject("resourceId")?.optString("channelId").orEmpty()
                            if(rid.isBlank())continue
                            val title=sn.optString("title","YouTube 频道")
                            val thumbs=sn.optJSONObject("thumbnails")
                            val img=thumbs?.optJSONObject("high")?.optString("url",thumbs.optJSONObject("medium")?.optString("url",thumbs.optJSONObject("default")?.optString("url").orEmpty()).orEmpty()).orEmpty()
                            all+=arrayOf(rid,title,img)
                        }
                        token=j.optString("nextPageToken","")
                        guard++
                    }while(token.isNotBlank() && guard<4)

                    val pageSize=18
                    val pages=maxOf(1,(all.size+pageSize-1)/pageSize)
                    val page=requestedPage.coerceIn(1,pages)
                    val start=(page-1)*pageSize
                    val slice=all.drop(start).take(pageSize)
                    val cards=StringBuilder()
                    for(ch in slice){
                        cards.append("<a class='subCard53' href='c16://channel?id=${Uri.encode(ch[0])}&title=${Uri.encode(ch[1])}'><img class='subAvatar53' src='${esc(ch[2])}'><div class='subInfo53'><b>${esc(ch[1])}</b><span>查看频道最新视频</span></div><span class='subArrow53'>›</span></a>")
                    }
                    val pager=StringBuilder("<div class='subPager53'>")
                    if(page>1)pager.append("<a href='c16://subscriptions?page=${page-1}'>‹ 上一页</a>") else pager.append("<span class='disabled'>‹ 上一页</span>")
                    for(n in 1..pages){
                        if(pages<=5 || n==1 || n==pages || kotlin.math.abs(n-page)<=1){
                            pager.append("<a class='${if(n==page)"on" else ""}' href='c16://subscriptions?page=$n'>$n</a>")
                        }else if((n==2 && page>3)||(n==pages-1 && page<pages-2))pager.append("<span class='disabled'>…</span>")
                    }
                    if(page<pages)pager.append("<a href='c16://subscriptions?page=${page+1}'>下一页 ›</a>") else pager.append("<span class='disabled'>下一页 ›</span>")
                    pager.append("</div>")
                    val from=if(slice.isEmpty())0 else start+1;val to=start+slice.size
                    val html="<div class='subTop53'><div><h1>订阅频道</h1><p>频道优先的大屏布局 · 点击头像卡片直接进入频道</p></div><div class='subCount53'>共 ${all.size} 个频道</div></div><div class='subGrid53'>$cards</div>$pager<div class='subRange53'>当前显示 $from–$to / ${all.size} · 第 $page / $pages 页</div><div style='height:42px'></div>"
                    main.post{load(shell("subscriptions",html))}
                }catch(e:Exception){main.post{showApiError("订阅频道",e)}}
            }.start()
        }
    }

'''
if marker not in s: raise SystemExit('v5.3 method marker missing')
s=s.replace(marker,method+marker,1)

s=s.replace('C16 YouTube · V5.2','C16 YouTube · V5.3')
s=s.replace('"应用版本" to "5.2.40069"','"应用版本" to "5.3.40070"')

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V5.3 subscription gallery redesign')
