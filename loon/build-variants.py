#!/usr/bin/env python3
# 从 Beta 版 config.lcf 生成「正常版」与「tvOS 版」两个变体，并给 config.lcf 本身
# 补上三变体说明（幂等）。三份共享同一骨架与规则集绑定，差异只限各自文件头注明处。
# 锚点一律从 config.lcf 运行时提取，多空格前缀用 SP*n 构造，不写死在字面量里。
import pathlib

HERE = pathlib.Path(__file__).parent
SP = " "
P2 = "#" + SP * 2
P5 = "#" + SP * 5
FILE_LINE = "# 本文件：wenrouXN/proxy-config · loon/config.lcf"
BETA_BANNER = "\n".join([
"# 【三变体分工】本文件为「Beta 版」（手机 TestFlight 3.5.4+，全功能）；另有",
P2 + "「正常版」loon/config-normal.lcf（App Store 3.5.3 用，无 Tailscale/代理链）与",
P2 + "「tvOS 版」loon/config-tvos.lcf（Apple TV 旁路由）分别维护，三份共享同一骨架。",
]) + "\n"

raw = (HERE / "config.lcf").read_text(encoding="utf-8")
beta = raw.replace(BETA_BANNER, "")
lines = beta.split("\n")


def rep(text, old, new, count, label): n = text.count(old); assert n == count, label + ": 期望命中 " + str(count) + " 次，实际 " + str(n) + " 次"; return text.replace(old, new)


block = lambda ls: "\n".join(ls)
span = lambda a, b: "\n".join(lines[[i for i, l in enumerate(lines) if a in l][0]:[i for i, l in enumerate(lines) if b in l][0] + 1])
find1 = lambda sub: [l for l in lines if sub in l][0]

ITEM6 = span("Tailscale 回家：[Proxy]", "上游原行不动")
ITEM8 = span("WARP 代理链：新增", "全流量不从家里出")
ITEM19 = span("19. 新增「落地」层", "本机化参数（2026-11-21")
ITEM20_BODY = span("20. 落地手动策略加入", "本机化参数（2026-11-21").split("\n")[:-2]
LOCAL_LINE = find1("本机化参数（2026-11-21")
LOCALP = span("本机化参数（2026-11-21", "会下发 Fake-IP")
ITEM1LINE = find1("连上家里 Wi-Fi 时同样塌缩为 DIRECT")
TS_NODE = "Tailscale=tailscale, hostname=loon-iphone\n"
HOME_POLICY = "回家手动策略=select, Tailscale, img-url="
LANDING_POLICY = "WARP落地策略=select, WARP节点, img-url=https://raw.githubusercontent.com/Orz-3/mini/master/Color/Global.png\n"
WARP_POLICY = "WARP手动策略=select, WARP代理链, WARP节点, img-url="
WARP_CHAIN_LINE = "WARP代理链 = Tailscale,WARP落地策略, udp=true\n"
LANDING_CHAIN_LINE = "落地代理链 = 落地前置策略,落地出口策略, udp=true\n"
FRONT_POLICY = "落地前置策略=select, 兜底后备策略, Tailscale, img-url=https://raw.githubusercontent.com/Orz-3/mini/master/Color/Global.png\n"
LANDING_MANUAL = "落地手动策略=select, 落地代理链, 落地出口策略, img-url="

# ---------------- 正常版（App Store 3.5.3） ----------------
normal = beta
normal = rep(normal, FILE_LINE, block([
"# 本文件：wenrouXN/proxy-config · loon/config-normal.lcf",
"# 【正常版】面向 App Store 正式版 Loon（3.5.3）：不含 tailscale 节点类型（3.5.4 才有）。",
P2 + "与 Beta 版（loon/config.lcf）的差异仅第 6、8、19 条所述几处，其余逐字一致。",
]), 1, "normal 本文件行")
normal = rep(normal, ITEM6, block([
P2 + "6. （Beta 版）Tailscale 回家——本正常版无此项：3.5.3 不支持 tailscale 节点，",
P5 + "[Proxy] 为空；回家手动策略成员改为 DIRECT（在家局域网直达；在外无回家通道，",
P5 + "回家请用 Beta 版，或单独开 Tailscale App——但与 Loon 不能同时开）。",
P5 + "[General] 的 include-tun 保留：回家网段进隧道后由 home.lsr 交回家手动场景",
]), 1, "normal 第6条")
normal = rep(normal, ITEM8, block([
P2 + "8. （Beta 版）WARP 代理链——本正常版无此项：无 [Proxy Chain] 段与 WARP落地策略组；",
P5 + "WARP手动策略 = WARP节点（默认，与 tvOS 版一致）+ 兜底后备策略（手动后备，",
P5 + "在外无回家通道时切它走机场）；在家场景塌缩 DIRECT，YouTube 由家里 MSM 接管",
]), 1, "normal 第8条")
normal = rep(normal, TS_NODE, "", 1, "normal 删除 Tailscale 节点")
normal = rep(normal, HOME_POLICY, "回家手动策略=select, DIRECT, img-url=", 1, "normal 回家策略")
normal = rep(normal, LANDING_POLICY, "", 1, "normal 删除 WARP落地策略")
normal = rep(normal, WARP_POLICY, "WARP手动策略=select, WARP节点, 兜底后备策略, img-url=", 1, "normal WARP策略")
normal = rep(normal, ITEM19, block([
P2 + "19. （Beta 版）「落地」层——本正常版无代理链：落地代理链与落地前置策略",
P5 + "组不存在；落地手动策略 = 落地出口策略（默认，3.5.3 无链、只能裸节点直用）",
P5 + "+ 兜底后备策略（手动后备）；落地节点过滤器与全球节点排除规则与 Beta 版一致，节点仍",
P5 + "只在落地出口策略里出现、不混入任何通用策略组",
*ITEM20_BODY,
"#",
LOCAL_LINE,
]), 1, "normal 第19条")
normal = rep(normal, FRONT_POLICY, "", 1, "normal 删除落地前置策略")
normal = rep(normal, LANDING_MANUAL, "落地手动策略=select, 落地出口策略, 兜底后备策略, img-url=", 1, "normal 落地手动策略")
normal = rep(normal, WARP_CHAIN_LINE, "", 1, "normal 删除 WARP 链行")
normal = rep(normal, LANDING_CHAIN_LINE, "", 1, "normal 删除落地链行")
normal = rep(normal, "[Proxy Chain]\n", "", 1, "normal 删除代理链段头")
(HERE / "config-normal.lcf").write_text(normal, encoding="utf-8")
print("config-normal.lcf 已生成")

