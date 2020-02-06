from flask import Flask
from controller.control_panel.control_members import control_members
from controller.control_panel.control_categories import control_categories
from controller.control_panel.control_items import control_items

# configure the apps
e_commerce = Flask(__name__)
e_commerce.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mhqvluwu:SoaOFudyzAgBywON6U3P6vIq02kyC5J5@rajje.db.elephantsql.com/mhqvluwu'
e_commerce.secret_key = 'DevAhmed2772003@#'
# create the image upload configuration
e_commerce.config['IMAGE_UPLOADS'] = 'static/data/uploads/images'
# register blueprints
e_commerce.register_blueprint(control_members)
e_commerce.register_blueprint(control_categories)
e_commerce.register_blueprint(control_items)
# create the index page
@e_commerce.route('/')
def index():
    return """
    <!doctype HTML>
    <html>
        <head>
            <title>Index Page</title>
        </head>
        <body>
            <h1>Hello this is my e-commerce app</h1>
        </body>
    </html>
    """

if __name__ == '__main__':
    e_commerce.run()
