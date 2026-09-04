from pathlib import Path
import re

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

# Runtime state for real channel pages, same-author recommendations and comment errors.
if 'private val channelVideoCache' not in s:
    s = s.replace(
        '    private val relatedVideoCache = mutableMapOf<String, List<Video>>()\n',
        '    private val relatedVideoCache = mutableMapOf<String, List<Video>>()\n'
        '    private val channelVideoCache = mutableMapOf<String, List<Video>>()\n'
        '    private val channelIdCache = mutableMapOf<String, String>()\n'
        '    private val channelLoading = mutableSetOf<String>()\n'
        '    private val commentsError = mutableMapOf<String, String>()\n'
        '    @Volatile private var currentChannelPage = ""\n',
        1,
    )

# Include channel-fetched videos in every player/search pool.
s = s.replace(
    '(categoryVideoCache.values.flatten() + accountExtraVideos + accountSubscriptionVideos + accountLikedVideos + accountHomeVideos + videos).distinctBy { it.id }',
    '(channelVideoCache.values.flatten() + categoryVideoCache.values.flatten() + accountExtraVideos + accountSubscriptionVideos + accountLikedVideos + accountHomeVideos + videos).distinctBy { it.id }',
    1,
)

# Playback/account routes.
if '"channel" -> showChannel' not in s:
    s = s.replace(
        '            "drive" -> showDrivingMode()\n',
        '            "drive" -> showDrivingMode()\n'
        '            "channel" -> showChannel(uri.getQueryParameter("name").orEmpty())\n'
        '            "subscribe" -> subscribeChannel(uri.getQueryParameter("name").orEmpty())\n'
        '            "comments" -> fetchCommentsAsync(uri.getQueryParameter("id").orEmpty(), true)\n',
        1,
    )

# New OAuth authorizations can really subscribe to channels. Existing readonly tokens keep
# working for viewing and will show a clear re-authorize message if subscribe is tapped.
s = s.replace(
    '"scope" to "https://www.googleapis.com/auth/youtube.readonly"',
    '"scope" to "https://www.googleapis.com/auth/youtube"',
    1,
)

# V3.6 playback layout: sidebar hidden by default, larger recommendation rail and proper
# clickable channel identity + comments.
css = r'''.sidePeek{position:fixed;z-index:30;left:0;top:44%;width:42px;height:74px;border-radius:0 20px 20px 0;background:rgba(20,20,20,.82);color:#fff;display:flex;align-items:center;justify-content:center;font-size:22px;border:1px solid rgba(255,255,255,.18);border-left:0}.playerPage{grid-template-columns:minmax(0,1fr) 420px;gap:20px}.recommend{padding:16px;max-height:calc(100vh - 120px)}.rec{grid-template-columns:150px 1fr;gap:12px;margin-bottom:15px}.rec img{width:150px;border-radius:11px}.recTitle{font-size:18px;line-height:1.34;max-height:49px}.recMeta{font-size:13px;line-height:1.4}.recTabs{margin-bottom:15px}.tab{font-size:15px;padding:9px 14px}.channelRow{gap:14px}.channelIdentity{display:flex;align-items:center;gap:16px;flex:1;min-width:0;border-radius:16px;padding:5px 7px;margin:-5px -7px}.channelIdentity:hover{background:$panel2}.channelIdentity .channelInfo{min-width:0}.channelIdentity .channelInfo b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.channelHint{font-size:14px!important}.subscribe{display:inline-flex;align-items:center;justify-content:center;min-width:96px}.comments{padding:20px;margin-bottom:34px}.commentsHead{display:flex;align-items:center;justify-content:space-between}.comment{grid-template-columns:50px 1fr;gap:14px}.comment img,.commentAvatar{width:50px;height:50px}.comment p{font-size:18px}.commentRetry{display:inline-flex;margin-top:12px;padding:9px 15px;border-radius:18px;background:$panel2;border:1px solid $border;font-size:15px;font-weight:750}.channelPage{max-width:1500px;margin:0 auto}.channelHeroV36{display:flex;align-items:center;gap:22px;background:$panel;border:1px solid $border;border-radius:24px;padding:24px;margin-bottom:22px}.channelHeroV36 .bigAvatar{width:92px;height:92px;border-radius:50%;background:linear-gradient(135deg,#357ec9,#153459);display:flex;align-items:center;justify-content:center;color:#fff;font-size:32px;font-weight:900;flex:0 0 auto}.channelHeroV36 .channelText{flex:1;min-width:0}.channelHeroV36 h1{margin:0 0 6px;font-size:34px}.channelHeroV36 p{margin:0;color:$sub;font-size:17px}.channelHeroV36 .subscribe{font-size:19px;padding:12px 22px}.loadingStrip{padding:24px;border-radius:18px;background:$panel;border:1px solid $border;color:$sub;font-size:18px}@media(max-width:1250px){.playerPage{grid-template-columns:minmax(0,1fr) 360px}.rec{grid-template-columns:132px 1fr}.rec img{width:132px}.recTitle{font-size:16px}}'''
s = s.replace('</style><script>', css + '</style><script>', 1)

