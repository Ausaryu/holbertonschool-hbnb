from app import create_app
from app.services import facade


def seed_admin():
    admin_email = "admin@hbnb.io"

    existing_user = facade.get_user_by_email(admin_email)
    if existing_user:
        return

    facade.create_user({
        "email": admin_email,
        "first_name": "Admin",
        "last_name": "User",
        "password": "admin123",
        "is_admin": True
    })


app = create_app()

with app.app_context():
    seed_admin()

if __name__ == '__main__':
    app.run(debug=True)