# ---------------- tvOS 版（Apple TV 旁路由） ----------------
tvos = beta
tvos = rep(tvos, FILE_LINE, block([
"# 本文件：wenrouXN/proxy-config · loon/config-tvos.lcf",
"# 【tvOS 旁路由版】用于家里 Apple TV：电视常驻局域网，Loon 在本机主动分流",
P2 + "（不像手机在家时让位给 MSM），故场景不塌缩、DNS 不走家里 Fake-IP 链，",
P2 + "差异见第 1、6、8、19 条与文末本机化参数，其余与 Beta 版逐字一致。",
]), 1, "tvos 本文件行")
tvos = rep(tvos, ITEM1LINE, P5 + "与家里 MSM 的「家宽」组对应；本 tvOS 版场景不塌缩，家宽在本机直接生效）", 1, "tvos 第1条")
tvos = rep(tvos, ITEM6, block([
P2 + "6. （Beta 版）Tailscale 回家——本 tvOS 版无此项：电视本就在家里，局域网直达；",
P5 + "回家手动策略成员为 DIRECT，home.lsr 照常绑定（效果即局域网直连）；",
P5 + "[General] 不设 include-tun（局域网段由上游 bypass-tun 原生绕过隧道）",
]), 1, "tvos 第6条")
tvos = rep(tvos, ITEM8, block([
P2 + "8. （Beta 版）WARP 代理链——本 tvOS 版无此项：电视与 WARP 容器同在局域网，",
P5 + "无 [Proxy Chain] 段与 WARP落地策略组；WARP手动策略直接选 WARP节点",
P5 + "（192.168.1.251:1080），兜底后备策略作手动后备",
]), 1, "tvos 第8条")
tvos = rep(tvos, ITEM19, block([
P2 + "19. （Beta 版）「落地」层——本 tvOS 版无代理链：电视直连 URnetwork 端点",
P5 + "即可，落地手动策略 = 落地出口策略（默认）+ 兜底后备策略（手动后备）；",
P5 + "落地前置策略组不存在；落地节点过滤器与全球节点排除规则与 Beta 版一致",
*ITEM20_BODY,
"#",
LOCAL_LINE,
]), 1, "tvos 第19条")
tvos = rep(tvos, LOCALP, block([
"# 本机化参数（tvOS 版）：",
P2 + "- 无 SSID 参数：全部场景组已去掉「HOMEair=DIRECT」，全网一致不塌缩",
P2 + "- DNS 用公共 DNS（见 [General]），不经家里 MosDNS，避免拿到 28.x Fake-IP",
P2 + "- [Host] 为空（原 SSID DNS 行已移除）",
]), 1, "tvos 本机化参数")
tvos = rep(tvos, "dns-server=system", "dns-server=223.5.5.5, 8.8.8.8", 1, "tvos dns-server")
tvos = rep(tvos, "include-tun=192.168.1.0/24, 100.64.0.0/10\n", "", 1, "tvos 删除 include-tun")
tvos = rep(tvos, ', "HOMEair"=DIRECT', "", 23, "tvos 场景去塌缩")
tvos = rep(tvos, TS_NODE, "", 1, "tvos 删除 Tailscale 节点")
tvos = rep(tvos, HOME_POLICY, "回家手动策略=select, DIRECT, img-url=", 1, "tvos 回家策略")
tvos = rep(tvos, LANDING_POLICY, "", 1, "tvos 删除 WARP落地策略")
tvos = rep(tvos, WARP_POLICY, "WARP手动策略=select, WARP节点, 兜底后备策略, img-url=", 1, "tvos WARP策略")
tvos = rep(tvos, FRONT_POLICY, "", 1, "tvos 删除落地前置策略")
tvos = rep(tvos, LANDING_MANUAL, "落地手动策略=select, 落地出口策略, 兜底后备策略, img-url=", 1, "tvos 落地手动策略")
tvos = rep(tvos, WARP_CHAIN_LINE, "", 1, "tvos 删除 WARP 链行")
tvos = rep(tvos, LANDING_CHAIN_LINE, "", 1, "tvos 删除落地链行")
tvos = rep(tvos, "[Proxy Chain]\n", "", 1, "tvos 删除代理链段头")
tvos = rep(tvos, "ssid: HOMEair=server: 192.168.1.2\n", "", 1, "tvos 删除 Host 行")
(HERE / "config-tvos.lcf").write_text(tvos, encoding="utf-8")
print("config-tvos.lcf 已生成")

# ---------------- Beta 版补三变体说明（幂等） ----------------
new_raw = beta.replace(FILE_LINE, FILE_LINE + "\n" + BETA_BANNER.rstrip("\n"), 1)
(HERE / "config.lcf").write_text(new_raw, encoding="utf-8")
print("config.lcf 已补三变体说明")
