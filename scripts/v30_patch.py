from pathlib import Path
import re

path = Path("app/src/main/java/com/c16/video/MainActivity.kt")
s = path.read_text(encoding="utf-8")


def replace(old: str, new: str, label: str):
    global s
    if old not in s:
        raise SystemExit(f"v3.0 patch failed: missing {label}")
    s = s.replace(old, new, 1)


def sub(pattern: str, repl: str, label: str):
    global s
    s2, n = re.subn(pattern, repl, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"v3.0 patch failed: {label} matches={n}")
    s = s2

# Account-backed resource models and runtime caches.
replace(
    '    data class Hero(val eyebrow: String, val title: String, val copy: String, val bg: String, val videoId: String, val badge: String)\n',
    '    data class Hero(val eyebrow: String, val title: String, val copy: String, val bg: String, val videoId: String, val badge: String)\n'
    '    data class SubChannel(val id: String, val title: String, val avatar: String)\n'
    '    data class YtPlaylist(val id: String, val title: String, val thumb: String, val count: Int)\n',
    'account models',
)

replace(
    '    private val commentsLoaded = mutableSetOf<String>()\n',
    '    private val commentsLoaded = mutableSetOf<String>()\n'
    '    private val accountLoading = AtomicBoolean(false)\n'
    '    @Volatile private var accountLoaded = false\n'
    '    @Volatile private var accountSyncError = ""\n'
    '    private val accountLikedVideos = mutableListOf<Video>()\n'
    '    private val accountSubscriptionVideos = mutableListOf<Video>()\n'
    '    private val accountHomeVideos = mutableListOf<Video>()\n'
    '    private val accountExtraVideos = mutableListOf<Video>()\n'
    '    private val accountSubscriptions = mutableListOf<SubChannel>()\n'
    '    private val accountPlaylists = mutableListOf<YtPlaylist>()\n',
    'account caches',
)

# Account routes.
replace(
    '            "logout" -> logout()\n',
    '            "logout" -> logout()\n'
    '            "sync" -> { accountLoaded = false; refreshAccountData { showHome() } }\n'
    '            "playlist" -> showPlaylist(uri.getQueryParameter("id").orEmpty(), uri.getQueryParameter("title").orEmpty())\n',
    'account routes',
)

# Styles for account identity, subscribed channels and playlists.
replace(
    '</style><script>',
    ".accountBanner{display:flex;align-items:center;gap:16px;background:$panel;border:1px solid $border;border-radius:20px;padding:14px 18px;margin-bottom:16px}.accountBanner img{width:54px;height:54px;border-radius:50%;object-fit:cover;background:$panel2}.accountBanner .who{flex:1;min-width:0}.accountBanner .who b{display:block;font-size:20px}.accountBanner .who span{display:block;color:$sub;font-size:14px;margin-top:3px}.syncBtn{padding:9px 14px;border-radius:18px;background:$panel2;border:1px solid $border;font-size:15px;font-weight:750}.channelGrid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:14px;margin-bottom:24px}.channelCard{background:$panel;border:1px solid $border;border-radius:18px;padding:16px 10px;text-align:center;min-width:0}.channelCard img{width:72px;height:72px;border-radius:50%;object-fit:cover;background:$panel2}.channelCard b{display:block;margin-top:9px;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.channelCard span{display:block;color:$sub;font-size:12px;margin-top:3px}.playlistGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.playlistCard{background:$panel;border:1px solid $border;border-radius:18px;overflow:hidden}.playlistCard img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:$panel2}.playlistCard .plText{padding:12px}.playlistCard b{display:block;font-size:17px;line-height:1.3}.playlistCard span{display:block;color:$sub;font-size:13px;margin-top:5px}.syncState{padding:20px;border-radius:18px;background:$panel;border:1px solid $border;color:$sub;font-size:18px;margin-bottom:18px}@media(max-width:1250px){.channelGrid{grid-template-columns:repeat(4,minmax(0,1fr))}.playlistGrid{grid-template-columns:repeat(3,minmax(0,1fr))}}</style><script>",
    'account CSS',
)

