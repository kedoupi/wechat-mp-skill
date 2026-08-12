# wechat-mp（微信公众号 Skill）

面向 AI Agent 的**微信公众号**技能：默认在本地写出一篇可用的成稿；可与 kedoupi 套件中的生图、飞书推送**组合**；在配置 appid 且用户明确授权后，可推入**草稿箱**。

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

## 对 Agent 怎么说

- 「写一篇关于 … 的公众号」→ 本地 `article.md`
- 「完整制作一篇公众号」→ 成稿 +（若已装 tzai）封面 + `preview.html`
- 「推到草稿箱」→ 调用微信草稿 API（需确认与配置）

## 安全默认

| 动作 | 默认 |
| --- | --- |
| 本地成稿 | 开 |
| 生图（可能产生费用） | 关，需明确配图/完整制作 |
| 飞书通知 | 关 |
| 微信草稿 | 关；**不做一键群发** |

## CLI 摘要

在**内容项目根目录**执行，产物会落在该项目的 `./wechat-mp-out/`，下次写作可当作历史资料：

```bash
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp doctor
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp list-out    # 本项目历史成稿
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp new-out --title "选题"
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp preview --dir ./wechat-mp-out/<slug>
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp draft --dir ./wechat-mp-out/<slug> --dry-run
```

本地预览只做**结构自检**，不是公众号编辑器的像素级还原。

## 微信开放平台注意

- 草稿接口权限以[微信公众平台](https://mp.weixin.qq.com/)当前规则为准（类型/认证可能影响可用性）。  
- 推草稿必须有封面图。  
- 密钥写在 durable 配置中，不要放进 skill 包目录。

## 相关

- 英文 README：[README.md](./README.md)  
- 套件父仓：[kedoupi/skills](https://github.com/kedoupi/skills)  

## License

MIT
