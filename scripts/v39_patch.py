from pathlib import Path
import re

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

# --- OAuth / routes ---------------------------------------------------------
# Re-authorize without deleting the stored TV OAuth client configuration.
if '"reauth" -> reauthorizeYoutube()' not in s:
    s = s.replace(
        '            "comments" -> fetchCommentsAsync(uri.getQueryParameter("id").orEmpty(), true)\n',
        '            "comments" -> fetchCommentsAsync(uri.getQueryParameter("id").orEmpty(), true)\n'
        '            "reauth" -> reauthorizeYoutube()\n',
        1,
    )

# New phone authorizations request the scopes used by subscriptions and comments.
s = s.replace(
    '"scope" to "https://www.googleapis.com/auth/youtube"',
    '"scope" to "https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.force-ssl"',
    1,
)

# --- UI helpers -------------------------------------------------------------
css = r'''.recTabBtn{display:inline-flex;border:0;cursor:pointer;padding:9px 15px;border-radius:18px;background:$panel2;color:$text;font:800 16px inherit}.recTabBtn.on{background:$text;color:$bg}.recList{display:block}.recList.hidden{display:none}.channelTabsV39{display:flex;gap:8px;overflow-x:auto;margin:-6px 0 22px;padding:0 2px 9px;border-bottom:1px solid $border;scrollbar-width:none}.channelTabsV39::-webkit-scrollbar{display:none}.channelTabsV39 span{white-space:nowrap;padding:10px 17px;border-radius:19px;background:$panel2;border:1px solid $border;font-size:17px;font-weight:750}.channelTabsV39 span.on{background:$text;color:$bg}.railHeaderV39{display:flex;align-items:center;justify-content:space-between;margin:24px 0 14px}.railHeaderV39 h2{font-size:31px;margin:0}.railActionsV39{display:flex;align-items:center;gap:9px;color:$sub}.railArrowV39{width:46px;height:46px;border-radius:50%;background:$panel;border:1px solid $border;display:flex;align-items:center;justify-content:center;font-size:31px;font-weight:500;box-shadow:0 6px 18px rgba(0,0,0,.10)}.channelRailV39{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding:1px 2px 12px}.channelRailV39::-webkit-scrollbar{display:none}.channelRailV39 .card{flex:0 0 min(330px,27vw);scroll-snap-align:start}.channelRailV39 .ctitle{height:auto;min-height:48px}.commentsAuth{margin-top:12px;display:inline-flex;padding:12px 18px;border-radius:22px;background:#ff0033;color:#fff;font-weight:850;font-size:16px}.commentsState{padding:6px 0 3px;font-size:17px;line-height:1.55;color:$sub}.playerPage .recommend{overflow-y:auto}.recommend .rec{cursor:pointer}@media(max-width:1400px){.channelRailV39 .card{flex-basis:300px}.railHeaderV39 h2{font-size:28px}}'''
if '.recTabBtn{' not in s:
    s = s.replace(
        '</style><script>',
        css + "</style><script>function switchRec(mode){var a=document.getElementById('sameAuthorList'),b=document.getElementById('relatedList'),ta=document.getElementById('tabSame'),tb=document.getElementById('tabRelated');if(!a||!b)return;if(mode==='related'){a.classList.add('hidden');b.classList.remove('hidden');if(ta)ta.classList.remove('on');if(tb)tb.classList.add('on')}else{b.classList.add('hidden');a.classList.remove('hidden');if(tb)tb.classList.remove('on');if(ta)ta.classList.add('on')}}function scrollRail(id,dir){var e=document.getElementById(id);if(e)e.scrollBy({left:dir*e.clientWidth*.82,behavior:'smooth'})}",
        1,
    )

