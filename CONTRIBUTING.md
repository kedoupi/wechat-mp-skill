# Contributing

Thanks for your interest in improving `wechat-mp`.

## Development setup

```bash
git clone https://github.com/kedoupi/wechat-mp-skill.git
cd wechat-mp-skill
npx skills add ./ --list
bash tests/run.sh
```

## Guidelines

1. Keep `skills/wechat-mp/SKILL.md` under ~500 lines.
2. Do not hardcode private credentials.
3. Scripts must resolve their own directory with `pwd -P` for symlink installs.
4. Keep the default README in **English**; update `README.zh-CN.md` for user-facing changes.
5. Bump `metadata.version` in `SKILL.md` when behavior changes.
6. Keep `--dry-run` offline / side-effect free.

## Validation

```bash
bash tests/run.sh
bash skills/wechat-mp/scripts/wechat-mp --help
bash skills/wechat-mp/scripts/wechat-mp doctor
bash skills/wechat-mp/scripts/wechat-mp new-out --title "Test" --base /tmp/wechat-mp-out
```
