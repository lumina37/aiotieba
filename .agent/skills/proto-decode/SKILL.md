---
name: proto-decode
description: >-
  解析multipart二进制payload文件，提取protobuf内容并使用protoc --decode_raw解码
---

# Protobuf解码Skill

## 触发时机

当你拿到一个multipart payload二进制文件，想要查看其中`name="data"`字段的protobuf内容时。

## 使用方法

```bash
python scripts/proto_decode.py <file>
```
