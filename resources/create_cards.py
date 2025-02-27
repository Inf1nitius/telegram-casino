import toml


def create_cards(
    suits: list[str], values: list[str], custom: list[str] | None = None
) -> list[str]:
    cards = [value['value'] + suit["symbol"] for suit in suits for value in values]
    if custom is not None:
        cards.extend(custom)
    return cards


def create_cards_txt(config: dict) -> None:
    with open("resources/cards.txt", "w", encoding="utf-8") as f:
        f.write(
            "\n".join(create_cards(config["cards"]["suits"], config["cards"]["values"]))
        )


if __name__ == "__main__":
    """for testing only"""
    config = toml.load("config.toml")
    create_cards_txt(config)
