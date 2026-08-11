# WeChat platform constraints (authoring notes)

## HTML / 排版

- 正文样式以**内联 style** 为主；公众号编辑器对外部 CSS / `<style>` / JS 支持差或直接剥离。  
- 外链在 App 内常不可点：转换时会把链接做成脚注。  
- 原生列表渲染不稳定：转换器用 section 化列表。  
- `preview.html` 只做结构自检，**不是**编辑器像素级还原。

## 图片

- 草稿正文图需上传微信（`uploadimg`）拿到 CDN URL。  
- 封面必须有 `thumb_media_id`（永久素材），否则 `draft/add` 失败。  
- 单图建议 < 5MB；JPG/PNG 常见更稳。

## 草稿 API

- 使用 `draft/add`；本 skill **不提供一键群发**。  
- 需公众号具备相应接口权限（以微信公众平台当前规则为准）。  
- JSON 必须 `ensure_ascii=False`，否则中文标题/正文会异常。

## 合规

- 默认只到本地成稿或草稿箱。  
- AI 辅助披露：按 style `aigc_disclosure` 询问用户，不强行插入。
