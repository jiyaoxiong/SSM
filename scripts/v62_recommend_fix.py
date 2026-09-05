from pathlib import Path

p=Path('app/src/main/java/com/c16/video/MainActivity.kt')
s=p.read_text(encoding='utf-8')

# V6.2 final recommendation fix. The playback/IFrame/WebView stack stays untouched.
# Replace the initially rendered mixed local pool with async, source-aware recommendations:
# same-author videos come from the author's uploads playlist; related videos come from
# YouTube's real video category instead of unrelated items accumulated in dynamicVideos.

old_tail='''load(shell("",body,true));loadPlayerChannelUi62(id);fetchCommentsAsync(id)'''
new_tail='''load(shell("",body,true));loadPlayerChannelUi62(id);loadPlayerRecommendations62(id);fetchCommentsAsync(id)'''
if old_tail not in s:
    raise SystemExit('v6.2 recommendation player tail anchor missing')
s=s.replace(old_tail,new_tail,1)

marker='''    private fun accountPill51():String{'''
methods=r'''    private fun recHtml62(list:List<Video>):String{
        if(list.isEmpty())return "<div class='recEmpty'>暂时没有更多视频</div>"
        return list.distinctBy{it.id}.take(24).joinToString(""){r->"<a class='rec' href='c16://watch?id=${Uri.encode(r.id)}'><img src='${thumb(r)}'><div><b>${esc(r.title)}</b><span>${esc(r.channel)}<br>${esc(r.meta)}</span></div></a>"}
    }
    private fun loadPlayerRecommendations62(videoId:String){
        if(videoId.isBlank())return
        Thread{
            try{
                val currentJson=apiGet("videos?part=snippet&id=${Uri.encode(videoId)}&maxResults=1")
                val currentItem=currentJson.optJSONArray("items")?.optJSONObject(0)
                val currentSn=currentItem?.optJSONObject("snippet")?:JSONObject()
                val channelId=currentSn.optString("channelId",dynamicVideoChannelIds[videoId].orEmpty())
                val categoryId=currentSn.optString("categoryId","")
                val currentChannel=currentSn.optString("channelTitle",dynamicVideos[videoId]?.channel.orEmpty())
                if(channelId.isNotBlank())dynamicVideoChannelIds[videoId]=channelId

                val same=mutableListOf<Video>()
                if(channelId.isNotBlank()){
                    try{
                        val cj=apiGet("channels?part=contentDetails&id=${Uri.encode(channelId)}")
                        val uploads=cj.optJSONArray("items")?.optJSONObject(0)?.optJSONObject("contentDetails")?.optJSONObject("relatedPlaylists")?.optString("uploads").orEmpty()
                        if(uploads.isNotBlank()){
                            val got=apiVideoList(apiGet("playlistItems?part=snippet&playlistId=${Uri.encode(uploads)}&maxResults=25"),true)
                            got.filterTo(same){it.id!=videoId}
                            got.forEach{dynamicVideoChannelIds[it.id]=channelId}
                        }
                    }catch(_:Exception){}
                }

                val related=mutableListOf<Video>()
                if(categoryId.isNotBlank()){
                    try{
                        val pop=apiGet("videos?part=snippet&chart=mostPopular&maxResults=35&videoCategoryId=${Uri.encode(categoryId)}")
                        apiVideoList(pop).filterTo(related){it.id!=videoId && !it.channel.equals(currentChannel,true)}
                    }catch(_:Exception){}
                }
                // Prefer already-loaded videos that share the current app category before broad fallbacks.
                val appCat=dynamicVideos[videoId]?.category.orEmpty()
                val localRelated=dynamicVideos.values.filter{it.id!=videoId && !it.channel.equals(currentChannel,true) && appCat.isNotBlank() && appCat!="推荐" && it.category==appCat}
                val relatedFinal=(localRelated+related).distinctBy{it.id}.take(24)
                val sameFinal=same.distinctBy{it.id}.take(24)
                main.post{
                    val sameHtml=recHtml62(sameFinal)
                    val relHtml=recHtml62(relatedFinal)
                    val js="(function(){var s=document.getElementById('samePane');if(s)s.innerHTML="+JSONObject.quote(sameHtml)+";var r=document.getElementById('relatedPane');if(r)r.innerHTML="+JSONObject.quote(relHtml)+";})()"
                    web.evaluateJavascript(js,null)
                }
            }catch(_:Exception){}
        }.start()
    }
'''
if marker not in s:
    raise SystemExit('v6.2 recommendation helper marker missing')
s=s.replace(marker,methods+marker,1)

p.write_text(s,encoding='utf-8')
print('Applied V6.2 source-aware player recommendations')
