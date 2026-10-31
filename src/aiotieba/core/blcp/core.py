from __future__ import annotations

import asyncio
import contextlib
import dataclasses as dcs
import random
import socket
import ssl
import time
import weakref
from sys import maxsize as LONG_MAX
from typing import TYPE_CHECKING, cast

from ...api._protobuf import Lcm_pb2
from ...config import TimeoutConfig
from ...enums import BlcpStatus
from ...helper import timeout
from .enums import BlcpMetaType, BlcpMethodID, BlcpServiceID
from .exception import BlcpConnectionError
from .packet import (
    BlcpFrame,
    BlcpMsgFactory,
    BlcpNotify,
    BlcpRequest,
    BlcpResponse,
    ProtoLcmBody,
    TypeBlcpMsg,
)

if TYPE_CHECKING:
    from ..account import Account


@dcs.dataclass
class BlcpFuture:
    """
    BLCP响应占位

    Args:
        correlation_id (int): 请求id
        read_timeout (float): 读超时时间
    """

    loop: asyncio.AbstractEventLoop
    future: asyncio.Future
    correlation_id: int
    read_timeout: float

    def __init__(self, correlation_id: int, read_timeout: float) -> None:
        self.loop = asyncio.get_running_loop()
        self.future = self.loop.create_future()
        self.correlation_id = correlation_id
        self.read_timeout = read_timeout

    async def read(self) -> BlcpResponse:
        """
        等待并读取响应

        Returns:
            BlcpResponse: 响应报文

        Raises:
            TimeoutError: 读取超时
        """

        try:
            async with timeout(self.read_timeout, self.loop):
                return await self.future
        except TimeoutError as err:
            self.future.cancel()
            raise TimeoutError("Timeout to read") from err
        except BaseException:
            self.future.cancel()
            raise


@dcs.dataclass
class BlcpWaiter:
    """
    BLCP等待映射 以请求id为键

    Args:
        read_timeout (float): 读超时时间
    """

    waiter: weakref.WeakValueDictionary[int, BlcpFuture]
    read_timeout: float

    def __init__(self, read_timeout: float) -> None:
        self.waiter = weakref.WeakValueDictionary()
        self.read_timeout = read_timeout

    def new(self, correlation_id: int) -> BlcpFuture:
        """
        创建一个用于等待指定请求响应的占位

        Args:
            correlation_id (int): 请求id

        Returns:
            BlcpFuture: 占位
        """

        future = BlcpFuture(correlation_id, self.read_timeout)
        self.waiter[correlation_id] = future
        return future

    def set_done(self, correlation_id: int, response: BlcpResponse) -> None:
        """
        将指定请求id的占位设置为已完成

        Args:
            correlation_id (int): 请求id
            response (BlcpResponse): 响应报文
        """

        future = self.waiter.get(correlation_id, None)
        if future is None or future.future.done():
            return
        future.future.set_result(response)

    def fail_all(self, err: BaseException) -> None:
        """
        使所有等待中的占位以异常结束

        Args:
            err (BaseException): 异常
        """

        for future in list(self.waiter.values()):
            if not future.future.done():
                future.future.set_exception(err)


