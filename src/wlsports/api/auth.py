import bcrypt
from tornado_json import schema
from tornado_json.exceptions import APIError, api_assert
from tornado.web import authenticated
from pony.orm import db_session

from wlsports.handlers import APIHandler
from wlsports.db import Player as PlayerEntity


class PlayerLogin(APIHandler):

    @schema.validate(
        input_schema={
            "required": ["username", "password"],
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "username": {"type": "string"}
            }
        },
    )
    def post(self):
        """
        POST the required credentials to get back a cookie

        * `username`: Username
        * `password`: Password
        """
        api_assert(
            self.body['username'],
            400,
            log_message="Username field is empty!"
        )

        with db_session:
            player = PlayerEntity.get(username=self.body['username'])
            api_assert(
                player is not None,
                400,
                log_message="No such player {}".format(self.body['username'])
            )

        password = self.body['password']
        # Check if the given password hashed with the player's known
        #   salt matches the stored password
        password_match = bcrypt.hashpw(
            password.encode(),
            player.salt.encode()
        ) == player.password.encode()
        if password_match:
            self.set_secure_cookie(
                "user",
                self.body['username'],
                self.settings['app_config'].session_timeout_days
            )
            return {"username": player.username}
        else:
            raise APIError(
                400,
                log_message="Bad student_number/password combo"
            )

    @schema.validate(
        output_schema={"type": "string"}
    )
    def get(self):
        """GET to check if authenticated.

        Should be obvious from status code (403 vs. 200).
        """
        if not self.get_current_user():
            raise APIError(
                403,
                log_message="Please post to {} to get a cookie".format(
                    "/api/auth/playerlogin")
            )
        else:
            return "You are already logged in."
