from aiogram import Router, F
from aiogram.filters import MagicData
from aiogram.types import Message
from fluent.runtime import FluentLocalization

router = Router(name="error")


# TODO: отправлять ошибку, которая пришла из мидлвари
# TODO: и уходить в errors_handler, если он есть
@router.message(MagicData(F.error))
async def error_in_transfer(
        message: Message,
        error: str,
        l10n: FluentLocalization
):
    await message.answer(l10n.format_value(error))
