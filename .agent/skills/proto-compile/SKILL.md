---
name: proto-compile
description: >-
  将protobuf消息定义文件.proto编译为python代码
---

# Protobuf编译Skill

## 触发时机

变更或新增`.proto`文件时

## 使用方法

```bash
python scripts/proto_compile.py -a            # 编译全部
python scripts/proto_compile.py -c            # 仅编译公共protobuf定义
python scripts/proto_compile.py -d <api_name> # 编译指定名称的API模块
python scripts/proto_compile.py -c -d A -d B  # 组合使用
python scripts/proto_compile.py -a -s         # 仅重新生成类型存根(.pyi)
```

每次编译都会同时生成`_pb2.py`与`_pb2.pyi`（供类型检查器使用），
`-s/--stubs`用于在不改动`_pb2.py`的前提下单独刷新存根。