# Helpers: every dynamically fetched account video must be playable by the same player.
insert_marker = '    private fun videoCard(v: Video, history: Boolean = false): String {'
helpers = '''    private fun isSignedIn(): Boolean = prefs.getString("access_token", "").orEmpty().isNotBlank()

    private fun allKnownVideos(): List<Video> =
        (accountExtraVideos + accountSubscriptionVideos + accountLikedVideos + accountHomeVideos + videos).distinctBy { it.id }

    private fun findVideo(id: String): Video = allKnownVideos().find { it.id == id } ?: videos.first()

    private fun accountBannerHtml(): String {
        if (!isSignedIn()) return ""
        val title = prefs.getString("channel_title", "").orEmpty().ifBlank { "你的 YouTube" }
        val avatar = prefs.getString("channel_avatar", "").orEmpty()
        val image = if (avatar.isNotBlank()) "<img src='${escAttr(avatar)}'>" else "<div class='avatar' style='width:54px;height:54px'></div>"
        val state = when {
            accountLoading.get() -> "正在同步你的 YouTube 账号…"
            accountSyncError.isNotBlank() -> "同步有部分失败：${esc(accountSyncError)}"
            accountLoaded -> "${accountSubscriptions.size} 个订阅频道 · ${accountLikedVideos.size} 个点赞视频 · ${accountPlaylists.size} 个播放列表"
            else -> "已授权 · 等待同步账号内容"
        }
        return "<div class='accountBanner'>$image<div class='who'><b>${esc(title)}</b><span>$state</span></div><a class='syncBtn' href='c16://sync'>↻ 刷新账号</a></div>"
    }

'''
if insert_marker not in s:
    raise SystemExit('v3.0 patch failed: videoCard marker')
s = s.replace(insert_marker, helpers + insert_marker, 1)

# Personalized home: once authorized, use actual subscription activity and liked videos.
sub(
    r'    private fun showHome\(\) \{.*?\n    \}\n\n    private fun showCategory',
    '''    private fun showHome() {
        currentVideoId = null
        val signed = isSignedIn()
        if (signed && !accountLoaded && !accountLoading.get()) refreshAccountData { showHome() }
        val personalized = if (signed && accountHomeVideos.isNotEmpty()) accountHomeVideos.take(10) else videos.take(10)
        val first = if (signed) accountHomeVideos.firstOrNull() else null
        val hero = if (first != null) Hero(
            "YOUR YOUTUBE",
            first.title.take(38),
            "来自你订阅的频道与点赞内容。",
            "https://i.ytimg.com/vi/${first.id}/maxresdefault.jpg",
            first.id,
            first.channel
        ) else heroFor("推荐")
        val sectionTitle = if (signed && accountHomeVideos.isNotEmpty()) "来自你的 YouTube" else "为你推荐"
        val sectionMeta = if (signed && accountHomeVideos.isNotEmpty()) "订阅动态 + 点赞内容" else "精选内容 · 大屏优化"
        val loading = if (signed && !accountLoaded) "<div class='syncState'>正在读取你的订阅、点赞视频和播放列表，完成后首页会自动刷新。</div>" else ""
        val body = "<div class='chips'>${chipsHtml("推荐")}</div>${accountBannerHtml()}$loading${heroHtml(hero)}<div class='sectionTitle'><h2>$sectionTitle</h2><span>$sectionMeta</span></div><div class='videoGrid'>${personalized.joinToString("") { videoCard(it) }}</div>"
        load(shell("home", body))
    }

    private fun showCategory''',
    'showHome replacement',
)

