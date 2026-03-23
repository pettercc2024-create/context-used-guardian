#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试脚本"""

import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\skills\context-used-guardian')
from scripts.context_guardian import ContextGuardian

# 测试配置加载
guardian = ContextGuardian()
print('Config loaded OK')

# 测试硬件检测
hardware = guardian.hardware_info
print(f'Hardware detected: RAM={hardware["ram_gb"]}GB, VRAM={hardware["vram_gb"]}GB')

# 测试阈值计算
thresholds = guardian.calculate_safe_threshold()
print(f'Thresholds: P={thresholds["P_percent"]}%, 1.5P={thresholds["P_percent_1_5"]}%')

# 测试模型参数提取
params = guardian.get_current_model_params()
print(f'Model params: {params}B')

# 测试上下文检查
stats = guardian.check_and_alert()
print(f'Alert triggered: {stats["alert_triggered"]}')

print('\nAll tests passed!')