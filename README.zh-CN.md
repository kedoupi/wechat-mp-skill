# wechat-mp（微信公众号 Skill）

面向 AI Agent 的**微信公众号**技能：默认在本地写出一篇可用的成稿；可与 kedoupi 套件中的生图、飞书推送**组合**；在配置 appid 且用户明确授权后，可推入**草稿箱**。

英文版：[README.md](./README.md)

## 你能做到哪一步（按需升级）

| 层级 | 目标 | 要不要凭证 |
| --- | --- | --- |
| **A — 写作** | 本地 `article.md` + 审稿轨 | 不需要 |
| **B — 成套** | 成稿 + 封面（tzai-image）+ `preview.html` | 不要 appid；生图才需要 tzai key |
| **C — 草稿箱** | 推到微信**草稿箱**（不是群发） | 需要 appid + secret |

| 场景 | 安装 |
| --- | --- |
| 只写公众号文稿 | `npx skills add kedoupi/wechat-mp-skill` |
| 文稿 + 封面配图 | 再装 [tzai-image-skill](https://github.com/kedoupi/tzai-image-skill) |
| + 飞书完成通知 | 再装 [lark-push-skill](https://github.com/kedoupi/lark-push-skill) |
| + 推微信草稿箱 | `wechat-mp init --appid … --secret …` |

**写作成稿 / 本地预览不需要公众号 appid。**

## 安装

```bash
npx skills add kedoupi/wechat-mp-skill
# 或装到所有 Agent：
npx skills add kedoupi/wechat-mp-skill -g --all
```

依赖：`python3`（预览与草稿辅助脚本）。

### 安装后（复制粘贴）

`npx skills add` **只装代码**，不会自动写密钥或文风。请自行（或让 Agent）执行：

```bash
SK=~/.agents/skills/wechat-mp

# 随时可跑：环境自检（缺草稿配置会打印可复制 init）
bash $SK/scripts/wechat-mp doctor

# 可选：账号文风（不要 appid）→ ~/.config/kedoupi/wechat-mp/style.yaml
bash $SK/scripts/wechat-mp init-style

# 可选：仅在需要推草稿箱时
bash $SK/scripts/wechat-mp init \
  --appid 'wx_YOUR_APPID' \
  --secret 'YOUR_APPSECRET'
# 若官方 API 被 IP 白名单拦住，再加：
#   --api-base 'https://YOUR_PROXY_HOST'
# → ~/.config/kedoupi/wechat-mp/config.env  (chmod 600)
```

**不要**把密钥只写在 skill 包目录里（`npx skills update` 会清空）。  
**不要**为了本 skill 去改 `~/.zshrc`——优先用 `init` 写配置文件。

## 对 Agent 怎么说

- 「写一篇关于 … 的公众号」→ 本地 `article.md`（模式 A）
- 「完整制作一篇公众号」→ 成稿 +（若已装 tzai）封面 + `preview.html`（模式 B）
- 「推到草稿箱」→ 确认后调用草稿 API（模式 C）

## 第一篇（CLI）

在**内容项目根目录**执行，历史会落在该项目的 `./wechat-mp-out/`：

```bash
SK=~/.agents/skills/wechat-mp

bash $SK/scripts/wechat-mp doctor
bash $SK/scripts/wechat-mp new-out --title "选题"
# 编辑 ./wechat-mp-out/<slug>/article.md（通常由 Agent 写）
bash $SK/scripts/wechat-mp preview --dir ./wechat-mp-out/<slug>
bash $SK/scripts/wechat-mp list-out

# 推草稿前先 dry-run（需 init + 封面图才可真推）
bash $SK/scripts/wechat-mp draft --dir ./wechat-mp-out/<slug> --dry-run
```

本地预览只做**结构自检**，不是公众号编辑器的像素级还原。

## 安全默认

| 动作 | 默认 |
| --- | --- |
| 本地成稿 | 开 |
| 生图（可能产生费用） | 关，需明确配图/完整制作 |
| 飞书通知 | 关 |
| 微信草稿 | 关；**不做一键群发** |
| `--dry-run` | 不访问微信网络 |

## 配置

### 凭证（仅草稿箱）

| 变量 | 含义 |
| --- | --- |
| `WECHAT_MP_APPID` | 公众号 appid |
| `WECHAT_MP_SECRET` | AppSecret |
| `WECHAT_MP_AUTHOR` | 可选默认作者 |
| `WECHAT_MP_API_BASE` | 可选 API 主机（IP 白名单代理） |
| `WECHAT_MP_CONFIG` | 可选显式配置文件路径 |

推荐路径（`init` 默认）：

```text
~/.config/kedoupi/wechat-mp/config.env
```

### 账号文风（`style.yaml`）

```bash
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp init-style
# → ~/.config/kedoupi/wechat-mp/style.yaml
```

| 字段 | 作用 |
| --- | --- |
| `positioning` | 一句话账号定位 |
| `topics` | 选题边界 |
| `voice` | `clear-judgment`（默认）· `warm-practical` · `sharp-brief` |
| `taboo` | 硬禁忌（禁止编造等） |
| `aigc_disclosure` | `ask` · `always` · `never` |

查看生效配置：

```bash
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp which-config
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp doctor
```

## 产物目录（跟内容项目走）

```text
<你的内容项目>/
  wechat-mp-out/            # 项目内历史（list-out 读这里）
    README.md
    <slug>/
      manifest.json
      brief.md
      article.md
      cover.png             # 真推草稿箱需要封面
      figures/
      preview.html
```

## 微信开放平台注意

- 草稿接口权限以[微信公众平台](https://mp.weixin.qq.com/)当前规则为准（类型/认证可能影响可用性）。  
- 推草稿必须有封面图。  
- 密钥写在 durable 配置中，不要放进 skill 包目录。

## 相关

- 英文 README：[README.md](./README.md)  
- 生图：[tzai-image-skill](https://github.com/kedoupi/tzai-image-skill)  
- 飞书：[lark-push-skill](https://github.com/kedoupi/lark-push-skill)  
- 套件父仓：[kedoupi/skills](https://github.com/kedoupi/skills)  

## License

MIT