# Search, player, fullscreen and history must understand dynamically fetched IDs.
replace(
    '        val pool = videos.filter { key.isBlank() || it.title.lowercase().contains(key) || it.channel.lowercase().contains(key) || it.category.lowercase().contains(key) }.ifEmpty { videos }',
    '        val known = allKnownVideos()\n        val pool = known.filter { key.isBlank() || it.title.lowercase().contains(key) || it.channel.lowercase().contains(key) || it.category.lowercase().contains(key) }.ifEmpty { known }',
    'search dynamic pool',
)
replace('        val current = videos.find { it.id == id } ?: videos.first()', '        val current = findVideo(id)', 'player dynamic lookup')
replace('        val recs = videos.filter { it.id != current.id }.take(8).joinToString("") { v ->', '        val recs = allKnownVideos().filter { it.id != current.id }.take(8).joinToString("") { v ->', 'player dynamic recs')
replace('        val current = videos.find { it.id == id } ?: videos.first()', '        val current = findVideo(id)', 'fullscreen dynamic lookup')
replace('        val list = if (ids.isEmpty()) videos.take(8) else ids.mapNotNull { id -> videos.find { it.id == id } }', '        val known = allKnownVideos()\n        val list = if (ids.isEmpty()) known.take(8) else ids.mapNotNull { id -> known.find { it.id == id } }', 'history dynamic lookup')

# Favorites page now makes the authorized account visible: real likes + real playlists + local car favorites.
sub(
    r'    private fun showFavorites\(\) \{.*?\n    \}\n\n    private fun showSubscriptions',
    '''    private fun showFavorites() {
        if (isSignedIn() && !accountLoaded && !accountLoading.get()) refreshAccountData { showFavorites() }
        val localSet = prefs.getStringSet("favorites", emptySet()).orEmpty()
        val known = allKnownVideos()
        val localList = localSet.mapNotNull { id -> known.find { it.id == id } }
        val likes = if (isSignedIn()) accountLikedVideos.toList() else emptyList()
        val likeHtml = if (isSignedIn()) {
            if (likes.isEmpty()) "<div class='empty'>还没有读取到账号的点赞视频。</div>" else "<div class='videoGrid'>${likes.take(15).joinToString("") { videoCard(it) }}</div>"
        } else "<div class='empty'>登录后这里会显示你真实 YouTube 账号的点赞视频和播放列表。<br><br><a class='loginButton' href='c16://login'>手机扫码登录</a></div>"
        val playlists = if (accountPlaylists.isEmpty()) "" else "<div class='sectionTitle'><h2>你的播放列表</h2><span>${accountPlaylists.size} 个</span></div><div class='playlistGrid'>${accountPlaylists.joinToString("") { p -> "<a class='playlistCard' href='c16://playlist?id=${Uri.encode(p.id)}&title=${Uri.encode(p.title)}'>${if (p.thumb.isNotBlank()) "<img src='${escAttr(p.thumb)}'>" else "<div style='aspect-ratio:16/9;background:#222'></div>"}<div class='plText'><b>${esc(p.title)}</b><span>${p.count} 个视频</span></div></a>" }}</div>"
        val localHtml = if (localList.isEmpty()) "<div class='empty'>车机本地还没有收藏视频。</div>" else "<div class='videoGrid'>${localList.joinToString("") { videoCard(it) }}</div>"
        val body = "${accountBannerHtml()}<div class='sectionTitle'><h2>你的点赞</h2><span>来自 YouTube 账号</span></div>$likeHtml$playlists<div class='sectionTitle'><h2>车机收藏</h2><span>${localList.size} 个</span></div>$localHtml"
        load(shell("favorites", body))
    }

    private fun showSubscriptions''',
    'favorites replacement',
)

