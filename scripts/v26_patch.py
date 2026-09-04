from pathlib import Path

path = Path("app/src/main/java/com/c16/video/MainActivity.kt")
s = path.read_text(encoding="utf-8")


def replace(old: str, new: str, label: str):
    global s
    if old not in s:
        raise SystemExit(f"v2.6 patch failed: missing {label}")
    s = s.replace(old, new, 1)


replace(
    ".iconBtn{width:52px;height:52px;border-radius:26px;background:$panel;border:1px solid $border;display:flex;align-items:center;justify-content:center;font-size:23px}",
    ".iconBtn{width:46px;height:46px;border-radius:23px;background:$panel;border:1px solid $border;display:flex;align-items:center;justify-content:center;font-size:20px}",
    "top icon button CSS",
)

replace(
    ".playerPage{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:22px}",
    ".playerPage{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:18px}",
    "player page columns",
)

replace(
    ".playerBox{position:relative;aspect-ratio:16/9;border-radius:20px;overflow:hidden;background:#000;border:1px solid $border}",
    ".playerBox{position:relative;aspect-ratio:16/9;border-radius:20px;overflow:hidden;background:linear-gradient(135deg,#06131f 0%,#0b2438 48%,#101820 100%);border:1px solid $border;box-shadow:0 18px 42px rgba(0,0,0,.16)}",
    "player box CSS",
)

replace(
    ".playerBox iframe{width:100%;height:100%;border:0}",
    ".playerBox iframe{position:relative;z-index:1;width:100%;height:100%;border:0;background:transparent}",
    "player iframe CSS",
)

replace(
    ".quality{position:absolute;left:16px;top:16px;background:rgba(0,0,0,.64);color:#fff;padding:7px 10px;border-radius:10px;font-size:14px;font-weight:900}",
    ".quality{position:absolute;z-index:5;left:16px;top:16px;background:rgba(0,0,0,.64);color:#fff;padding:7px 10px;border-radius:10px;font-size:14px;font-weight:900}",
    "quality badge CSS",
)

replace(
    ".fullBtn{position:absolute;right:16px;bottom:16px;background:rgba(0,0,0,.74);color:#fff;border:1px solid rgba(255,255,255,.36);padding:10px 15px;border-radius:13px;font-size:19px;font-weight:800}",
    ".fullBtn{position:absolute;z-index:5;right:16px;bottom:16px;background:rgba(0,0,0,.74);color:#fff;border:1px solid rgba(255,255,255,.36);padding:10px 15px;border-radius:13px;font-size:19px;font-weight:800}",
    "fullscreen button CSS",
)

replace(
    ".pTitle{font-size:46px;font-weight:880;line-height:1.18;margin:18px 0 9px;letter-spacing:-.8px}",
    ".pTitle{font-size:36px;font-weight:860;line-height:1.22;margin:16px 0 8px;letter-spacing:-.55px}",
    "player title CSS",
)

replace(
    ".recommend{background:$panel;border:1px solid $border;border-radius:20px;padding:14px;align-self:start}",
    ".recommend{background:$panel;border:1px solid $border;border-radius:20px;padding:13px;align-self:start;max-height:calc(100vh - 132px);overflow:auto;scrollbar-width:none}.recommend::-webkit-scrollbar{display:none}",
    "recommendation panel CSS",
)

replace(
    ".rec{display:grid;grid-template-columns:128px 1fr;gap:10px;margin-bottom:13px}",
    ".rec{display:grid;grid-template-columns:118px 1fr;gap:9px;margin-bottom:12px}",
    "recommendation card columns",
)

replace(
    ".rec img{width:128px;aspect-ratio:16/9;object-fit:cover;border-radius:9px}",
    ".rec img{width:118px;aspect-ratio:16/9;object-fit:cover;border-radius:9px}",
    "recommendation thumbnail CSS",
)

replace(
    ".settings{max-width:1000px}",
    ".videoLoading{position:absolute;z-index:4;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;color:#fff;background:radial-gradient(circle at 50% 45%,rgba(36,86,120,.68) 0%,rgba(10,34,52,.95) 42%,rgba(5,16,27,.99) 100%);transition:opacity .35s ease}.videoLoading.hide{opacity:0;pointer-events:none}.videoLoading .spinner{width:54px;height:54px;border-radius:50%;border:4px solid rgba(255,255,255,.28);border-top-color:#ff0033;animation:c16spin .85s linear infinite}.videoLoading strong{font-size:22px;letter-spacing:.3px}.videoLoading span{font-size:15px;color:rgba(255,255,255,.72)}@keyframes c16spin{to{transform:rotate(360deg)}}.app.hideSide{grid-template-columns:0 1fr}.app.hideSide .sidebar{display:none}.playerPage.hideRec{grid-template-columns:minmax(0,1fr)}.playerPage.hideRec .recommend{display:none}.settings{max-width:1000px}",
    "v2.6 loading and cinema CSS insertion",
)

replace(
    "@media(max-width:1250px){.app{grid-template-columns:220px 1fr}.videoGrid{grid-template-columns:repeat(4,1fr)}.playerPage{grid-template-columns:minmax(0,1fr) 330px}.pTitle{font-size:40px}}",
    "@media(max-width:1250px){.app{grid-template-columns:220px 1fr}.videoGrid{grid-template-columns:repeat(4,1fr)}.playerPage{grid-template-columns:minmax(0,1fr) 300px}.pTitle{font-size:34px}}",
    "small-screen media query",
)

replace(
    "function startQr(){var c=document.getElementById('client').value.trim();location.href='c16://startQr?client='+encodeURIComponent(c)}</script>",
    "function startQr(){var c=document.getElementById('client').value.trim();location.href='c16://startQr?client='+encodeURIComponent(c)}function hideVideoLoading(){setTimeout(function(){var e=document.getElementById('videoLoading');if(e)e.classList.add('hide')},1100)}function toggleSide(){var a=document.querySelector('.app');if(a)a.classList.toggle('hideSide')}function toggleRec(){var p=document.querySelector('.playerPage');if(p)p.classList.toggle('hideRec')}</script>",
    "v2.6 playback Javascript",
)

replace(
    "<div class='playerBox'><iframe src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0&modestbranding=1' allow='autoplay; encrypted-media; picture-in-picture'></iframe><span class='quality'>4K · HDR</span>",
    "<div class='playerBox'><div class='videoLoading' id='videoLoading'><div class='spinner'></div><strong>正在加载视频</strong><span>正在准备 YouTube 播放器…</span></div><iframe onload='hideVideoLoading()' src='https://www.youtube.com/embed/${current.id}?autoplay=1&playsinline=1&rel=0&fs=0&modestbranding=1' allow='autoplay; encrypted-media; picture-in-picture'></iframe><span class='quality'>4K · HDR</span>",
    "player loading overlay HTML",
)

replace(
    "<span class='action'>⋯ 更多</span>$loginHint</div>",
    "<span class='action'>⋯ 更多</span><a class='action' href='javascript:toggleSide()'>☰ 左栏</a><a class='action' href='javascript:toggleRec()'>▥ 推荐</a>$loginHint</div>",
    "player hide/show controls",
)

s = s.replace("C16 YouTube v2.5", "C16 YouTube v2.6")
s = s.replace("v2.5.40043", "v2.6.40044")

path.write_text(s, encoding="utf-8")
print("Applied C16 YouTube v2.6 playback UI patch")
