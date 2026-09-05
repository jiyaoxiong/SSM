from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V5.9: account/library dashboard + cleaner drive mode + grouped settings.
# Keep the proven V4.8+ WebView/IFrame/Media Integrity playback core untouched.

# Routes.
route_anchor='''"home"->showHome();'''
if route_anchor not in s: raise SystemExit('v5.9 home route anchor missing')
s=s.replace(route_anchor,'''"home"->showHome();"library59"->showLibrary59();"drive59"->showDrive59();"settings59"->showSettings59();''',1)

# Top account pill becomes the entry to the new account/library center.
s=s.replace("<a class='pill accountPill51' href='c16://login'>${accountPill51()}</a>","<a class='pill accountPill51' href='c16://library59'>${accountPill51()}</a>",1)

# Sidebar keeps all V5.8 shortcuts, but Driving Mode / Settings now open the V5.9 pages.
s=s.replace('''${nav("drive","drive","驾驶模式","drivehome")}''','''${nav("drive","drive","驾驶模式","drive59")}''',1)
s=s.replace('''${nav("settings","settings","设置","settings")}''','''${nav("settings","settings","设置","settings59")}''',1)

css=r'''
/* V5.9 account center / drive mode / settings */
.myHero59{display:grid;grid-template-columns:112px minmax(0,1fr) auto;gap:24px;align-items:center;padding:26px 28px;border-radius:26px;background:$panel;border:1px solid $border;margin-bottom:24px}.myHero59 img,.myAvatar59{width:112px;height:112px;border-radius:50%;object-fit:cover;background:linear-gradient(135deg,#2d7dff,#9c4cff)}.myHero59 h1{font-size:34px;margin:0 0 7px}.myHero59 p{font-size:16px;color:$sub;margin:0}.myBadge59{padding:9px 14px;border-radius:18px;background:$p2;font-size:15px;font-weight:700}.myGrid59{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.myTile59{min-height:142px;padding:20px 22px;border-radius:22px;background:$panel;border:1px solid $border;display:flex;flex-direction:column;justify-content:space-between}.myTile59 b{font-size:24px}.myTile59 span{font-size:15px;color:$sub}.myTile59 strong{font-size:28px;font-weight:760}.settingsGroup59{margin-bottom:24px}.settingsGroup59 h2{font-size:27px;margin:0 0 12px}.settingsGrid59{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.settingCard59{min-height:92px;padding:18px 20px;border-radius:20px;background:$panel;border:1px solid $border;display:flex;align-items:center;justify-content:space-between;gap:16px}.settingCard59 b{font-size:19px}.settingCard59 span{font-size:14px;color:$sub}.driveHero59{min-height:260px;padding:30px 32px;border-radius:28px;background:linear-gradient(120deg,#07131f,#163a5b);color:white;display:grid;grid-template-columns:1fr auto;align-items:end;gap:24px}.driveHero59 h1{font-size:42px;line-height:1.08;margin:8px 0}.driveHero59 p{font-size:17px;color:#d5e6f5;margin:0}.driveMain59{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:18px}.driveCard59{min-height:160px;padding:22px;border-radius:24px;background:$panel;border:1px solid $border;display:flex;flex-direction:column;justify-content:space-between}.driveCard59 b{font-size:26px}.driveCard59 span{font-size:15px;color:$sub}.drivePlay59{display:inline-flex;align-items:center;justify-content:center;min-width:190px;height:58px;padding:0 24px;border-radius:29px;background:white;color:#111;font-size:19px;font-weight:800}.drive59 .rail{grid-auto-columns:calc((100% - 32px)/3)!important}.drive59 .ctitle{font-size:19px!important;height:56px!important}.drive59 .cmeta{font-size:15px!important}
@media(max-width:1600px){.myGrid59,.driveMain59{grid-template-columns:repeat(2,minmax(0,1fr))}.settingsGrid59{grid-template-columns:1fr}}
'''
if 'V5.9 account center / drive mode / settings' not in s:
    if '</style>' not in s: raise SystemExit('v5.9 style anchor missing')
    s=s.replace('</style>',css+'</style>',1)