# Real subscription channels and their recent upload activities.
sub(
    r'    private fun showSubscriptions\(\) \{.*?\n    \}\n\n    private fun showLocal',
    '''    private fun showSubscriptions() {
        if (!isSignedIn()) {
            val body = "<div class='sectionTitle'><h2>订阅</h2><span>你的 YouTube 频道</span></div><div class='empty'>手机扫码登录后，这里会显示你真实订阅的频道及其近期上传。<br><br><a class='loginButton' href='c16://login'>手机扫码登录</a></div>"
            load(shell("subs", body))
            return
        }
        if (!accountLoaded && !accountLoading.get()) refreshAccountData { showSubscriptions() }
        val channels = if (accountSubscriptions.isEmpty()) "<div class='empty'>${if (accountLoading.get()) "正在同步订阅频道…" else "暂未读取到订阅频道。"}</div>" else "<div class='channelGrid'>${accountSubscriptions.joinToString("") { c -> "<div class='channelCard'>${if (c.avatar.isNotBlank()) "<img src='${escAttr(c.avatar)}'>" else "<div class='avatar' style='margin:auto;width:72px;height:72px'></div>"}<b>${esc(c.title)}</b><span>已订阅</span></div>" }}</div>"
        val latest = if (accountSubscriptionVideos.isEmpty()) "<div class='empty'>正在等待订阅频道的近期上传内容。</div>" else "<div class='videoGrid'>${accountSubscriptionVideos.take(15).joinToString("") { videoCard(it) }}</div>"
        val body = "${accountBannerHtml()}<div class='sectionTitle'><h2>你订阅的频道</h2><span>${accountSubscriptions.size} 个已读取</span></div>$channels<div class='sectionTitle'><h2>近期上传</h2><span>来自你的订阅频道</span></div>$latest"
        load(shell("subs", body))
    }

    private fun showLocal''',
    'subscriptions replacement',
)

