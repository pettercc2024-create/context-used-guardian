# ContextUsed-Guardian 使用指南

## 快速开始

### 1. 安装依赖
```bash
pip install psutil pynvml
```

### 2. 检查当前状态
```bash
cd C:\Users\Administrator\.openclaw\skills\context-used-guardian\scripts
python context_guardian.py status
```

### 3. 启动持续监控
```bash
python context_guardian.py start
```
按 `Ctrl+C` 停止监控。

### 4. 单次检查
```bash
python context_guardian.py check
```

## 配置说明

编辑 `references/config.json`：

```json
{
  "hardware": {
    "ram_gb": 16,
    "vram_gb": 8
  },
  "models": {
    "deepseek-v3:16b": 16,
    "deepseek-v3:32b": 32,
    "qwen2.5-7b": 7,
    "qwen2.5-14b": 14,
    "qwen2.5-32b": 32,
    "default": 7
  }
}
```

### 配置项说明

- **hardware.ram_gb**: 系统内存大小 (GB)
- **hardware.vram_gb**: NVIDIA 显存大小 (GB)
  - 云端模式（无 GPU）设置为 0 或留空
- **models.模型名**: 模型参数量，用于计算阈值
- **models.default**: 默认模型参数量（无法识别时使用）

## 工作原理

### 阈值计算

**本地模式** (有 VRAM):
```
S = (RAM + VRAM) ÷ 2
P = (S ÷ 模型参数B) × 100%
```

**云端模式** (无 VRAM):
```
S = RAM
P = (S ÷ 模型参数B) × 100%
```

### 防护阶段

- **预警** (P%): 发送警告提醒
- **熔断** (1.5×P%): 自动执行 `/new` 切换会话

## 注意事项

1. 首次运行会自动检测硬件
2. 模型名称必须与 OpenClaw 中一致
3. 持续监控模式下需等待当前周期结束
4. 建议定期更新配置文件中的硬件参数

## 故障排查

### 检测不到显存
```bash
pip install nvidia-ml-py  # 替代 pynvml
nvidia-smi  # 检查 GPU 是否被识别
```

### 阈值不准确
运行 `python context_guardian.py status` 查看检测结果，然后更新配置文件

### 无法执行 /new
需要根据 OpenClaw API 自定义 `execute_new_command()` 方法

## 技术支持

详细文档请参考 `SKILL.md` 文件。

## 文件结构

```
context-used-guardian/
├── SKILL.md                      # 完整文档
├── README-CN.md                  # 本文件
├── scripts/
│   └── context_guardian.py      # 核心脚本
└── references/
    ├── config.json              # 配置文件
    └── quick-start.md           # 快速入门
```