marker='''    private fun accountPill51():String{'''
methods=r'''    private fun showLibrary59(){
        currentVideoId=null
        val signed=prefs.getString("access_token","").orEmpty().isNotBlank()
        val title=prefs.getString("account_title",if(signed)"YouTube 账号" else "我的媒体库").orEmpty().ifBlank{if(signed)"YouTube 账号" else "我的媒体库"}
        val avatar=prefs.getString("account_avatar","").orEmpty()
        val history=historyVideos()
        val favCount=prefs.getStringSet("favorites",emptySet()).orEmpty().size
        val laterCount=watchLaterIds().size
        val avatarHtml=if(avatar.isBlank())"<div class='myAvatar59'></div>" else "<img src='${esc(avatar)}'>"
        val action=if(signed)"<a class='chip' href='c16://login'>账号管理</a>" else "<a class='chip' href='c16://login'>登录 YouTube</a>"
        val hero="<div class='myHero59'>$avatarHtml<div><h1>${esc(title)}</h1><p>${if(signed)"YouTube 账号内容 + C16 本地媒体库" else "C16 本地观看记录、收藏与稍后观看"}</p></div>$action</div>"
        val tiles="<div class='myGrid59'><a class='myTile59' href='c16://history'><b>历史记录</b><strong>${history.size}</strong><span>这台 C16 的真实观看记录</span></a><a class='myTile59' href='c16://favorites'><b>我的收藏</b><strong>$favCount</strong><span>本地保存的视频</span></a><a class='myTile59' href='c16://watchlater'><b>稍后观看</b><strong>$laterCount</strong><span>待观看列表</span></a><a class='myTile59' href='c16://subscriptions'><b>订阅频道</b><strong>›</strong><span>全部订阅频道</span></a><a class='myTile59' href='c16://likes'><b>点赞视频</b><strong>›</strong><span>YouTube 账号点赞内容</span></a><a class='myTile59' href='c16://playlists'><b>播放列表</b><strong>›</strong><span>YouTube 播放列表</span></a></div>"
        val recent=if(history.isEmpty())"<div class='section'><div class='simple'><h1>还没有观看记录</h1><p>开始播放视频后，最近观看会显示在这里。</p></div></div>" else rail("最近观看","左右滑动查看更多",history.take(30))
        load(shell("",hero+tiles+recent+"<div style='height:40px'></div>"))
    }
    private fun showDrive59(){
        currentVideoId=null
        val history=historyVideos()
        val next=history.firstOrNull()?:homeSubscriptionFeed.firstOrNull()?:videos.first()
        val hero="<div class='driveHero59'><div><small style='letter-spacing:3px;font-weight:800;color:#72c7ff'>C16 DRIVE</small><h1>${if(history.isEmpty())"大屏娱乐中心" else "继续上次播放"}</h1><p>${esc(next.title)} · ${esc(next.channel)}</p></div><a class='drivePlay59' href='c16://watch?id=${Uri.encode(next.id)}'>▶ ${if(history.isEmpty())"开始播放" else "继续播放"}</a></div>"
        val cards="<div class='driveMain59'><a class='driveCard59' href='c16://category?name=音乐'><b>音乐</b><span>车内氛围与热门音乐</span></a><a class='driveCard59' href='c16://history'><b>最近播放</b><span>${history.size} 个观看记录</span></a><a class='driveCard59' href='c16://watchlater'><b>稍后观看</b><span>${watchLaterIds().size} 个待看视频</span></a><a class='driveCard59' href='c16://favorites'><b>收藏</b><span>${prefs.getStringSet("favorites",emptySet()).orEmpty().size} 个收藏</span></a><a class='driveCard59' href='c16://subscriptions'><b>订阅</b><span>浏览订阅频道</span></a><a class='driveCard59' href='c16://home'><b>标准首页</b><span>返回完整 YouTube 首页</span></a></div>"
        val recent=if(history.isEmpty())"" else "<div class='drive59'>${rail("继续观看","驾驶模式快捷入口",history.take(18))}</div>"
        load(shell("drive",hero+cards+recent+"<div style='height:40px'></div>"))
    }
    private fun showSettings59(){
        currentVideoId=null
        val signed=prefs.getString("access_token","").orEmpty().isNotBlank()
        val mode=prefs.getString("player_mode","auto").orEmpty()
        val interfaceGroup="<div class='settingsGroup59'><h2>界面</h2><div class='settingsGrid59'><a class='settingCard59' href='c16://theme'><div><b>${if(dark)"浅色模式" else "深色模式"}</b><span>切换车机界面主题</span></div><strong>›</strong></a><a class='settingCard59' href='c16://home'><div><b>返回首页</b><span>标准 C16 大屏首页</span></div><strong>›</strong></a></div></div>"
        val playerGroup="<div class='settingsGroup59'><h2>播放</h2><div class='settingsGrid59'><a class='settingCard59' href='c16://playermode?mode=${if(mode=="web")"auto" else "web"}'><div><b>播放模式：${if(mode=="web")"YouTube 网页" else "自动嵌入"}</b><span>播放器稳定时建议保持自动嵌入</span></div><strong>›</strong></a><a class='settingCard59' href='c16://diagnostics'><div><b>播放诊断</b><span>查看 WebView / Media Integrity 环境</span></div><strong>›</strong></a></div></div>"
        val accountGroup="<div class='settingsGroup59'><h2>账号与媒体库</h2><div class='settingsGrid59'><a class='settingCard59' href='c16://library59'><div><b>我的媒体库</b><span>历史、收藏、稍后观看、订阅与播放列表</span></div><strong>›</strong></a><a class='settingCard59' href='c16://login'><div><b>${if(signed)"YouTube 账号管理" else "登录 YouTube"}</b><span>${if(signed)"查看账号并可退出登录" else "使用手机完成设备授权"}</span></div><strong>›</strong></a></div></div>"
        load(shell("settings", "<div class='sectionHead'><h2>设置</h2><span>C16 YouTube · V5.9</span></div>"+interfaceGroup+playerGroup+accountGroup+"<div style='height:40px'></div>"))
    }
'''
if marker not in s: raise SystemExit('v5.9 helper anchor missing')
s=s.replace(marker,methods+marker,1)

s=s.replace('C16 YouTube · V5.8','C16 YouTube · V5.9')
s=s.replace('"应用版本" to "5.8.40075"','"应用版本" to "5.9.40076"')

p.write_text(s,encoding='utf-8')
print('Applied V5.9 account/library dashboard, drive mode and grouped settings; playback core untouched')
