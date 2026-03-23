#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Gateway RPC 集成"""

import subprocess
import json

print("测试 Gateway RPC session.new 调用...")
print("-" * 60)

result = subprocess.run(
    ["openclaw", "gateway", "call", "session.new"],
    capture_output=True,
    text=True,
    timeout=10
)

print(f"返回码: {result.returncode}")
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")

if result.returncode == 0:
    try:
        response = json.loads(result.stdout)
        print("\n✅ JSON 解析成功:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"\n⚠️ JSON 解析失败: {e}")
else:
    print("\n❌ Gateway RPC 调用失败")