# --- Recommendation model --------------------------------------------------
pattern = r'    private fun relatedVideos\(current: Video\): List<Video> \{.*?\n    \}\n\n    private fun channelKey'
replacement = r'''    private fun sameAuthorVideos(current: Video): List<Video> {
        val key = current.channel.trim().lowercase()
        return (channelVideoCache[key].orEmpty() + allKnownVideos().filter { it.channel.equals(current.channel, ignoreCase = true) })
            .filter { it.id != current.id }
            .distinctBy { it.id }
            .take(16)
    }

    private fun relatedContentVideos(current: Video): List<Video> {
        val currentCat = inferredCategory(current)
        val title = current.title.lowercase()
        val keys = listOf(
            "ai", "人工智能", "agent", "chatgpt", "claude", "obsidian", "codex", "npu", "芯片", "电脑", "iphone", "apple", "科技", "数码",
            "汽车", "新能源", "tesla", "零跑", "音乐", "music", "remix", "dj", "旅行", "travel", "4k", "电影", "film",
            "哲学", "philosophy", "宇宙", "心理", "思想", "知识库", "自动化"
        )
        return allKnownVideos()
            .filter { it.id != current.id && !it.channel.equals(current.channel, ignoreCase = true) }
            .map { v ->
                val vt = v.title.lowercase()
                var score = 0
                if (inferredCategory(v) == currentCat) score += 70
                if (v.category == current.category) score += 18
                score += keys.count { title.contains(it) && vt.contains(it) } * 22
                v to score
            }
            .sortedWith(compareByDescending<Pair<Video, Int>> { it.second }.thenBy { it.first.title })
            .map { it.first }
            .distinctBy { it.id }
            .take(16)
    }

    private fun relatedVideos(current: Video): List<Video> =
        (sameAuthorVideos(current) + relatedContentVideos(current)).distinctBy { it.id }.take(16)

    private fun channelKey'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n == 1:
    s = s2
else:
    raise SystemExit(f'v3.9 patch failed: recommendation block matches={n}')

# Fetch the maximum page allowed by search.list for a channel so the horizontal rail has more data.
s = s.replace('order=date&maxResults=30&channelId=', 'order=date&maxResults=50&channelId=', 1)
s = s.replace('order=date&maxResults=20&channelId=', 'order=date&maxResults=50&channelId=', 1)

# --- Channel page -----------------------------------------------------------
pattern = r'    private fun showChannel\(name: String\) \{.*?\n    \}\n\n    private fun subscribeChannel'
replacement = r'''    private fun showChannel(name: String) {
        val channelName = name.trim()
        if (channelName.isBlank()) { showHome(); return }
        currentVideoId = null
        currentChannelPage = channelName
        val key = channelKey(channelName)
        val known = (channelVideoCache[key].orEmpty() + allKnownVideos().filter { it.channel.equals(channelName, ignoreCase = true) }).distinctBy { it.id }
        val sub = accountSubscriptions.any { it.title.equals(channelName, ignoreCase = true) }
        val avatar = accountSubscriptions.firstOrNull { it.title.equals(channelName, ignoreCase = true) }?.avatar.orEmpty()
        val avatarHtml = if (avatar.isNotBlank()) "<img class='bigAvatar' src='${escAttr(avatar)}'>" else "<div class='bigAvatar'>${esc(channelName.take(1).uppercase())}</div>"
        val rail = if (known.isEmpty()) {
            "<div class='loadingStrip'>正在读取这个频道的视频…</div>"
        } else {
            "<div class='channelRailV39' id='channelRail'>${known.take(50).joinToString("") { videoCard(it) }}</div>"
        }
        val body = """<div class='channelPage'><div class='channelHeroV36'>$avatarHtml<div class='channelText'><h1>${esc(channelName)}</h1><p>频道主页 · ${known.size} 个视频已读取</p></div><a class='subscribe' href='c16://subscribe?name=${Uri.encode(channelName)}'>${if (sub) "已订阅" else "订阅"}</a></div><div class='channelTabsV39'><span class='on'>首页</span><span>视频</span><span>Shorts</span><span>直播</span><span>播放列表</span></div><div class='railHeaderV39'><h2>为你推荐</h2><div class='railActionsV39'><span>${known.size} 个已读取</span><a class='railArrowV39' href=\"javascript:scrollRail('channelRail',1)\">›</a></div></div>$rail</div>"""
        load(shell("", body))
        loadChannelVideosAsync(channelName)
    }

    private fun subscribeChannel'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n == 1:
    s = s2
