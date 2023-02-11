#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Bot who automatice the download of torrents for vistamar-server.
"""

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )


from api import Dontorrent


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
dontorrent = Dontorrent()

users = list(os.environ["USERS"].split(","))

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

# restrict bot usage only to users in list users=[149984283]


def restricted(func):
    """Restrict the bot access only to users in list users"""

    def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in users:
            logger.warning("Unauthorized access denied for %s.", user_id)
            return update.message.reply_text("No tienes permiso para usar este bot")
        return func(update, context, *args, **kwargs)

    return wrapped


async def set_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store the url in the DonTorrent object."""
    dontorrent.url = "https://" + str(context.args[0])
    await update.message.reply_text(f"Url guardada: {dontorrent.url}")


async def show_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the url in the DonTorrent object."""
    await update.message.reply_text(f"Url guardada: {dontorrent.url}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Bienvenido al bot de Vistamar Server")


def create_keyboard_search(data):
    """Create a keyboard with the search results"""
    keyboard = []
    if len(data) % 2 == 0:
        for i in range(0, len(data), 2):
            double_button = []
            for j in range(2):
                double_button.append(
                    InlineKeyboardButton(data[i + j][0], callback_data=i + j)
                )
            keyboard.append(double_button)
        keyboard = keyboard[0:5]
        keyboard.append([InlineKeyboardButton("Cancelar", callback_data="cancel")])
    else:
        for i in range(0, len(data) - 1, 2):
            double_button = []
            for j in range(2):
                double_button.append(
                    InlineKeyboardButton(data[i + j][0], callback_data=i + j)
                )
            keyboard.append(double_button)
        keyboard = keyboard[0:5]
        keyboard.append(
            [
                InlineKeyboardButton(data[-1][0], callback_data=len(data) - 1),
                InlineKeyboardButton("Cancelar", callback_data="cancel"),
            ]
        )

    return keyboard


async def search_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Search for the tv show and return a list with the results"""
    search = " ".join(context.args)
    context.user_data["search"] = search
    hrefs = dontorrent.get_hrefs(search)
    if hrefs is None:
        await update.message.reply_text("No se encontraron resultados")
        return ConversationHandler.END
    context.user_data["hrefs"] = hrefs
    keyboard = create_keyboard_search(hrefs)
    reply_markup = InlineKeyboardMarkup(keyboard[0:6])

    await update.message.reply_text("Por favor escoja:", reply_markup=reply_markup)
    return 1


def create_keyboard_episodes(data):
    """Create a keyboard with the episodes"""
    keyboard = []
    if len(data) % 2 == 0:
        for i in range(0, len(data), 2):
            double_buton = []
            for j in range(2):
                double_buton.append(
                    InlineKeyboardButton(data[i + j].name, callback_data=i + j)
                )
            keyboard.append(double_buton)
        keyboard.append(
            [
                InlineKeyboardButton("Todos", callback_data="ALL"),
                InlineKeyboardButton("Cancelar", callback_data="cancel"),
            ]
        )
    else:
        for i in range(0, len(data) - 1, 2):
            double_buton = []
            for j in range(2):
                double_buton.append(
                    InlineKeyboardButton(data[i + j].name, callback_data=i + j)
                )
            keyboard.append(double_buton)
        keyboard.append(
            [
                InlineKeyboardButton(data[-1].name, callback_data=len(data) - 1),
                InlineKeyboardButton("Todos", callback_data="cancel"),
            ]
        )
        keyboard.append([InlineKeyboardButton("Cancelar", callback_data="cancel")])
    return keyboard


async def ask_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text(text="¡Hasta otra!")
        return ConversationHandler.END

    episodes = dontorrent.get_episodes(
        context.user_data["hrefs"][int(query.data)][1], context.user_data["search"]
    )

    if episodes is None:
        await query.edit_message_text(text="No se encontraron resultados")
        return ConversationHandler.END

    context.user_data["episodes"] = episodes

    keyboard = create_keyboard_episodes(episodes)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Por favor escoja:", reply_markup=reply_markup)
    return 2


async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text(text="¡Hasta otra!")
        return ConversationHandler.END

    if query.data == "ALL":
        for episode in context.user_data["episodes"]:
            if dontorrent.download_torrent(episode):
                await query.edit_message_text(
                    text="Torrent añadido a la cola de descargas"
                )
            else:
                await query.edit_message_text(text="No se ha podido añadir el torrent")
    else:
        if dontorrent.download_torrent(
            context.user_data["episodes"][int(query.data)]
        ):
            await query.edit_message_text(text="Torrent añadido a la cola de descargas")
        else:
            await query.edit_message_text(text="No se ha podido añadir el torrent")

    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Usa /start para empezar a usar este bot.")


async def show_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display user id"""
    await update.message.reply_text(f"El usuario es: {update.effective_user.id}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Bye! I hope we can talk again some day.")

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""   
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    # create a conversation handler to handle the keyboard buttoms inputs
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("buscar", restricted(search_item))],
        states={
            1: [CallbackQueryHandler(ask_episodes)],
            2: [CallbackQueryHandler(end_conversation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", restricted(start)))
    application.add_handler(CommandHandler("help", restricted(help_command)))
    application.add_handler(CommandHandler("url", restricted(set_url)))
    application.add_handler(CommandHandler("show", restricted(show_url)))
    application.add_handler(CommandHandler("user", restricted(show_user)))
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
