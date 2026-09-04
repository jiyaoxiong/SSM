from pathlib import Path

path = Path("app/src/main/java/com/c16/video/MainActivity.kt")
s = path.read_text(encoding="utf-8")


def replace(old: str, new: str, label: str):
    global s
    if old not in s:
        raise SystemExit(f"v3.1 patch failed: missing {label}")
    s = s.replace(old, new, 1)

marker = '    private fun apiGet(url: String, token: String): Pair<Int, String> {'
helper = '''    private fun googleApiError(body: String, status: Int): String {
        return try {
            val root = JSONObject(body)
            val err = root.optJSONObject("error")
            val message = err?.optString("message", "").orEmpty()
            val errors = err?.optJSONArray("errors")
            val reason = if (errors != null && errors.length() > 0) errors.optJSONObject(0)?.optString("reason", "").orEmpty() else ""
            val friendly = when (reason) {
                "accessNotConfigured" -> "YouTube Data API 未在这个 OAuth 客户端所属的 Google Cloud 项目中启用"
                "insufficientPermissions" -> "当前 OAuth Token 权限不足，请退出后重新扫码授权"
                "authenticatedUserNotChannel" -> "当前授权的 Google 账号没有解析到可用的 YouTube 频道"
                "subscriptionForbidden" -> "当前账号无权读取订阅列表"
                "quotaExceeded" -> "YouTube Data API 项目配额已用完"
                "forbidden" -> "请求未被 YouTube 正确授权"
                else -> ""
            }
            listOf("HTTP $status", reason, friendly, message).filter { it.isNotBlank() }.joinToString(" · ")
        } catch (_: Exception) {
            "HTTP $status · ${body.take(220)}"
        }
    }

'''
if marker not in s:
    raise SystemExit("v3.1 patch failed: apiGet marker")
s = s.replace(marker, helper + marker, 1)

replace(
    '            if (channelR.first !in 200..299) throw IllegalStateException("账号资料读取失败 (${channelR.first})")',
    '            if (channelR.first !in 200..299) throw IllegalStateException("账号资料读取失败：${googleApiError(channelR.second, channelR.first)}")',
    'channel profile 403 detail',
)

# Make the account banner wrap long Google error details instead of clipping them.
replace(
    '.accountBanner .who span{display:block;color:$sub;font-size:14px;margin-top:3px}',
    '.accountBanner .who span{display:block;color:$sub;font-size:14px;line-height:1.45;margin-top:3px;white-space:normal;word-break:break-word}',
    'account banner error wrapping',
)

s = s.replace("C16 YouTube v3.0", "C16 YouTube v3.1")
s = s.replace("v3.0.40048", "v3.1.40049")

path.write_text(s, encoding="utf-8")
print("Applied C16 YouTube v3.1 YouTube API diagnostic patch")