else:
    raise SystemExit(f'v3.9 patch failed: channel page matches={n}')

# --- Player / recommendation tabs -----------------------------------------
pattern = r'    private fun showPlayer\(id: String\) \{.*?\n    \}\n\n    private fun buildCommentsHtml'
replacement = r'''    private fun showPlayer(id: String) {
        val current = findVideo(id)
        currentVideoId = current.id
        currentChannelPage = ""
        addHistory(current.id)
        loadChannelVideosAsync(current.channel, inferredCategory(current), current.id)

        val sameAuthor = sameAuthorVideos(current)
        val related = relatedContentVideos(current)
        val sameHtml = if (sameAuthor.isEmpty()) "<div class='muted'>正在读取同作者更多视频…</div>" else sameAuthor.joinToString("") { v ->
            "<a class='rec' href='c16://watch?id=${v.id}'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><div><div class='recTitle'>${esc(v.title)}</div><div class='recMeta'>${esc(v.channel)}<br>${esc(v.meta)}</div></div></a>"
        }
        val relatedHtml = if (related.isEmpty()) "<div class='muted'>暂时没有更多相关推荐。</div>" else related.joinToString("") { v ->
            "<a class='rec' href='c16://watch?id=${v.id}'><img src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'><div><div class='recTitle'>${esc(v.title)}</div><div class='recMeta'>${esc(v.channel)}<br>${esc(v.meta)}</div></div></a>"
        }

        val fav = prefs.getStringSet("favorites", emptySet()).orEmpty().contains(current.id)
        val subscribed = accountSubscriptions.any { it.title.equals(current.channel, ignoreCase = true) }
        val commentsHtml = buildCommentsHtml(current.id)
        val loginHint = if (!isSignedIn()) "<a class='action' href='c16://login'>◉ 手机扫码登录</a>" else ""
        val body = """<a class='sidePeek' href='javascript:toggleSide()'>☰</a><div class='playerPage'><div class='playerCol'><div class='playerBox'><div class='videoLoading' id='videoLoading'><div class='spinner'></div><strong>正在加载视频</strong><span>正在准备 YouTube 播放器…</span></div><div id='ytPlayer'></div><span class='quality'>4K · HDR</span><a class='fullBtn' href='c16://fullscreen?id=${current.id}'>⛶ 全屏</a></div><div class='pTitle'>${esc(current.title)}</div><div class='pMeta'>${esc(current.meta)}　#${esc(if (inferredCategory(current) == "科技") "科技AI" else inferredCategory(current))}</div><div class='channelRow'><a class='channelIdentity' href='c16://channel?name=${Uri.encode(current.channel)}'><div class='avatar'></div><div class='channelInfo'><b>${esc(current.channel)}</b><span class='channelHint'>点击进入频道主页 ›</span></div></a><a class='subscribe' href='c16://subscribe?name=${Uri.encode(current.channel)}'>${if (subscribed) "已订阅" else "订阅"}</a></div><div class='actions'><span class='action'>👍 点赞</span><a class='action' href='c16://favorite?id=${current.id}'>${if (fav) "♥ 已收藏" else "♡ 收藏"}</a><a class='action' href='javascript:toggleSide()'>☰ 左栏</a><a class='action' href='javascript:toggleRec()'>▥ 推荐</a><a class='action' href='javascript:toggleCinema()'>▣ 影院模式</a>$loginHint</div>$commentsHtml</div><aside class='recommend'><div class='recTabs'><a id='tabSame' class='recTabBtn on' href=\"javascript:switchRec('same')\">同作者优先</a><a id='tabRelated' class='recTabBtn' href=\"javascript:switchRec('related')\">相关推荐</a></div><div id='sameAuthorList' class='recList'>$sameHtml</div><div id='relatedList' class='recList hidden'>$relatedHtml</div></aside></div><script>setTimeout(function(){var a=document.querySelector('.app');if(a)a.classList.add('hideSide')},0)</script>"""
        load(shell("", body))
        if (isSignedIn() && current.id !in commentsLoaded) fetchCommentsAsync(current.id)
    }

    private fun buildCommentsHtml'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n == 1:
    s = s2
else:
    raise SystemExit(f'v3.9 patch failed: player matches={n}')

# --- Comments ---------------------------------------------------------------
pattern = r'    private fun buildCommentsHtml\(videoId: String\): String \{.*?\n    \}\n\n    private fun fetchCommentsAsync'
replacement = r'''    private fun buildCommentsHtml(videoId: String): String {
        val token = prefs.getString("access_token", "").orEmpty()
        val list = commentsCache[videoId]
        val error = commentsError[videoId].orEmpty()
        val title = if (list != null && list.isNotEmpty()) "评论 ${list.size}" else "评论"
        val inner = when {
            token.isBlank() -> "<div class='commentsState'>手机扫码授权后，可读取这个视频公开开放的评论。</div><a class='commentsAuth' href='c16://login'>手机扫码登录</a>"
            error == "__SCOPE__" -> "<div class='commentsState'>当前 YouTube 授权权限不足。重新扫码授权后即可读取评论，原来的 OAuth 客户端配置会保留。</div><a class='commentsAuth' href='c16://reauth'>重新手机扫码授权</a>"
            error == "__DISABLED__" -> "<div class='commentsState'>该视频未开放公开评论。</div>"
            error.isNotBlank() -> "<div class='commentsState'>暂时无法读取评论：${esc(error)}</div><a class='commentRetry' href='c16://comments?id=${Uri.encode(videoId)}'>重新加载评论</a>"
            list == null -> "<div class='commentsState'>正在从 YouTube 读取公开评论…</div>"
            list.isEmpty() -> "<div class='commentsState'>这个视频暂时没有可显示的公开评论。</div>"
            else -> list.take(12).joinToString("") { c -> "<div class='comment'>${if (c.avatar.isNotBlank()) "<img src='${escAttr(c.avatar)}'>" else "<div class='commentAvatar'></div>"}<div><b>${esc(c.author)}</b><p>${esc(c.text)}</p></div></div>" }
        }
        return "<div class='comments'><div class='commentsHead'><span>$title</span><span class='muted'>YouTube 公开评论 · 车机只读</span></div>$inner</div>"
    }

    private fun fetchCommentsAsync'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n == 1:
    s = s2