# Prefer cached videos from the exact same author first; then rank semantically related items.
pattern = r'    private fun relatedVideos\(current: Video\): List<Video> \{.*?\n    \}\n\n    private fun showPlayer'
replacement = r'''    private fun relatedVideos(current: Video): List<Video> {
        val key = current.channel.trim().lowercase()
        val sameAuthor = (channelVideoCache[key].orEmpty() + allKnownVideos().filter { it.channel.equals(current.channel, ignoreCase = true) })
            .filter { it.id != current.id }
            .distinctBy { it.id }
        val currentCat = inferredCategory(current)
        val currentTitle = current.title.lowercase()
        val topicKeys = listOf(
            "ai", "人工智能", "npu", "芯片", "电脑", "iphone", "apple", "科技", "数码",
            "汽车", "新能源", "tesla", "零跑", "音乐", "music", "remix", "dj", "旅行", "travel", "4k",
            "电影", "film", "哲学", "philosophy", "宇宙", "心理", "思想"
        )
        val related = allKnownVideos().filter { it.id != current.id && !it.channel.equals(current.channel, ignoreCase = true) }
            .sortedWith(compareByDescending<Video> { v ->
                var score = 0
                if (inferredCategory(v) == currentCat) score += 60
                val t = v.title.lowercase()
                score += topicKeys.count { currentTitle.contains(it) && t.contains(it) } * 16
                if (v.category == current.category) score += 12
                score
            }.thenBy { it.title })
        return (sameAuthor + related).distinctBy { it.id }.take(12)
    }

    private fun showPlayer'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'v3.6 patch failed: relatedVideos block matches={n}')
s = s2

# Channel lookup and same-author video loading. Cache per author so playback does not repeatedly
# spend YouTube search quota.
player_marker = '    private fun showPlayer(id: String) {'
helpers = r'''    private fun channelKey(name: String): String = name.trim().lowercase()

    private fun resolveChannelId(name: String, token: String): String {
        val key = channelKey(name)
        channelIdCache[key]?.let { if (it.isNotBlank()) return it }
        accountSubscriptions.firstOrNull { it.title.equals(name, ignoreCase = true) }?.id?.let {
            if (it.isNotBlank()) { channelIdCache[key] = it; return it }
        }
        val q = URLEncoder.encode(name, "UTF-8")
        val r = apiGet("https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&maxResults=1&q=$q", token)
        if (r.first !in 200..299) return ""
        val items = JSONObject(r.second).optJSONArray("items")
        val id = if (items != null && items.length() > 0) items.optJSONObject(0)?.optJSONObject("id")?.optString("channelId", "").orEmpty() else ""
        if (id.isNotBlank()) channelIdCache[key] = id
        return id
    }

    private fun loadChannelVideosAsync(channelName: String, categoryHint: String = "推荐", refreshVideoId: String = "") {
        val key = channelKey(channelName)
        if (key.isBlank() || channelVideoCache.containsKey(key) || !channelLoading.add(key)) return
        Thread {
            try {
                val token = ensureAccessToken()
                if (token.isBlank()) return@Thread
                val channelId = resolveChannelId(channelName, token)
                if (channelId.isBlank()) return@Thread
                val url = "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&videoEmbeddable=true&order=date&maxResults=20&channelId=${URLEncoder.encode(channelId, "UTF-8")}" 
                val r = apiGet(url, token)
                if (r.first in 200..299) {
                    val items = JSONObject(r.second).optJSONArray("items")
                    val out = mutableListOf<Video>()
                    if (items != null) for (i in 0 until items.length()) {
                        val item = items.optJSONObject(i) ?: continue
                        val id = item.optJSONObject("id")?.optString("videoId", "").orEmpty()
                        val sn = item.optJSONObject("snippet") ?: continue
                        if (id.isBlank()) continue
                        out.add(Video(id, sn.optString("title", "YouTube 视频"), sn.optString("channelTitle", channelName), "频道近期上传", categoryHint))
                    }
                    if (out.isNotEmpty()) channelVideoCache[key] = out.distinctBy { it.id }
                }
            } catch (_: Exception) {
            } finally {
                channelLoading.remove(key)
                relatedVideoCache.remove(refreshVideoId)
                main.post {
                    when {
                        refreshVideoId.isNotBlank() && currentVideoId == refreshVideoId -> showPlayer(refreshVideoId)
                        currentChannelPage.equals(channelName, ignoreCase = true) -> showChannel(channelName)
                    }
                }
            }
        }.start()
    }

    private fun apiPostJson(url: String, token: String, json: String): Pair<Int, String> {
        val c = (URL(url).openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 15000
            readTimeout = 15000
            doOutput = true
            setRequestProperty("Authorization", "Bearer $token")
            setRequestProperty("Content-Type", "application/json; charset=UTF-8")
            setRequestProperty("Accept", "application/json")
        }
        c.outputStream.use { it.write(json.toByteArray(StandardCharsets.UTF_8)) }
        return c.responseCode to readResponse(c)
    }

    private fun showChannel(name: String) {
        val channelName = name.trim()
        if (channelName.isBlank()) { showHome(); return }
        currentVideoId = null
        currentChannelPage = channelName
        val key = channelKey(channelName)
        val known = (channelVideoCache[key].orEmpty() + allKnownVideos().filter { it.channel.equals(channelName, ignoreCase = true) }).distinctBy { it.id }
        val sub = accountSubscriptions.any { it.title.equals(channelName, ignoreCase = true) }
        val avatar = accountSubscriptions.firstOrNull { it.title.equals(channelName, ignoreCase = true) }?.avatar.orEmpty()
        val avatarHtml = if (avatar.isNotBlank()) "<img class='bigAvatar' src='${escAttr(avatar)}'>" else "<div class='bigAvatar'>${esc(channelName.take(1).uppercase())}</div>"
        val cards = if (known.isEmpty()) "<div class='loadingStrip'>正在读取这个频道的近期视频…</div>" else "<div class='videoGrid'>${known.take(30).joinToString("") { videoCard(it) }}</div>"
        val body = "<div class='channelPage'><div class='channelHeroV36'>$avatarHtml<div class='channelText'><h1>${esc(channelName)}</h1><p>频道主页 · 点击视频即可播放</p></div><a class='subscribe' href='c16://subscribe?name=${Uri.encode(channelName)}'>${if (sub) "已订阅" else "订阅"}</a></div><div class='sectionTitle'><h2>近期视频</h2><span>${known.size} 个已读取</span></div>$cards</div>"
        load(shell("", body))
        loadChannelVideosAsync(channelName)
    }

    private fun subscribeChannel(name: String) {
        val channelName = name.trim()
        if (channelName.isBlank()) return
        if (!isSignedIn()) { showLoginCenter("请先登录 YouTube 再订阅频道"); return }
        if (accountSubscriptions.any { it.title.equals(channelName, ignoreCase = true) }) {
            Toast.makeText(this, "已经订阅 $channelName", Toast.LENGTH_SHORT).show()
            return
        }
        val returnVideo = currentVideoId.orEmpty()
        Thread {
            try {
                val token = ensureAccessToken()
                if (token.isBlank()) throw IllegalStateException("登录状态已失效，请重新扫码登录")
                val channelId = resolveChannelId(channelName, token)
                if (channelId.isBlank()) throw IllegalStateException("没有找到这个 YouTube 频道")
                val body = JSONObject().put("snippet", JSONObject().put("resourceId", JSONObject().put("kind", "youtube#channel").put("channelId", channelId))).toString()
                val r = apiPostJson("https://www.googleapis.com/youtube/v3/subscriptions?part=snippet", token, body)
                if (r.first !in 200..299) {
                    val detail = googleApiError(r.second, r.first)
                    if (detail.contains("insufficientPermissions", true) || detail.contains("权限不足")) {
                        throw IllegalStateException("当前登录是旧的只读授权。请退出账号后重新扫码一次，即可使用订阅功能。")
                    }
                    throw IllegalStateException(detail)
                }
                accountSubscriptions.add(SubChannel(channelId, channelName, ""))
                main.post {
                    Toast.makeText(this, "已订阅 $channelName", Toast.LENGTH_LONG).show()
                    if (returnVideo.isNotBlank()) showPlayer(returnVideo) else showChannel(channelName)
                }
            } catch (e: Exception) {
                main.post { Toast.makeText(this, "订阅失败：${e.message ?: "未知错误"}", Toast.LENGTH_LONG).show() }
            }
        }.start()
    }

