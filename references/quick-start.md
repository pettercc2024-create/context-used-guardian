# ContextUsed-Guardian 快速开始

## 一键启动检查

```bash
cd C:\Users\Administrator\.openclaw\skills\context-used-guardian\scripts
python context_guardian.py check
```

## 持续监控模式

```bash
python context_guardian.py start
```

## 查看系统状态

```bash
python context_guardian.py status
```

## 配置示例

编辑 `config.json`:

```json
{
  "hardware": {
    "ram_gb": 64,
    "vram_gb": 32
  },
  "models": {
    "deepseek-v3:16b": 16,
    "default": 7
  }
}
```

## 常见问题

**Q: 如何添加新的模型配置？**
A: 在 `models` 节点中添加：`"模型名": 参数量`

**Q: 如何知道当前检测到的硬件信息？**
A: 运行 `python context_guardian.py status` 查看

**Q: 如何禁用监控？**
A: 删除或重命名脚本文件即可