# ContextUsed-Guardian 环境变量配置

## 环境变量优先级

CUG 按以下优先级读取硬件配置：

1. **环境变量**（最高优先级）
2. **自动检测**（默认）
3. **配置文件**（手动指定）

## 环境变量说明

### CUG_RAM_GB

指定系统内存大小（GB）

**作用**：覆盖自动检测的 RAM 值

**示例**：
```bash
# Windows PowerShell
$env:CUG_RAM_GB="32"
python context_guardian.py start

# Windows CMD
set CUG_RAM_GB=32
python context_guardian.py start

# Linux/Mac
export CUG_RAM_GB=32
python context_guardian.py start
```

### CUG_VRAM_GB

指定 NVIDIA 显存大小（GB）

**作用**：
- 云端模式（无 GPU）：设置为 0 或留空
- 多 GPU：设置为总显存（自动检测会聚合所有 GPU）

**示例**：
```bash
# 单 GPU 设置
$env:CUG_VRAM_GB="16"
python context_guardian.py start

# 多 GPU 设置（总显存）
$env:CUG_VRAM_GB="48"
python context_guardian.py start
```

## 使用场景

### 场景 1：自动化部署

```bash
# 设置环境变量后启动
$env:CUG_RAM_GB="64"
$env:CUG_VRAM_GB="32"
python context_guardian.py start
```

### 场景 2：云端 API 模式

```bash
# 云端模式：无 GPU，只使用 RAM
$env:CUG_RAM_GB="16"
$env:CUG_VRAM_GB="0"
python context_guardian.py start
```

### 场景 3：远程服务器

```bash
# SSH 远程启动，通过环境变量配置
ssh user@server
$env:CUG_RAM_GB="32"
$env:CUG_VRAM_GB="24"
cd ~/context-used-guardian/scripts
python context_guardian.py start
```

## 日志配置

### CUG_LOG_LEVEL

设置日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）

**默认**：DEBUG

**示例**：
```bash
$env:CUG_LOG_LEVEL="INFO"
python context_guardian.py start
```

### CUG_LOG_PATH

自定义日志文件路径

**默认**：`C:\Users\Administrator\.openclaw\skills\context-used-guardian\cug.log`

**示例**：
```bash
$env:CUG_LOG_PATH="D:\Logs\cug.log"
python context_guardian.py start
```

## Windows PowerShell 常用命令

```powershell
# 设置并启动（单行）
$env:CUG_RAM_GB="32"; $env:CUG_VRAM_GB="16"; python context_guardian.py start

# 临时设置
$env:CUG_RAM_GB="32"

# 查看当前环境变量
Get-ChildItem Env: | Where-Object {$_.Name -like "CUG_*"}

# 删除环境变量
Remove-Item Env:CUG_RAM_GB
```

## Linux/Mac 常用命令

```bash
# 设置并启动
export CUG_RAM_GB=32 CUG_VRAM_GB=16 && python context_guardian.py start

# 临时设置
export CUG_RAM_GB=32

# 查看环境变量
env | grep CUG_

# 删除环境变量
unset CUG_RAM_GB
```

## 完整示例：Docker 容器

```dockerfile
# Dockerfile
FROM python:3.12-slim

# 安装依赖
RUN pip install psutil pynvml

# 设置环境变量
ENV CUG_RAM_GB=8
ENV CUG_VRAM_GB=4
ENV CUG_LOG_LEVEL=INFO

# 挂载日志目录
VOLUME /app/logs

# 运行
CMD ["python", "/app/context_guardian.py", "start"]
```

```bash
# docker run
docker run -e CUG_RAM_GB=16 -e CUG_VRAM_GB=8 \
  -v $(pwd)/logs:/app/logs \
  context-used-guardian
```

## 故障排查

### 环境变量不生效

1. 检查环境变量是否设置正确：
   ```bash
   echo $CUG_RAM_GB  # Linux/Mac
   echo %CUG_RAM_GB%  # Windows CMD
   $env:CUG_RAM_GB   # Windows PowerShell
   ```

2. 确保在运行 Python 脚本**之前**设置环境变量

3. 如果使用 systemd/service，在服务配置中添加：
   ```ini
   [Service]
   Environment="CUG_RAM_GB=32"
   Environment="CUG_VRAM_GB=16"
   Environment="CUG_LOG_LEVEL=INFO"
   ```

### 日志文件权限问题

如果无法写入日志文件，检查目录权限：

```bash
# Linux/Mac
chmod 755 /path/to/logs
chown user:group /path/to/logs

# Windows
icacls "C:\path\to\logs" /grant User:(OI)(CI)F
```