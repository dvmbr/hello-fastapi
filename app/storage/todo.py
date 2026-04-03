# In-memory Storage

todos: dict[int, dict] = {}
todo_id_counter = 0


def get_todo_db() -> dict[int, dict]:
    return todos


def auto_increment_todo_id() -> int:
    global todo_id_counter
    todo_id_counter += 1
    return todo_id_counter
