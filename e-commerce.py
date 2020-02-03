import os
from flask import Flask
from controller.control_panel.control_panel import control_panel

# configure the apps
e_commerce = Flask(__name__)
e_commerce.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mhqvluwu:SoaOFudyzAgBywON6U3P6vIq02kyC5J5@rajje.db.elephantsql.com/mhqvluwu'
e_commerce.secret_key = 'DevAhmed2772003@#'
# register blueprints
e_commerce.register_blueprint(control_panel) 

if __name__ == '__main__':
    e_commerce.run()
