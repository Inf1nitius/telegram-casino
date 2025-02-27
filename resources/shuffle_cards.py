from random import shuffle


def shuffle_cards() -> list[str]:
    with open("resources/cards.txt", "r", encoding="utf-8") as f:
        cards = f.read().splitlines()
    shuffle(cards)
    return cards

def shuffle_cards_txt() -> None:
    with open("resources/shuffled_cards.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(shuffle_cards()))


if __name__ == "__main__":
    shuffle_cards_txt()
