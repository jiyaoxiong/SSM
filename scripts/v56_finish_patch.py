from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# Final V5.6 visual balance requested after V5.5: keep player engine untouched.
css=r'''
/* V5.6 final player typography balance. */
.pTitle{font-size:35px!important;line-height:1.20!important;font-weight:760!important;max-width:95%!important}
.recommend .rec b,.recommend .recTitle{font-size:18px!important;line-height:1.32!important;font-weight:680!important}
.recommend .rec span,.recommend .recMeta{font-size:16px!important;line-height:1.45!important}
.recTabButton{font-size:16px!important;padding:10px 14px!important}
@media(max-width:1500px){.pTitle{font-size:32px!important}.recommend .rec b,.recommend .recTitle{font-size:17px!important}.recommend .rec span,.recommend .recMeta{font-size:15px!important}}
'''
if 'V5.6 final player typography balance' not in s:
    if '</style>' not in s: raise SystemExit('v5.6 finish style anchor missing')
    s=s.replace('</style>',css+'</style>',1)

p.write_text(s,encoding='utf-8')
print('Applied V5.6 final player title/recommendation typography balance')
