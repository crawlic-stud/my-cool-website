from starlette_admin.contrib.sqlmodel import ModelView

from tables.user import User


class UserView(ModelView):
    exclude_fields_from_list = [User.hashed_password]
