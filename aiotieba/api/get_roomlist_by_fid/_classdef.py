import dataclasses as dcs


@dcs.dataclass
class RoomList:
    """
    某吧的聊天室列表

    Attributes:
        room_list (list[dict]): 每个聊天室的json内容

    """

    room_list: list

    @staticmethod
    def from_tbdata(resjson: dict) -> "RoomList":  # todo:解析json并参数化而不是直接返回
        room_list = []
        for x in resjson["data"]["list"]:
            for y in x["room_list"]:
                room_list.append(y)
        return RoomList(room_list)