else:
    raise SystemExit(f'v3.9 patch failed: comments html matches={n}')

pattern = r'    private fun fetchCommentsAsync\(videoId: String, force: Boolean = false\) \{.*?\n    \}\n\n    private fun showFullscreen'
replacement = r'''    private fun fetchCommentsAsync(videoId: String, force: Boolean = false) {
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
                if (r.first !in 200..299) {
                    val detail = googleApiError(r.second, r.first)
                    when {
                        r.first == 403 && (detail.contains("insufficientPermissions", true) || detail.contains("insufficient authentication scopes", true) || detail.contains("权限不足")) -> throw IllegalStateException("__SCOPE__")
                        detail.contains("commentsDisabled", true) || detail.contains("disabled comments", true) -> throw IllegalStateException("__DISABLED__")
                        else -> throw IllegalStateException(detail)
                    }
                }
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

    private fun reauthorizeYoutube() {
        loginPolling.set(false)
        prefs.edit()
            .remove("access_token")
            .remove("refresh_token")
            .remove("token_expiry")
            .apply()
        accountLoaded = false
        commentsCache.clear()
        commentsLoaded.clear()
        commentsError.clear()
        showLoginCenter()
    }

    private fun showFullscreen'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n == 1:
    s = s2
else:
    raise SystemExit(f'v3.9 patch failed: comments fetch matches={n}')

# Visible labels.
s = s.replace('C16 YouTube v3.7', 'C16 YouTube v3.9')
s = s.replace('v3.7.40054', 'v3.9.40055')

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v3.9 browsing, recommendation tabs and comment authorization fixes')
