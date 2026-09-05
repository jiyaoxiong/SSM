from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V5.5 is visual-only. Use the last pre-WebView-rework V4.2 C16 UI as the reference.
# Do not touch IFrame Player API, Media Integrity, WebView settings, OAuth or pagination logic.
s=s.replace('val sideW=if(c)"104px" else "260px"','val sideW=if(c)"124px" else "260px"',1)

css=r'''
/* V5.5 visual baseline = V4.2 C16 14.6-inch large-screen UI. */
html,body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC','PingFang SC','Microsoft YaHei',Arial,sans-serif!important;font-size:18px!important}
.main{grid-template-rows:90px 1fr!important}.top{padding:14px 28px!important;gap:12px!important}.content{padding:22px 30px 84px!important}
.sidebar{padding:18px 12px!important}.brand{height:66px!important;margin-bottom:16px!important}.ytLogo{width:56px!important;height:38px!important;border-radius:11px!important;font-size:20px!important}.brand strong{font-size:31px!important}
.nav{height:68px!important;border-radius:18px!important;margin:4px 0!important;font-size:21px!important;gap:16px!important}.navIcon,.navIcon svg{width:36px!important;height:36px!important}.nav b{font-size:21px!important;font-weight:680!important}.collapse{width:42px!important;height:78px!important;font-size:34px!important}
.search{height:56px!important;max-width:900px!important;border-radius:29px!important;padding:0 18px!important}.search input{font-size:20px!important}.search button{font-size:23px!important}.pill{height:50px!important;border-radius:25px!important;padding:0 18px!important;font-size:18px!important;font-weight:750!important}.round{width:50px!important;height:50px!important;font-size:22px!important}
.chips{gap:10px!important;margin-bottom:18px!important}.chip{padding:10px 18px!important;border-radius:20px!important;font-size:17px!important;font-weight:720!important}
.hero{height:312px!important;border-radius:27px!important}.heroCopy{left:40px!important;top:28px!important;width:46%!important}.heroCopy h1{font-size:44px!important;line-height:1.06!important;margin:10px 0 12px!important}.heroCopy p{font-size:18px!important}.btn{font-size:18px!important;padding:11px 20px!important}
.section{margin-top:30px!important}.sectionHead{margin-bottom:15px!important}.sectionHead h2{font-size:31px!important;font-weight:720!important}.sectionHead span{font-size:16px!important}.ctitle{font-size:19px!important;font-weight:720!important;line-height:1.32!important;height:52px!important;margin-top:9px!important}.cmeta{font-size:15px!important;line-height:1.45!important}.grid{gap:28px 20px!important}
.pTitle{font-size:40px!important;font-weight:800!important;line-height:1.18!important;margin:16px 0 8px!important;max-width:95%!important}.pMeta{font-size:18px!important}.channel{gap:14px!important;padding:17px 0!important}.avatar{width:62px!important;height:62px!important}.channelText b{font-size:25px!important;font-weight:720!important}.channelText span{font-size:16px!important}.subscribe{font-size:18px!important;padding:12px 22px!important}.actions{gap:9px!important;margin-top:14px!important}.action{font-size:17px!important;padding:10px 16px!important}
.playerLayout{grid-template-columns:minmax(0,2.35fr) minmax(470px,1fr)!important;gap:22px!important}.recommend{padding:16px!important;border-radius:22px!important;max-height:calc(100vh - 116px)!important}.recTabs{padding:4px 0 12px!important}.tab{font-size:15px!important;padding:9px 13px!important}.rec{grid-template-columns:190px minmax(0,1fr)!important;gap:14px!important;margin-bottom:14px!important;padding:5px 0!important}.rec img{width:190px!important}.rec b,.recTitle{font-size:20px!important;line-height:1.28!important;font-weight:700!important}.rec span,.recMeta{font-size:14px!important;line-height:1.38!important}.comments{padding:22px!important;border-radius:18px!important}.comments h2{font-size:27px!important}.comment b{font-size:16px!important}.comment p{font-size:16px!important;line-height:1.55!important}.commentStats52{font-size:14px!important}
.simple{padding:32px!important}.simple h1{font-size:36px!important}.simple p{font-size:20px!important}.channelHero50 h1,.channelVideoHead54 h1,.subTop53 h1{font-size:34px!important}.channelHero50 p,.channelVideoHead54 p,.subTop53 p{font-size:16px!important}.channelTab51,.subButton51{font-size:17px!important;padding:10px 17px!important}.subCard53{min-height:122px!important;padding:17px!important}.subAvatar53{width:82px!important;height:82px!important;min-width:82px!important}.subInfo53 b{font-size:18px!important}.subInfo53 span{font-size:14px!important}.subCount53{font-size:16px!important}.more54{height:54px!important;min-width:210px!important;font-size:18px!important}.loaded54,.collectionNote54{font-size:16px!important}.accountPill51 span{font-size:17px!important}
@media(max-width:1500px){.playerLayout{grid-template-columns:minmax(0,2fr) minmax(410px,1fr)!important}.rec{grid-template-columns:160px minmax(0,1fr)!important}.rec img{width:160px!important}.rec b,.recTitle{font-size:18px!important}.grid{grid-template-columns:repeat(3,minmax(0,1fr))!important}}
'''
if 'V5.5 visual baseline = V4.2' not in s:
    if '</style>' not in s: raise SystemExit('v5.5 style anchor missing')
    s=s.replace('</style>',css+'</style>',1)

s=s.replace('C16 YouTube · V5.4','C16 YouTube · V5.5')
s=s.replace('"应用版本" to "5.4.40071"','"应用版本" to "5.5.40072"')

p.write_text(s,encoding='utf-8')
print('Applied V5.5 V4.2-reference large fonts, larger sidebar controls and C16 visual proportions')
