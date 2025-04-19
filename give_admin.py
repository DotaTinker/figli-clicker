from data import db_session
from data.databaseee import User


def make_user_admin(user_id):
    db_sess = db_session.create_session()

    user = db_sess.query(User).get(user_id)

    if user:
        user.is_admin = True
        db_sess.commit()
        print(f"Пользователь с ID {user_id} теперь является администратором.")
    else:
        print(f"Пользователь с ID {user_id} не найден.")


if __name__ == "__main__":
    db_session.global_init("db/databasee.db")

    user_id = input("Введите ID пользователя, которому нужно предоставить права администратора: ")

    try:
        user_id = int(user_id)
        make_user_admin(user_id)
    except ValueError:
        print("Пожалуйста, введите корректный числовой ID.")