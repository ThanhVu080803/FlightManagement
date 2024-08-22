from app import db, app
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from flask_login import UserMixin
from datetime import datetime, date, time

class UserRoleEnum(enum.Enum):
    CUSTOMER = 1
    STAFF = 2
    ADMIN = 3

class AirportRole(enum.Enum):
    DEPARTURE = 1
    ARRIVAL = 2
    INTERMEDIATE = 3

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=True)
    avatar = Column(String(100), default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg')
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.CUSTOMER)
    joined_date = Column(DateTime, default=datetime.now())
    def __str__(self):
        return self.firstname

class Customer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=True)
    User = relationship('User', uselist=False)
    ticket = relationship('Ticket', backref='Customer', lazy=True)
    def __str__(self):
        return self.user_id.name

class Staff(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=True)
    User = relationship('User', uselist=False)
    flight_schedules = relationship("FlightSchedule", backref='Staff', lazy=True)

class Admin(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=True)
    User = relationship('User', uselist=False)
    Stats = relationship('Stats', backref='Admin', lazy=True)

class Airport(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    airport_address = Column(String(50), nullable=False)
    routes = relationship("RoutesInfo", backref="Airport", lazy=True)
    def __str__(self):
        return self.name

class Stats(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey(Admin.id), nullable=False)
    revenue = Column(Float, nullable=False)
    num_of_flights = Column(Integer, nullable=False)
    ratio = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)
    total_revenue = Column(Float, nullable=False)
    routes = relationship('Routes', backref='Stats', lazy=True)


