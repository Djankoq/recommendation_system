from items.position import Position

positions = Position.get_recommend_position(1000)
for position in positions:
    print(position)