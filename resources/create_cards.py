def create_cards(suits: list[str], values: list[str], custom: list[str] | None = None) -> list[str]:
    suits = ['♠', '♥', '♦', '♣']
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    cards = [suits[i] + value for i in range(len(suits)) for value in values]
    if custom is not None:
        cards.extend(custom)
    return cards

if __name__ == "__main__":
    with open('cards.txt', 'w') as f:
        f.write('\n'.join(create_cards()))