'''
if player_marker not in s:
    raise SystemExit('v3.6 patch failed: showPlayer marker missing')
s = s.replace(player_marker, helpers + player_marker, 1)

# Replace the full player/comments block. Playback now auto-hides the sidebar, makes the author
# clickable, gives recommendations more space, and surfaces actual comment API errors/retry.
pattern = r'    private fun showPlayer\(id: String\) \{.*?\n    private fun showFullscreen\(id: String\) \{'
replacement = r'''    private fun showPlayer(id: String) {
        val current = findVideo(id)
        currentVideoId = current.id
        currentChannelPage = ""
        addHistory(current.id)
        loadChannelVideosAsync(current.channel, inferredCategory(current), current.id)
        val recs = relatedVideos(current).joinToString("") { v ->
            "<a class='rec' href='c16://watch?id=${v.id}'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><div><div class='recTitle'>${esc(v.title)}</div><div class='recMeta'>${esc(v.channel)}<br>${esc(v.meta)}</div></div></a>"
        }
        val fav = prefs.getStringSet("favorites", emptySet()).orEmpty().contains(current.id)
        val subscribed = accountSubscriptions.any { it.title.equals(current.channel, ignoreCase = true) }
        val commentsHtml = buildCommentsHtml(current.id)
        val loginHint = if (!isSignedIn()) "<a class='action' href='c16://login'>◉ 手机扫码登录</a>" else ""
        val body = """<a class='sidePeek' href='javascript:toggleSide()'>☰</a><div class='playerPage'><div class='playerCol'><div class='playerBox'><div class='videoLoading' id='videoLoading'><div class='spinner'></div><strong>正在加载视频</strong><span>正在准备 YouTube 播放器…</span></div><div id='ytPlayer'></div><span class='quality'>4K · HDR</span><a class='fullBtn' href='c16://fullscreen?id=${current.id}'>⛶ 全屏</a></div><div class='pTitle'>${esc(current.title)}</div><div class='pMeta'>${esc(current.meta)}　#${esc(if (inferredCategory(current) == "科技") "科技AI" else inferredCategory(current))}</div><div class='channelRow'><a class='channelIdentity' href='c16://channel?name=${Uri.encode(current.channel)}'><div class='avatar'></div><div class='channelInfo'><b>${esc(current.channel)}</b><span class='channelHint'>点击进入频道主页 ›</span></div></a><a class='subscribe' href='c16://subscribe?name=${Uri.encode(current.channel)}'>${if (subscribed) "已订阅" else "订阅"}</a></div><div class='actions'><span class='action'>👍 点赞</span><a class='action' href='c16://favorite?id=${current.id}'>${if (fav) "♥ 已收藏" else "♡ 收藏"}</a><a class='action' href='javascript:toggleSide()'>☰ 左栏</a><a class='action' href='javascript:toggleRec()'>▥ 推荐</a><a class='action' href='javascript:toggleCinema()'>▣ 影院模式</a>$loginHint</div>$commentsHtml</div><aside class='recommend'><div class='recTabs'><span class='tab on'>同作者优先</span><span class='tab'>相关内容</span></div>$recs</aside></div><script>setTimeout(function(){var a=document.querySelector('.app');if(a)a.classList.add('hideSide')},0)</script>"""
        load(shell("", body))
        if (isSignedIn() && current.id !in commentsLoaded) fetchCommentsAsync(current.id)
    }

    private fun buildCommentsHtml(videoId: String): String {
        val token = prefs.getString("access_token", "").orEmpty()
        val list = commentsCache[videoId]
        val error = commentsError[videoId].orEmpty()
        val title = if (list != null && list.isNotEmpty()) "评论 ${list.size}" else "评论"
        val inner = when {
            token.isBlank() -> "<div class='muted'>手机扫码授权后，可读取这个视频公开开放的评论。</div>"
            error.isNotBlank() -> "<div class='muted'>评论加载失败：${esc(error)}</div><a class='commentRetry' href='c16://comments?id=${Uri.encode(videoId)}'>重新加载评论</a>"
            list == null -> "<div class='muted'>正在从 YouTube 读取评论…</div>"
            list.isEmpty() -> "<div class='muted'>这个视频暂时没有可显示的公开评论。</div>"
            else -> list.take(12).joinToString("") { c -> "<div class='comment'>${if (c.avatar.isNotBlank()) "<img src='${escAttr(c.avatar)}'>" else "<div class='commentAvatar'></div>"}<div><b>${esc(c.author)}</b><p>${esc(c.text)}</p></div></div>" }
        }
        return "<div class='comments'><div class='commentsHead'><span>$title</span></div>$inner</div>"
    }

    private fun fetchCommentsAsync(videoId: String, force: Boolean = false) {
        if (videoId.isBlank()) return
        if (!force && videoId in commentsLoaded) return
        commentsLoaded.add(videoId)
        commentsError.remove(videoId)
        if (force) commentsCache.remove(videoId)
        Thread {
            val out = mutableListOf<Comment>()
            try {
                val token = ensureAccessToken()
                if (token.isBlank()) throw IllegalStateException("登录状态已失效，请重新扫码登录")
                val url = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=${URLEncoder.encode(videoId, "UTF-8")}&maxResults=12&order=relevance&textFormat=plainText"
                val r = apiGet(url, token)
                if (r.first !in 200..299) throw IllegalStateException(googleApiError(r.second, r.first))
                val items = JSONObject(r.second).optJSONArray("items")
                if (items != null) for (i in 0 until items.length()) {
                    val sn = items.optJSONObject(i)?.optJSONObject("snippet")?.optJSONObject("topLevelComment")?.optJSONObject("snippet") ?: continue
                    out.add(Comment(sn.optString("authorDisplayName", "YouTube 用户"), sn.optString("textDisplay", ""), sn.optString("authorProfileImageUrl", "")))
                }
                commentsCache[videoId] = out
            } catch (e: Exception) {
                commentsCache[videoId] = emptyList()
                commentsError[videoId] = e.message ?: "无法读取评论"
            }
            main.post { if (currentVideoId == videoId) showPlayer(videoId) }
        }.start()
    }

    private fun showFullscreen(id: String) {'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'v3.6 patch failed: player/comments block matches={n}')
s = s2

# Clear new caches on logout.
s = s.replace(
    '        commentsCache.clear()\n        commentsLoaded.clear()\n',
    '        commentsCache.clear()\n        commentsLoaded.clear()\n        commentsError.clear()\n        channelVideoCache.clear()\n        channelIdCache.clear()\n        channelLoading.clear()\n',
    1,
)

# Visible version labels.
s = s.replace('C16 YouTube v3.5', 'C16 YouTube v3.6')
s = s.replace('v3.5.40052', 'v3.6.40053')

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v3.6 channel, subscription, comments and playback layout patch')
