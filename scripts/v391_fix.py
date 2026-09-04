from pathlib import Path

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

bad = '"scope" to "https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.force-ssl"'
good = '"scope" to "https://www.googleapis.com/auth/youtube"'
if bad not in s:
    raise SystemExit('v3.9.1 fix failed: combined device-flow scope not found')
s = s.replace(bad, good, 1)

# Google TV / limited-input device flow only accepts a restricted scope set.
# Keep the broad YouTube account scope, which is supported by device flow and is used
# by the app for account/subscribe/comment reads after re-authorization.
s = s.replace('C16 YouTube v3.9', 'C16 YouTube v3.9.1')
s = s.replace('v3.9.40055', 'v3.9.1.40056')

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v3.9.1 device-flow scope compatibility fix')
