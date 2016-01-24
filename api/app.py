from flask import Flask, request
from flask_restful import Resource, Api

from drive import Sheet

app = Flask(__name__)
app.config['DEBUG'] = True
api = Api(app)

sheet = Sheet()


@app.before_request
def before_request():
    sheet.refresh()


class People(Resource):
    def get(self):
        email = request.args.get('email')
        if email:
            return sheet.get_by_email(email)
        return sheet.records

    def post(self):
        sheet.update(**request.form)
        return

api.add_resource(People, '/people')


class Fields(Resource):
    def get(self):
        return sheet.fields

api.add_resource(Fields, '/people/fields')




if __name__ == '__main__':
    app.run(debug=True)
