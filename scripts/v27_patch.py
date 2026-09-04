from pathlib import Path

path = Path("app/src/main/java/com/c16/video/MainActivity.kt")
s = path.read_text(encoding="utf-8")


def replace(old: str, new: str, label: str):
    global s
    if old not in s:
        raise SystemExit(f"v2.7 patch failed: missing {label}")
    s = s.replace(old, new, 1)

# Keep the custom loading layer above all YouTube-owned loading surfaces until
# the IFrame Player API reports PLAYING. This masks the gray splash seen after
# iframe onload but before actual playback begins.
replace(
    ".playerBox iframe{position:relative;z-index:1;width:100%;height:100%;border:0;background:transparent}",
    ".playerBox iframe,.playerBox #ytPlayer{position:relative;z-index:1;width:100%;height:100%;border:0;background:#07131f}",
    "player iframe CSS",
)

replace(
    ".videoLoading{position:absolute;z-index:4;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;color:#fff;background:radial-gradient(circle at 50% 45%,rgba(36,86,120,.68) 0%,rgba(10,34,52,.95) 42%,rgba(5,16,27,.99) 100%);transition:opacity .35s ease}",
    ".videoLoading{position:absolute;z-index:6;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;color:#fff;background:radial-gradient(circle at 50% 45%,rgba(36,86,120,.72) 0%,rgba(10,34,52,.96) 42%,rgba(5,16,27,.995) 100%);transition:opacity .28s ease}",
    "loading overlay z-index",
)

replace(
    "function startQr(){var c=document.getElementById('client').value.trim();location.href='c16://startQr?client='+encodeURIComponent(c)}function hideVideoLoading(){setTimeout(function(){var e=document.getElementById('videoLoading');if(e)e.classList.add('hide')},1100)}function toggleSide(){var a=document.querySelector('.app');if(a)a.classList.toggle('hideSide')}function toggleRec(){var p=document.querySelector('.playerPage');if(p)p.classList.toggle('hideRec')}</script>",
    "function startQr(){var c=document.getElementById('client').value.trim();location.href='c16://startQr?client='+encodeURIComponent(c)}function revealVideo(){var e=document.getElementById('videoLoading');if(e)e.classList.add('hide')}function initC16Player(id){window.c16VideoId=id;window.c16Fallback=setTimeout(revealVideo,15000);if(window.YT&&YT.Player)c16BuildPlayer()}function c16BuildPlayer(){if(!window.c16VideoId||window.c16Player)return;window.c16Player=new YT.Player('ytPlayer',{videoId:window.c16VideoId,playerVars:{autoplay:1,playsinline:1,rel:0,fs:0,modestbranding:1},events:{onReady:function(e){try{e.target.playVideo()}catch(x){}},onStateChange:function(e){if(e.data===1){clearTimeout(window.c16Fallback);setTimeout(revealVideo,180)}}}})}function onYouTubeIframeAPIReady(){c16BuildPlayer()}function toggleSide(){var a=document.querySelector('.app');if(a)a.classList.toggle('hideSide')}function toggleRec(){var p=document.querySelector('.playerPage');if(p)p.classList.toggle('hideRec')}</script>",
    "player API javascript",
)

replace(
    "<div class='playerBox'><div class='videoLoading' id='videoLoading'><div class='spinner'></div><strong>正在加载视频</strong><span>正在准备 YouTube 播放器…</span></div><iframe onload='hideVideoLoading()' src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0&modestbranding=1' allow='autoplay; encrypted-media; picture-in-picture'></iframe><span class='quality'>4K · HDR</span>",
    "<div class='playerBox'><div class='videoLoading' id='videoLoading' style=\"background:linear-gradient(135deg,rgba(5,16,27,.80),rgba(9,35,55,.88)),url('https://i.ytimg.com/vi/${current.id}/hqdefault.jpg') center/cover no-repeat\"><div class='spinner'></div><strong>正在加载视频</strong><span>正在等待画面开始播放…</span></div><div id='ytPlayer'></div><script src='https://www.youtube.com/iframe_api'></script><script>initC16Player('${current.id}')</script><span class='quality'>4K · HDR</span>",
    "player API HTML",
)

# Give fullscreen playback the same behavior, so YouTube's gray intermediate
# frame is masked there as well.
replace(
    ".stage iframe{position:absolute;inset:0;width:100%;height:100%;border:0}.back{position:absolute;left:26px;top:22px;z-index:5;background:rgba(0,0,0,.66);color:#fff;border:1px solid rgba(255,255,255,.30);padding:13px 20px;border-radius:24px;font:800 21px sans-serif;text-decoration:none}",
    ".stage iframe,.stage #fullPlayer{position:absolute;inset:0;width:100%;height:100%;border:0;background:#07131f}.fullLoad{position:absolute;z-index:6;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:13px;color:#fff;background:radial-gradient(circle at center,#153b57 0%,#0a2234 45%,#050f19 100%);transition:opacity .28s}.fullLoad.hide{opacity:0;pointer-events:none}.fullSpin{width:58px;height:58px;border:4px solid rgba(255,255,255,.25);border-top-color:#ff0033;border-radius:50%;animation:fsSpin .85s linear infinite}@keyframes fsSpin{to{transform:rotate(360deg)}}.back{position:absolute;left:26px;top:22px;z-index:7;background:rgba(0,0,0,.66);color:#fff;border:1px solid rgba(255,255,255,.30);padding:13px 20px;border-radius:24px;font:800 21px sans-serif;text-decoration:none}",
    "fullscreen loading CSS",
)

replace(
    "<body><div class='stage'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0&modestbranding=1' allow='autoplay; encrypted-media; picture-in-picture'></iframe><a class='back' href='c16://watch?id=${current.id}'>‹ 返回</a></div></body></html>",
    "<body><div class='stage'><div class='fullLoad' id='fullLoad'><div class='fullSpin'></div><strong style='font:800 24px sans-serif'>正在加载视频</strong></div><div id='fullPlayer'></div><a class='back' href='c16://watch?id=${current.id}'>‹ 返回</a></div><script>var fullFallback=setTimeout(function(){document.getElementById('fullLoad').classList.add('hide')},15000);function onYouTubeIframeAPIReady(){new YT.Player('fullPlayer',{videoId:'${current.id}',playerVars:{autoplay:1,playsinline:1,rel:0,fs:0,modestbranding:1},events:{onReady:function(e){try{e.target.playVideo()}catch(x){}},onStateChange:function(e){if(e.data===1){clearTimeout(fullFallback);setTimeout(function(){document.getElementById('fullLoad').classList.add('hide')},180)}}}})}</script><script src='https://www.youtube.com/iframe_api'></script></body></html>",
    "fullscreen loading HTML",
)

s = s.replace("C16 YouTube v2.6", "C16 YouTube v2.7")
s = s.replace("v2.6.40044", "v2.7.40045")

path.write_text(s, encoding="utf-8")
print("Applied C16 YouTube v2.7 gray-loading mask fix")
