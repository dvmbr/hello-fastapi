fake_user_db: dict[int, dict] = {}
user_id_counter = 0


def get_user_db() -> dict[int, dict]:
    return fake_user_db


def auto_increment_user_id() -> int:
    global user_id_counter
    user_id_counter += 1
    return user_id_counter
