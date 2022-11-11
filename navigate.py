"""Navigate Function

Used to move up or down a list when a keypress is used."""
def navigate(direction, item, position):
    item_length = len(item)
    position += direction
    if position < 0:
        position = 0
    elif position >= item_length:
        position = item_length - 1
    return position
