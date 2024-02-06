from typing import List

from ._classdef import WsNotify
from .protobuf import PushNotifyResIdl_pb2

CMD = 202006


def parse_body(body: bytes) -> List[WsNotify]:
    res_proto = PushNotifyResIdl_pb2.PushNotifyResIdl()
    res_proto.ParseFromString(body)

    notifies = [WsNotify.from_tbdata(p) for p in res_proto.multiMsg]

    return notifies
