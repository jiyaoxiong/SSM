from pathlib import Path

path = Path("app/src/main/java/com/c16/video/MainActivity.kt")
s = path.read_text(encoding="utf-8")


def replace(old: str, new: str, label: str):
    global s
    if old not in s:
        raise SystemExit(f"v2.8 patch failed: missing {label}")
    s = s.replace(old, new, 1)

# Cleaner, consistent line icons for the left navigation.
old_nav = '''        fun nav(id: String, icon: String, label: String, host: String) =
            "<a class='nav ${if (active == id) \"on\" else \"\"}' href='c16://$host'><span class='navIcon'>$icon</span><b>$label</b></a>"'''
new_nav = '''        fun nav(id: String, icon: String, label: String, host: String): String {
            val svg = when (id) {
                "home" -> "<svg viewBox='0 0 24 24'><path d='M3.5 11.2 12 4l8.5 7.2v8.3a1 1 0 0 1-1 1h-5.2v-6h-4.6v6H4.5a1 1 0 0 1-1-1z'/></svg>"
                "search" -> "<svg viewBox='0 0 24 24'><circle cx='10.8' cy='10.8' r='6.2'/><path d='m15.4 15.4 5 5'/></svg>"
                "subs" -> "<svg viewBox='0 0 24 24'><rect x='4' y='6' width='16' height='13' rx='2.2'/><path d='M9.5 10 15 12.5 9.5 15z'/></svg>"
                "history" -> "<svg viewBox='0 0 24 24'><circle cx='12' cy='12' r='8.2'/><path d='M12 7.5V12l3.3 2'/></svg>"
                "favorites" -> "<svg viewBox='0 0 24 24'><path d='M12 20s-7-4.7-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.3-7 10-7 10z'/></svg>"
                "local" -> "<svg viewBox='0 0 24 24'><rect x='4' y='5' width='16' height='14' rx='2'/><path d='m10 9 5 3-5 3z'/></svg>"
                else -> "<svg viewBox='0 0 24 24'><circle cx='12' cy='12' r='3'/><path d='M12 3.5v2M12 18.5v2M3.5 12h2M18.5 12h2M6 6l1.4 1.4M16.6 16.6 18 18M18 6l-1.4 1.4M7.4 16.6 6 18'/></svg>"
            }
            return "<a class='nav ${if (active == id) \"on\" else \"\"}' href='c16://$host'><span class='navIcon'>$svg</span><b>$label</b></a>"
        }'''
replace(old_nav, new_nav, "nav helper")

replace(
    ".navIcon{width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-size:22px}",
    ".navIcon{width:30px;height:30px;display:flex;align-items:center;justify-content:center}.navIcon svg{width:25px;height:25px;fill:none;stroke:currentColor;stroke-width:1.85;stroke-linecap:round;stroke-linejoin:round}.navIcon svg path[d*='M9.5 10'],.navIcon svg path[d*='m10 9']{fill:currentColor;stroke:none}",
    "nav icon CSS",
)

# Account chip: show avatar and channel title after phone authorization.
replace(
    "        val accountText = if (prefs.getString(\"access_token\", \"\").orEmpty().isNotBlank()) \"已登录\" else \"登录\"",
    "        val signedIn = prefs.getString(\"access_token\", \"\").orEmpty().isNotBlank()\n        val accountText = if (signedIn) prefs.getString(\"channel_title\", \"\").orEmpty().ifBlank { \"已登录\" } else \"登录\"\n        val accountAvatar = if (signedIn) prefs.getString(\"channel_avatar\", \"\").orEmpty() else \"\"",
    "account text variables",
)

replace(
    ".pill{height:52px;border-radius:26px;background:$panel;border:1px solid $border;padding:0 19px;display:flex;align-items:center;justify-content:center;font-size:19px;font-weight:800}",
    ".pill{height:52px;max-width:220px;border-radius:26px;background:$panel;border:1px solid $border;padding:0 15px;display:flex;align-items:center;justify-content:center;gap:9px;font-size:18px;font-weight:800;white-space:nowrap;overflow:hidden}.accountAvatar{width:34px;height:34px;border-radius:50%;object-fit:cover;flex:0 0 auto}.accountName{overflow:hidden;text-overflow:ellipsis}",
    "account pill CSS",
)

replace(
    "<a class='pill' href='c16://login'>◉ $accountText</a>",
    "<a class='pill' href='c16://login'>${if (accountAvatar.isNotBlank()) \"<img class='accountAvatar' src='${escAttr(accountAvatar)}'>\" else \"◉\"}<span class='accountName'>${esc(accountText)}</span></a>",
    "account pill HTML",
)