class Routes(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    stats_id = Column(Integer, ForeignKey(Stats.id), nullable=False)
    flights = relationship('Flight', backref='Routes', lazy=True)
    airport = relationship("RoutesInfo", backref="Routes")

    def __str__(self):
        return self.name

class RoutesInfo(db.Model):
    airport_id = Column(Integer, ForeignKey(Airport.id), primary_key=True)
    routes_id = Column(Integer, ForeignKey(Routes.id), primary_key=True)
    airport_role = Column(Enum(AirportRole), nullable=False)
    stop_time = Column(Float, nullable=True)
    note = Column(String(500), nullable=True)

class Plane(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    flight = relationship('Flight', backref='Plane', lazy=True)
    seats = relationship('Seat', backref='Plane', lazy=True)
    def __str__(self):
        return self.name



# default value for empty ticket
def default_value(column_name):
    def default(context):
        return context.get_current_parameters()[column_name]
    return default


class FlightSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_details = relationship("FlightDetails", backref='FlightSchedule', lazy=True)
    staff = Column(Integer, ForeignKey(Staff.id), nullable=False)

class Flight(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    plane_id = Column(Integer, ForeignKey(Plane.id), nullable=False)
    routes_id = Column(Integer, ForeignKey(Routes.id), nullable=False)
    flight_detail_id = relationship("FlightDetails", backref="Flight", uselist=False)
    tickets = relationship('Ticket', backref='Flight', lazy=True)
    flight_name = db.Column(db.String(64), unique=True)

class FlightDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False, unique=True)
    flight_schedule_id = Column(Integer, ForeignKey(FlightSchedule.id), nullable=False)
    time = Column(DateTime, nullable=False)
    flight_duration = Column(Float, nullable=False)
    num_of_seats_1st_class = Column(Integer, nullable=False)
    num_of_seats_2st_class = Column(Integer, nullable=False)
    num_of_empty_seats_1st_class = Column(Integer, default=default_value('num_of_seats_1st_class'), nullable=False)
    num_of_empty_seats_2st_class = Column(Integer, default=default_value('num_of_seats_2st_class'), nullable=False)

    def __str__(self):
        return f'Chi tiết chuyến bay có mã {self.flight_id}'

class FareClass(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    tickets = relationship('Ticket', backref='FareClass', lazy=True)
    def __str__(self):
        return self.name

class Seat(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    plane_id = Column(Integer, ForeignKey(Plane.id), nullable=False)
    fare_class_id = Column(Integer, ForeignKey(FareClass.id), nullable=False)
    ticket = relationship("Ticket", backref="Seat", uselist=False)
    def __str__(self):
        return self.name

class Ticket(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False)
    fare_class_id = Column(Integer, ForeignKey(FareClass.id), nullable=False)
    booking_date = Column(DateTime, default=datetime.now())
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    seat = Column(Integer, ForeignKey(Seat.id), nullable=False, unique=True)

# class Rule(db.Model):
#     num_of_airport = Column(Integer, nullable=False)
#     minimum_duration = Column(Integer, nullable=False)
#     num_of_intermediate_airport = Column(Integer, nullable=False)
#     max_stoptime = Column(Float, nullable=False)
#     min_stoptime = Column(Float, nullable=False)
#     num_of_seats_1st_class = Column(Integer, nullable=False)
#     num_of_seats_2st_class = Column(Integer, nullable=False)
#     price_of_seats_1st_class = Column(Float, nullable=False)


if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        #
        # user1 = User(last_name='Nguyen', first_name='Van A', phone='0931825412', address='111 van troi',
        #              email='vana@gmail.com', password='123')
        # user2 = User(last_name='Nguyen', first_name='Van B', phone='0731825412', address='112 van troi',
        #              email='vanb@gmail.com', password='123')
        # user3 = User(last_name='Nguyen', first_name='Van C', phone='0831825412', address='113 van troi',
        #              email='vanc@gmail.com', password='123')
        # user4 = User(last_name='Nguyen', first_name='Van D', phone='0631825412', address='114 van troi',
        #              email='vand@gmail.com', password='123')
        # db.session.add_all([user1, user2, user3, user4])
        # db.session.commit()
        #
        # customer1 = Customer(user_id=2)
        # customer2 = Customer(user_id=3)
        # customer3 = Customer(user_id=4)
        # db.session.add_all([customer1, customer2, customer3])
        # db.session.commit()
        #
        # staff1 = Staff(user_id=3)
        # staff2 = Staff(user_id=4)
        # staff3 = Staff(user_id=1)
        # db.session.add_all([staff1, staff2, staff3])
        # db.session.commit()
        #
        # admin1 = Admin(user_id=4)
        # admin2 = Admin(user_id=1)
        # admin3 = Admin(user_id=2)
        # db.session.add_all([admin1, admin2, admin3])
        # db.session.commit()
        #
        #
        #
        #
        # stats1 = Stats(admin_id=1, revenue=9213000, num_of_flights=321, ratio=88, month=1, total_revenue=593100000)
        # stats2 = Stats(admin_id=1, revenue=3986000, num_of_flights=222, ratio=74, month=2, total_revenue=361200000)
        # stats3 = Stats(admin_id=1, revenue=3123000, num_of_flights=263, ratio=62, month=3, total_revenue=461000000)
        # stats4 = Stats(admin_id=2, revenue=4657000, num_of_flights=314, ratio=91, month=4, total_revenue=562000000)
        # stats5 = Stats(admin_id=2, revenue=5354000, num_of_flights=110, ratio=86, month=5, total_revenue=253000000)
        # stats6 = Stats(admin_id=2, revenue=6123000, num_of_flights=91, ratio=78, month=6, total_revenue=164000000)
        # stats7 = Stats(admin_id=3, revenue=7543000, num_of_flights=112, ratio=67, month=7, total_revenue=265000000)
        # stats8 = Stats(admin_id=3, revenue=8120000, num_of_flights=120, ratio=57, month=8, total_revenue=366000000)
        # stats9 = Stats(admin_id=3, revenue=2840000, num_of_flights=100, ratio=79, month=9, total_revenue=166000000)
        # stats10 = Stats(admin_id=1, revenue=9840000, num_of_flights=98, ratio=90, month=10, total_revenue=166000000)
        # stats11 = Stats(admin_id=2, revenue=7640000, num_of_flights=113, ratio=60, month=11, total_revenue=321100000)
        # stats12 = Stats(admin_id=3, revenue=6640000, num_of_flights=103, ratio=79, month=12, total_revenue=226000000)
        #
        #
        #
        # db.session.add_all([stats1,stats2,stats3,stats4, stats5, stats6, stats7, stats8])
        # db.session.commit()
        #
        # airport1 = Airport(name='Noi Bai', airport_address='Ha Noi')
        # airport2 = Airport(name='Tan Son Nhat', airport_address='TP Ho Chi Minh')
        # airport3 = Airport(name='Can Tho', airport_address='Can Tho')
        # airport4 = Airport(name='Da Nang', airport_address='Da Nang')
        # airport5 = Airport(name='Ca Mau', airport_address='Ca Mau')
        # airport6 = Airport(name='Phu Quoc', airport_address='Phu Quoc')
        # airport7 = Airport(name='Dien Bien Phu', airport_address='Dien Bien')
        # airport8 = Airport(name='Tho Xuan', airport_address='Thanh Hoa')
        # airport9 = Airport(name='Phu Bai', airport_address='Hue')
        # airport10 = Airport(name='Pleiku', airport_address='Pleiku')
        # airport11 = Airport(name='Chu Lai', airport_address='Chu Lai')
        # airport12 = Airport(name='Dong Hoi', airport_address='Dong Hoi')
        # airport13 = Airport(name='Rach Gia', airport_address='Rach Gia')
        # airport14 = Airport(name='Buon Ma Thuot', airport_address='Buon Ma Thuot')
        # airport15 = Airport(name='Lien Khuong', airport_address='Lien Khuong')
        # airport16 = Airport(name='Con Dao', airport_address='Con Dao')
        # airport17 = Airport(name='Vinh ', airport_address='Vinh ')
        #
        # db.session.add_all([airport1,airport2,airport3,airport4, airport5, airport6,airport7,airport8, airport9
        #                     ,airport10,airport11,airport12,airport13,airport14,airport15,airport16,airport17])
        # db.session.commit()
        #
        # routes1 = Routes(name='Ha Noi - TP HCM', stats_id=1)
        # routes2 = Routes(name='Can Tho - TP HCM', stats_id=2)
        # routes3 = Routes(name='Da Nang - TP HCM', stats_id=3)
        # routes4 = Routes(name='Ca Mau - Phu Quoc', stats_id=4)
        # routes5 = Routes(name='Can Tho - Ha Noi', stats_id=5)
        # # routes6 = Routes(name='Phu Quoc - Tho Xuan', stats_id=6)
        # # routes7 = Routes(name='Dien Bien Phu - Tho Xuan', stats_id=7)
        # # routes8 = Routes(name='Tho Xuan - Can Tho', stats_id=8)
        # # routes9 = Routes(name='Ha Noi - Phu Bai', stats_id=9)
        # # routes10 = Routes(name='Pleiku - Dong Hoi', stats_id=10)
        # # routes11 = Routes(name='Chu Lai - Phu Bai', stats_id=11)
        # # routes12 = Routes(name='Tho Xuan - TP HCM', stats_id=12)
        # # routes13 = Routes(name='Rach Gia - Can Tho', stats_id=1)
        # # routes14= Routes(name='Buon Ma Thuot - TP HCM', stats_id=2)
        # # routes15= Routes(name='Rach Gia - Lien Khuong', stats_id=3)
        # # routes16= Routes(name='Con Dao - Phu Quoc', stats_id=3)
        # # routes17= Routes(name='Phu Cat - Tho Xuan', stats_id=4)
        # # routes18= Routes(name='Vinh - Tho Xuan', stats_id=5)
        # # routes19= Routes(name='Lien Khuong - Can Tho', stats_id=6)
        # # routes20= Routes(name='Chu Lai - Phu Bai', stats_id=7)
        #
        # db.session.add_all([routes1, routes2, routes3, routes4, routes5])
        # db.session.commit()
        #
        # routes_info1 = RoutesInfo(airport_id=1,routes_id=1, airport_role=AirportRole.DEPARTURE)
        # routes_info2 = RoutesInfo(airport_id=2, routes_id=1, airport_role=AirportRole.ARRIVAL)
        # routes_info3 = RoutesInfo(airport_id=3, routes_id=2, airport_role=AirportRole.DEPARTURE)
        # routes_info4 = RoutesInfo(airport_id=2, routes_id=2, airport_role=AirportRole.ARRIVAL)
        # routes_info5 = RoutesInfo(airport_id=4, routes_id=3, airport_role=AirportRole.DEPARTURE)
        # routes_info6 = RoutesInfo(airport_id=2, routes_id=3, airport_role=AirportRole.ARRIVAL)
        # routes_info7 = RoutesInfo(airport_id=5, routes_id=4, airport_role=AirportRole.DEPARTURE)
        # routes_info8 = RoutesInfo(airport_id=6, routes_id=4, airport_role=AirportRole.ARRIVAL)
        # routes_info9 = RoutesInfo(airport_id=3, routes_id=5, airport_role=AirportRole.DEPARTURE)
        # routes_info10 = RoutesInfo(airport_id=1, routes_id=5, airport_role=AirportRole.ARRIVAL)
        #
        # db.session.add_all([routes_info1,routes_info2,routes_info3,routes_info4,routes_info5,routes_info6,routes_info7
        #                        ,routes_info8,routes_info9, routes_info10])
        # db.session.commit()
        #
        # plane1 = Plane(name='VietNam Airlines')
        # plane2 = Plane(name='Vietjet Air')
        # plane3 = Plane(name='Jetstar Pacific')
        # plane4 = Plane(name='Bamboo Airways')
        # plane5 = Plane(name='Japan Airlines')
        # db.session.add_all([plane1,plane2,plane3,plane4,plane5])
        # db.session.commit()
        #
        #
        # flight_schedule1 = FlightSchedule(staff=1)
        # flight_schedule2 = FlightSchedule(staff=2)
        # flight_schedule3 = FlightSchedule(staff=3)
        # db.session.add_all([flight_schedule1,flight_schedule2,flight_schedule3])
        # db.session.commit()
        #
        #
        # flight1 = Flight(plane_id=1, routes_id=1, flight_name='VN001')
        # flight2 = Flight(plane_id=2, routes_id=1, flight_name='VN002')
        # flight3 = Flight(plane_id=3, routes_id=1, flight_name='VN003')
        # flight4 = Flight(plane_id=4, routes_id=2, flight_name='VN004')
        # flight5 = Flight(plane_id=1, routes_id=2, flight_name='VN005')
        # flight6 = Flight(plane_id=2, routes_id=2, flight_name='VN006')
        # flight7 = Flight(plane_id=3, routes_id=2, flight_name='VN007')
        # flight8 = Flight(plane_id=4, routes_id=3, flight_name='VN008')
        # flight9 = Flight(plane_id=1, routes_id=3, flight_name='VN009')
        # flight10 = Flight(plane_id=1, routes_id=3, flight_name='VN010')
        # flight11 = Flight(plane_id=2, routes_id=3, flight_name='VN011')
        # flight12 = Flight(plane_id=3, routes_id=3, flight_name='VN012')
        # flight13 = Flight(plane_id=4, routes_id=4, flight_name='VN013')
        # flight14 = Flight(plane_id=1, routes_id=4, flight_name='VN014')
        # flight15 = Flight(plane_id=2, routes_id=4, flight_name='VN015')
        # flight16 = Flight(plane_id=3, routes_id=5, flight_name='VN016')
        # flight17 = Flight(plane_id=4, routes_id=5, flight_name='VN017')
        # flight18 = Flight(plane_id=1, routes_id=5, flight_name='VN018')
        # flight19 = Flight(plane_id=4, routes_id=5, flight_name='VN019')
        # flight20 = Flight(plane_id=1, routes_id=5, flight_name='VN020')
        #
        # db.session.add_all([flight1,flight2,flight3,flight4,flight5,flight6,flight7,flight8,flight9,flight10
        #                     ,flight11,flight12,flight13,flight14,flight15,flight16,flight17,flight18,flight19,flight20])
        # db.session.commit()
        #
        # flight_details1 = FlightDetails(flight_id=1, time=datetime(2024,5,9,11,00,00),
        #                                flight_duration=6.5, num_of_seats_1st_class = 100
        #                                , num_of_seats_2st_class=50, flight_schedule_id=1)
        # flight_details2 = FlightDetails(flight_id=2, time=datetime(2024,6,23,10,00,00),
        #                                 flight_duration=11.2, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=1)
        # flight_details3 = FlightDetails(flight_id=3, time=datetime(2024,7,12,12,00,00),
        #                                 flight_duration=8, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50,  flight_schedule_id=1)
        # flight_details4 = FlightDetails(flight_id=4, time=datetime(2024,6,15,12,00,00),
        #                                 flight_duration=9, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=2)
        # flight_details5 = FlightDetails(flight_id=5, time=datetime(2024, 6, 15, 3, 00, 00),
        #                                 flight_duration=2, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=3)
        # flight_details6 = FlightDetails(flight_id=6, time=datetime(2024, 2, 3, 4, 00, 00),
        #                                 flight_duration=5, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=3)
        # flight_details7 = FlightDetails(flight_id=7, time=datetime(2024, 8, 9, 12, 00, 00),
        #                                 flight_duration=9, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=1)
        # flight_details8 = FlightDetails(flight_id=8, time=datetime(2024, 4, 2, 23, 00, 00),
        #                                 flight_duration=4, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=3)
        # flight_details9 = FlightDetails(flight_id=9, time=datetime(2024, 3, 17, 21, 00, 00),
        #                                 flight_duration=7, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=2)
        # flight_details10 = FlightDetails(flight_id=10, time=datetime(2024, 10, 19, 15, 35, 00),
        #                                 flight_duration=7.5, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=1)
        # flight_details11 = FlightDetails(flight_id=11, time=datetime(2024, 8, 22, 16, 40, 00),
        #                                 flight_duration=12.3, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=1)
        # flight_details12 = FlightDetails(flight_id=12, time=datetime(2024, 12, 12, 12, 00, 00),
        #                                 flight_duration=8.7, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=1)
        # flight_details13 = FlightDetails(flight_id=13, time=datetime(2024, 5, 13, 18, 30, 00),
        #                                 flight_duration=9, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=2)
        # flight_details14 = FlightDetails(flight_id=14, time=datetime(2024, 2, 25, 13, 45, 00),
        #                                 flight_duration=5.6, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=3)
        # flight_details15 = FlightDetails(flight_id=15, time=datetime(2024, 4, 13, 14, 00, 00),
        #                                 flight_duration=5, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=3)
        # flight_details16 = FlightDetails(flight_id=16, time=datetime(2024, 1, 12, 22, 50, 00),
        #                                 flight_duration=5.8, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=1)
        # flight_details17 = FlightDetails(flight_id=17, time=datetime(2024, 7, 13, 6, 45, 00),
        #                                 flight_duration=4.5, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=3)
        # flight_details18 = FlightDetails(flight_id=18, time=datetime(2024, 4, 27, 11, 00, 00),
        #                                 flight_duration=6.9, num_of_seats_1st_class=100
        #                                 , num_of_seats_2st_class=50, flight_schedule_id=2)
        # flight_details19 = FlightDetails(flight_id=19, time=datetime(2024, 12, 29, 4, 25, 00),
        #                                  flight_duration=4.5, num_of_seats_1st_class=100
        #                                  , num_of_seats_2st_class=50, flight_schedule_id=3)
        # flight_details20 = FlightDetails(flight_id=20, time=datetime(2024, 11, 8, 14, 50, 00),
        #                                  flight_duration=6.9, num_of_seats_1st_class=100
        #                                  , num_of_seats_2st_class=50, flight_schedule_id=2)
        # db.session.add_all([flight_details1,flight_details2,flight_details3,flight_details4,flight_details5,flight_details6,flight_details7,flight_details8,flight_details9,
        #                     flight_details10,flight_details11,flight_details12,flight_details13,flight_details14,flight_details15,flight_details16,flight_details17,
        #                     flight_details18,flight_details19,flight_details20])
        # db.session.commit()
        #
        # fareclass1 = FareClass(name = 'Thuong Gia', price=9800000)
        # fareclass2 = FareClass(name='Pho Thong', price=1200000)
        # db.session.add_all([fareclass1,fareclass2])
        # db.session.commit()
        # #
        # seat1 = Seat(name='Ghe 1', plane_id=1, fare_class_id=1)
        # seat2 = Seat(name='Ghe 2', plane_id=1, fare_class_id=2)
        # seat3 = Seat(name='Ghe 3', plane_id=2, fare_class_id=1)
        # seat4 = Seat(name='Ghe 4', plane_id=2, fare_class_id=2)
        # seat5 = Seat(name='Ghe 5', plane_id=3, fare_class_id=1)
        # seat6 = Seat(name='Ghe 6', plane_id=3, fare_class_id=2)
        # seat7 = Seat(name='Ghe 7', plane_id=4, fare_class_id=1)
        # seat8 = Seat(name='Ghe 8', plane_id=4, fare_class_id=2)
        # seat9 = Seat(name='Ghe 9', plane_id=5, fare_class_id=2)
        # seat10 = Seat(name='Ghe 10', plane_id=5, fare_class_id=1)
        # seat1 = Seat(name='Ghe 1', plane_id=1, fare_class_id=1)
        # seat2 = Seat(name='Ghe 2', plane_id=1, fare_class_id=2)
        # seat3 = Seat(name='Ghe 3', plane_id=2, fare_class_id=1)
        # seat4 = Seat(name='Ghe 4', plane_id=2, fare_class_id=2)
        # seat5 = Seat(name='Ghe 5', plane_id=3, fare_class_id=1)
        # seat6 = Seat(name='Ghe 6', plane_id=3, fare_class_id=2)
        # seat7 = Seat(name='Ghe 7', plane_id=4, fare_class_id=1)
        # seat8 = Seat(name='Ghe 8', plane_id=4, fare_class_id=2)
        # seat9 = Seat(name='Ghe 9', plane_id=5, fare_class_id=2)
        # seat10 = Seat(name='Ghe 10', plane_id=5, fare_class_id=1)
        # seat1 = Seat(name='Ghe 1', plane_id=1, fare_class_id=1)
        # seat2 = Seat(name='Ghe 2', plane_id=1, fare_class_id=2)
        # seat3 = Seat(name='Ghe 3', plane_id=2, fare_class_id=1)
        # seat4 = Seat(name='Ghe 4', plane_id=2, fare_class_id=2)
        # seat5 = Seat(name='Ghe 5', plane_id=3, fare_class_id=1)
        # seat6 = Seat(name='Ghe 6', plane_id=3, fare_class_id=2)
        # seat7 = Seat(name='Ghe 7', plane_id=4, fare_class_id=1)
        # seat8 = Seat(name='Ghe 8', plane_id=4, fare_class_id=2)
        # seat9 = Seat(name='Ghe 9', plane_id=5, fare_class_id=2)
        # seat10 = Seat(name='Ghe 10', plane_id=5, fare_class_id=1)
        # seat1 = Seat(name='Ghe 1', plane_id=1, fare_class_id=1)
        # seat2 = Seat(name='Ghe 2', plane_id=1, fare_class_id=2)
        # seat3 = Seat(name='Ghe 3', plane_id=2, fare_class_id=1)
        # seat4 = Seat(name='Ghe 4', plane_id=2, fare_class_id=2)
        # seat5 = Seat(name='Ghe 5', plane_id=3, fare_class_id=1)
        # seat6 = Seat(name='Ghe 6', plane_id=3, fare_class_id=2)
        # seat7 = Seat(name='Ghe 7', plane_id=4, fare_class_id=1)
        # seat8 = Seat(name='Ghe 8', plane_id=4, fare_class_id=2)
        # seat9 = Seat(name='Ghe 9', plane_id=5, fare_class_id=2)
        # seat10 = Seat(name='Ghe 10', plane_id=5, fare_class_id=1)
        #
        # db.session.add_all([seat1,seat2,seat3,seat4,seat5,seat6,seat7,seat8,seat9,seat10])
        # db.session.commit()
        # #
        # ticket1 = Ticket(flight_id=1,  fare_class_id=1, customer_id=1, seat=1)
        # ticket2 = Ticket(flight_id=1, fare_class_id=2, customer_id=2, seat=2)
        # ticket3 = Ticket(flight_id=2, fare_class_id=1, customer_id=3, seat=3)
        # ticket4 = Ticket(flight_id=2, fare_class_id=2, customer_id=1, seat=4)
        # ticket5 = Ticket(flight_id=3, fare_class_id=1, customer_id=2, seat=5)
        # ticket6 = Ticket(flight_id=3, fare_class_id=2, customer_id=3, seat=6)
        # ticket7 = Ticket(flight_id=4, fare_class_id=1, customer_id=1, seat=7)
        # ticket8 = Ticket(flight_id=4, fare_class_id=2, customer_id=2, seat=8)
        # ticket9 = Ticket(flight_id=5, fare_class_id=1, customer_id=3, seat=9)
        # ticket10 = Ticket(flight_id=5, fare_class_id=2, customer_id=1, seat=10)
        # ticket11 = Ticket(flight_id=6, fare_class_id=1, customer_id=2, seat=11)
        # ticket12 = Ticket(flight_id=6, fare_class_id=2, customer_id=3, seat=12)
        # ticket13 = Ticket(flight_id=7, fare_class_id=1, customer_id=1, seat=14)
        # ticket14 = Ticket(flight_id=7, fare_class_id=2, customer_id=2, seat=15)
        # ticket15 = Ticket(flight_id=8, fare_class_id=1, customer_id=3, seat=16)
        # ticket16 = Ticket(flight_id=8, fare_class_id=2, customer_id=1, seat=13)
        # ticket17 = Ticket(flight_id=9, fare_class_id=1, customer_id=2, seat=17)
        # ticket18 = Ticket(flight_id=9, fare_class_id=2, customer_id=3, seat=18)
        # ticket19 = Ticket(flight_id=10, fare_class_id=1, customer_id=1, seat=19)
        # ticket20 = Ticket(flight_id=10, fare_class_id=2, customer_id=2, seat=20)
        # ticket21 = Ticket(flight_id=11, fare_class_id=1, customer_id=3, seat=21)
        # ticket22 = Ticket(flight_id=11, fare_class_id=2, customer_id=1, seat=22)
        # ticket23 = Ticket(flight_id=12, fare_class_id=1, customer_id=2, seat=23)
        # ticket24 = Ticket(flight_id=12, fare_class_id=2, customer_id=3, seat=24)
        # ticket25 = Ticket(flight_id=13, fare_class_id=1, customer_id=1, seat=25)
        # ticket26 = Ticket(flight_id=13, fare_class_id=2, customer_id=2, seat=26)
        # ticket27 = Ticket(flight_id=14, fare_class_id=1, customer_id=3, seat=27)
        # ticket28 = Ticket(flight_id=14, fare_class_id=2, customer_id=1, seat=28)
        # ticket29 = Ticket(flight_id=15, fare_class_id=1, customer_id=2, seat=29)
        # ticket30 = Ticket(flight_id=15, fare_class_id=2, customer_id=3, seat=30)
        # ticket31 = Ticket(flight_id=16, fare_class_id=1, customer_id=1, seat=31)
        # ticket32 = Ticket(flight_id=16, fare_class_id=2, customer_id=2, seat=32)
        # ticket33 = Ticket(flight_id=17, fare_class_id=1, customer_id=3, seat=33)
        # ticket34 = Ticket(flight_id=17, fare_class_id=2, customer_id=1, seat=34)
        # ticket35 = Ticket(flight_id=18, fare_class_id=1, customer_id=2, seat=35)
        # ticket36= Ticket(flight_id=18, fare_class_id=2, customer_id=3, seat=36)
        # ticket37 = Ticket(flight_id=19, fare_class_id=1, customer_id=1, seat=37)
        # ticket38 = Ticket(flight_id=19, fare_class_id=2, customer_id=2, seat=38)
        # ticket39 = Ticket(flight_id=20, fare_class_id=1, customer_id=3, seat=39)
        # ticket40 = Ticket(flight_id=20, fare_class_id=2, customer_id=1, seat=40)
        #
        # db.session.add_all([ticket1,ticket2,ticket3,ticket4,ticket5,ticket6,ticket7,ticket8,ticket9,ticket10,ticket11,
        #                     ticket12,ticket13,ticket14,ticket15,ticket16,ticket17,ticket18,ticket19,ticket20,ticket21,
        #                     ticket22, ticket23,ticket24,ticket25,ticket26,ticket27,ticket28,ticket29,ticket30,ticket31,
        #                     ticket32,ticket33,ticket34,ticket35,ticket36,ticket37,ticket38,ticket39,ticket40])
        # db.session.commit()
