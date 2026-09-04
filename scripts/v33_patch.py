from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# v3.3: fixed category order
s=s.replace('音乐、旅行、科技、汽车、电影、哲学','音乐、旅行、科技AI、汽车、电影、哲学')

# Hide endless recommendation scroll area and use fixed recommendation list.
s=s.replace('overflow:auto;scrollbar-width:none','overflow:hidden;scrollbar-width:none')
s=s.replace('max-height:calc(100vh - 132px);','height:calc(100vh - 160px);')

# Version label
s=s.replace('C16 YouTube v3.2','C16 YouTube v3.3')
s=s.replace('v3.2.40050','v3.3.40051')

p.write_text(s,encoding='utf-8')
print('Applied C16 YouTube v3.3 recommendation/category patch')
