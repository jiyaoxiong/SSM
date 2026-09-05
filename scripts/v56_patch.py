from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V5.6: product/UX fixes only. Keep the proven V4.8+ IFrame/WebView/Media Integrity playback core untouched.

# 1) Player sidebar: do not rerender/reload the player. Toggle the already-rendered sidebar in DOM.
old='''"sidebar"->{collapsed=!collapsed;prefs.edit().putBoolean("collapsed",collapsed).apply();rerender()};'''
new='''"sidebar"->{if(currentVideoId!=null)togglePlayerSidebar56() else {collapsed=!collapsed;prefs.edit().putBoolean("collapsed",collapsed).apply();rerender()}};'''
if old not in s: raise SystemExit('v5.6 sidebar route anchor missing')
s=s.replace(old,new,1)

# 2) History: V4.4 only resolved IDs against the tiny static demo list, so real API videos disappeared.
old_hist='''    private fun historyVideos():List<Video> = historyIds().mapNotNull{id->videos.firstOrNull{it.id==id}}.take(20)
    private fun addHistory(id:String){
        if(id.isBlank())return
        val ids=(listOf(id)+historyIds().filter{it!=id}).take(30)
        prefs.edit().putString("history_ids",ids.joinToString(",")).apply()
    }
'''
new_hist='''    private fun historyMeta56():JSONObject=try{JSONObject(prefs.getString("history_meta_56","{}").orEmpty())}catch(_:Exception){JSONObject()}
    private fun historyVideos():List<Video>{
        val meta=historyMeta56()
        return historyIds().mapNotNull{id->
            dynamicVideos[id]?:videos.firstOrNull{it.id==id}?:meta.optJSONObject(id)?.let{j->Video(id,j.optString("title","YouTube 视频"),j.optString("channel","YouTube"),j.optString("meta","观看记录"),j.optString("category","推荐"))}
        }
    }
    private fun persistHistoryVideo56(id:String){
        val v=dynamicVideos[id]?:videos.firstOrNull{it.id==id}?:return
        val root=historyMeta56();root.put(id,JSONObject().put("title",v.title).put("channel",v.channel).put("meta",v.meta).put("category",v.category))
        prefs.edit().putString("history_meta_56",root.toString()).apply()
    }
    private fun addHistory(id:String){
        if(id.isBlank())return
        val ids=(listOf(id)+historyIds().filter{it!=id}).take(200)
        prefs.edit().putString("history_ids",ids.joinToString(",")).apply()
        persistHistoryVideo56(id)
    }
'''
if old_hist not in s: raise SystemExit('v5.6 history methods anchor missing')
s=s.replace(old_hist,new_hist,1)

# Route history through a recovery-aware renderer. It can recover metadata for old dynamic IDs via Data API.
s=s.replace('''"history"->showHistory();''','''"history"->showHistory56();''',1)

# 3) Channel home: show every video already fetched on a horizontal swipe rail, then expose the unlimited V5.4 videos tab.
old_home='''                            val homeVideos=if(latest.isEmpty())"" else "<div class='sectionHead'><h2>最新视频</h2><span>${latest.size} 个</span></div><div class='grid'>${latest.take(12).joinToString(""){card(it)}}</div>"'''
new_home='''                            val homeVideos=if(latest.isEmpty())"" else rail("最新视频","左右滑动查看更多 · 已读取 ${latest.size} 个",latest)+"<div class='channelMore56'><a class='more54' href='c16://channel?id=${Uri.encode(id)}&title=${Uri.encode(channelTitle)}&tab=videos'>查看频道全部视频</a><span>进入后每次继续加载 50 个，直到该频道全部视频加载完成</span></div>"'''
if old_home not in s: raise SystemExit('v5.6 channel home anchor missing')
s=s.replace(old_home,new_home,1)

