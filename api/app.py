from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime
import os
import datetime
import click
from flask_marshmallow import Marshmallow


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'PayTaxes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


#Create database
@app.cli.command("db_create")
def db_create():
    db.create_all()
    print('Database created!')

#Delete database
@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')

#Insert default values to DB
@app.cli.command('db_seed')
def db_seed():
    test_voucher = Voucher(service_name='Energy',
                     service_description='January',
                     #expiration_date='2017-03-02T15:34:10.000272',
                     expiration_date=datetime.date(2013, 1, 1),
                     service_amount=2.258,
                     status='pending',
                     barcode='3598e6')

    db.session.add(test_voucher)
    db.session.commit()
    print('Database seeded!')


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/super_simple')
def super_simple():
    return jsonify(message='Hello from the API.'), 200


@app.route('/not_found')
def not_found():
    return jsonify(message='That resource was not found'), 404


@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message="Sorry " + name + ", you are not old enough."), 401
    else:
        return jsonify(message="Welcome " + name + ", you are old enough!")


@app.route('/voucher', methods=['GET'])
def voucher():
    voucher_list = Voucher.query.all()
    result = voucher_schema.dump(voucher_list)
    return jsonify(result)


@app.route('/add_voucher', methods=['POST'])
def add_voucher():
    barcode = request.form['barcode']
    test = Voucher.query.filter_by(barcode=barcode).first()
    if test:
        return jsonify(message='That barcode already exists.'), 409
    else:
        service_name = request.form['service_name']
        service_description = request.form['service_description']
        expiration_date = datetime.datetime.strptime(request.form['expiration_date'],'%Y-%m-%d') # 2202-04-10
        service_amount = request.form['service_amount']
        status = request.form['status']
        barcode = request.form['barcode']

        voucher = Voucher(service_name=service_name, service_description=service_description, expiration_date=expiration_date, service_amount=service_amount, status=status,barcode=barcode)

        db.session.add(voucher)
        db.session.commit()
        return jsonify(message="Voucher created successfully."), 201



@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("your planetary API password is " + user.password,
                      sender="admin@planetary-api.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to " + email)
    else:
        return jsonify(message="That email doesn't exist"), 401


@app.route('/planet_details/<int:planet_id>', methods=["GET"])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result.data)
    else:
        return jsonify(message="That planet does not exist"), 404


# database models
class Voucher(db.Model):
    __tablename__ = 'voucher'
    id = Column(Integer, primary_key=True)
    service_name = Column(String)
    service_description = Column(String)
    expiration_date = Column(DateTime)
    service_amount = Column(Float)
    status = Column(String)
    barcode = Column(String, unique=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id = Column(Integer, primary_key=True)
    payment_method = Column(String)
    creditcard_number = Column(String)
    payment_amount = Column(Float)
    codio_barra = Column(String, unique=True)
    payment_date = Column(DateTime)


class VoucherSchema(ma.Schema):
    class Meta:
        fields = ('id', 'service_name', 'service_description', 'expiration_date', 'amount','status','codio_barra','created_date' )


class PaymentSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'payment_method', 'creditcard_number', 'payment_amount', 'codio_barra', 'payment_date') 


voucher_schema = VoucherSchema()
vouchers_schema = VoucherSchema(many=True)

payment_schema = PaymentSchema()
payment_schema = PaymentSchema(many=True) 


if __name__ == '__main__':
    app.run()

