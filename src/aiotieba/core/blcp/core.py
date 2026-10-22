from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Any

from .conn import BLCPConn
from .packet import BLCPBody, BLCPRequest, BLCPResponse, JsonBody

if TYPE_CHECKING:
    import asyncio

    from ...config import TimeoutConfig
    from ..account import Account


@dcs.dataclass
class BLCPCore:
    """
    BLCP业务层

    Args:
        account (Account): 用户参数容器
        timeout (TimeoutConfig, optional): 超时配置. Defaults to None.
        max_notify_queue (int, optional): 推送队列长度上限. Defaults to 100.
    """

    account: Account
    conn: BLCPConn

    def __init__(
        self,
        account: Account,
        timeout: TimeoutConfig | None = None,
        max_notify_queue: int = 100,
    ) -> None:
        self.account = account
        self.conn = BLCPConn(timeout=timeout, max_notify_queue=max_notify_queue)

    def set_account(self, new_account: Account) -> None:
        """
        更新用户参数

        Args:
            new_account (Account): 用户参数容器
        """

        self.account = new_account

    @property
    def message_queue(self) -> asyncio.Queue:
        """
        服务端推送队列
        """

        return self.conn.notifies

    async def close(self) -> None:
        """
        关闭连接
        """

        await self.conn.close()

    async def request(
        self,
        service_id: int,
        method_id: int,
        body: BLCPBody | dict[str, Any] | None = None,
    ) -> BLCPResponse:
        """
        发送一次业务请求并等待响应

        Args:
            service_id (int): 服务号
            method_id (int): 方法号
            body (BLCPBody | dict | None, optional): 报文体 传入dict时自动包装为JsonBody. Defaults to None.

        Returns:
            BLCPResponse: 响应报文
        """

        if isinstance(body, dict):
            body = JsonBody(body)

        request = BLCPRequest.create(service_id, method_id, body)

        return await self.conn.send(request)