# 4) Recommendation typography: V5.5 made title too dominant while metadata stayed too small.
css=r'''
/* V5.6 targeted UX corrections. */
.app.playerSideOpen56{grid-template-columns:260px 1fr!important}.app.playerSideOpen56 .brand{justify-content:flex-start!important}.app.playerSideOpen56 .brand strong,.app.playerSideOpen56 .nav b{display:block!important}.app.playerSideOpen56 .nav{justify-content:flex-start!important;padding:0 18px!important}
.channelMore56{display:flex;align-items:center;justify-content:center;gap:16px;margin:18px 0 8px}.channelMore56 span{font-size:16px;color:$sub}.channelMore56 .more54{min-width:230px}
.recommend .rec b,.recommend .recTitle{font-size:18px!important;line-height:1.32!important;font-weight:680!important;max-height:50px!important;overflow:hidden!important}.recommend .rec span,.recommend .recMeta{font-size:16px!important;line-height:1.45!important}.recommend .rec{gap:14px!important}.recommend .tab{font-size:16px!important}
.historyState56{padding:18px 20px;border-radius:18px;background:$panel;border:1px solid $border;color:$sub;font-size:16px;margin-bottom:18px}
@media(max-width:1500px){.recommend .rec b,.recommend .recTitle{font-size:17px!important}.recommend .rec span,.recommend .recMeta{font-size:15px!important}}
'''
if 'V5.6 targeted UX corrections' not in s:
    if '</style>' not in s: raise SystemExit('v5.6 style anchor missing')
    s=s.replace('</style>',css+'</style>',1)

# Add helpers before the V5.1 account helper (stable insertion point after all earlier patches).
marker='''    private fun accountPill51():String{'''
methods=r'''    private fun togglePlayerSidebar56(){
        val js="(function(){var a=document.querySelector('.app');if(!a)return;var o=a.classList.toggle('playerSideOpen56');var b=document.querySelector('.collapse');if(b)b.textContent=o?'‹':'›';})()"
        web.evaluateJavascript(js,null)
    }
    private fun renderHistory56(note:String=""){
        val list=historyVideos()
        val status=if(note.isBlank())"" else "<div class='historyState56'>${esc(note)}</div>"
        val inner=if(list.isEmpty())status+"<div class='simple'><h1>历史记录</h1><p>播放视频后会自动保存在这台 C16；旧版本记录也会尝试自动恢复。</p></div>" else status+"<div class='sectionHead'><h2>历史记录</h2><span>${list.size} 个视频</span></div><div class='grid'>${list.joinToString(""){card(it)}}</div><div style='height:36px'></div>"
        load(shell("history",inner))
    }
    private fun showHistory56(){
        currentVideoId=null
        val ids=historyIds().distinct()
        if(ids.isEmpty()){renderHistory56();return}
        val resolved=historyVideos().map{it.id}.toSet();val missing=ids.filter{it !in resolved}
        if(missing.isEmpty()){renderHistory56();return}
        renderHistory56("正在恢复旧版本观看记录…")
        if(prefs.getString("access_token","").orEmpty().isBlank())return
        Thread{
            try{
                missing.chunked(50).forEach{chunk->
                    val j=apiGet("videos?part=snippet&id=${chunk.joinToString(",")}&maxResults=50")
                    val got=apiVideoList(j);got.forEach{v->dynamicVideos[v.id]=v;persistHistoryVideo56(v.id)}
                }
                main.post{renderHistory56()}
            }catch(e:Exception){main.post{renderHistory56("部分旧记录暂时无法恢复：${(e.message?:"请求失败").take(120)}")}}
        }.start()
    }
'''
if marker not in s: raise SystemExit('v5.6 helper insertion anchor missing')
s=s.replace(marker,methods+marker,1)

s=s.replace('C16 YouTube · V5.5','C16 YouTube · V5.6')
s=s.replace('"应用版本" to "5.5.40072"','"应用版本" to "5.6.40073"')

p.write_text(s,encoding='utf-8')
print('Applied V5.6 history recovery, live player sidebar, full channel-home rail and recommendation typography balance')
