import hashlib
from app.models import User, Airport, FlightDetails, AirportRole, Routes, RoutesInfo, Flight, Plane, FareClass, Seat, \
    Staff, FlightSchedule, Ticket
from app import app, db
from datetime import datetime
from sqlalchemy import and_, func
from flask import redirect, url_for

def get_user_by_id(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        return user


def add_user(last_name=None, first_name=None, phone=None, address=None, email=None, password=None):
    if last_name and first_name and phone and address and email and password:
        last_name = last_name.strip()
        first_name = first_name.strip()
        phone = phone.strip()
        address = address.strip()
        email = email.strip()
        password = password.strip()

        user = User(last_name=last_name, first_name=first_name, phone=phone,
                    address=address, email=email, password=password)

        db.session.add(user)
        db.session.commit()


def check_user_existence(email=None, last_name=None, first_name=None):
    if email:
        existing_user_email = User.query.filter_by(email=email.strip()).first()
        if existing_user_email:
            return False
    if last_name and first_name:
        existing_user_name = User.query.filter_by(last_name=last_name.strip(), first_name=first_name.strip()).first()
        if existing_user_name:
            return False
    return True


def auth_user(email=None, password=None):
    if email and password:
        with app.app_context():
            user = User.query.filter_by(email=email.strip()).first()

            if user and user.password == password:
                return user

def get_departure_points():
    return Airport.query.all()
  
def get_flight_details_info(airport_id = None, from_date =None, to_date=None):

    flights = db.session.query(
                    Routes.id.label('route_id'),
                    Routes.name.label('route_name'),
                    Routes.stats_id.label('route_stats_id'),
                    RoutesInfo.airport_id.label('routes_info_airport_id'),
                    RoutesInfo.routes_id.label('routes_info_routes_id'),
                    RoutesInfo.airport_role.label('routes_info_airport_role'),
                    RoutesInfo.stop_time.label('routes_info_stop_time'),
                    RoutesInfo.note.label('routes_info_note'),
                    Flight.id.label('flight_id'),
                    Flight.plane_id.label('flight_plane_id'),
                    Flight.routes_id.label('flight_routes_id'),
                    Flight.flight_name.label('flight_name'),
                    FlightDetails.id.label('flight_details_id'),
                    FlightDetails.flight_id.label('flight_details_flight_id'),
                    FlightDetails.flight_schedule_id.label('flight_details_flight_schedule_id'),
                    FlightDetails.time.label('flight_details_time'),
                    FlightDetails.flight_duration.label('flight_details_duration'),
                    FlightDetails.num_of_seats_1st_class.label('flight_details_seats_1st_class'),
                    FlightDetails.num_of_seats_2st_class.label('flight_details_seats_2st_class'),
                    FlightDetails.num_of_empty_seats_1st_class.label('flight_details_empty_seats_1st_class'),
                    FlightDetails.num_of_empty_seats_2st_class.label('flight_details_empty_seats_2nd_class')
                ).join(RoutesInfo, Routes.id == RoutesInfo.routes_id)\
                 .join(Flight, Routes.id == Flight.routes_id)\
                 .join(FlightDetails, Flight.id == FlightDetails.flight_id)

    if airport_id:
        flights = flights.filter(RoutesInfo.airport_id == airport_id)

    if from_date and to_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%d')  # Remove spaces around the time
        to_date = datetime.strptime(to_date, '%Y-%m-%d')  # Remove spaces around the time
        flights = flights.filter(FlightDetails.time.between(from_date, to_date))
        print(flights)

    return flights.all()

def read_planes():
    return Plane.query.all()
def read_airports():
    return Airport.query.all()

def read_flights():
    return Flight.query.all()
def read_flight_schedules():
    return FlightSchedule.query.all()

def read_staffs():
    return Staff.query.all()
def read_routes():
    return Routes.query.all()

def add_flight_schedule(
                        airport_id = None, routes_id =None,airport_role=None
                        , flight_id = None,
                        flight_schedule_id= None,
                        time= None,flight_duration=None, num_of_seats_1st_class= None,
                        num_of_seats_2st_class= None):

    if ( airport_id and  routes_id and airport_role and
            flight_id and flight_schedule_id and
            time and flight_duration and
            num_of_seats_1st_class and num_of_seats_2st_class ):

        #-----Routes Info
        airport_id = airport_id
        routes_id  = routes_id
        airport_role = airport_role
        # ----Flight details
        flight_id = flight_id
        flight_schedule_id = flight_schedule_id
        time = time
        flight_duration = flight_duration
        num_of_seats_1st_class = num_of_seats_1st_class
        num_of_seats_2st_class = num_of_seats_2st_class


        routes_info = RoutesInfo( airport_id = airport_id,
                                    routes_id  = routes_id ,
                                  airport_role=airport_role)
        db.session.add(routes_info)
        db.session.commit()

        flight_details = FlightDetails(flight_id = flight_id,
                                      flight_schedule_id = flight_schedule_id,
                                       time=time,
                                    flight_duration = flight_duration,
                                    num_of_seats_1st_class = num_of_seats_1st_class,
                                       num_of_seats_2st_class=num_of_seats_2st_class)

        db.session.add(flight_details)
        db.session.commit()
        return redirect(url_for("ticket"))
def read_ticket_by_id(flight_detail_id):
    flights = db.session.query(
        Routes.id.label('route_id'),
        Routes.name.label('route_name'),
        Routes.stats_id.label('route_stats_id'),
       RoutesInfo.airport_id.label('routes_info_airport_id'),
        RoutesInfo.routes_id.label('routes_info_routes_id'),
        RoutesInfo.airport_role.label('routes_info_airport_role'),
        RoutesInfo.stop_time.label('routes_info_stop_time'),
      RoutesInfo.airport_id.label('routes_info_airport_id'),
        RoutesInfo.routes_id.label('routes_info_routes_id'),
        RoutesInfo.airport_role.label('routes_info_airport_role'),
        RoutesInfo.stop_time.label('routes_info_stop_time'),
       RoutesInfo.note.label('routes_info_note'),
        Flight.id.label('flight_id'),
        Flight.plane_id.label('flight_plane_id'),
        Flight.routes_id.label('flight_routes_id'),
        Flight.flight_name.label('flight_name'),
        FlightDetails.id.label('flight_details_id'),
        FlightDetails.flight_id.label('flight_details_flight_id'),
        FlightDetails.flight_schedule_id.label('flight_details_flight_schedule_id'),
        FlightDetails.time.label('flight_details_time'),
        FlightDetails.flight_duration.label('flight_details_duration'),
        FlightDetails.num_of_seats_1st_class.label('flight_details_seats_1st_class'),
        FlightDetails.num_of_seats_2st_class.label('flight_details_seats_2st_class'),
        FlightDetails.num_of_empty_seats_1st_class.label('flight_details_empty_seats_1st_class'),
        FlightDetails.num_of_empty_seats_2st_class.label('flight_details_empty_seats_2nd_class')
    ).join(RoutesInfo, Routes.id == RoutesInfo.routes_id) \
        .join(Flight, Routes.id == Flight.routes_id) \
        .join(FlightDetails, Flight.id == FlightDetails.flight_id)

    for flight in flights:
        if flight.flight_details_id == flight_detail_id:
            return flight
    return None

def get_flight_details(departure_airport_id, arrival_airport_id, departure_date, return_date, num_of_tickets):

    current_time = datetime.now()
    departure_date_input = datetime.strptime(departure_date, '%Y-%m-%d')

    routes_data =  db.session.query(
        Routes.id.label('route_id'),
        Routes.name.label('route_name'),
        RoutesInfo.airport_id.label('routes_info_airport_id'),
        RoutesInfo.routes_id.label('routes_info_routes_id'),
        RoutesInfo.airport_role.label('routes_info_airport_role'),
        RoutesInfo.stop_time.label('routes_info_stop_time'),
        RoutesInfo.note.label('routes_info_note')
    ).join(RoutesInfo, Routes.id == RoutesInfo.routes_id).all()

    temp_route_1 =[]
    temp_route_2 =[]
    for x in routes_data:
        if x.routes_info_airport_id == int(departure_airport_id) and x.routes_info_airport_role == AirportRole.DEPARTURE:
            temp_route_1.append(x)
        if x.routes_info_airport_id == int(arrival_airport_id) and x.routes_info_airport_role == AirportRole.ARRIVAL:
            temp_route_2.append(x)

    route_id = None
    for x in temp_route_1:
        for y in temp_route_2:
            if x.route_id == y.route_id:
                route_id = x.route_id
                break

    flights = (db.session.query(
                Routes.id.label('route_id'),
                Routes.name.label('route_name'),
                RoutesInfo.airport_id.label('routes_info_airport_id'),
                RoutesInfo.routes_id.label('routes_info_routes_id'),
                RoutesInfo.airport_role.label('routes_info_airport_role'),
                RoutesInfo.stop_time.label('routes_info_stop_time'),
                RoutesInfo.note.label('routes_info_note'),
                Flight.id.label('flight_id'),
                Flight.plane_id.label('flight_plane_id'),
                Flight.routes_id.label('flight_routes_id'),
                Flight.flight_name.label('flight_name'),
                FlightDetails.id.label('flight_details_id'),
                FlightDetails.flight_id.label('flight_details_flight_id'),
                FlightDetails.flight_schedule_id.label('flight_details_flight_schedule_id'),
                FlightDetails.time.label('flight_details_time'),
                FlightDetails.flight_duration.label('flight_details_duration'),
                FlightDetails.num_of_seats_1st_class.label('flight_details_seats_1st_class'),
                FlightDetails.num_of_seats_2st_class.label('flight_details_seats_2st_class'),
                FlightDetails.num_of_empty_seats_1st_class.label('flight_details_empty_seats_1st_class'),
                FlightDetails.num_of_empty_seats_2st_class.label('flight_details_empty_seats_2nd_class')
            ).join(RoutesInfo, Routes.id == RoutesInfo.routes_id)
               .join(Flight, Routes.id == Flight.routes_id)
               .join(FlightDetails, Flight.id == FlightDetails.flight_id).all())

    tickets = db.session.query(
                Plane.id.label('plane_id'),
                Plane.name.label('plane_name'),
                FareClass.id.label('fare_class_id'),
                FareClass.name.label('fare_class_name'),
                FareClass.price.label('fare_class_price'),
                Seat.id.label('seat_id'),
                Seat.name.label('seat_name'),
                Flight.id.label('flight_id'),
                Flight.plane_id.label('flight_plane_id'),
                Flight.routes_id.label('flight_routes_id'),
                Flight.flight_name.label('flight_name')
            ).join(Seat, Plane.id == Seat.plane_id) \
                .join(FareClass, Seat.fare_class_id == FareClass.id) \
                .join(Flight, Plane.id == Flight.plane_id).all()

    departure_flight_data = []
    arrival_flight_data = []
    ticket_info =[]

    if route_id:
        for flight in flights:
            if flight.routes_info_airport_id == route_id and flight.routes_info_airport_role == AirportRole.DEPARTURE and flight.flight_details_time.date() == departure_date_input.date():
                departure_flight_data.append(flight)
            if flight.routes_info_airport_id == route_id and flight.routes_info_airport_role == AirportRole.ARRIVAL and flight.flight_details_time.date() == departure_date_input.date():
                arrival_flight_data.append(flight)

    for flight in departure_flight_data:
        for i in range(0, len(tickets)):
            if flight.flight_id == tickets[i].flight_id:
                ticket_info.append(tickets[i])

    return departure_flight_data, arrival_flight_data, ticket_info

def add_user(last_name, first_name, phone, address, email,password):
    new_user = User(last_name=last_name, first_name=first_name, phone=phone,
                    address=address, password=password,email=email)
    db.session.add(new_user)
    db.session.commit()
    
def add_customer():
    pass

def seat(name, plane_id, fare_class_id):
    pass

def add_ticket(flight_id, fare_class_id, customer_id, seat):
    pass



def total_revenue():
    return (db.session.query(
        Routes.id.label('route_id'),
        Routes.name.label('route_name'),
        func.MONTH(FlightDetails.time).label('month'),
        (
            func.sum(func.IF(Ticket.fare_class_id == 1, FareClass.price, 0) +
                     func.IF(Ticket.fare_class_id == 2, FareClass.price, 0))
            * func.count(Flight.id)
        ).label('total_revenue')
    )
              .outerjoin(Flight, Routes.id == Flight.routes_id)
              .outerjoin(FlightDetails, Flight.id == FlightDetails.flight_id)
              .outerjoin(Ticket, Flight.id == Ticket.flight_id)
              .outerjoin(FareClass, Ticket.fare_class_id == FareClass.id)
              .group_by(Routes.id, Routes.name, func.MONTH(FlightDetails.time))
              .all())

if __name__ == "__main__":
    with app.app_context():
        print(total_revenue())