@dcs.dataclass
class BlcpCore:
    """
    BLCP核心容器 负责连接、报文收发与心跳维持

    Args:
        account (Account): 用户参数容器
        timeout (TimeoutConfig, optional): 超时配置. Defaults to None.
        max_notify_queue (int, optional): 推送队列长度上限. Defaults to 100.
    """

    account: Account
    timeout: TimeoutConfig
    loop: asyncio.AbstractEventLoop
    status: BlcpStatus
    reader: asyncio.StreamReader | None
    writer: asyncio.StreamWriter | None
    waiter: BlcpWaiter | None
    dispatcher: asyncio.Task | None
    heartbeater: asyncio.Task | None
    message_queue: asyncio.Queue
    heartbeat_interval: float | None

    def __init__(
        self,
        account: Account,
        timeout: TimeoutConfig | None = None,
        max_notify_queue: int = 100,
    ) -> None:
        self.account = account
        self.timeout = timeout if isinstance(timeout, TimeoutConfig) else TimeoutConfig()
        self.loop = asyncio.get_running_loop()

        self.status = BlcpStatus.CLOSED
        self.reader = None
        self.writer = None
        self.waiter = None
        self.dispatcher = None
        self.heartbeater = None
        self.message_queue = asyncio.Queue(maxsize=max_notify_queue)
        self.heartbeat_interval = None

    def set_account(self, new_account: Account) -> None:
        """
        更新用户参数

        Args:
            new_account (Account): 用户参数容器
        """

        self.account = new_account

    @property
    def is_open(self) -> bool:
        """
        连接是否可用
        """

        return (
            self.status in (BlcpStatus.OPEN, BlcpStatus.LOGGED_IN)
            and self.writer is not None
            and not self.writer.is_closing()
        )

    async def connect(self) -> None:
        """
        建立TCP+TLS连接并启动接收任务
        """

        if self.writer is not None and not self.writer.is_closing():
            await self.close()

        self.status = BlcpStatus.CONNECTING

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False

        self.reader, self.writer = await asyncio.wait_for(
            asyncio.open_connection("common.lcs.baidu.com", 443, ssl=ssl_context, family=socket.AF_INET),
            timeout=self.timeout.blcp_connect,
        )

        self.waiter = BlcpWaiter(self.timeout.blcp_read)
        self.dispatcher = self.loop.create_task(self.__dispatch(), name="blcp_dispatcher")
        self.status = BlcpStatus.OPEN

    async def close(self) -> None:
        """
        关闭连接并终止后台任务
        """

        self.status = BlcpStatus.CLOSED

        for task in (self.heartbeater, self.dispatcher):
            if task is not None and not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError, Exception):
                    await task

        self.heartbeater = None
        self.dispatcher = None

        if self.writer is not None:
            self.writer.close()
            with contextlib.suppress(ConnectionError, OSError):
                await self.writer.wait_closed()
            self.writer = None

        self.reader = None

        if self.waiter is not None:
            self.waiter.fail_all(BlcpConnectionError("BLCP连接已关闭"))
            self.waiter = None

    async def send(self, request: BlcpRequest) -> BlcpResponse:
        """
        发送请求报文并等待响应

        Args:
            request (BlcpRequest): 请求报文

        Returns:
            BlcpResponse: 响应报文
        """

        future = self.waiter.new(request.correlation_id)

        self.writer.write(BlcpFrame.from_msg(request).encode())
        await self.writer.drain()

        return await future.read()

    async def send_nowait(self, msg: TypeBlcpMsg) -> None:
        """
        发送请求报文但不等待响应

        Args:
            msg (TypeBlcpMsg): 报文
        """

        self.writer.write(BlcpFrame.from_msg(msg).encode())
        await self.writer.drain()

    async def heartbeat(self) -> None:
        """
        发送一次LCM心跳 不等待响应
        """

        correlation_id = random.randint(0, LONG_MAX)
        rpc_data = Lcm_pb2.RpcData()
        rpc_data.lcm_request.log_id = correlation_id
        rpc_data.lcm_request.timestamp = int(time.time() * 1000)
        body = ProtoLcmBody.from_proto(rpc_data)

        await self.send_nowait(
            BlcpRequest.create(BlcpServiceID.LCM, BlcpMethodID.HEARTBEAT, body, correlation_id=correlation_id)
        )

    def start_heartbeat(self, interval_ms: int = 0) -> None:
        """
        重设心跳任务

        Args:
            interval_ms (int, optional): 服务端下发的间隔 单位毫秒. Defaults to 0.
        """

        if self.heartbeater is not None:
            self.heartbeater.cancel()
            self.heartbeater = None

        interval = interval_ms / 1000 if interval_ms > 0 else self.timeout.blcp_heartbeat
        self.heartbeat_interval = interval

        if not interval or interval <= 0:
            return

        self.heartbeater = self.loop.create_task(self.__heartbeat_loop(), name="blcp_heartbeater")

    async def __heartbeat_loop(self) -> None:
        while True:
            await asyncio.sleep(self.heartbeat_interval)

            try:
                await self.heartbeat()
            except Exception:
                self.status = BlcpStatus.CLOSED
                return

    async def __dispatch(self) -> None:
        try:
            while True:
                frame = await BlcpFrame.read_from(self.reader)
                msg = BlcpMsgFactory.from_frame(frame)

                if msg.header.meta_type is BlcpMetaType.RESPONSE:
                    self.__on_response(cast("BlcpResponse", msg))
                elif msg.header.meta_type is BlcpMetaType.NOTIFY:
                    self.__on_notify(cast("BlcpNotify", msg))

        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        finally:
            self.status = BlcpStatus.CLOSED
            if self.waiter is not None:
                self.waiter.fail_all(BlcpConnectionError("BLCP连接已断开"))

    def __on_response(self, response: BlcpResponse) -> None:
        if response.service_id == BlcpServiceID.LCM and response.method_id == BlcpMethodID.HEARTBEAT:
            lcm = response.lcm
            if lcm is not None and lcm.next_interval_ms > 0:
                self.start_heartbeat(lcm.next_interval_ms)

        if self.waiter is not None:
            self.waiter.set_done(response.correlation_id, response)

    def __on_notify(self, notify: BlcpNotify) -> None:
        if self.message_queue.full():
            self.message_queue.get_nowait()

        self.message_queue.put_nowait(notify)
