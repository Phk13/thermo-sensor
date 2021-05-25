from flask_restful import Api
from app.reading import Reading
from app import app


api = Api(app)
api.add_resource(Reading, '/sensor')
