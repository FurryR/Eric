from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    ElementMatch,
    ElementResult,
)
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.saya import Channel
from graiax.fastapi.saya import route
from loguru import logger

from library.decorator.distribute import Distribution
from library.decorator.switch import Switch
from library.decorator.timer import timer
from library.model.response import GeneralResponse
from library.util.dispatcher import PrefixMatch

channel = Channel.current()


@route.get("/ping", response_model=GeneralResponse)
async def ping_web():
    logger.success("[Ping] 收到来自 Web 的 Ping 请求")
    return {"code": 200, "message": "pong"}


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(ElementMatch(At, optional=True) @ "at", PrefixMatch(), FullMatch("ping"))
)
@decorate(Switch.check(channel.module))
@timer(channel.module)
async def ping_message(app: Ariadne, event: MessageEvent, at: ElementResult):
    if at.matched and at.result.target != app.account:
        return
    if Distribution.is_self(event.sender.id):
        logger.warning(f"[Ping] 由已登录账号 {event.sender.id} 触发，停止执行")
        return
    await app.send_message(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain(Plain("pong")),
    )
