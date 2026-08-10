# wechat-mp

[一句话说明这个 skill 做什么。]

## 安装

```bash
npx skills add kedoupi/wechat-mp-skill -g --all
```

## 前置条件

1. [所需 CLI / 鉴权 / 权限]

## 快速开始

```bash
# 安装后一次性配置
bash <skill-dir>/scripts/wechat-mp init --chat-id <id>

# 预览（仅本地，无副作用）
bash <skill-dir>/scripts/wechat-mp --dry-run --title "Hello" --body "- item"

# 正式执行
bash <skill-dir>/scripts/wechat-mp --title "Hello" --body "World"
```

## 开发

```bash
bash tests/run.sh
npx skills add ./ --list
```

## 许可证

[MIT](./LICENSE)
