import json
import time
from dataclasses import dataclass

from ...core import BLCPCore, BLCPData
from ...exception import BoolResponse


@dataclass
class AppConstants:
    appid: int = 10773430
    sdk_version: int = 11250036


async def construct_request_data(
    blcpcore, room_id, uk, user_id, origin_id, name, portrait, text, forum_id, level, vip, glevel, atdata=None, robot=-1
):
    constants = AppConstants()

    # 构造app_safe_ext
    app_safe_ext = {"haotianjing": {"zid": blcpcore.account.z_id or ""}}

    # 构造content
    content = {
        "text": {
            "room_id": str(room_id),
            "type": "0",
            "to_uid": "0",
            "vip": str(int(vip)),
            "name": name,
            "portrait": portrait + "?t=" + str(int(time.time())),
            "content_type": "0",
            "content_body": json.dumps({"text": text}, ensure_ascii=False),
            "src": "",
            "baidu_uk": blcpcore.getBDUKfromUserId(str(user_id)),
            "ext": {},
        }
    }

    # 构造main_data，其主要包含名字、头像、昵称颜色、大会员标志等UI展示信息
    main_data = []
    if vip:
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

    if vip:
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
                + str(forum_id)
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
        "session_id": room_id,
        "type": 1,
        "user_name": name,
    }

    content["text"]["ext"].update(ext_data)

    # 携带文字、气泡信息，但这部分内容比较多，暂且未开发，注释之
    # content['text']['ext']['bubble_info'] = {'color_info': {'at_text_color': '', 'at_text_color_dark': 'AF9EFF', 'text_color': '141414', 'text_color_dark': 'FFFFFF'}, 'end_time': 0, 'id': 1380005, 'img_info': {'android_left': 'https://tieba-ares.cdn.bcebos.com/mis/2023-3/1678971300129/4d9fd67c26e3.png', 'android_left_dark': 'https://tieba-ares.cdn.bcebos.com/mis/2023-3/1678971300129/4d9fd67c26e3.png', 'android_right': 'https://tieba-ares.cdn.bcebos.com/mis/2023-3/1678971357436/745549b2ae39.png', 'android_right_dark': 'https://tieba-ares.cdn.bcebos.com/mis/2023-3/1678971357436/745549b2ae39.png', 'ios_left': 'https://tieba-ares.cdn.bcebos.com/mis/2023-3/1678876082814/0a1741207e0d.png', 'ios_left_dark': 'https://tieba-ares.cdn.bcebos.com/mis/2023-3/1678876082814/0a1741207e0d.png', 'ios_right': 'https://tieba-ares.cdn.bcebos.com/mis/2023-3/1678876082435/c07fbaa4ad57.png', 'ios_right_dark': 'https://tieba-ares.cdn.bcebos.com/mis/2023-3/1678876082435/c07fbaa4ad57.png'}, 'jump_url': 'https://tieba.baidu.com/mo/q/hybrid/decorator?pageType=4&from_page=4&nonavigationbar=1&customfullscreen=1&decoratorId=1380005', 'type': 2}

    if robot == -1:
        # 没有机器人指令
        content["text"]["ext"]["content"] = {}
    else:
        # 携带机器人指令代码 robot，如签到10005、领取福利10004等
        content["text"]["ext"]["content"] = {"robot_params": {"scene": "tieba_group_chat", "type": robot}}

    content["text"]["ext"]["level"] = level
    content["text"]["ext"]["forum_id"] = forum_id

    if atdata:
        # 携带艾特@信息
        content["text"]["at_data"] = atdata
    content["text"]["ext"] = json.dumps(content["text"]["ext"], ensure_ascii=False)

    content["text"] = json.dumps(content["text"], ensure_ascii=False)
    content = json.dumps(content, ensure_ascii=False)

    # 构造最终请求数据
    request_data = {
        "method": 185,
        "mcast_id": room_id,
        "role": 3,
        "token": blcpcore.account.BDUSS,
        "appid": constants.appid,
        "uk": uk,
        "origin_id": origin_id,
        "type": 81,
        "app_safe_ext": json.dumps(app_safe_ext, ensure_ascii=False),
        "content": content,
        "msg_key": blcpcore.getmsgkey(blcpcore.getBDUKfromUserId(str(user_id))),
        "account_type": 1,
        "sdk_version": constants.sdk_version,
        "event_list": [
            {"event": "CClickSendBegin", "timestamp_ms": 0},
            {"event": "CSendBegin", "timestamp_ms": 0},
            {"event": "CIMSendBegin", "timestamp_ms": int(time.time() * 1000)},
        ],
    }

    return request_data


async def send_request(blcpcore, request_data):
    loginBLCPRequest = BLCPData(serviceId=3, methodId=185)
    loginBLCPRequest.correlationId = int(time.time() * 1000 * 1000)
    loginBLCPRequest.RpcBody = blcpcore.buildRpcBody(
        serviceId=3, methodId=185, correlationId=loginBLCPRequest.correlationId
    )

    request_data["client_logid"] = loginBLCPRequest.correlationId
    request_data["rpc"] = '{"rpc_retry_time":0}'

    loginBLCPRequest.LcmBody = json.dumps(request_data, ensure_ascii=False).encode("utf-8")
    response = blcpcore.waiter.new(loginBLCPRequest.correlationId)
    blcpcore.writer.write(loginBLCPRequest.toBytes())
    reps = await response.read()
    try:
        err_code = json.loads(reps.LcmBody)["err_code"]
    except json.JSONDecodeError:
        raise
    if err_code == 0:
        return BoolResponse()
    raise


async def request(
    blcpcore: BLCPCore,
    room_id: int,
    uk: int,
    user_id: int,
    origin_id: int,
    name: str,
    portrait: str,
    text: str,
    forum_id: int,
    level: int,
    vip: bool,
    glevel: int,
    atdata: list[dict] = None,
    robot=-1,
):
    request_data = await construct_request_data(
        blcpcore, room_id, uk, user_id, origin_id, name, portrait, text, forum_id, level, vip, glevel, atdata, robot
    )
    return await send_request(blcpcore, request_data)
