from pathlib import Path
import re

p = Path('app/src/main/java/com/c16/video/MainActivity.kt')
s = p.read_text(encoding='utf-8')

# Route for one-time OAuth setup. Normal users stay on the direct QR flow.
if '"oauthSetup" -> showOAuthSetup()' not in s:
    s = s.replace(
        '            "login" -> showLoginCenter()\n',
        '            "login" -> showLoginCenter()\n            "oauthSetup" -> showOAuthSetup()\n',
        1,
    )

# TV-style login visuals.
if '.tvLogin{' not in s:
    css = r'''.tvLogin{max-width:1120px;margin:28px auto}.tvLoginCard{background:$panel;border:1px solid $border;border-radius:28px;padding:34px;text-align:center;box-shadow:0 18px 50px rgba(0,0,0,.10)}.tvLoginLogo{width:84px;height:56px;border-radius:16px;background:#ff0033;color:#fff;margin:0 auto 18px;display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:900}.tvLoginCard h1{font-size:38px;margin:0 0 10px}.tvLoginCard p{font-size:19px;line-height:1.6;color:$sub;margin:0 auto;max-width:760px}.tvPrimary{display:inline-flex;margin-top:24px;padding:15px 28px;border-radius:28px;background:#ff0033;color:#fff;font-size:21px;font-weight:850}.tvSecondary{display:inline-flex;margin-top:16px;padding:11px 18px;border-radius:22px;background:$panel2;border:1px solid $border;font-size:16px;font-weight:750}.tvQrWrap{display:grid;grid-template-columns:1fr 1fr;gap:26px;align-items:center;max-width:1080px;margin:20px auto}.tvQrInfo,.tvQrBox{background:$panel;border:1px solid $border;border-radius:26px;padding:30px}.tvQrInfo h1{font-size:36px;margin:0 0 12px}.tvQrInfo p{font-size:19px;line-height:1.65;color:$sub}.tvQrBox{text-align:center}.tvQrBox img{width:320px;height:320px;background:#fff;padding:10px;border-radius:20px}.tvCode{font-size:38px;font-weight:900;letter-spacing:5px;margin-top:16px}.tvHint{font-size:15px!important;color:$sub!important;margin-top:10px!important}.setupNote{max-width:920px;margin:18px auto 0;color:$sub;font-size:15px;line-height:1.6;text-align:center}@media(max-width:1250px){.tvQrWrap{grid-template-columns:1fr 1fr}.tvQrBox img{width:270px;height:270px}.tvLoginCard h1{font-size:32px}}'''
    s = s.replace('</style><script>', css + '</style><script>', 1)

