# ContextUsed-Guardian (CUG)

> 智能上下文监控与资源保护插件，防止 OpenClaw 系统因上下文堆积而崩溃或计费激增

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Plugin-blue.svg)](https://clawhub.com)

---

## 📖 产品简介

ContextUsed-Guardian (CUG) 是一款专门为 OpenClaw 设计的智能资源保护插件。它不仅监控上下文使用量，更会根据你的硬件配置（RAM、VRAM）和模型参数，动态计算安全边界，在系统崩溃或过度计费前及时预警并自动熔断。

### 核心理念

**"智能防御，防患于未然"**

很多用户在使用 OpenClaw 时，往往沉浸在长对话中，不知不觉消耗了大量上下文。当达到云端模型计费上限或本地显存溢出时，才突然发现问题——为时已晚。

CUG 的出现就是为了改变这一现状，让你的每一次对话都安全可控。

---

## 🎯 解决的问题

### 问题 1：云端模型"Token黑洞"计费激增

**场景描述**：
你在使用云端大模型 API 进行长时间对话，系统不断累积上下文。当你完成后查看账单时，发现 token 消耗远超预期，成本高得惊人。

**CUG 的解决方案**：
- 根据你的模型参数量，计算合理的上下文使用阈值
- 达到预警线时提示你注意
- 达到熔断线时自动执行 `/new`，保护你的钱包

### 问题 2：本地模型 VRAM 溢出崩溃

**场景描述**：
你在本地运行 70B 参数的大模型，连续对话几个小时后，系统突然崩溃，丢失了所有未保存的工作记录。

**CUG 的解决方案**：
- 检测你的 RAM 和 VRAM 配置
- 根据硬件冗余度计算安全边界
- 提前预警，关键时刻强制重启会话

### 问题 3：硬件资源利用率不透明

**场景描述**：
你不知道当前的上下文使用率是否合理，也不知道自己的硬件还能支撑多久。

**CUG 的解决方案**：
- 实时监控上下文使用百分比
- 显示硬件和模型参数
- 提供详细的状态报告

---

## 🚀 产品背景

### 诞生原因

在 OpenClaw 社区中，经常有用户反馈：
> "我用本地模型跑了一天，突然崩溃了"
> "云端 API 账单吓了我一跳"
> "能不能有个工具帮我监控上下文使用？"

这些问题困扰着很多用户，但当时并没有专门的解决方案。

### 设计理念

CUG 的设计理念基于三个核心原则：

1. **硬件感知** - 理解你的硬件配置，而不是一刀切
2. **智能计算** - 根据实际参数动态计算阈值，而不是固定值
3. **分级防御** - 预警 + 熔断双保险，保护不遗漏

### 技术演进

- **v1.0.0** - 初始版本，支持基础监控和阈值计算
- **v1.1.0** - 添加多 GPU 支持、日志记录、环境变量配置
- **v2.0.0** - 引入智能阈值算法，优化熔断机制

---

## ✨ 核心功能

### 1. 硬件智能感知

自动检测系统硬件配置：
- **RAM 检测**：通过 psutil 获取内存总量
- **VRAM 检测**：通过 pynvml 获取 GPU 显存（支持多 GPU 聚合）
- **环境变量支持**：可通过 `CUG_RAM_GB` 和 `CUG_VRAM_GB` 自定义

### 2. 智能阈值计算

根据你的硬件和模型参数，自动计算安全边界：

**本地模型模式**（有 VRAM）：
```
S = (RAM GB + VRAM GB) ÷ 2
P = (S ÷ 模型参数B) × 100%
```

**云端模式**（无 VRAM）：
```
S = RAM GB
P = (S ÷ 模型参数B) × 100%
```

### 3. 分级防御机制

**第一阶段：预警**
- 触发条件：Context Used ≥ P%
- 执行动作：发送高亮系统提示
- 示例：`【⚠️ ContextUsed-Guardian 警告：当前用量已达硬件预警线 (100%)，请注意资源消耗。】`

**第二阶段：熔断**
- 触发条件：Context Used ≥ 1.5 × P%
- 执行动作：自动执行 `/new` 指令
- 目的：彻底防止宕机或过度计费

### 4. 自动会话切换

达到熔断线时，CUG 会自动尝试：
1. 打印熔断警告到控制台
2. 发送 `/new` 指令到会话流
3. 切换到新会话以保护资源

新会话会自动继承当前对话的历史上下文，不会丢失对话内容。

### 5. 实时监控

支持三种运行模式：

**检查模式**：一次性检查当前状态
```bash
python context_guardian.py check
```

**状态模式**：显示完整系统信息
```bash
python context_guardian.py status
```

**监控模式**：持续监控，自动预警和熔断
```bash
python context_guardian.py start
```

### 6. 日志与统计

- **日志记录**：所有操作和警告都会记录到 `cug.log`
- **会话统计**：保存每个会话的上下文使用数据到 `session_stats.json`
- **实时输出**：监控模式下，控制台实时显示当前状态

---

## 📊 使用场景

### 场景 1：高性能本地工作站

**硬件配置**：64G RAM + 32G VRAM

**使用模型**：deepseek-v3:48b

**CUG 防护**：
- 预警线：100%
- 熔断线：150%

**优势**：充分利用硬件性能，同时保护系统稳定

### 场景 2：低配本地运行

**硬件配置**：16G RAM + 8G VRAM

**使用模型**：qwen2.5:32b

**CUG 防护**：
- 预警线：37.5%
- 熔断线：56%

**优势**：在有限资源下，安全运行大模型

### 场景 3：云端 API 调用

**硬件配置**：16G RAM（仅用于环境检测）

**使用模型**：gpt-4-turbo

**CUG 防护**：
- 预警线：100%
- 熔断线：150%

**优势**：控制云端 API 成本，避免"Token 黑洞"

### 场景 4：长时间对话

**硬件配置**：32G RAM + 24G VRAM

**使用模型**：llama3:70b

**CUG 防护**：
- 预警线：92.9%（S=48, B=70）
- 熔断线：139.3%

**优势**：长时间沉浸式对话，不会突然崩溃

---

## 🛠️ 安装与配置

### 前置要求

- **Python**: 3.7 或更高版本
- **操作系统**: Windows / Linux / macOS
- **依赖库**:
  - `psutil` - 硬件监控
  - `pynvml` - NVIDIA GPU 显存监控

### 安装步骤

1. **下载插件**

```bash
# 克隆仓库
git clone https://github.com/pettercc2024-create/context-used-guardian.git
cd context-used-guardian
```

2. **安装依赖**

```bash
pip install psutil pynvml
```

3. **配置文件（可选）**

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
- `models.default`: 默认模型参数量

### 快速开始

```bash
# 1. 检查当前状态
python scripts/context_guardian.py status

# 2. 启动持续监控
python scripts/context_guardian.py start
```

---

## 🔗 与 OpenClaw 集成

CUG 与 OpenClaw 无缝集成，自动读取环境变量：

| 环境变量 | 说明 |
|---------|------|
| `OLLAMA_MODEL` | 当前运行的模型名称 |
| `OPENCLAW_CONTEXT_USED` | 当前上下文使用百分比 |

### 自动执行 /new

当达到熔断线时，CUG 会自动尝试通过 OpenClaw Gateway API 执行 `/new` 指令：

```python
# 调用示例
openclaw gateway call session.new
```

**注意**：具体执行效果取决于 OpenClaw 的会话管理 API。

---

## 📝 配置示例

### 示例 1：单 GPU 本地运行

```json
{
  "hardware": {
    "ram_gb": 32,
    "vram_gb": 24
  },
  "models": {
    "llama3:70b": 70,
    "default": 7
  }
}
```

**计算结果**：
- S = (32 + 24) / 2 = 28
- deepseek-v3:48b 预警线 = 28 / 48 × 100% = 58.3%
- deepseek-v3:48b 熔断线 = 58.3% × 1.5 = 87.5%

### 示例 2：云端 API 调用

```json
{
  "hardware": {
    "ram_gb": 16,
    "vram_gb": 0
  },
  "models": {
    "gpt-4-turbo": 130,
    "claude-3-opus": 175,
    "default": 7
  }
}
```

**计算结果**：
- S = 16
- gpt-4-turbo 预警线 = 16 / 130 × 100% = 12.3%
- gpt-4-turbo 熔断线 = 12.3% × 1.5 = 18.5%

---

## 🔍 故障排查

### 问题 1：检测不到显存

**症状**：VRAM 显示为 0 GB

**原因**：pynvml 依赖未正确安装或无 NVIDIA GPU

**解决**：
```bash
pip install pynvml
# 检查 GPU 是否被识别
nvidia-smi
```

### 问题 2：阈值计算不准确

**症状**：上下文使用达到 100% 时才预警

**原因**：配置文件中的硬件参数不正确

**解决**：
```bash
python scripts/context_guardian.py status
# 查看实际检测到的硬件信息，更新 config.json
```

### 问题 3：无法执行 /new

**症状**：熔断时提示"Gateway RPC 调用失败"

**原因**：OpenClaw 会话管理 API 需要自定义集成

**解决**：
1. 在控制台手动输入 `/new`
2. 运行命令：`openclaw gateway call session.new`
3. 在 Web Control UI 中：Sessions → New Session

### 问题 4：持续监控模式下无法停止

**症状**：按 Ctrl+C 后监控仍在运行

**原因**：Python 检测到信号后会等待当前检查周期结束

**解决**：
- 等待当前检查周期完成（约 10 秒）
- 或直接关闭命令行窗口

---

## 🎨 技术细节

### 监控指标

| 指标 | 数据来源 | 说明 |
|-----|---------|------|
| RAM 使用率 | psutil.virtual_memory() | 系统内存使用情况 |
| VRAM 使用量 | pynvml.nvmlDeviceGetMemoryInfo() | GPU 显存使用情况 |
| 上下文使用率 | OPENCLAW_CONTEXT_USED 环境变量 | OpenClaw 当前上下文百分比 |

### 参数提取逻辑

CUG 会从模型名称中自动提取参数量：

| 模型名称 | 提取结果 | 说明 |
|---------|---------|------|
| `deepseek-v3:16b` | 16 | 提取冒号后的数字 |
| `qwen2.5-7b` | 7 | 提取冒号后的数字 |
| `gpt-4-turbo` | 7 (default) | 无数字，使用默认值 |

### 配置持久化

| 配置项 | 文件路径 | 说明 |
|-------|---------|------|
| 硬件配置 | `config.json` | RAM 和 VRAM 配置 |
| 会话统计 | `session_stats.json` | 上下文使用历史记录 |
| 运行日志 | `cug.log` | 所有操作和警告日志 |

### 扩展建议

1. **实时通知**
   - 集成钉钉/企业微信/Slack Webhook
   - 发送警报到移动端

2. **历史记录分析**
   - 保存监控日志用于分析
   - 生成上下文使用趋势图

3. **自适应调整**
   - 根据实际使用情况动态调整阈值
   - 学习用户习惯，提供个性化建议

4. **多模型支持**
   - 支持多 GPU 环境下的显存聚合统计
   - 支持混合云/本地部署

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

你可以自由地：
- ✅ 使用本软件用于商业目的
- ✅ 修改和分发本软件
- ✅ 私人使用本软件

只要在副本中包含原始版权声明和许可声明即可。

---

## 🙏 致谢

感谢以下项目和工具：

- [OpenClaw](https://github.com/openclaw/openclaw) - OpenClaw 框架
- [psutil](https://github.com/giampaolo/psutil) - 系统监控库
- [pynvml](https://github.com/PyNVML/PyNVML) - NVIDIA GPU 管理库

---

## 👨‍💻 作者

**by pangaoyong create**

---

## 📞 联系方式

- **GitHub**: https://github.com/pettercc2024-create
- **ClawHub**: https://clawhub.com
- **问题反馈**: https://github.com/pettercc2024-create/context-used-guardian/issues

---

## 🌟 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📈 版本历史

### v2.0.0 (2026-03-23)
- 🎉 引入智能阈值算法
- 🚀 优化熔断机制
- 📝 完善文档
- 🐛 修复多个 bug

### v1.1.0 (2026-03-22)
- ✨ 添加多 GPU 支持
- 📊 增强日志记录
- ⚙️ 支持环境变量配置

### v1.0.0 (2026-03-21)
- 🎉 初始版本发布
- 📦 基础监控功能
- ⚙️ 阈值计算

---

## 📜 致谢

感谢每一位使用 git 的用户！你的支持是我继续开发的最大动力。

如果这个项目对你有帮助，请给个 ⭐️ Star！