from __future__ import annotations

import json
import time
from typing import Any

from ...core import CHAT_APPID, CHAT_SDK_VERSION, BlcpCore, BlcpMethodID, BlcpRequest, BlcpServiceID, JsonBody
from ...exception import BoolResponse, TiebaServerError
from ...helper.crypto import compute_msg_key


def construct_request_data(
    core: BlcpCore,
    chatroom_id: int,
    text: str,
    fid: int,
    level: int,
    atdata: list[dict] | None = None,
    robot: int = -1,
) -> dict[str, Any]:
    user = core.account.user
    uk = user.uk
    bduk = core.account.bduk
    origin_id = user.trigger_id
    name = user.nick_name
    portrait = user.portrait
    is_vip = user.is_vip
    glevel = user.glevel

    # 构造app_safe_ext
    app_safe_ext = {"haotianjing": {"zid": core.account.zid or ""}}

    # 构造content
    content = {
        "text": {
            "room_id": str(chatroom_id),
            "type": "0",
            "to_uid": "0",
            "vip": str(int(is_vip)),
            "name": name,
            "portrait": portrait + "?t=" + str(int(time.time())),
            "content_type": "0",
            "content_body": json.dumps({"text": text}, ensure_ascii=False),
            "src": "",
            "baidu_uk": bduk,
            "ext": {},
        }
    }

    # 构造main_data，其主要包含名字、头像、昵称颜色、大会员标志等UI展示信息
    main_data = []
    if is_vip:
        main_data.append({
            "icon": {
                "height": 75,
                "priority": 2,
                "schema": "https://tieba.baidu.com/mo/q/hybrid-business-vip/tbvip?customfullscreen=1&nonavigationbar=1",
                "type": "1",
                "url": "https://tieba-ares.cdn.bcebos.com/mis/2023-7/1689061482682/13afea50121d.png",
                "width": 75,
            },
            "type": 2,
        })

    # namedata将被包含在main_data中
    namedata = {
        "text": {
            "short_enable": 1,
            "short_length": 5,
            "short_priority": 1,
            "priority": 1,
            "str": name,
            "suffix": "...",
            "type": "1",
        },
        "type": 1,
    }

    if is_vip:
        # 开通了贴吧大会员，更新名称颜色
        namedata["text"].update({"text_color": {"day": "CAM_X0301", "night": "CAM_X0301", "type": 2}})
    main_data.extend((
        namedata,
        {
            "icon": {
                "height": 15,
                "priority": 5,
                "schema": "https://tieba.baidu.com/mo/q/hybrid-main-user/taskCenter?customfullscreen=1&nonavigationbar=1",
                "type": "3",
                "url": "local://icon/icon_mask_level_usergrouth_" + str(glevel) + "?type=webp",
                "width": 24,
            },
            "type": 2,
        },
        {
            "icon": {
                "height": 12,
                "priority": 2,
                "schema": "https://tieba.baidu.com/mo/q/wise-bawu-core/forum-level?customfullscreen=1&forum_id="
                + str(fid)
                + "&nonavigationbar=1&obj_locate=5&portrait="
                + portrait
                + "?t="
                + str(int(time.time())),
                "type": "4",
                "url": "local://icon/icon_level_" + f"{level:02d}" + "?type=webp",
                "width": 16,
            },
            "type": 2,
        },
    ))

    ext_data = {
        "main_data": main_data,
        "is_sys_msg": 0,
        "version": "",
        "portrait": portrait + "?t=" + str(int(time.time())),
        "robot_role": 0,
        "role": 0,
        "send_status": 0,
        "from": "android",
        "session_id": chatroom_id,
        "type": 1,
        "user_name": name,
    }

    content["text"]["ext"].update(ext_data)

    # 携带文字、气泡信息，但这部分内容比较多，暂且未开发，注释之
    # content['text']['ext']['bubble_info'] = {...}

    if robot == -1:
        # 没有机器人指令
        content["text"]["ext"]["content"] = {}
    else:
        # 携带机器人指令代码 robot，如签到10005、领取福利10004等
        content["text"]["ext"]["content"] = {"robot_params": {"scene": "tieba_group_chat", "type": robot}}

    content["text"]["ext"]["level"] = level
    content["text"]["ext"]["forum_id"] = fid

    if atdata:
        # 携带艾特@信息
        content["text"]["at_data"] = atdata
    content["text"]["ext"] = json.dumps(content["text"]["ext"], ensure_ascii=False)

    content["text"] = json.dumps(content["text"], ensure_ascii=False)
    content = json.dumps(content, ensure_ascii=False)

    # 构造最终请求数据
    request_data = {
        "method": BlcpMethodID.SEND_MCAST_MSG,
        "mcast_id": chatroom_id,
        "role": 3,
        "token": core.account.BDUSS,
        "appid": CHAT_APPID,
        "uk": uk,
        "origin_id": origin_id,
        "type": 81,
        "app_safe_ext": json.dumps(app_safe_ext, ensure_ascii=False),
        "content": content,
        "msg_key": compute_msg_key(bduk),
        "account_type": 1,
        "sdk_version": CHAT_SDK_VERSION,
        "event_list": [
            {"event": "CClickSendBegin", "timestamp_ms": 0},
            {"event": "CSendBegin", "timestamp_ms": 0},
            {"event": "CIMSendBegin", "timestamp_ms": int(time.time() * 1000)},
        ],
    }

    return request_data


async def send_request(core: BlcpCore, request_data: dict[str, Any]) -> BoolResponse:
    request_data["client_logid"] = int(time.time() * 1_000_000)
    request_data["rpc"] = '{"rpc_retry_time":0}'

    request = BlcpRequest.create(BlcpServiceID.MCAST, BlcpMethodID.SEND_MCAST_MSG, JsonBody(request_data))
    response = await core.send(request)

    payload = response.payload
    err_code = payload["err_code"]
    if err_code == 0:
        return BoolResponse()

    raise TiebaServerError(err_code, payload["msg"])


async def request(
    core: BlcpCore,
    chatroom_id: int,
    text: str,
    fid: int,
    level: int,
    atdata: list[dict] | None = None,
    robot: int = -1,
) -> BoolResponse:
    request_data = construct_request_data(core, chatroom_id, text, fid, level, atdata, robot)
    response = await send_request(core, request_data)

    return response
