from pathlib import Path

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

# V4.1 focuses on the real C16 14.6-inch landscape layout: compact/collapsible
# navigation, five-card content rails, a calmer hero, and a more balanced player.
css = r'''.app{grid-template-columns:124px 1fr!important;transition:grid-template-columns .22s ease}.sidebar{padding:18px 12px!important}.brand{justify-content:center!important;margin-bottom:16px!important}.brand strong{display:none!important}.ytLogo{width:52px!important;height:36px!important}.nav{height:62px!important;justify-content:center!important;padding:0!important;gap:0!important}.nav b{display:none!important}.navIcon{width:36px!important;height:36px!important}.sideToggleV41{height:52px;border:1px solid $border;background:$panel;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:29px;font-weight:800;margin-top:10px}.app.sideWideV41{grid-template-columns:260px 1fr!important}.app.sideWideV41 .sidebar{padding:24px 20px!important}.app.sideWideV41 .brand{justify-content:flex-start!important}.app.sideWideV41 .brand strong{display:block!important}.app.sideWideV41 .nav{justify-content:flex-start!important;padding:0 18px!important;gap:16px!important}.app.sideWideV41 .nav b{display:block!important}.app.sideWideV41 .sideToggleV41{justify-content:flex-end;padding-right:18px}.homeRailV40{gap:16px!important;padding-right:58px!important}.homeRailV40 .card{flex:0 0 calc((100% - 64px)/5)!important;min-width:220px!important}.homeRailV40 .ctitle{font-size:18px!important;min-height:49px!important}.homeRailV40 .cmeta{font-size:14px!important}.homeRailArrowV40{width:56px!important;height:56px!important;font-size:38px!important;right:4px!important}.hero{height:312px!important}.heroCopy{width:46%!important;top:28px!important}.hero h1{font-size:44px!important;line-height:1.06!important;max-width:720px}.hero p{font-size:18px!important}.driveHero{min-height:300px!important;background:linear-gradient(125deg,#07131f,#0f2e4a)!important}.driveHeroText{max-width:820px!important}.driveHeroText h1{font-size:50px!important}.driveGrid{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:14px!important}.driveTile{min-height:190px!important}.driveTile b{font-size:28px!important}.driveTile span{font-size:16px!important}.app.hideSide .playerPage{grid-template-columns:minmax(0,2.6fr) minmax(430px,.92fr)!important;gap:20px!important}.app.hideSide .recommend{padding:16px!important}.app.hideSide .rec{grid-template-columns:184px minmax(0,1fr)!important;gap:14px!important}.app.hideSide .rec img{width:184px!important}.app.hideSide .recTitle{font-size:19px!important;line-height:1.3!important}.app.hideSide .recMeta{font-size:14px!important}.app.hideSide .pTitle{font-size:41px!important}.app.hideSide .top{padding-left:24px!important;padding-right:24px!important}@media(max-width:1500px){.homeRailV40 .card{flex-basis:calc((100% - 48px)/4)!important;min-width:230px!important}.driveGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}.app.hideSide .playerPage{grid-template-columns:minmax(0,2.25fr) minmax(390px,1fr)!important}.app.hideSide .rec{grid-template-columns:158px minmax(0,1fr)!important}.app.hideSide .rec img{width:158px!important}}'''
if '.sideToggleV41{' not in s:
    s = s.replace('</style><script>', css + '</style><script>', 1)

# Sidebar toggle. Persist the user's choice locally, while playback still uses the
# existing full-width hideSide mode.
js = """function applySideV41(){try{var a=document.querySelector('.app');if(!a)return;if(localStorage.getItem('c16_side_wide')==='1')a.classList.add('sideWideV41');else a.classList.remove('sideWideV41')}catch(e){}}function toggleSideV41(){try{var a=document.querySelector('.app');if(!a)return;var wide=a.classList.toggle('sideWideV41');localStorage.setItem('c16_side_wide',wide?'1':'0')}catch(e){}}setTimeout(applySideV41,0);"""
if 'function toggleSideV41()' not in s:
    s = s.replace('</script></head>', js + '</script></head>', 1)

# Add the compact-side expansion control at the bottom of the sidebar.
if 'sideToggleV41' in s and "href='javascript:toggleSideV41()'" not in s:
    s = s.replace("<div style='flex:1'></div></aside>", "<div style='flex:1'></div><a class='sideToggleV41' href='javascript:toggleSideV41()' title='展开或收起侧栏'>›</a></aside>", 1)

# Keep the home hero readable from the driver's/passenger's viewing distance.
if 'private fun compactHeroTitleV41' not in s:
    marker = '    private fun homeRailHtmlV40('
    helper = '''    private fun compactHeroTitleV41(title: String): String {\n        val clean = title.replace("\\n", " ").replace(Regex("\\\\s+"), " ").trim()\n        return if (clean.length > 30) clean.take(30).trimEnd() + "…" else clean\n    }\n\n'''
    if marker in s:
        s = s.replace(marker, helper + marker, 1)
s = s.replace('heroSource.title.take(42)', 'compactHeroTitleV41(heroSource.title)', 1)

# Make the existing driving page feel like the C16 entertainment home rather than a
# generic collection of links. It intentionally does not fake vehicle battery/range data.
s = s.replace('DRIVING MODE', 'C16 LARGE SCREEN', 1)
s = s.replace('更少操作，更多内容。', 'C16 大屏娱乐中心', 1)
s = s.replace('为 C16 横屏和行车场景优化的大按钮入口。选择一个主题即可开始浏览。', '为 14.6 英寸横屏优化的大按钮入口。视频、AI、音乐和旅行内容，一次点击即可进入。', 1)
s = s.replace('<b>汽车资讯</b><span>新能源 · 智能驾驶 · 车型体验</span>', '<b>视频中心</b><span>汽车 · 新能源 · 智能驾驶</span>', 1)
s = s.replace('<b>AI 每日精选</b><span>人工智能 · 芯片 · 数码科技</span>', '<b>AI 科技</b><span>人工智能 · 芯片 · 数码科技</span>', 1)
s = s.replace('<b>精选音乐</b><span>让旅途更有节奏</span>', '<b>音乐中心</b><span>热门音乐 · 长时混音 · 驾乘氛围</span>', 1)
s = s.replace('<b>世界旅行</b><span>风景 · 4K · 纪录片</span>', '<b>旅行影院</b><span>风景 · 4K · 纪录片</span>', 1)

# Visible version labels in settings/login/help areas created by previous patches.
s = s.replace('C16 YouTube v4.0', 'C16 YouTube v4.1')
s = s.replace('v4.0.40057', 'v4.1.40058')

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v4.1 compact sidebar, five-card rails and C16 large-screen player UI')