# One-tap cinema mode: hide sidebar, top bar and recommendations, while keeping
# the separate left/right toggles already added in v2.6.
replace(
    ".app.hideSide{grid-template-columns:0 1fr}.app.hideSide .sidebar{display:none}.playerPage.hideRec{grid-template-columns:minmax(0,1fr)}.playerPage.hideRec .recommend{display:none}.settings{max-width:1000px}",
    ".app.hideSide{grid-template-columns:0 1fr}.app.hideSide .sidebar{display:none}.playerPage.hideRec{grid-template-columns:minmax(0,1fr)}.playerPage.hideRec .recommend{display:none}.app.cinema{grid-template-columns:0 1fr}.app.cinema .sidebar{display:none}.app.cinema .main{grid-template-rows:0 1fr}.app.cinema .top{display:none}.app.cinema .content{padding:12px 16px 30px}.app.cinema .playerPage{grid-template-columns:minmax(0,1fr)}.app.cinema .recommend{display:none}.app.cinema .playerBox{border-radius:16px}.settings{max-width:1000px}",
    "cinema CSS",
)

replace(
    "function toggleSide(){var a=document.querySelector('.app');if(a)a.classList.toggle('hideSide')}function toggleRec(){var p=document.querySelector('.playerPage');if(p)p.classList.toggle('hideRec')}</script>",
    "function toggleSide(){var a=document.querySelector('.app');if(a)a.classList.toggle('hideSide')}function toggleRec(){var p=document.querySelector('.playerPage');if(p)p.classList.toggle('hideRec')}function toggleCinema(){var a=document.querySelector('.app');if(a)a.classList.toggle('cinema')}</script>",
    "cinema javascript",
)

replace(
    "<a class='action' href='javascript:toggleRec()'>▥ 推荐</a>$loginHint</div>",
    "<a class='action' href='javascript:toggleRec()'>▥ 推荐</a><a class='action' href='javascript:toggleCinema()'>▣ 影院模式</a>$loginHint</div>",
    "cinema action",
)

# Load the authorized YouTube channel profile so the login state feels like a
# real account rather than a generic token flag.
insert_before = '''    private fun postForm(url: String, params: Map<String, String>): Pair<Int, String> {'''
profile_func = '''    private fun fetchAccountProfile() {
        val token = prefs.getString("access_token", "").orEmpty()
        if (token.isBlank()) return
        try {
            val u = URL("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true&maxResults=1")
            val c = (u.openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = 12000
                readTimeout = 12000
                setRequestProperty("Authorization", "Bearer $token")
            }
            val text = readResponse(c)
            if (c.responseCode in 200..299) {
                val items = JSONObject(text).optJSONArray("items")
                if (items != null && items.length() > 0) {
                    val snippet = items.getJSONObject(0).optJSONObject("snippet")
                    val title = snippet?.optString("title", "").orEmpty()
                    val thumbs = snippet?.optJSONObject("thumbnails")
                    val avatar = thumbs?.optJSONObject("default")?.optString("url", "").orEmpty()
                    prefs.edit().putString("channel_title", title).putString("channel_avatar", avatar).apply()
                }
            }
        } catch (_: Exception) { }
    }

'''
if insert_before not in s:
    raise SystemExit("v2.8 patch failed: missing postForm insertion point")
s = s.replace(insert_before, profile_func + insert_before, 1)

replace(
    '''                        loginPolling.set(false)
                        main.post {
                            Toast.makeText(this@MainActivity, "YouTube 手机授权成功", Toast.LENGTH_LONG).show()
                            showHome()
                        }''',
    '''                        loginPolling.set(false)
                        fetchAccountProfile()
                        main.post {
                            Toast.makeText(this@MainActivity, "YouTube 手机授权成功", Toast.LENGTH_LONG).show()
                            showHome()
                        }''',
    "profile fetch after login",
)

replace(
    '''        prefs.edit().remove("access_token").remove("refresh_token").remove("token_time").apply()''',
    '''        prefs.edit().remove("access_token").remove("refresh_token").remove("token_time").remove("channel_title").remove("channel_avatar").apply()''',
    "logout profile cleanup",
)

s = s.replace("C16 YouTube v2.7", "C16 YouTube v2.8")
s = s.replace("v2.7.40045", "v2.8.40046")

path.write_text(s, encoding="utf-8")
print("Applied C16 YouTube v2.8 account, SVG navigation and cinema mode patch")
