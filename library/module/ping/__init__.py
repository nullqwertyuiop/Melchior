from graia.amnesia.message import MessageChain, Text
from graiax.shortcut import decorate, listen
from graiax.shortcut.text_parser import MatchContent, MatchTemplate
from ichika.client import Client
from ichika.core import Friend, Group
from ichika.graia.event import FriendMessage, GroupMessage


@listen(GroupMessage)
@decorate(MatchContent(".ping"), MatchTemplate([Text]))
async def group_ping(client: Client, group: Group):
    await client.send_group_message(group.uin, MessageChain([Text("pong")]))


@listen(FriendMessage)
@decorate(MatchContent(".ping"), MatchTemplate([Text]))
async def friend_ping(client: Client, friend: Friend):
    await client.send_friend_message(friend.uin, MessageChain([Text("pong")]))
