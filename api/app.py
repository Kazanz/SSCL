import os

from flask import Flask, request
from flask.ext.cors import CORS
from flask_mail import Mail
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from drive import Sheet
from messaging import Messenger


#############
# Configure #
#############

app = Flask(__name__)
app.config['DEBUG'] = True
app.config.from_object('config')
app.config['MAIL_DEBUG'] = app.debug
CORS(app)

api = Api(app)
db = SQLAlchemy(app)
mail = Mail(app)


##########
# Models #
##########

class Player(db.Model):
    email = db.Column(db.String(40), primary_key=True)
    hash = db.Column(db.String(10), unique=True)
    confirmed = db.Column(db.Boolean(), default=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Player %r>' % self.email

    @staticmethod
    def confirm(hash):
        player = Player.query.filter_by(hash=hash).first()
        if player:
            player.confirmed = True
            db.session.add(player)
            db.session.commit()

    @staticmethod
    def update(email, **kwargs):
        player = Player.query.filter_by(email=email).first()
        if not player:
            player = Player(email=email)
        for k, v in kwargs.items():
            setattr(player, k, v)
        db.session.add(player)
        db.session.commit()


db.create_all()
app.Player = Player


##############
# End Points #
##############

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
        return None, 204

api.add_resource(People, '/api/people')


class Fields(Resource):
    def get(self):
        return sheet.fields

api.add_resource(Fields, '/api/people/fields')


class Messaging(Resource):
    def post(self):
        messenger = Messenger(mail, sheet)
        messenger.subject = request.form.get('subject')
        messenger.body = request.form.get('body')
        success = messenger.send()
        return None, 200

api.add_resource(Messaging, '/api/msg')


class Confirm(Resource):
    def get(self, hash):
        Player.confirm(hash)
        return "Thank you."

api.add_resource(Confirm, '/api/confirm/<path:hash>')


class Confirmed(Resource):
    def get(self):
        return db.session.query(Player.email).filter_by(confirmed=True).all()

api.add_resource(Confirmed, '/api/confirmed')


class Debug(Resource):
    def get(self):
        from flask import current_app
        return current_app.config['DEBUG']

api.add_resource(Debug, '/api/debug')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