# Replace the account/login center. If credentials were configured once in an older version,
# opening Login now immediately starts the official device authorization flow and shows the QR.
pattern = r'    private fun showLoginCenter\(message: String = ""\) \{.*?\n    \}\n\n    private fun startDeviceLogin'
replacement = r'''    private fun showLoginCenter(message: String = "") {
        val client = prefs.getString("oauth_client_id", "").orEmpty()
        val secret = prefs.getString("oauth_client_secret", "").orEmpty()
        val logged = isSignedIn()
        if (logged) {
            if (!accountLoaded && !accountLoading.get()) refreshAccountData { showLoginCenter() }
            val title = prefs.getString("channel_title", "").orEmpty().ifBlank { "你的 YouTube" }
            val avatar = prefs.getString("channel_avatar", "").orEmpty()
            val avatarHtml = if (avatar.isNotBlank()) "<img src='${escAttr(avatar)}'>" else "<div class='avatar' style='width:84px;height:84px'></div>"
            val body = """<div class='accountCenter'><div class='profileHero'>$avatarHtml<div class='profileText'><h2>${esc(title)}</h2><p>已通过手机扫码关联 YouTube · 后续会自动刷新登录状态</p></div><a class='syncBtn' href='c16://sync'>↻ 同步账号</a></div><div class='statGrid'><div class='statCard'><b>${accountSubscriptions.size}</b><span>订阅频道</span></div><div class='statCard'><b>${accountLikedVideos.size}</b><span>点赞视频</span></div><div class='statCard'><b>${accountPlaylists.size}</b><span>播放列表</span></div><div class='statCard'><b>${prefs.getString("history", "").orEmpty().split(',').count { it.isNotBlank() }}</b><span>车机观看记录</span></div></div><div class='accountMenu'><a href='c16://subscriptions'><span>我的订阅</span><b>›</b></a><a href='c16://favorites'><span>点赞、播放列表与收藏</span><b>›</b></a><a href='c16://history'><span>观看历史</span><b>›</b></a><a href='c16://oauthSetup'><span>OAuth 高级设置</span><b>›</b></a><a href='c16://logout'><span>退出 YouTube 登录</span><b>›</b></a></div></div>"""
            load(shell("", body))
            return
        }

        if (client.isNotBlank() && secret.isNotBlank() && message.isBlank()) {
            startDeviceLogin(client, secret)
            return
        }

        val msg = if (message.isNotBlank()) "<p style='color:#e34b5d;font-weight:750;margin-top:14px'>${esc(message)}</p>" else ""
        val configured = client.isNotBlank() && secret.isNotBlank()
        val action = if (configured) "<a class='tvPrimary' href='c16://login'>重新生成扫码登录</a>" else "<a class='tvPrimary' href='c16://oauthSetup'>首次设置</a>"
        val copy = if (configured) "授权没有完成或已过期，点击下方按钮重新生成二维码。" else "首次安装需要配置一次你自己的 Google TV OAuth 客户端。配置完成后，以后点“登录”都会直接出现二维码，不再输入 Client ID 或 Secret。"
        val body = """<div class='tvLogin'><div class='tvLoginCard'><div class='tvLoginLogo'>▶</div><h1>手机扫码登录 YouTube</h1><p>$copy</p>$msg$action</div><div class='setupNote'>C16 YouTube 不会把你的 Google 密码输入到车机。授权在手机端完成，车机会保存刷新令牌用于后续自动登录。</div></div>"""
        load(shell("", body))
    }

    private fun showOAuthSetup() {
        val client = prefs.getString("oauth_client_id", "").orEmpty()
        val secret = prefs.getString("oauth_client_secret", "").orEmpty()
        val body = """<div class='loginWrap'><div class='loginCard'><h2>首次 OAuth 设置</h2><p>这里只需要配置一次。填写 Google Cloud 中“TVs and Limited Input devices”客户端的 Client ID 与 Client Secret。保存后立即进入手机扫码授权。</p><input class='clientInput' id='client' value='${escAttr(client)}' placeholder='OAuth Client ID'><div style='height:12px'></div><input class='clientInput' type='password' id='secret' value='${escAttr(secret)}' placeholder='OAuth Client Secret'><a class='loginButton' href='javascript:startQr()'>保存并生成二维码</a><p style='font-size:15px'>凭据仅保存在当前车机应用数据中。升级安装会保留；卸载 App / 清除数据后需要重新配置。</p></div><div class='qrCard'><div style='font-size:62px;margin-top:54px'>▦</div><h2>以后无需再填</h2><p>完成这一次设置后，正常点击“登录 YouTube”会直接显示二维码。</p></div></div>"""
        load(shell("", body))
    }

    private fun startDeviceLogin'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'v3.7 patch failed: showLoginCenter matches={n}')
s = s2

# TV login QR: make scanning the primary action. Google may still request the displayed device
# code on the phone; this is part of the official limited-input authorization flow.
pattern = r'    private fun showQrCode\(userCode: String, verifyUrl: String, expires: Int\) \{.*?\n    \}\n\n    private fun pollDeviceToken'
replacement = r'''    private fun showQrCode(userCode: String, verifyUrl: String, expires: Int) {
        val qr = "https://api.qrserver.com/v1/create-qr-code/?size=420x420&data=${URLEncoder.encode(verifyUrl, "UTF-8")}" 
        val body = """<div class='tvQrWrap'><div class='tvQrInfo'><div class='tvLoginLogo' style='margin-left:0'>▶</div><h1>扫描二维码登录</h1><p>用手机相机扫描右侧二维码，在手机上选择你的 Google / YouTube 账号并完成授权。授权完成后，车机会自动进入你的 YouTube 首页。</p><div class='tvCode'>${esc(userCode)}</div><p class='tvHint'>如果手机页面要求“设备代码”，输入上面的代码即可。二维码约 ${expires / 60} 分钟内有效。</p><a class='tvSecondary' href='c16://login'>重新生成二维码</a></div><div class='tvQrBox'><img src='$qr'><h2 style='margin:16px 0 3px'>YouTube 手机授权</h2><p class='tvHint'>正在等待手机确认…</p></div></div>"""
        load(shell("", body))
    }

    private fun pollDeviceToken'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'v3.7 patch failed: showQrCode matches={n}')
s = s2

# After successful authorization, immediately refresh account data so the account chip/home are real.
s = s.replace(
    '                            Toast.makeText(this@MainActivity, "YouTube 手机授权成功", Toast.LENGTH_LONG).show()\n                            showHome()',
    '                            Toast.makeText(this@MainActivity, "YouTube 手机授权成功", Toast.LENGTH_LONG).show()\n                            accountLoaded = false\n                            refreshAccountData { showHome() }',
    1,
)

# Settings label.
s = s.replace('C16 YouTube v3.6', 'C16 YouTube v3.7')
s = s.replace('v3.6.40053', 'v3.7.40054')

p.write_text(s, encoding='utf-8')
print('Applied C16 YouTube v3.7 direct QR login and automatic account refresh patch')
