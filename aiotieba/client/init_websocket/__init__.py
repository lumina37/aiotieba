from ..._exception import TiebaServerError
from .protobuf import UpdateClientInfoReqIdl_pb2, UpdateClientInfoResIdl_pb2


def pack_proto(bduss: str, version: str, cuid: str, cuid_galaxy2: str, secret_key: str) -> bytes:

    req_proto = UpdateClientInfoReqIdl_pb2.UpdateClientInfoReqIdl()
    req_proto.data.bduss = bduss
    req_proto.data.device = f"""{{"subapp_type":"mini","_client_version":"{version}","pversion":"1.0.3","_msg_status":"1","_phone_imei":"000000000000000","from":"1021099l","cuid_galaxy2":"{cuid_galaxy2}","model":"LIO-AN00","_client_type":"2"}}"""
    req_proto.data.secretKey = secret_key
    req_proto.cuid = f"{cuid}|com.baidu.tieba_mini{version}"

    return req_proto.SerializeToString()


def parse_proto(response: bytes) -> None:
    res_proto = UpdateClientInfoResIdl_pb2.UpdateClientInfoResIdl()
    res_proto.ParseFromString(response)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)
