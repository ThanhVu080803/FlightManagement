
from flask_login import login_user, logout_user
from app import dao, db, app, login
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user
import json
import urllib.request
import urllib
import uuid
import requests
import hmac
import hashlib

from app.models import FlightDetails, RoutesInfo, Routes, Flight, AirportRole


@app.route('/')
def index():
    locations = dao.get_departure_points()

    return render_template('index.html', locations=locations)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        last_name = request.form.get('last-name')
        first_name = request.form.get('first-name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        email = request.form.get('email')
        password = request.form.get('password')


        if not (last_name and first_name and phone and address and email and password):
            flash('Please fill in all the fields', 'error')
            return redirect(url_for('register'))

        if not dao.check_user_existence(email=email, last_name=last_name, first_name=first_name):
            flash('User already exists. Please choose a different email or username.', 'error')
            return redirect(url_for('register'))

        dao.add_user(last_name=last_name, first_name=first_name, phone=phone, address=address, email=email, password=password)

        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    err_msg = ""
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = dao.auth_user(email=email, password=password)
        if user:
            login_user(user=user)
            return redirect(url_for('/'))
        else:
            err_msg = "Invalid email or password."

    return render_template("login.html", err_msg=err_msg)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/ticket')
def ticket():
    airport_id = request.args.get("airport_id")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    fli = dao.get_flight_details_info(airport_id=airport_id, from_date=from_date, to_date=to_date)
    air = dao.read_airports()

    return render_template("ticket.html",
                           flights=fli, airports=air)

# logging.basicConfig(filename='error.log', level=logging.ERROR)
@app.route('/ticket/add', methods=["GET", "POST"])
def add_or_update_ticket():
    err = " "
    if request.method == "POST":
        #----- Routes Info
        airport_id = request.form.get('routes_info_airport_id')
        routes_id = request.form.get('routes_info_routes_id')
        airport_role = request.form.get('routes_info_airport_role')

        #----- Flight Details
        flight_id = request.form.get('flight_details_flight_id')
        flight_schedule_id = request.form.get('flight_details_flight_schedule_id')
        time = request.form.get('flight_details_time')
        flight_duration = request.form.get('flight_details_duration', 3.2)
        num_of_seats_1st_class = request.form.get('flight_details_seats_1st_class', 0)
        num_of_seats_2st_class = request.form.get('flight_details_seats_2st_class', 0)

        if airport_role in AirportRole.__members__:
            airport_role = AirportRole[airport_role]



        if dao.add_flight_schedule( airport_id= airport_id,
                                    routes_id=routes_id,
                                    airport_role=airport_role,
                                    flight_id = flight_id,
                                    flight_schedule_id = flight_schedule_id,
                                    time=time,
                                    flight_duration=flight_duration,
                                    num_of_seats_1st_class = num_of_seats_1st_class,
                                    num_of_seats_2st_class = num_of_seats_2st_class):

            return redirect(url_for("ticket"))
        else:
            err = "Something wrong !!!"

    flight_details = FlightDetails.query.get(id)

    return render_template("ticket-add.html",
                           routes=dao.read_routes(),
                           planes=dao.read_planes(),
                           airports=dao.read_airports(),
                           flights=dao.read_flights(),
                           flight_details=dao.get_flight_details_info(),
                           flight_schedules = dao.read_flight_schedules(),
                           staffs = dao.read_staffs(),
                           flight = flight_details,
                           err=err)

@app.route('/ticket/update/flight = <int:flight_details_id>', methods=['GET', 'POST'])
def update_ticket_by_id(flight_details_id):

    flight_detail = FlightDetails.query \
        .join(Flight, FlightDetails.flight_id == Flight.id) \
        .join(Routes, Flight.routes_id == Routes.id) \
        .join(RoutesInfo, Routes.id == RoutesInfo.routes_id) \
        .filter(FlightDetails.id == flight_details_id) \
        .first()

    routes_info = RoutesInfo.query.join(FlightDetails, RoutesInfo.routes_id == FlightDetails.id) \
                                  .filter(FlightDetails.id == flight_details_id) \
                                  .first()

    if request.method == 'POST':
            if routes_info:
                # Update routes_info
                routes_info.airport_id = request.form.getlist('routes_info_airport_id')[0]
                routes_info.routes_id = request.form.getlist('routes_info_routes_id')[0]
                routes_info.airport_role = request.form.getlist('routes_info_airport_role')[0]
                db.session.commit()

            if flight_detail:
                # Update flight_detail
                flight_detail.flight_id = request.form.getlist('flight_details_flight_id')[0]
                flight_detail.flight_schedule_id = request.form.getlist('flight_details_flight_schedule_id')[0]
                flight_detail.time = request.form.getlist('flight_details_time')[0]
                flight_detail.flight_duration = request.form.getlist('flight_details_duration')[0]
                flight_detail.num_of_seats_1st_class = request.form.getlist('flight_details_seats_1st_class')[0]
                flight_detail.num_of_seats_2st_class = request.form.getlist('flight_details_seats_2st_class')[0]

                db.session.commit()

            return redirect(url_for('ticket'))

    return render_template("ticket-update.html",
                           routes=dao.read_routes(),
                           planes=dao.read_planes(),
                           airports=dao.read_airports(),
                           flights=dao.read_flights(),
                           flight_details=dao.get_flight_details_info(),
                           flight_schedules=dao.read_flight_schedules(),
                           staffs=dao.read_staffs(),
                           flight=flight_detail,
                           routes_info=routes_info)


@app.route('/ticket/delete/<int:flight_details_id>', methods=['GET','POST'])
def delete_ticket_by_id(flight_details_id):
        flight_details = FlightDetails.query.filter_by(id=flight_details_id).first()

        if flight_details:
            db.session.delete(flight_details)
            db.session.commit()

            return redirect(url_for('ticket'))



@app.route('/bookticket', methods=['POST'])
def find_ticket():
    departure_airport_id = request.form.get('departure')
    arrival_airport_id = request.form.get('destination')
    departure_date = request.form.get('departure-date')
    return_date = request.form.get('return-date')
    num_of_tickets = request.form.get('quantity-tickets')

    departure_flight_data, arrival_flight_data, ticket_info = dao.get_flight_details(departure_airport_id,
                                                                                     arrival_airport_id,
                                                                                     departure_date,
                                                                                     return_date,
                                                                                     num_of_tickets)
    return render_template("bookticket.html", departure_flight_data=departure_flight_data,
                           arrival_flight_data=arrival_flight_data, ticket_info=ticket_info,
                           num_of_tickets=num_of_tickets)


@app.route(
    '/load_form_passenger/<flight_id>/<plane_id>/<time>/<duration>/<fare_class_id>/<fare_class_price>/<num_of_tickets>')
def load_form_passenger(flight_id, plane_id, time, duration, fare_class_id, fare_class_price, num_of_tickets):
    ticket_info = {
        "flight_id": flight_id,
        "plane_id": plane_id,
        "time": time,
        "duration": duration,
        "fare_class_id": fare_class_id,
        "fare_class_price": fare_class_price,
        "num_of_tickets": num_of_tickets
    }

    session["ticket_info"] = ticket_info

    return render_template('passenger.html', flight_id=flight_id,
                           plane_id=plane_id, time=time, duration=duration, fare_class_id=fare_class_id,
                           fare_class_price=fare_class_price, num_of_tickets=num_of_tickets)


@app.route('/payments', methods=["GET", "POST"])
def payments():
    first_name = request.form.get('first-name')
    last_name = request.form.get('last-name')
    email = request.form.get('email')
    phone_number = request.form.get('phone-number')
    address = request.form.get('address')

    passenger_info = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": phone_number,
        "address": address
    }

    print(passenger_info)

    session["passenger"] = passenger_info

    return render_template('payment.html', session=session)

