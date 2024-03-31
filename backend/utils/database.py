import time

from tinydb import TinyDB, Query
from pathlib import Path

userdb = TinyDB(Path("data/userdb.json"))

class DatabaseError(LookupError):
    pass


class NotInDatabaseError(DatabaseError):
    pass


class AlreadyInDatabaseError(DatabaseError):
    pass


class DatabasePermissionsError(DatabaseError):
    pass


def create_new_user(discord_id: int):
    User = Query()
    if userdb.contains(User.id == discord_id):
        raise AlreadyInDatabaseError
    else:
        userdb.insert({"id": discord_id})