import toml

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from resources.shuffle_cards import shuffle_cards


def draw(deck: list) -> tuple[str, str, list[str]]:
    return deck.pop(0), deck.pop(0), deck


def get_card_value(card_drawn: str, config: dict) -> int:
    return next(
        (
            card['score']
            for card in config['cards']['values']
            if card['value'] == card_drawn[:-1]
        ),
        None,
    )


def save_game_state(ctx: ContextTypes.DEFAULT_TYPE, chat_id: int, state: dict) -> None:
    if 'highlow' not in ctx.bot_data:
        ctx.bot_data['highlow'] = {}

    ctx.bot_data['highlow'][chat_id] = state


def get_game_state(ctx: ContextTypes.DEFAULT_TYPE, chat_id: int) -> dict:
    if 'highlow' not in ctx.bot_data:
        ctx.bot_data['highlow'] = {}

    return ctx.bot_data['highlow'].get(
        chat_id,
        {
            'score': 0,
            'high_score': 0,
        },
    )


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if 'deck' not in ctx.user_data:
        ctx.user_data['deck'] = shuffle_cards()

    player_card, dealer_card, deck = draw(ctx.user_data['deck'])
    ctx.user_data['deck'] = deck

    save_game_state(
        ctx,
        update.effective_chat.id,
        {
            'player_card': player_card,
            'dealer_card': dealer_card,
            'score': 0,
            'high_score': 0,
        },
    )

    keyboard = [[InlineKeyboardButton('Draw a card', callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(
            'Welcome to Higher or Lower!', reply_markup=reply_markup
        )
    elif hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(
            'Welcome to Higher or Lower!', reply_markup=reply_markup
        )


async def play(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE,
    player_card: str,
    dealer_card: str,
    deck: list[str],
) -> None:
    query = update.callback_query
    await query.answer()

    config = toml.load('config.toml')

    chat_id = update.effective_chat.id
    game_state = get_game_state(ctx, chat_id)

    if query.data == 'start':
        keyboard = [
            [
                InlineKeyboardButton('Higher', callback_data='higher'),
                InlineKeyboardButton('Lower', callback_data='lower'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f'Your card: {player_card}\n\nWill the dealer\'s card be Higher or Lower?',
            reply_markup=reply_markup,
        )

    elif query.data in ['higher', 'lower']:
        player_value = get_card_value(player_card, config)
        dealer_value = get_card_value(dealer_card, config)

        win = (query.data == 'higher' and player_value < dealer_value) or (
            query.data == 'lower' and player_value > dealer_value
        )

        if win:
            game_state['score'] += 1
            result_text = 'You won!'
        else:
            if game_state['score'] > game_state['high_score']:
                game_state['high_score'] = game_state['score']
            game_state['score'] = 0
            result_text = 'You lost!\nScore reset to 0'

        high_score_text = (
            f'\nHigh Score: {game_state.get('high_score', 0)}'
            if game_state['high_score'] > 0
            else ''
        )

        keyboard = [
            [
                InlineKeyboardButton('Higher', callback_data='higher'),
                InlineKeyboardButton('Lower', callback_data='lower'),
            ],
            [InlineKeyboardButton('Quit', callback_data='quit')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if len(deck) >= 2:
            player_card_next, dealer_card_next, deck = draw(deck)
        else:
            deck = shuffle_cards()
            player_card_next, dealer_card_next, deck = draw(deck)

        ctx.user_data['deck'] = deck

        await query.edit_message_text(
            f'{result_text}\n\nYour card was: {player_card}\nDealer\'s card was: {dealer_card}\n\n'
            + f'Score: {game_state['score']}{high_score_text}\n\n'
            + f'Your card: {player_card_next}\n\nWill the dealer\'s card be Higher or Lower?',
            reply_markup=reply_markup,
        )

        save_game_state(
            ctx,
            chat_id,
            {
                'player_card': player_card_next,
                'dealer_card': dealer_card_next,
                'score': game_state['score'],
                'high_score': game_state['high_score'],
            },
        )

    elif query.data == 'quit':
        await query.edit_message_text(f'Game Over.\n\nFinal Score: {game_state['score']}')


async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:    
    chat_id = update.effective_chat.id

    if 'highlow' not in ctx.bot_data:
        ctx.bot_data['highlow'] = {}

    if chat_id not in ctx.bot_data.get('highlow', {}):
        await start(update, ctx)
        if update.callback_query.data == 'start':
            game_state = get_game_state(ctx, chat_id)
            await play(
                update,
                ctx,
                game_state['player_card'],
                game_state['dealer_card'],
                ctx.user_data['deck'],
            )
        return

    game_state = get_game_state(ctx, chat_id)
    await play(
        update,
        ctx,
        game_state['player_card'],
        game_state['dealer_card'],
        ctx.user_data['deck'],
    )


if __name__ == '__main__':
    '''for testing only'''
    with open('shuffled_cards.txt', 'r', encoding='utf-8') as f:
        cards = f.read().splitlines()
    player_card, dealer_card, deck = draw(cards)
