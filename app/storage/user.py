fake_user_db: dict[int, dict] = {}
user_id_counter = 0


def get_user_db() -> dict[int, dict]:
    return fake_user_db
