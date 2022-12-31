# 枚举

## ReqUInfo

使用该枚举类指定待获取的用户信息字段

**USER_ID** = 1 << 0<br>
**PORTRAIT** = 1 << 1<br>
**USER_NAME** = 1 << 2<br>
**NICK_NAME** = 1 << 3<br>
**TIEBA_UID** = 1 << 4<br>
**OTHER** = 1 << 5<br>
**BASIC** = USER_ID | PORTRAIT | USER_NAME<br>
**ALL** = (1 << 6) - 1
