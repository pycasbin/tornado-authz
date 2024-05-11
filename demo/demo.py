# Copyright 2024 The Casbin Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import tornado
from casbin import Enforcer

from tornado_authz import CasbinMiddleware


# Create a CasbinMiddleware instance with the enforcer
enforcer = Enforcer("../examples/authz_model.conf", "../examples/authz_policy.csv")
middleware = CasbinMiddleware(enforcer)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = None
        if self.get_secure_cookie("user"):
            user = self.get_secure_cookie("user").decode('utf-8')
        return user

    def prepare(self):
        # Check the permission for the current request
        middleware(self)


class MainHandler(BaseHandler):
    def get(self):
        self.write("Main Page")


class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/dataset1/")


class DatasetHandler(BaseHandler):
    def get(self):
        self.write("You must be alice to see this.")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/dataset1/.*", DatasetHandler),
    ], cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__")


async def main():
    app = make_app()
    app.listen(8888)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
