from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V4.7: use the real Android WebView UA instead of impersonating desktop Chrome.
old_ua='userAgentString="Mozilla/5.0 (Linux; Android 12; C16) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"'
new_ua='userAgentString=WebSettings.getDefaultUserAgent(this@MainActivity)'
if old_ua not in s:
    raise SystemExit('v4.7 UA target missing')
s=s.replace(old_ua,new_ua,1)

# Give the embedded player a distinct app origin so loadDataWithBaseURL supplies a stable Referer.
old_load='private fun load(html:String){web.loadDataWithBaseURL("https://www.youtube.com/",html,"text/html","UTF-8",null)}'
new_load='private fun load(html:String){web.loadDataWithBaseURL("https://c16.local/",html,"text/html","UTF-8",null)}'
if old_load not in s:
    raise SystemExit('v4.7 base URL target missing')
s=s.replace(old_load,new_load,1)

# Add explicit referrer policy for the IFrame API generated iframe.
head="<head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>"
head_new="<head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><meta name='referrer' content='strict-origin-when-cross-origin'><style>"
if head not in s:
    raise SystemExit('v4.7 head target missing')
s=s.replace(head,head_new,1)

# Preserve metadata for videos loaded from the YouTube API so account videos do not become generic "YouTube 视频" on playback.
field='    private var currentVideoId: String? = null\n'
if 'dynamicVideos' not in s:
    s=s.replace(field,field+'    private val dynamicVideos=java.util.concurrent.ConcurrentHashMap<String,Video>()\n',1)

old_lookup='val v=videos.firstOrNull{it.id==id}?:Video(id,"YouTube 视频","YouTube","正在播放","推荐");currentVideoId=id'
new_lookup='val v=videos.firstOrNull{it.id==id}?:dynamicVideos[id]?:Video(id,"YouTube 视频","YouTube","正在播放","推荐");currentVideoId=id'
if old_lookup not in s:
    raise SystemExit('v4.7 player metadata target missing')
s=s.replace(old_lookup,new_lookup,1)

old_api_add='out+=Video(id,sn.optString("title","YouTube 视频"),sn.optString("channelTitle","YouTube"),"YouTube · 账号内容","推荐")'
new_api_add='val v=Video(id,sn.optString("title","YouTube 视频"),sn.optString("channelTitle","YouTube"),"YouTube · 账号内容","推荐");dynamicVideos[id]=v;out+=v'
if old_api_add not in s:
    raise SystemExit('v4.7 dynamic API video target missing')
s=s.replace(old_api_add,new_api_add,1)

# Split the right rail into genuinely switchable same-author and related lists.
old_rec='''        val same=videos.filter{it.id!=id&&it.channel==v.channel};val related=videos.filter{it.id!=id&&it.category==v.category&&it !in same}+videos.filter{it.id!=id&&it !in same&&it.category!=v.category};val recs=(same+related).distinctBy{it.id}.take(12)
        val recHtml=recs.joinToString(""){r->"<a class='rec' href='c16://watch?id=${r.id}'><img src='${thumb(r)}'><div><b>${esc(r.title)}</b><span>${esc(r.channel)}<br>${esc(r.meta)}</span></div></a>"}
'''
new_rec='''        val pool=(videos+dynamicVideos.values).distinctBy{it.id}
        val same=pool.filter{it.id!=id&&it.channel.equals(v.channel,true)}.take(12)
        val related=(pool.filter{it.id!=id&&!it.channel.equals(v.channel,true)&&it.category==v.category}+pool.filter{it.id!=id&&!it.channel.equals(v.channel,true)&&it.category!=v.category}).distinctBy{it.id}.take(12)
        val sameHtml=if(same.isEmpty())"<div class='recEmpty'>暂无更多同作者视频</div>" else same.joinToString(""){r->"<a class='rec' href='c16://watch?id=${r.id}'><img src='${thumb(r)}'><div><b>${esc(r.title)}</b><span>${esc(r.channel)}<br>${esc(r.meta)}</span></div></a>"}
        val relatedHtml=if(related.isEmpty())"<div class='recEmpty'>暂无相关推荐</div>" else related.joinToString(""){r->"<a class='rec' href='c16://watch?id=${r.id}'><img src='${thumb(r)}'><div><b>${esc(r.title)}</b><span>${esc(r.channel)}<br>${esc(r.meta)}</span></div></a>"}
'''
if old_rec not in s:
    raise SystemExit('v4.7 recommendation target missing')
