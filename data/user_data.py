from models.user import UserModel


def create_test_users():
    user1 = UserModel(
        name="Arjun Dev",
        username="arjun_dev",
        email="arjun@devmail.in",
        phone="39000001",
    )
    user1.set_password("123")

    user2 = UserModel(
        name="Emma Johnson",
        username="emma_johnson",
        email="emma.johnson@email.com",
        phone="39000002",
    )
    user2.set_password("123")

    user3 = UserModel(
        name="Fatima Ali",
        username="fatima_ali",
        email="fatima.ali@mail.ae",
        phone="39000003",
    )
    user3.set_password("123")

    user4 = UserModel(
        name="Lucas Silva",
        username="lucas_silva",
        email="lucas.silva@correo.br",
        phone="39000004",
    )
    user4.set_password("123")

    user5 = UserModel(
        name="Elena Popov",
        username="elena_popov",
        email="elena.popov@mail.ru",
        phone="39000005",
    )
    user5.set_password("123")

    return [user1, user2, user3, user4, user5]


user_list = create_test_users()