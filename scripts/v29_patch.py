from pathlib import Path

path = Path("app/src/main/java/com/c16/video/MainActivity.kt")
s = path.read_text(encoding="utf-8")


def replace(old: str, new: str, label: str):
    global s
    if old not in s:
        raise SystemExit(f"v2.9 patch failed: missing {label}")
    s = s.replace(old, new, 1)

# Google currently requires the client_secret during the polling/token step for
# TV / Limited Input Device OAuth clients. Keep both values local on the car.
replace(
    '            "startQr" -> startDeviceLogin(uri.getQueryParameter("client").orEmpty())',
    '            "startQr" -> startDeviceLogin(uri.getQueryParameter("client").orEmpty(), uri.getQueryParameter("secret").orEmpty())',
    "startQr route",
)

replace(
    "function startQr(){var c=document.getElementById('client').value.trim();location.href='c16://startQr?client='+encodeURIComponent(c)}",
    "function startQr(){var c=document.getElementById('client').value.trim();var s=document.getElementById('secret').value.trim();location.href='c16://startQr?client='+encodeURIComponent(c)+'&secret='+encodeURIComponent(s)}",
    "startQr javascript",
)

replace(
    '        val client = prefs.getString("oauth_client_id", "").orEmpty()\n        val logged = prefs.getString("access_token", "").orEmpty().isNotBlank()',
    '        val client = prefs.getString("oauth_client_id", "").orEmpty()\n        val secret = prefs.getString("oauth_client_secret", "").orEmpty()\n        val logged = prefs.getString("access_token", "").orEmpty().isNotBlank()',
    "login credential variables",
)

replace(
    "<input class='clientInput' id='client' value='${escAttr(client)}' placeholder='粘贴 OAuth Client ID'><a class='loginButton' href='javascript:startQr()'>生成手机登录二维码</a>$status<p style='font-size:15px'>Client ID 仅保存在车机本地。扫码后如果手机页面要求授权码，请输入车机显示的代码。</p>",
    "<input class='clientInput' id='client' value='${escAttr(client)}' placeholder='粘贴 OAuth Client ID'><div style='height:12px'></div><input class='clientInput' type='password' id='secret' value='${escAttr(secret)}' placeholder='粘贴 OAuth Client Secret'><a class='loginButton' href='javascript:startQr()'>生成手机登录二维码</a>$status<p style='font-size:15px'>Client ID 与 Client Secret 仅保存在车机本地，不上传到我们的服务器。请使用 Google Cloud 中“TVs and Limited Input devices”类型的 OAuth 客户端。</p>",
    "login form secret field",
)

replace(
    '    private fun startDeviceLogin(clientId: String) {\n        val client = clientId.trim()\n        if (client.isBlank()) {\n            showLoginCenter("请先填写 OAuth Client ID")\n            return\n        }\n        prefs.edit().putString("oauth_client_id", client).apply()',
    '    private fun startDeviceLogin(clientId: String, clientSecret: String) {\n        val client = clientId.trim()\n        val secret = clientSecret.trim()\n        if (client.isBlank()) {\n            showLoginCenter("请先填写 OAuth Client ID")\n            return\n        }\n        if (secret.isBlank()) {\n            showLoginCenter("请填写该 OAuth 客户端对应的 Client Secret")\n            return\n        }\n        prefs.edit().putString("oauth_client_id", client).putString("oauth_client_secret", secret).apply()',
    "startDeviceLogin signature and validation",
)

replace(
    '                pollDeviceToken(client, deviceCode, interval, expires)',
    '                pollDeviceToken(client, secret, deviceCode, interval, expires)',
    "pollDeviceToken invocation",
)

replace(
    '    private fun pollDeviceToken(clientId: String, deviceCode: String, baseInterval: Int, expiresIn: Int) {',
    '    private fun pollDeviceToken(clientId: String, clientSecret: String, deviceCode: String, baseInterval: Int, expiresIn: Int) {',
    "pollDeviceToken signature",
)

replace(
    '                    val response = postForm("https://oauth2.googleapis.com/token", mapOf(\n                        "client_id" to clientId,\n                        "device_code" to deviceCode,',
    '                    val response = postForm("https://oauth2.googleapis.com/token", mapOf(\n                        "client_id" to clientId,\n                        "client_secret" to clientSecret,\n                        "device_code" to deviceCode,',
    "token polling client secret",
)

# Make the configuration state clearer in Settings.
replace(
    '        val hasClient = prefs.getString("oauth_client_id", "").orEmpty().isNotBlank()\n        val logged = prefs.getString("access_token", "").orEmpty().isNotBlank()',
    '        val hasClient = prefs.getString("oauth_client_id", "").orEmpty().isNotBlank()\n        val hasSecret = prefs.getString("oauth_client_secret", "").orEmpty().isNotBlank()\n        val logged = prefs.getString("access_token", "").orEmpty().isNotBlank()',
    "settings credential state",
)

replace(
    '${if (logged) "已授权" else if (hasClient) "Client ID 已配置" else "未配置"}',
    '${if (logged) "已授权" else if (hasClient && hasSecret) "OAuth 凭据已配置" else if (hasClient) "缺少 Client Secret" else "未配置"}',
    "settings login state text",
)

s = s.replace("C16 YouTube v2.8", "C16 YouTube v2.9")
s = s.replace("v2.8.40046", "v2.9.40047")

path.write_text(s, encoding="utf-8")
print("Applied C16 YouTube v2.9 Google device-login client_secret fix")