s=s.replace(old_rec,new_rec,1)

css_anchor='.playerStatus{font-size:15px;color:rgba(255,255,255,.75)}'
css_add=""".playerStatus{font-size:15px;color:rgba(255,255,255,.75)}.ytMount{position:absolute;inset:0;z-index:2;background:#000}.ytMount iframe{width:100%!important;height:100%!important}.playerError{position:absolute;inset:0;z-index:5;display:none;align-items:center;justify-content:center;text-align:center;padding:38px;background:radial-gradient(circle at 70% 45%,#32113f,#0b0b0d 55%);color:#fff}.playerBox.hasError .playerError{display:flex}.playerError h3{font-size:28px;margin:0 0 10px}.playerError p{font-size:16px;opacity:.78;line-height:1.5}.playerError .errActions{display:flex;gap:10px;justify-content:center;margin-top:18px}.playerError .errActions a{padding:11px 17px;border-radius:22px;background:#fff;color:#111;font-weight:850}.recTabButton{border:0;padding:9px 13px;border-radius:18px;background:$p2;color:$text;font-size:15px;font-weight:750}.recTabButton.on{background:$text;color:$bg}.recPane{display:none}.recPane.on{display:block}.recEmpty{padding:24px 8px;color:$sub;text-align:center;font-size:15px}"""
if css_anchor not in s:
    raise SystemExit('v4.7 CSS target missing')
s=s.replace(css_anchor,css_add,1)

# The V4.6 raw iframe is replaced with the official YouTube IFrame Player API.
old_box='''<div class='playerBox' id='playerBox'><iframe id='ytFrame' src='$embed' allow='autoplay; encrypted-media; picture-in-picture; fullscreen' allowfullscreen referrerpolicy='strict-origin-when-cross-origin' onload="this.classList.add('playerReady');document.getElementById('loadState').innerText='播放器已连接'"></iframe><div class='loading'><div class='spinner'></div><b style='font-size:22px'>正在连接 YouTube</b><span class='playerStatus' id='loadState'>正在加载官方嵌入播放器…</span></div><div class='playerFallback'><a href='c16://playerreload?id=${Uri.encode(id)}'>重新加载</a><a href='c16://watchweb?id=${Uri.encode(id)}'>YouTube 网页模式</a></div></div>'''
new_box='''<div class='playerBox' id='playerBox'><div id='ytPlayer' class='ytMount'></div><div class='loading' id='playerLoading'><div class='spinner'></div><b style='font-size:22px'>正在连接 YouTube</b><span class='playerStatus' id='loadState'>正在初始化官方 IFrame Player API…</span></div><div class='playerFallback'><a href='c16://playerreload?id=${Uri.encode(id)}'>重新加载</a><a href='c16://watchweb?id=${Uri.encode(id)}'>YouTube 网页模式</a></div><div class='playerError' id='playerError'><div><h3>嵌入播放暂不可用</h3><p id='playerErrorText'>YouTube 拒绝了当前嵌入播放请求。</p><div class='errActions'><a href='c16://playerreload?id=${Uri.encode(id)}'>重试</a><a href='c16://watchweb?id=${Uri.encode(id)}'>在 YouTube 网页播放</a></div></div></div></div>'''
if old_box not in s:
    raise SystemExit('v4.7 player box target missing')
s=s.replace(old_box,new_box,1)

