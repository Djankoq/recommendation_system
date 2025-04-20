from items.position import Position


def main_logic():
    positions = Position.get_recommend_position(44)
    for position in positions:
        print(position)


if __name__ == "__main__":
    main_logic()