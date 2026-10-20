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

from ...config import TimeoutConfig
from ...enums import BLCPStatus
from ...helper import timeout
from .enums import BLCPMethodID, BLCPServiceID
from .exception import BLCPConnectionError
from .packet import BLCPNotify, BLCPPacket, BLCPRequest, BLCPResponse, LcmBody, LCPFrame


@dcs.dataclass
class BLCPFuture:
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

    async def read(self, read_timeout: float | None = None) -> BLCPResponse:
        """
        等待并读取响应

        Args:
            read_timeout (float | None, optional): 本次读取的超时时间. Defaults to None.

        Returns:
            BLCPResponse: 响应报文

        Raises:
            TimeoutError: 读取超时
        """

        delay = self.read_timeout if read_timeout is None else read_timeout

        try:
            async with timeout(delay, self.loop):
                return await self.future
        except TimeoutError as err:
            self.future.cancel()
            raise TimeoutError("Timeout to read") from err
        except BaseException:
            self.future.cancel()
            raise


@dcs.dataclass
class BLCPWaiter:
    """
    BLCP等待映射 以请求id为键

    Args:
        read_timeout (float): 读超时时间
    """

    waiter: weakref.WeakValueDictionary[int, BLCPFuture]
    read_timeout: float

    def __init__(self, read_timeout: float) -> None:
        self.waiter = weakref.WeakValueDictionary()
        self.read_timeout = read_timeout
        weakref.finalize(self, self.__cancel_all)

    def __cancel_all(self) -> None:
        for future in self.waiter.values():
            future.future.cancel()

    def new(self, correlation_id: int) -> BLCPFuture:
        """
        创建一个用于等待指定请求响应的占位

        Args:
            correlation_id (int): 请求id

        Returns:
            BLCPFuture: 占位
        """

        future = BLCPFuture(correlation_id, self.read_timeout)
        self.waiter[correlation_id] = future
        return future

    def set_done(self, correlation_id: int, response: BLCPResponse) -> None:
        """
        将指定请求id的占位设置为已完成

        Args:
            correlation_id (int): 请求id
            response (BLCPResponse): 响应报文
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
class BLCPConn:
    """
    BLCP连接层 负责传输、RPC配对与心跳维持

    Args:
        timeout (TimeoutConfig, optional): 超时配置. Defaults to None.
        max_notify_queue (int, optional): 推送队列长度上限. Defaults to 100.
    """

    timeout: TimeoutConfig
    loop: asyncio.AbstractEventLoop
    status: BLCPStatus
    reader: asyncio.StreamReader | None
    writer: asyncio.StreamWriter | None
    waiter: BLCPWaiter | None
    dispatcher: asyncio.Task | None
    heartbeater: asyncio.Task | None
    notifies: asyncio.Queue
    heartbeat_interval: float | None

    def __init__(
        self,
        timeout: TimeoutConfig | None = None,
        max_notify_queue: int = 100,
    ) -> None:
        self.timeout = timeout if isinstance(timeout, TimeoutConfig) else TimeoutConfig()
        self.loop = asyncio.get_running_loop()

        self.status = BLCPStatus.CLOSED
        self.reader = None
        self.writer = None
        self.waiter = None
        self.dispatcher = None
        self.heartbeater = None
        self.notifies = asyncio.Queue(maxsize=max_notify_queue)
        self.heartbeat_interval = None

    @property
    def is_open(self) -> bool:
        """
        连接是否可用
        """

        return self.status is BLCPStatus.OPEN and self.writer is not None and not self.writer.is_closing()

    async def connect(self) -> None:
        """
        建立TCP+TLS连接并启动接收任务
        """

        if self.writer is not None and not self.writer.is_closing():
            await self.close()

        self.status = BLCPStatus.CONNECTING

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False

        self.reader, self.writer = await asyncio.wait_for(
            asyncio.open_connection("common.lcs.baidu.com", 443, ssl=ssl_context, family=socket.AF_INET),
            timeout=self.timeout.blcp_connect,
        )

        self.waiter = BLCPWaiter(self.timeout.blcp_read)
        self.dispatcher = self.loop.create_task(self._dispatch(), name="blcp_dispatcher")
        self.status = BLCPStatus.OPEN

    async def heartbeat(self) -> None:
        """
        发送一次LCM心跳 不等待响应
        """

        correlation_id = random.randint(0, LONG_MAX)
        body = LcmBody.heartbeat(log_id=correlation_id, timestamp=int(time.time() * 1000))

        await self.send(
            BLCPRequest.create(BLCPServiceID.LCM, BLCPMethodID.HEARTBEAT, body, correlation_id=correlation_id)
        )

    async def request(self, request: BLCPRequest, read_timeout: float | None = None) -> BLCPResponse:
        """
        发送请求并等待响应

        Args:
            request (BLCPRequest): 请求报文
            read_timeout (float | None, optional): 读超时时间. Defaults to None.

        Returns:
            BLCPResponse: 响应报文
        """

        if self.waiter is None or self.writer is None or self.writer.is_closing():
            raise BLCPConnectionError("BLCP连接未建立")

        future = self.waiter.new(request.correlation_id)

        self.writer.write(request.to_bytes())
        await self.writer.drain()

        return await future.read(read_timeout)

    async def send(self, packet: BLCPPacket) -> None:
        """
        发送报文 不等待响应

        Args:
            packet (BLCPPacket): 报文
        """

        if self.writer is None or self.writer.is_closing():
            raise BLCPConnectionError("BLCP连接未建立")

        self.writer.write(packet.to_bytes())
        await self.writer.drain()

    async def close(self) -> None:
        """
        关闭连接并终止后台任务
        """

        self.status = BLCPStatus.CLOSED

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
            self.waiter.fail_all(BLCPConnectionError("BLCP连接已关闭"))
            self.waiter = None

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

        self.heartbeater = self.loop.create_task(self._heartbeat_loop(), name="blcp_heartbeater")

    async def _heartbeat_loop(self) -> None:
        while True:
            await asyncio.sleep(self.heartbeat_interval)

            try:
                await self.heartbeat()
            except Exception:
                self.status = BLCPStatus.CLOSED
                return

    async def _dispatch(self) -> None:
        try:
            while True:
                frame = await LCPFrame.read_from(self.reader)
                packet = BLCPPacket.from_frame(frame)

                if isinstance(packet, BLCPResponse):
                    self._on_response(packet)
                elif isinstance(packet, BLCPNotify):
                    self._on_notify(packet)

        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        finally:
            self.status = BLCPStatus.CLOSED
            if self.waiter is not None:
                self.waiter.fail_all(BLCPConnectionError("BLCP连接已断开"))

    def _on_response(self, response: BLCPResponse) -> None:
        if response.service_id == BLCPServiceID.LCM and response.method_id == BLCPMethodID.HEARTBEAT:
            lcm = response.lcm
            if lcm is not None and lcm.next_interval_ms > 0:
                self.start_heartbeat(lcm.next_interval_ms)

        if self.waiter is not None:
            self.waiter.set_done(response.correlation_id, response)

    def _on_notify(self, notify: BLCPNotify) -> None:
        if self.notifies.full():
            self.notifies.get_nowait()

        self.notifies.put_nowait(notify)
