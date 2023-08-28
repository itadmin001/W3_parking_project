from flask import Flask, render_template, url_for,request,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete,select,update,and_
from sqlalchemy import create_engine, Column, String, Integer,DateTime,UniqueConstraint,ForeignKey,REAL,Text,text
from datetime import datetime,UTC,timedelta,time
import random


parking = Flask(__name__)
parking.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_.db'
db=SQLAlchemy(parking)
parking.config['SECRET_KEY'] = 'superKalfragilistic'

class Vehicle(db.Model):
    __tablename__ =     "vehicles"
    id =                Column("vehicle_id",Integer,primary_key=True)
    license_plate =     Column("license_plate",String(20),nullable=False, unique=True)
   
    def __repr__(self):
        return f"license plate: {self.license_plate}"


class ParkingSpot(db.Model):
    __tablename__ =     "parking_spots"
    spot_number =       Column(Text,primary_key=True)
    is_occupied =       Column(Integer,default=0)

    def __init__(self, spot_number, is_occupied):
        self.spot_number = spot_number
        self.is_occupied = is_occupied
        
    def __repr__(self):
        return f"spot number: {self.spot_number} is occupied: {self.is_occupied}"

class Transaction(db.Model):
    __tablename__ =     "transactions"
    transaction_id =    Column("transaction_id", Integer,primary_key=True,autoincrement=True)
    ticket_number =     Column("ticket_number", Integer)
    license_plate =     Column("license_plate", Text, ForeignKey('vehicles.license_plate'))
    spot_number =       Column("spot_number", Text,ForeignKey('parking_spots.spot_number'))
    entry_time =        Column("entry_time", DateTime)
    exit_time =         Column("exit_time", DateTime)
    transaction_amount = Column("transaction_amount", REAL)

    def __init__(self,ticket_number,license_plate, spot_number,entry_time):
        self.ticket_number = ticket_number
        self.license_plate = license_plate
        self.entry_time = entry_time
        self.spot_number = spot_number
    def __repr__(self):
        return f"ticket number: {self.ticket_number} license plate: {self.license_plate} entry time: {self.entry_time}, exit time: {datetime.utcnow()} spot number: {self.spot_number}"



@parking.route('/', methods=['POST','GET'])
def index():
    spots_available = db.session.query(ParkingSpot).where(ParkingSpot.is_occupied == 0).all()
    spots = len(spots_available)

    return render_template('index.html', spots=spots)

@parking.route('/ticket/', methods=['POST','GET'])
def ticket():
    return render_template('ticket.html')

@parking.route('/exit/', methods=['POST','GET'])
def exit():
    return render_template('exit.html')

@parking.route('/payment/', methods=['POST','GET'])
def payment():
    cost,total_time,entry_time = int,int,int
    if request.form.get('lic_plate'):
        license_plate = request.form.get('lic_plate')
        session['lic_plate'] = license_plate
    else:
        license_plate = session['lic_plate']
    
    vehicle = db.session.query(Transaction).where(Transaction.license_plate == license_plate).all()
    now = ((datetime.now().replace(microsecond=0).time().hour)*60) + (datetime.now().replace(microsecond=0).time().minute)
    entry_time = ((vehicle[0].entry_time.time().hour)*60) + (vehicle[0].entry_time.time().minute)
    total_time = abs(entry_time-now)
    cost = ((total_time)*(.08))
    
    return render_template('payment.html',cost=cost,now=datetime.now().replace(microsecond=0),entry_time=vehicle[0].entry_time,license_plate=license_plate)

@parking.route('/process/',methods=['POST','GET'])
def process():
    license_plate = session['lic_plate']
    payment_submit = request.form.get('exit_pay')
    exit_time = datetime.now().replace(microsecond=0)
    cost = request.form.get('cost')
    if payment_submit < cost:
        flash("payment declined...please try again")
        return redirect(url_for('payment'))
    else:
        # this_spot = db.session.query(ParkingSpot).where(ParkingSpot.spot_number == Transaction.spot_number)
        release_spot = update(ParkingSpot).where(and_(ParkingSpot.spot_number == Transaction.spot_number,Transaction.license_plate == license_plate)).values(is_occupied=0)
        exit_tm = update(Transaction).where(Transaction.license_plate == license_plate).values(exit_time = exit_time)
        trans_amt = update(Transaction).where(Transaction.license_plate == license_plate).values(transaction_amount=payment_submit)

        db.session.execute(release_spot)
        db.session.execute(exit_tm)
        db.session.execute(trans_amt)
        db.session.commit()

    return redirect(url_for('index'))

@parking.route('/', methods=['POST','GET'])
def help():
    return render_template('help.html')

@parking.route('/functions/', methods=['POST','GET'])
def functions():

    """  ******* VEHICLE IN *******  """
    print(request.method)
    rand = random.randint(1111,9999)
    if request.method == 'POST':
        if request.form.get('submit_val') == 'from_ticket':
            license_plate = request.form.get('lic_plate')
            this_vehicle = Vehicle(license_plate=license_plate)
            spot = db.session.query(ParkingSpot).where(ParkingSpot.is_occupied == 0).all()
            this_spot= (update(ParkingSpot).where(ParkingSpot.spot_number == spot[0].spot_number).values(is_occupied=1))
            now = datetime.now().replace(microsecond=0)
            this_transaction = Transaction(ticket_number=license_plate+str(rand),spot_number=spot[0].spot_number,license_plate=license_plate,entry_time=now)

            db.session.execute(this_spot)
            db.session.add(this_transaction)
            db.session.add(this_vehicle)
            db.session.commit()
        
    return redirect(url_for('index'))
            

@parking.route('/', methods=['POST','GET'])
def admin():
    return render_template('admin.html')


# with parking.app_context():
#     db.create_all()

# with parking.app_context():
#     parking_level = ['A','B','C','D']
#     x = 0
#     y = 1
#     for i in range(1,301):
#         if y > 75:
#             x+=1
#             y=1

#         this_spot_number = parking_level[x]+str(y)
#         this = ParkingSpot(spot_number=this_spot_number,is_occupied=0)
#         db.session.add(this)
#         db.session.commit()
#         y+=1

if __name__ == "__main__":
    parking.run(debug=True)
    
