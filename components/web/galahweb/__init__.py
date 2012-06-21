from flask import Flask
app = Flask("galahweb")

# Plug the auth system into our app
from auth import login_manager
login_manager.setup_app(app)

import views
