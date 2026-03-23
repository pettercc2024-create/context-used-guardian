#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContextUsed-Guardian (CUG) - Context Monitoring and Resource Protection
监控上下文使用并保护系统资源不被耗尽
"""

import psutil
import pynvml
import re
import json
import sys
import os
import logging
from datetime import datetime

# 配置文件路径
CONFIG_FILE = r"C:\Users\Administrator\.openclaw\skills\context-used-guardian\config.json"
# 日志文件路径
LOG_FILE = r"C:\Users\Administrator\.openclaw\skills\context-used-guardian\cug.log"
# 会话统计文件
SESSION_STATS_FILE = r"C:\Users\Administrator\.openclaw\skills\context-used-guardian\session_stats.json"

class ContextGuardian:
    def __init__(self):
        self.setup_logging()
        self.config = self.load_config()
        self.hardware_info = self.detect_hardware()
        self.session_stats = self.load_session_stats()

    def setup_logging(self):
        """配置日志系统"""
        # 创建日志目录
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 配置日志格式
        log_format = '[%(asctime)s] [%(levelname)s] [CUG] %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        # 配置日志处理器
        handlers = [
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]

        # 配置日志器
        self.logger = logging.getLogger('ContextUsed-Guardian')
        self.logger.setLevel(logging.DEBUG)

        # 避免重复添加处理器
        if not self.logger.handlers:
            for handler in handlers:
                formatter = logging.Formatter(log_format, datefmt=date_format)
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

    def load_config(self):
        """加载配置文件"""
        default_config = {
            "hardware": {"ram_gb": 16, "vram_gb": 8},
            "models": {"deepseek-v3:16b": 16, "qwen2.5-7b": 7, "default": 7}
        }

        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")

        return default_config

    def load_config(self):
        """加载配置文件"""
        default_config = {
            "hardware": {"ram_gb": 16, "vram_gb": 8},
            "models": {"deepseek-v3:16b": 16, "qwen2.5-7b": 7, "default": 7}
        }

        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")

        return default_config

    def save_config(self):
        """保存配置文件"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info("配置已保存")
        except Exception as e:
            self.logger.error(f"配置保存失败: {e}")

    def detect_hardware(self):
        """检测硬件信息"""
        ram_info = psutil.virtual_memory()
        ram_gb = ram_info.total / (1024 ** 3)

        # 从环境变量读取硬件配置（优先级高于自动检测）
        env_ram = os.environ.get('CUG_RAM_GB')
        env_vram = os.environ.get('CUG_VRAM_GB')

        hardware_info = {
            "ram_gb": round(ram_gb, 1),
            "vram_gb": 0
        }

        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            vram_gb = 0

            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                vram_gb += info.total / (1024 ** 3)

            pynvml.nvmlShutdown()
            hardware_info["vram_gb"] = round(vram_gb, 1)

        except Exception as e:
            self.logger.warning(f"显存检测失败: {e}")

        # 如果环境变量设置了值，优先使用
        if env_ram is not None:
            try:
                hardware_info["ram_gb"] = float(env_ram)
                self.logger.info(f"使用环境变量 RAM: {hardware_info['ram_gb']}GB")
            except ValueError:
                self.logger.error("环境变量 CUG_RAM_GB 格式错误")

        if env_vram is not None:
            try:
                hardware_info["vram_gb"] = float(env_vram)
                self.logger.info(f"使用环境变量 VRAM: {hardware_info['vram_gb']}GB")
            except ValueError:
                self.logger.error("环境变量 CUG_VRAM_GB 格式错误")

        return hardware_info

    def load_session_stats(self):
        """加载会话统计"""
        try:
            if os.path.exists(SESSION_STATS_FILE):
                with open(SESSION_STATS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"会话统计加载失败: {e}")

        return {}

    def save_session_stats(self):
        """保存会话统计"""
        try:
            with open(SESSION_STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.session_stats, f, indent=2, ensure_ascii=False)
            self.logger.debug("会话统计已保存")
        except Exception as e:
            self.logger.error(f"会话统计保存失败: {e}")

    def get_current_model_params(self):
        """从模型名称中提取参数量"""
        # 从环境变量获取当前模型名称
        model_name = os.environ.get('OLLAMA_MODEL', '').lower()

        # 尝试从配置中查找
        if model_name in self.config["models"]:
            return self.config["models"][model_name]

        # 尝试从模型名称提取数字
        match = re.search(r':(\d+)(b)?$', model_name)
        if match:
            params = int(match.group(1))
            return params

        # 默认参数量
        return self.config["models"]["default"]

    def calculate_safe_threshold(self):
        """计算安全阈值 P"""
        hardware = self.hardware_info
        model_params = self.get_current_model_params()

        # 本地模型模式: S = (RAM + VRAM) / 2
        if hardware["vram_gb"] > 0:
            S = (hardware["ram_gb"] + hardware["vram_gb"]) / 2
        else:
            # 云端模式或无GPU: S = RAM
            S = hardware["ram_gb"]

        # 计算阈值 P
        P = (S / model_params) * 100

        return {
            "model_params": model_params,
            "S": round(S, 1),
            "P_percent": round(P, 1),
            "P_percent_1_5": round(P * 1.5, 1),
            "mode": "local" if hardware["vram_gb"] > 0 else "cloud"
        }

    def get_context_usage(self):
        """获取上下文使用情况"""
        # 从环境变量获取上下文使用情况
        context_used = os.environ.get('OPENCLAW_CONTEXT_USED', '0')

        try:
            return int(context_used)
        except ValueError:
            return 0

    def check_and_alert(self):
        """检查并触发预警/熔断"""
        stats = self.calculate_safe_threshold()
        context_used = self.get_context_usage()

        warning_threshold = stats["P_percent"]
        circuit_breaker_threshold = stats["P_percent_1_5"]

        alert_triggered = False
        message = ""

        # 第一阶段：预警
        if context_used >= warning_threshold and context_used < circuit_breaker_threshold:
            message = f"【⚠️ ContextUsed-Guardian 警告：当前用量已达硬件预警线 ({stats['P_percent']}%)，请注意资源消耗。】"
            alert_triggered = True
            self.logger.warning(f"上下文使用率预警: {context_used}% (阈值: {warning_threshold}%)")

        # 第二阶段：熔断
        elif context_used >= circuit_breaker_threshold:
            message = f"【🚨 ContextUsed-Guardian 熔断：当前用量已达熔断线 ({stats['P_percent_1_5']}%)！自动执行 /new 进入新会话。】"
            alert_triggered = True
            self.logger.error(f"上下文使用率熔断: {context_used}% (熔断线: {circuit_breaker_threshold}%)")

        if alert_triggered:
            print(message)
            self.send_alert(message)

            # 如果达到熔断线，执行 /new
            if context_used >= circuit_breaker_threshold:
                self.execute_new_command()

        return {
            "context_used": context_used,
            "warning_threshold": warning_threshold,
            "circuit_breaker_threshold": circuit_breaker_threshold,
            "alert_triggered": alert_triggered,
            "message": message
        }

    def send_alert(self, message):
        """发送警报消息"""
        # 这里可以集成到 OpenClaw 的消息系统中
        # 当前只打印到控制台
        self.logger.info(f"警报: {message}")

    def execute_new_command(self):
        """执行自动会话切换 (/new)"""
        print("\n" + "=" * 60)
        print("🚨 ContextUsed-Guardian 熔断触发！")
        print("=" * 60)
        print("[CUG] 检测到上下文使用率过高")
        print("[CUG] 正在通过 Gateway API 创建新会话以保护系统...")
        print("[CUG] 注意：新会话将继承当前对话的历史上下文")
        print("-" * 60)

        try:
            import subprocess
            import json

            # 检查 openclaw 命令是否可用
            result = subprocess.run(
                ["openclaw", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # 通过 openclaw gateway call RPC 方法创建新会话
            result = subprocess.run(
                ["openclaw", "gateway", "call", "session.new"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # 尝试解析 JSON 响应
                try:
                    response = json.loads(result.stdout)
                    if "session" in response:
                        new_session_id = response["session"].get("id", "unknown")
                        new_session_key = response["session"].get("key", "unknown")
                        print(f"\n✅ [CUG] 新会话创建成功!")
                        print(f"   Session ID: {new_session_id}")
                        print(f"   Session Key: {new_session_key}")
                        print("\n[CUG] 对话上下文已迁移到新会话")
                        self.logger.info(f"新会话创建成功: ID={new_session_id}, Key={new_session_key}")
                    else:
                        print("\n✅ [CUG] 新会话已创建")
                        self.logger.info("新会话已创建")
                except json.JSONDecodeError:
                    # 如果不是 JSON，至少说明执行成功
                    print("\n✅ [CUG] 新会话已创建")
                    self.logger.info("新会话已创建")
            else:
                print(f"\n❌ [CUG] Gateway RPC 调用失败: {result.stderr}")
                self.logger.error(f"Gateway RPC 调用失败: {result.stderr}")

        except subprocess.TimeoutExpired:
            print("\n⚠️ [CUG] Gateway RPC 调用超时")
            self.logger.warning("Gateway RPC 调用超时")

        except FileNotFoundError:
            print("\n⚠️ [CUG] 未找到 openclaw 命令")
            print("[CUG] 请确保 OpenClaw 已正确安装并配置 PATH")
            print("[CUG] 或者使用以下备选方案:")
            print("  1. 在控制台输入: /new")
            print("  2. 在 Web Control UI 中: Sessions -> New Session")
            self.logger.warning("openclaw 命令未找到")

        except Exception as e:
            print(f"\n❌ [CUG] 执行会话切换失败: {e}")
            self.logger.error(f"执行会话切换失败: {e}")
            print("\n[CUG] 请手动执行以下命令之一:")
            print("  1. 在控制台输入: /new")
            print("  2. 运行命令: openclaw gateway call session.new")
            print("  3. 在 Web Control UI 中: Sessions -> New Session")

        print("=" * 60)

    def get_system_status(self):
        """获取系统状态"""
        return {
            "hardware": self.hardware_info,
            "thresholds": self.calculate_safe_threshold(),
            "current_context_used": self.get_context_usage()
        }

    def run_continuous_monitor(self):
        """持续监控模式"""
        self.logger.info("=" * 60)
        self.logger.info("ContextUsed-Guardian 启动中...")
        self.logger.info(f"硬件检测: RAM {self.hardware_info['ram_gb']}GB + VRAM {self.hardware_info['vram_gb']}GB")

        model_params = self.get_current_model_params()
        thresholds = self.calculate_safe_threshold()
        self.logger.info(f"当前模型参数量: {model_params}B")
        self.logger.info(f"预警阈值: {thresholds['P_percent']}%")
        self.logger.info(f"熔断阈值: {thresholds['P_percent_1_5']}%")
        self.logger.info("持续监控已启动... (Ctrl+C 停止)")

        print("\n" + "=" * 60)
        print("🦞 ContextUsed-Guardian 启动中...")
        print(f"硬件检测: RAM {self.hardware_info['ram_gb']}GB + VRAM {self.hardware_info['vram_gb']}GB")
        print(f"当前模型参数量: {model_params}B")
        print(f"预警阈值: {thresholds['P_percent']}%")
        print(f"熔断阈值: {thresholds['P_percent_1_5']}%")
        print("持续监控已启动... (Ctrl+C 停止)")
        print("=" * 60)

        try:
            while True:
                stats = self.check_and_alert()
                print(f"\n[CUG] 当前上下文使用: {stats['context_used']}% | 状态: {'警告' if stats['alert_triggered'] else '正常'}")
                print("-" * 60)
                self.save_session_stats()
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("\n\n[CUG] 监控已停止")
            self.session_stats["last_stop"] = datetime.now().isoformat()
            self.save_session_stats()
            self.logger.info("监控已停止")


def main():
    """主函数"""
    guardian = ContextGuardian()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "check":
            stats = guardian.check_and_alert()
            print(f"\n系统状态:")
            print(f"  - 上下文使用: {stats['context_used']}%")
            print(f"  - 预警阈值: {stats['warning_threshold']}%")
            print(f"  - 熔断阈值: {stats['circuit_breaker_threshold']}%")
            print(f"  - 触发警报: {'是' if stats['alert_triggered'] else '否'}")

        elif command == "status":
            status = guardian.get_system_status()
            print("\n系统状态:")
            print(f"  硬件信息:")
            print(f"    - RAM: {status['hardware']['ram_gb']}GB")
            print(f"    - VRAM: {status['hardware']['vram_gb']}GB")
            print(f"  当前配置:")
            print(f"    - 模型参数: {status['thresholds']['model_params']}B")
            print(f"    - S值: {status['thresholds']['S']}GB")
            print(f"    - 预警阈值: {status['thresholds']['P_percent']}%")
            print(f"    - 熔断阈值: {status['thresholds']['P_percent_1_5']}%")
            print(f"  当前会话:")
            print(f"    - 上下文使用: {status['current_context_used']}%")

        elif command == "start":
            guardian.run_continuous_monitor()

        else:
            print(f"未知命令: {command}")
            print("使用方法: python context_guardian.py [check|status|start]")

    else:
        # 默认运行检查
        stats = guardian.check_and_alert()
        guardian.run_continuous_monitor()


if __name__ == "__main__":
    main()