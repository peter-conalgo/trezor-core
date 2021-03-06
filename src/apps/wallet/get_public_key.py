from trezor.messages.HDNodeType import HDNodeType
from trezor.messages.PublicKey import PublicKey
from trezor import ui
from trezor.messages import ButtonRequestType
from trezor.ui.text import Text
from trezor.utils import chunks
from apps.common import coins, seed
from apps.common.confirm import require_confirm
from ubinascii import hexlify


async def get_public_key(ctx, msg):
    coin_name = msg.coin_name or 'Bitcoin'

    curve_name = msg.ecdsa_curve_name
    if not curve_name:
        node = await seed.derive_node(ctx, msg.address_n)
    else:
        node = await seed.derive_node(ctx, msg.address_n, curve_name=curve_name)
    coin = coins.by_name(coin_name)

    node_xpub = node.serialize_public(coin.xpub_magic)
    pubkey = node.public_key()
    if pubkey[0] == 1:
        pubkey = b'\x00' + pubkey[1:]
    node_type = HDNodeType(
        depth=node.depth(),
        child_num=node.child_num(),
        fingerprint=node.fingerprint(),
        chain_code=node.chain_code(),
        public_key=pubkey)

    if msg.show_display:
        await _show_pubkey(ctx, pubkey)

    return PublicKey(node=node_type, xpub=node_xpub)


async def _show_pubkey(ctx, pubkey: bytes):
    lines = chunks(hexlify(pubkey).decode(), 18)
    content = Text('Confirm public key', ui.ICON_RECEIVE, ui.MONO, *lines, icon_color=ui.GREEN)
    return await require_confirm(
        ctx,
        content,
        code=ButtonRequestType.PublicKey)