@app.route('/thanks', methods=["GET"])
def load_thanks_page():
    return render_template("thanks.html")

@app.route('/payUrl', methods=['GET'])
def handle_payments():
    # parameters send to MoMo get get payUrl
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    partnerCode = "MOMO"
    accessKey = "F8BBA842ECF85"
    secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    orderInfo = "Thanh toan qua MoMo"
    redirectUrl = "http://127.0.0.1:5000/thanks"
    ipnUrl = "http://127.0.0.1:5000/momo_ipn"
    amount = "10000"
    orderId = str(uuid.uuid4())
    requestId = str(uuid.uuid4())
    requestType = "payWithATM"
    extraData = ""  # pass empty value or Encode base64 JsonString
    # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
    # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
    # &requestType=$requestType
    rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType

    # puts raw signature
    print("--------------------RAW SIGNATURE----------------")
    print(rawSignature)
    # signature
    h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()
    print("--------------------SIGNATURE----------------")
    print(signature)

    # json object send to MoMo endpoint

    data = {
        'partnerCode': partnerCode,
        'partnerName': "Test",
        'storeId': "MomoTestStore",
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        'redirectUrl': redirectUrl,
        'ipnUrl': ipnUrl,
        'lang': "vi",
        'extraData': extraData,
        'requestType': requestType,
        'signature': signature
    }
    print("--------------------JSON REQUEST----------------\n")
    data = json.dumps(data)
    print(data)

    clen = len(data)
    response = requests.post(endpoint, data=data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

    # f.close()
    print("--------------------JSON response----------------\n")
    print(response.json())

    print(response.json()['payUrl'])

    try:
        response = requests.post(endpoint, data=data,
                                 headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

        # Xử lý phản hồi từ API
        if response.status_code == 200:
            data = response.json()
            user_ino = session.get("passenger")
            dao.add_user(user_ino.get("last_name"),
                         user_ino.get("first_name"),
                         user_ino.get("phone_number"),
                         user_ino.get("address"),
                         user_ino.get("email"))

            return redirect(data.get('payUrl'))
        else:
            return f'Error: {response.status_code}'
    except Exception as e:
        return f'Error: {str(e)}'

#------------Staff
@app.route('/staff/login', methods=["GET", "POST"])
def staff_login():
    err_msg = ""
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = dao.auth_user(email=email, password=password)
        if user:
            login_user(user=user)
            return redirect(url_for('ticket'))
        else:
            err_msg = "Invalid email or password."

    return render_template("staff-login.html", err_msg=err_msg)

@app.route('/staff/register', methods=['POST', 'GET'])
def staff_register():
    if request.method == 'POST':
        last_name = request.form.get('surname')
        first_name = request.form.get('firstname')
        phone = request.form.get('phone')
        address = request.form.get('address')
        email = request.form.get('email')
        password = request.form.get('password')

        if not (last_name and first_name and phone and address and email and password):
            return redirect(url_for('staff_register'))

        if not dao.check_user_existence(email=email, last_name=last_name, first_name=first_name):
            return redirect(url_for('staff_register'))

        dao.add_user(last_name=last_name, first_name=first_name,
                     phone=phone, address=address, email=email, password=password)
        return redirect(url_for('staff_login'))
    return render_template('staff-register.html')

@app.route('/staff/logout')
def staff_logout():
    logout_user()
    return redirect(url_for('staff_login'))

#------------Admin

@app.route('/stats')
def stats():
    return render_template("admin/stats.html")
@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = dao.auth_user(email=email, password=password)
        if user:
            login_user(user=user)
    return redirect('/admin')

@app.route('/admin/register', methods=['POST', 'GET'])
def admin_register():
    if request.method == 'POST':
        last_name = request.form.get('surname')
        first_name = request.form.get('firstname')
        phone = request.form.get('phone')
        address = request.form.get('address')
        email = request.form.get('email')
        password = request.form.get('password')

        if not (last_name and first_name and phone and address and email and password):
            return redirect(url_for('staff_register'))

        if not dao.check_user_existence(email=email, last_name=last_name, first_name=first_name):
            return redirect(url_for('staff_register'))

        dao.add_user(last_name=last_name, first_name=first_name,
                     phone=phone, address=address, email=email, password=password)
        return redirect(url_for('admin_login'))
    return render_template('admin/admin-register.html')

@app.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)


