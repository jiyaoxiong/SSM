from pathlib import Path
p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V5.7: clean production home. Playback core stays untouched.
# Remove developer/account sync banners from the home body only.
s=s.replace('''        return """$syncLine<div class='chips'>''','''        return """<div class='chips'>''',1)

# Home history must be real history only; no demo fallback is introduced.
# Make all home rails larger and easier to browse on the 14.6-inch C16 display.
css=r'''
/* V5.7 clean C16 home */
#homeRoot .homeSync{display:none!important}
#homeRoot .rail{grid-auto-columns:calc((100% - 48px)/4)!important;gap:16px!important;padding-bottom:12px!important}
#homeRoot .ctitle{height:60px!important;font-size:19px!important;line-height:1.38!important}
#homeRoot .cmeta{font-size:15px!important;line-height:1.45!important}
#homeRoot .heroCopy h1{font-size:38px!important;line-height:1.10!important;max-width:96%!important}
#homeRoot .heroCopy p{font-size:17px!important}
#homeRoot .arrow{width:58px!important;height:58px!important;right:8px!important;background:rgba(255,255,255,.94)!important;box-shadow:0 8px 24px rgba(0,0,0,.22)!important}
#homeRoot .section{margin-top:32px!important}
#homeRoot .sectionHead h2{font-size:30px!important}
#homeRoot .sectionHead span{font-size:16px!important}
@media(max-width:1700px){#homeRoot .rail{grid-auto-columns:calc((100% - 32px)/3)!important}}
'''
if 'V5.7 clean C16 home' not in s:s=s.replace('</style>',css+'</style>',1)

s=s.replace('C16 YouTube · V5.6','C16 YouTube · V5.7')
s=s.replace('"应用版本" to "5.6.40073"','"应用版本" to "5.7.40074"')
p.write_text(s,encoding='utf-8')
print('Applied V5.7 clean home, four-card rails, taller titles and smaller hero heading')