old_aside="""<aside class='recommend'><div class='recTabs'><span class='tab on'>同作者优先</span><span class='tab'>相关推荐</span></div>$recHtml</aside>"""
new_aside="""<aside class='recommend'><div class='recTabs'><button id='sameTab' class='recTabButton on' onclick=\"switchRec('same')\">同作者优先</button><button id='relatedTab' class='recTabButton' onclick=\"switchRec('related')\">相关推荐</button></div><div id='samePane' class='recPane on'>$sameHtml</div><div id='relatedPane' class='recPane'>$relatedHtml</div></aside>"""
if old_aside not in s:
    raise SystemExit('v4.7 recommendation UI target missing')
s=s.replace(old_aside,new_aside,1)

# Replace the V4.6 timeout/message hook with explicit IFrame API ready/error handling.
old_script='''</aside></div><script>setTimeout(function(){var b=document.getElementById('playerBox');if(b)b.classList.add('playerSlow')},8000);window.addEventListener('message',function(e){if(typeof e.data==='string'&&e.data.indexOf('onStateChange')>=0){var l=document.querySelector('.loading');if(l)l.style.display='none'}});</script>""";load(shell("",body,true));fetchCommentsAsync(id)
'''
new_script='''</aside></div><script>
function switchRec(mode){var s=document.getElementById('samePane'),r=document.getElementById('relatedPane'),st=document.getElementById('sameTab'),rt=document.getElementById('relatedTab');if(mode==='related'){s.classList.remove('on');r.classList.add('on');st.classList.remove('on');rt.classList.add('on')}else{r.classList.remove('on');s.classList.add('on');rt.classList.remove('on');st.classList.add('on')}}
var ytReady=false;function hideLoad(){var l=document.getElementById('playerLoading');if(l)l.style.display='none';var b=document.getElementById('playerBox');if(b)b.classList.remove('playerSlow')}
function showPlayerError(code){hideLoad();var b=document.getElementById('playerBox'),t=document.getElementById('playerErrorText');if(b)b.classList.add('hasError');var m='YouTube 播放器错误 '+code+'。';if(code==101||code==150)m='视频作者不允许第三方嵌入播放。';else if(code==153)m='播放器请求缺少 YouTube 要求的来源标识。';else if(code==5)m='当前 WebView 无法播放这个 HTML5 视频。';if(t)t.innerText=m+' 可以改用 YouTube 网页模式。'}
function onYouTubeIframeAPIReady(){ytReady=true;new YT.Player('ytPlayer',{videoId:'${id}',playerVars:{autoplay:1,controls:1,playsinline:1,rel:0,fs:1,origin:'https://c16.local',widget_referrer:'https://c16.local/'},events:{onReady:function(e){hideLoad();try{e.target.playVideo()}catch(x){}},onStateChange:function(e){if(e.data===YT.PlayerState.PLAYING||e.data===YT.PlayerState.PAUSED||e.data===YT.PlayerState.CUED)hideLoad()},onError:function(e){showPlayerError(e.data)},onAutoplayBlocked:function(){var t=document.getElementById('loadState');if(t)t.innerText='自动播放被系统拦截，请点击播放器开始播放'}}})}
var tag=document.createElement('script');tag.src='https://www.youtube.com/iframe_api';document.head.appendChild(tag);
setTimeout(function(){if(!ytReady){var b=document.getElementById('playerBox'),t=document.getElementById('loadState');if(b)b.classList.add('playerSlow');if(t)t.innerText='播放器连接较慢，可尝试重新加载或网页模式'}},9000);
</script>""";load(shell("",body,true));fetchCommentsAsync(id)
'''
if old_script not in s:
    raise SystemExit('v4.7 player script target missing')
s=s.replace(old_script,new_script,1)

# The old embed string is no longer used by the player.
old_embed='''        val embed="https://www.youtube.com/embed/${Uri.encode(id)}?autoplay=1&playsinline=1&rel=0&enablejsapi=1&fs=1&origin=https%3A%2F%2Fwww.youtube.com&widget_referrer=https%3A%2F%2Fwww.youtube.com%2F"
'''
if old_embed in s:
    s=s.replace(old_embed,'',1)

# Visible version label.
s=s.replace('C16 YouTube · V4.6</p>','C16 YouTube · V4.7</p>',1)

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube V4.7 IFrame API/referrer/recommendation upgrade')
