---
name: context-used-guardian
publisher: pettercc2024-create
description: Context monitoring and resource protection plugin for OpenClaw. Monitors RAM/VRAM usage and token consumption to prevent system crashes (local models) or billing surges (cloud models). Automatically triggers warnings and circuit breakers (/new) when context exceeds safe thresholds. Supports multi-GPU VRAM aggregation, logging, and environment variable configuration. Use when: (1) Running local models and need to prevent VRAM overflow, (2) Using cloud models and want to avoid token blackhole billing, (3) Managing long immersive conversations, (4) Setting up context usage alerts for complex tasks, (5) Multi-GPU setups with aggregated monitoring.
---

# ContextUsed-Guardian (CUG)

上下文使用监控与资源保护插件，防止系统因上下文堆积而崩溃或计费激增。

## 核心功能

1. **硬件感知** - 自动检测 RAM 和 VRAM 配置（支持多 GPU 聚合）
2. **智能阈值计算** - 根据硬件和模型参数计算安全边界
3. **分级防护** - 预警 → 熔断双阶段保护
4. **自动操作** - 达到熔断线时自动执行 `/new` 切换会话
5. **日志记录** - 完整的运行日志和警报记录
6. **环境变量配置** - 支持灵活的参数配置
7. **上下文保留** - 新会话自动继承当前对话历史

## 工作原理

### 阈值计算公式

**本地模型模式** (有 VRAM):
```
S = (RAM GB + VRAM GB) ÷ 2
P = (S ÷ 模型参数B) × 100%
```

**云端模式** (无 VRAM):
```
S = RAM GB
P = (S ÷ 模型参数B) × 100%
```

### 防护阶段

**第一阶段：预警**
- 条件：Context Used ≥ P%
- 动作：发送高亮警告，提醒注意资源消耗

**第二阶段：熔断**
- 条件：Context Used ≥ 1.5 × P%
- 动作：自动执行 `/new`，彻底防止宕机/过度计费

## 使用场景

### 场景 1：高性能本地工作站
- **硬件**：64G RAM + 32G VRAM
- **模型**：48B 参数
- **预警线**：100%
- **熔断线**：150%

### 场景 2：低配本地运行
- **硬件**：16G RAM + 8G VRAM
- **模型**：32B 参数
- **预警线**：37.5%
- **熔断线**：56%

### 场景 3：云端 API 调用
- **硬件**：16G RAM
- **模型**：16B 参数
- **预警线**：100%
- **熔断线**：150%

## 配置方法

### 1. 安装依赖

```bash
pip install psutil pynvml
```

### 2. 配置硬件参数

编辑 `references/config.json`:

```json
{
  "hardware": {
    "ram_gb": 16,
    "vram_gb": 8
  },
  "models": {
    "deepseek-v3:16b": 16,
    "qwen2.5-7b": 7,
    "default": 7
  }
}
```

**配置说明**：
- `hardware.ram_gb`: 系统内存大小 (GB)
- `hardware.vram_gb`: NVIDIA 显存大小 (GB)
- `models.{模型名}`: 模型参数量，用于计算阈值

**默认模型**：当模型名称无法匹配时，使用 `models.default`

### 3. 启动监控

#### 方式 A：Python 脚本检查

```bash
cd "C:\Users\Administrator\.openclaw\skills\context-used-guardian\scripts"
python context_guardian.py check
```

#### 方式 B：持续监控模式

```bash
python context_guardian.py start
```

按 `Ctrl+C` 停止监控。

#### 方式 C：获取状态

```bash
python context_guardian.py status
```

## 与 OpenClaw 集成

### 1. 环境变量自动读取

CUG 自动从 OpenClaw 环境变量读取：
- `OLLAMA_MODEL` - 当前运行的模型名称
- `OPENCLAW_CONTEXT_USED` - 当前上下文使用百分比

### 2. 自动执行 /new

当达到熔断线时，CUG 会自动尝试执行 `/new` 命令：
- 打印熔断警告到控制台
- 发送 `/new` 指令到会话流
- 切换到新会话以保护资源

**注意**：具体执行效果取决于 OpenClaw 的会话管理 API。

### 3. 警报集成

在 `execute_new_command()` 方法中，可以集成到 OpenClaw 的消息系统：
- 微信消息通知
- 邮件报警
- Webhook 回调

## 故障排查

### 问题：检测不到显存

**原因**：pynvml 依赖未正确安装或无 NVIDIA GPU

**解决**：
```bash
pip install pynvml
# 检查 GPU 是否被识别
nvidia-smi
```

### 问题：阈值计算不准确

**原因**：配置文件中的硬件参数不正确

**解决**：使用 `python context_guardian.py status` 检查当前检测到的硬件信息，并更新配置文件

### 问题：无法执行 /new

**原因**：OpenClaw 会话管理 API 需要自定义集成

**解决**：在 `execute_new_command()` 方法中根据实际 API 进行修改

## 注意事项

1. **首次运行会自动检测硬件**，之后可在配置文件中手动调整
2. **模型名称必须与 OpenClaw 中使用的名称一致**（区分大小写）
3. **持续监控模式下**，按 `Ctrl+C` 不会立即停止，需要等待当前检查周期结束
4. **云端模式**（无 VRAM）使用 RAM 作为安全边界，建议将 `vram_gb` 设置为 0 或留空
5. **参数量提取**支持从模型名称自动提取（如 `deepseek-v3:16b` → 16）

## 快速开始

```bash
# 1. 安装依赖
pip install psutil pynvml

# 2. 配置文件（可选，首次运行会自动检测）
# 编辑 references/config.json

# 3. 检查当前状态
python context_guardian.py status

# 4. 启动持续监控
python context_guardian.py start
```

## 技术细节

### 监控指标

- **RAM 使用率**：来自 psutil.virtual_memory()
- **VRAM 使用量**：来自 pynvml.nvmlDeviceGetMemoryInfo()
- **上下文使用率**：来自 `OPENCLAW_CONTEXT_USED` 环境变量

### 配置持久化

- 硬件配置保存在 `config.json`
- 会话统计保存在 `session_stats.json`
- 文件位置：`C:\Users\Administrator\.openclaw\skills\context-used-guardian\`

### 扩展建议

- **实时通知**：集成钉钉/企业微信/Slack Webhook
- **历史记录**：保存监控日志用于分析
- **自适应调整**：根据实际使用情况动态调整阈值
- **多模型支持**：支持多 GPU 环境下的显存聚合统计