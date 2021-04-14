def get_common_room(user1, user2):
    for room in user1:
        if room in user2:
            return room

    return None

def get_common_rooms(user1, user2):
    rooms = []
    for room in user1:
        if room in user2:
            rooms.append(room)

    return rooms

def get_common_rooms_no_groups(user1, user2):
    rooms = []
    for room in user1:
        if room in user2 and not room.is_group:
            rooms.append(room)

    return rooms