import bcrypt
from tornado_json.exceptions import api_assert
from tornado_json import schema
from pony.orm import db_session

from wlsports.db import Player as PlayerEntity
from wlsports.handlers import APIHandler


class Player(APIHandler):

    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "first": {"type": "string"},
                "last": {"type": "string"},
                "password": {"type": "string"},
                "gender": {"type": "string"},
                "birthday": {"type": "string"},
                "city": {"type": "string"},
                "country": {"type": "string"},
                "bio": {"type": "string"},
            },
            "required": [
                "username",
                "first",
                "last",
                "password",
                "birthday",
                "city",
                "country"
            ],
        },
        output_schema={
            "type": "object",
            "properties": {
                "username": {"type": "string"}
            }
        }
    )
    def put(self):
        """
        PUT the required parameters to permanently register a new player

        * `username`
        * `first`: First name
        * `last`: Last name
        * `password`: Password for future logins
        * `gender`: M/F
        * `birthday`: e.g., "1993-05-16"
        * `city`
        * `country`
        * `bio`
        """
        attrs = dict(self.body)

        # Set salt and password
        salt = bcrypt.gensalt(rounds=12)
        attrs['password'] = bcrypt.hashpw(
            password=attrs['password'].encode(),
            salt=salt
        ).decode()
        attrs['salt'] = salt.decode()

        # Create player
        with db_session:
            player = PlayerEntity(**attrs)

        # Log the user in
        self.set_secure_cookie(
            "user",
            attrs['username'],
            self.settings['app_config'].session_timeout_days
        )

        return {"username": player.username}