# Account API implementation. Uses low-quota list/activity calls instead of search.list.
api_marker = '    private fun fetchAccountProfile() {'
api_code = r'''    private fun apiGet(url: String, token: String): Pair<Int, String> {
        val c = (URL(url).openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 15000
            readTimeout = 15000
            setRequestProperty("Authorization", "Bearer $token")
            setRequestProperty("Accept", "application/json")
        }
        return c.responseCode to readResponse(c)
    }

    private fun ensureAccessToken(): String {
        var token = prefs.getString("access_token", "").orEmpty()
        if (token.isBlank()) return ""
        val age = System.currentTimeMillis() - prefs.getLong("token_time", 0L)
        if (age < 50L * 60L * 1000L) return token
        val refresh = prefs.getString("refresh_token", "").orEmpty()
        val client = prefs.getString("oauth_client_id", "").orEmpty()
        val secret = prefs.getString("oauth_client_secret", "").orEmpty()
        if (refresh.isBlank() || client.isBlank() || secret.isBlank()) return token
        return try {
            val r = postForm("https://oauth2.googleapis.com/token", mapOf(
                "client_id" to client,
                "client_secret" to secret,
                "refresh_token" to refresh,
                "grant_type" to "refresh_token"
            ))
            val j = JSONObject(r.second)
            if (r.first in 200..299 && j.optString("access_token").isNotBlank()) {
                token = j.optString("access_token")
                prefs.edit().putString("access_token", token).putLong("token_time", System.currentTimeMillis()).apply()
            }
            token
        } catch (_: Exception) { token }
    }

    private fun parsePlaylistVideos(playlistId: String, token: String, label: String, max: Int = 20): List<Video> {
        if (playlistId.isBlank()) return emptyList()
        val u = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&maxResults=$max&playlistId=${URLEncoder.encode(playlistId, "UTF-8")}" 
        val r = apiGet(u, token)
        if (r.first !in 200..299) return emptyList()
        val arr = JSONObject(r.second).optJSONArray("items") ?: return emptyList()
        val out = mutableListOf<Video>()
        for (i in 0 until arr.length()) {
            val item = arr.optJSONObject(i) ?: continue
            val snippet = item.optJSONObject("snippet") ?: continue
            val details = item.optJSONObject("contentDetails")
            val id = details?.optString("videoId").orEmpty().ifBlank { snippet.optJSONObject("resourceId")?.optString("videoId").orEmpty() }
            val title = snippet.optString("title", "")
            if (id.isBlank() || title.isBlank() || title == "Deleted video" || title == "Private video") continue
            val owner = snippet.optString("videoOwnerChannelTitle", snippet.optString("channelTitle", "YouTube"))
            out.add(Video(id, title, owner, "$label · 来自你的账号", "账号"))
        }
        return out
    }

    private fun syncAccountData() {
        if (!accountLoading.compareAndSet(false, true)) return
        try {
            accountSyncError = ""
            val token = ensureAccessToken()
            if (token.isBlank()) throw IllegalStateException("登录状态已失效，请重新扫码登录")

            val channelR = apiGet("https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails&mine=true&maxResults=1", token)
            if (channelR.first !in 200..299) throw IllegalStateException("账号资料读取失败 (${channelR.first})")
            val channelItems = JSONObject(channelR.second).optJSONArray("items")
            val me = if (channelItems != null && channelItems.length() > 0) channelItems.optJSONObject(0) else null
            val snippet = me?.optJSONObject("snippet")
            val content = me?.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")
            val title = snippet?.optString("title", "").orEmpty()
            val avatar = snippet?.optJSONObject("thumbnails")?.optJSONObject("default")?.optString("url", "").orEmpty()
            if (title.isNotBlank() || avatar.isNotBlank()) prefs.edit().putString("channel_title", title).putString("channel_avatar", avatar).apply()
            val likesId = content?.optString("likes", "").orEmpty()

            val liked = parsePlaylistVideos(likesId, token, "已点赞", 20)

            val playlistR = apiGet("https://www.googleapis.com/youtube/v3/playlists?part=snippet,contentDetails&mine=true&maxResults=12", token)
            val playlistsTmp = mutableListOf<YtPlaylist>()
            if (playlistR.first in 200..299) {
                val arr = JSONObject(playlistR.second).optJSONArray("items")
                if (arr != null) for (i in 0 until arr.length()) {
                    val p = arr.optJSONObject(i) ?: continue
                    val ps = p.optJSONObject("snippet") ?: continue
                    val thumb = ps.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url", "").orEmpty().ifBlank {
                        ps.optJSONObject("thumbnails")?.optJSONObject("default")?.optString("url", "").orEmpty()
                    }
                    playlistsTmp.add(YtPlaylist(p.optString("id", ""), ps.optString("title", "播放列表"), thumb, p.optJSONObject("contentDetails")?.optInt("itemCount", 0) ?: 0))
                }
            }

            val subsR = apiGet("https://www.googleapis.com/youtube/v3/subscriptions?part=snippet&mine=true&maxResults=12&order=relevance", token)
            val subsTmp = mutableListOf<SubChannel>()
            if (subsR.first in 200..299) {
                val arr = JSONObject(subsR.second).optJSONArray("items")
                if (arr != null) for (i in 0 until arr.length()) {
                    val ss = arr.optJSONObject(i)?.optJSONObject("snippet") ?: continue
                    val rid = ss.optJSONObject("resourceId")?.optString("channelId", "").orEmpty()
                    val av = ss.optJSONObject("thumbnails")?.optJSONObject("medium")?.optString("url", "").orEmpty().ifBlank {
                        ss.optJSONObject("thumbnails")?.optJSONObject("default")?.optString("url", "").orEmpty()
                    }
                    if (rid.isNotBlank()) subsTmp.add(SubChannel(rid, ss.optString("title", "YouTube 频道"), av))
                }
            }

            val recentTmp = mutableListOf<Video>()
            for (subc in subsTmp.take(8)) {
                val actUrl = "https://www.googleapis.com/youtube/v3/activities?part=snippet,contentDetails&channelId=${URLEncoder.encode(subc.id, "UTF-8")}&maxResults=3"
                val ar = apiGet(actUrl, token)
                if (ar.first !in 200..299) continue
                val aa = JSONObject(ar.second).optJSONArray("items") ?: continue
                for (i in 0 until aa.length()) {
                    val a = aa.optJSONObject(i) ?: continue
                    val upload = a.optJSONObject("contentDetails")?.optJSONObject("upload") ?: continue
                    val id = upload.optString("videoId", "")
                    val sn = a.optJSONObject("snippet") ?: continue
                    if (id.isNotBlank()) recentTmp.add(Video(id, sn.optString("title", "YouTube 视频"), sn.optString("channelTitle", subc.title), "订阅频道近期上传", "账号"))
                }
            }

            accountLikedVideos.clear(); accountLikedVideos.addAll(liked.distinctBy { it.id })
            accountPlaylists.clear(); accountPlaylists.addAll(playlistsTmp.filter { it.id.isNotBlank() })
            accountSubscriptions.clear(); accountSubscriptions.addAll(subsTmp.distinctBy { it.id })
            accountSubscriptionVideos.clear(); accountSubscriptionVideos.addAll(recentTmp.distinctBy { it.id }.take(20))
            accountHomeVideos.clear(); accountHomeVideos.addAll((accountSubscriptionVideos + accountLikedVideos).distinctBy { it.id }.take(24))
            accountLoaded = true
        } catch (e: Exception) {
            accountSyncError = e.message ?: "账号同步失败"
            accountLoaded = true
        } finally {
            accountLoading.set(false)
        }
    }

    private fun refreshAccountData(onDone: () -> Unit) {
        if (accountLoading.get()) return
        Thread {
            syncAccountData()
            main.post(onDone)
        }.start()
    }

    private fun showPlaylist(id: String, title: String) {
        if (!isSignedIn()) { showLoginCenter("请先登录 YouTube 账号"); return }
        val safeTitle = title.ifBlank { "播放列表" }
        load(shell("favorites", "${accountBannerHtml()}<div class='sectionTitle'><h2>${esc(safeTitle)}</h2><span>正在读取播放列表…</span></div><div class='syncState'>正在从你的 YouTube 账号加载视频。</div>"))
        Thread {
            val list = parsePlaylistVideos(id, ensureAccessToken(), "播放列表", 30)
            accountExtraVideos.clear(); accountExtraVideos.addAll(list)
            main.post {
                val html = if (list.isEmpty()) "<div class='empty'>这个播放列表没有可显示的视频，或当前账号没有访问权限。</div>" else "<div class='videoGrid'>${list.joinToString("") { videoCard(it) }}</div>"
                load(shell("favorites", "${accountBannerHtml()}<div class='sectionTitle'><h2>${esc(safeTitle)}</h2><span>${list.size} 个视频</span></div>$html"))
            }
        }.start()
    }

'''
if api_marker not in s:
    raise SystemExit('v3.0 patch failed: account API marker')
s = s.replace(api_marker, api_code + api_marker, 1)

# On login, fetch the actual YouTube account before rendering Home.
replace(
    '                        fetchAccountProfile()\n                        main.post {',
    '                        syncAccountData()\n                        main.post {',
    'sync after login',
)

# Logout clears account-backed UI caches and profile identity.
replace(
    '        commentsCache.clear()\n        commentsLoaded.clear()\n',
    '        commentsCache.clear()\n        commentsLoaded.clear()\n'
    '        accountLikedVideos.clear(); accountSubscriptionVideos.clear(); accountHomeVideos.clear(); accountExtraVideos.clear(); accountSubscriptions.clear(); accountPlaylists.clear()\n'
    '        accountLoaded = false; accountSyncError = ""\n'
    '        prefs.edit().remove("channel_title").remove("channel_avatar").apply()\n',
    'logout account cleanup',
)

# Version labels applied after previous incremental patches.
s = s.replace("C16 YouTube v2.9", "C16 YouTube v3.0")
s = s.replace("v2.9.40047", "v3.0.40048")

path.write_text(s, encoding="utf-8")
print("Applied C16 YouTube v3.0 real account data patch")
