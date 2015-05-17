from tornado_json import requesthandlers


class AuthMixin(object):

    def get_current_user(self):
        cookie = self.get_secure_cookie("user")
        if cookie is None:
            return None
        else:
            cookie = cookie.decode()

        #user_type, user_id = cookie.split(" ")
        user_id = cookie
        return user_id

    # @property
    # def user_type(self):
    #     cookie = self.get_secure_cookie("user")
    #     if cookie is None:
    #         return None
    #     else:
    #         cookie = cookie.decode()
    #
    #     user_type, user_id = cookie.split(" ")
    #     return user_type


class APIHandler(AuthMixin, requesthandlers.APIHandler):
    """APIHandler"""

    # For PyCharm completion, since this is otherwise dynamically  inserted
    body = None


class ViewHandler(AuthMixin, requesthandlers.ViewHandler):
    """ViewHandler"""
