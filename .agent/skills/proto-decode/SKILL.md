---
name: proto-decode
description: >-
  解析multipart二进制payload文件，提取protobuf内容并使用protoc解码
---

# Protobuf解码Skill

## 触发时机

当你拿到一个multipart payload二进制文件，想要查看其中`name="data"`字段的protobuf内容时。

## 使用方法

```bash
python scripts/proto_decode.py <file>
```

## 输出样例

`protoc --decode_raw`的输出格式为字段编号后接字段值，嵌套消息使用大括号缩进：

```
1: 1
4 {
  1: "楼主ID"
  2: "楼主昵称"
  3 {
    1: "帖子标题"
    2: 123456789
    3: 114514
  }
}
```

脚本的后处理会将八进制转义序列`\xxx`直接还原为UTF-8文本，URL编码则解码后追加`(urlquote)`标记。
