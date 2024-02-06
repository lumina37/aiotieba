import datetime
import time

import yarl

from ...__version__ import __version__
from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, POST_VERSION
from ...core import Account, HttpCore, WsCore
from ...exception import BoolResponse, TiebaServerError, TiebaValueError
from .protobuf import AddPostReqIdl_pb2, AddPostResIdl_pb2

CMD = 309731


def parse_body(body: bytes) -> None:
    res_proto = AddPostResIdl_pb2.AddPostResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)
    if int(res_proto.data.info.need_vcode):
        raise TiebaValueError("Need verify code")


def pack_proto(account: Account, fname: str, fid: int, tid: int, show_name: str, content: str) -> bytes:
    req_proto = AddPostReqIdl_pb2.AddPostReqIdl()
    req_proto.data.common.BDUSS = account.BDUSS
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = POST_VERSION
    req_proto.data.common._client_id = account.client_id
    req_proto.data.common._phone_imei = '000000000000000'
    req_proto.data.common._from = '1008621x'
    req_proto.data.common.cuid = account.cuid_galaxy2
    current_ts = time.time()
    current_tsms = int(current_ts * 1000)
    current_dt = datetime.datetime.fromtimestamp(current_ts)
    req_proto.data.common._timestamp = current_tsms
    req_proto.data.common.model = 'SM-G988N'
    req_proto.data.common.tbs = account.tbs
    req_proto.data.common.net_type = 1
    req_proto.data.common.pversion = '1.0.3'
    req_proto.data.common._os_version = '9'
    req_proto.data.common.brand = 'samsung'
    req_proto.data.common.lego_lib_version = '3.0.0'
    req_proto.data.common.applist = ''
    req_proto.data.common.stoken = account.STOKEN
    req_proto.data.common.z_id = account.z_id
    req_proto.data.common.cuid_galaxy2 = account.cuid_galaxy2
    req_proto.data.common.cuid_gid = ''
    req_proto.data.common.c3_aid = account.c3_aid
    req_proto.data.common.sample_id = account.sample_id
    req_proto.data.common.scr_w = 720
    req_proto.data.common.scr_w = 1280
    req_proto.data.common.scr_dip = 1.5
    req_proto.data.common.q_type = 0
    req_proto.data.common.is_teenager = 0
    req_proto.data.common.sdk_ver = '2.34.0'
    req_proto.data.common.framework_ver = '3340042'
    req_proto.data.common.naws_game_ver = '1038000'
    req_proto.data.common.active_timestamp = current_tsms - 86400 * 30
    req_proto.data.common.first_install_time = current_tsms - 86400 * 30
    req_proto.data.common.last_update_time = current_tsms - 86400 * 30
    req_proto.data.common.event_day = f'{current_dt.year}{current_dt.month}{current_dt.day}'
    req_proto.data.common.android_id = account.android_id
    req_proto.data.common.cmode = 1
    req_proto.data.common.start_scheme = ''
    req_proto.data.common.start_type = 1
    req_proto.data.common.idfv = '0'
    req_proto.data.common.extra = ''
    req_proto.data.common.user_agent = f'aiotieba/{__version__}'
    req_proto.data.common.personalized_rec_switch = 1
    req_proto.data.common.device_score = '0.4'

    req_proto.data.anonymous = '1'
    req_proto.data.can_no_forum = '0'
    req_proto.data.is_feedback = '0'
    req_proto.data.takephoto_num = '0'
    req_proto.data.entrance_type = '0'
    req_proto.data.vcode_tag = '12'
    req_proto.data.new_vcode = '1'
    req_proto.data.content = content
    req_proto.data.fid = str(fid)
    req_proto.data.v_fid = ''
    req_proto.data.v_fname = ''
    req_proto.data.kw = fname
    req_proto.data.is_barrage = '0'
    req_proto.data.from_fourm_id = str(fid)
    req_proto.data.tid = str(tid)
    req_proto.data.is_ad = '0'
    req_proto.data.post_from = '3'
    req_proto.data.name_show = show_name
    req_proto.data.is_pictxt = '0'
    req_proto.data.show_custom_figure = 0
    req_proto.data.is_show_bless = 0

    return req_proto.SerializeToString()


async def request_http(
    http_core: HttpCore, fname: str, fid: int, tid: int, show_name: str, content: str
) -> BoolResponse:
    data = pack_proto(http_core.account, fname, fid, tid, show_name, content)

    request = http_core.pack_proto_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/post/add", query_string=f"cmd={CMD}"),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()


async def request_ws(ws_core: WsCore, fname: str, fid: int, tid: int, show_name: str, content: str) -> BoolResponse:
    data = pack_proto(ws_core.account, fname, fid, tid, show_name, content)

    response = await ws_core.send(data, CMD)
    parse_body(await response.read())

    return BoolResponse()
