#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import logging, psycopg2, pyotp
import re

#library to hash de passwords
from argon2 import PasswordHasher

#library to define the session time
from datetime import datetime, timedelta

#library to generate a secret key
import os


app = Flask(__name__)
#secret key that will be used for securely signing the session
app.secret_key = os.urandom(24)
#Set the session time
app.permanent_session_lifetime = timedelta(minutes=1)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

ph = PasswordHasher()

def verify_login(conn, user, password):
    cur = conn.cursor()

    try:
        cur.execute('SELECT password FROM users WHERE username = %s', (user,))
        hashed_password = cur.fetchone()
        if hashed_password:
            #logger.info(hashed_password[0] + ": " + password)
            # Verify the password using Argon2
            if(ph.verify(hashed_password[0], password)):
                # Check if rehashing is needed and update the database if necessary
                if ph.check_needs_rehash(hashed_password[0]):
                    new_hash = ph.hash(password)
                    cur.execute('UPDATE users SET password = %s WHERE username = %s', (new_hash, user))
                    conn.commit()
                return True
            else:
                return False
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f'Error in verify_login: {error}')
        return False

    finally:
        if cur:
            cur.close()

def verify_token(conn, user, token):
    cur = conn.cursor()
    try:
        cur.execute('SELECT secret_key FROM users WHERE username = %s', (user,))
        secret_key = cur.fetchone()
        if secret_key:
            # verifying submitted OTP with PyOTP
            if pyotp.TOTP(secret_key[0]).verify(token):
                return True
            else:
                return False
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f'Error in verify_login: {error}')
        return False

    finally:
        if cur:
            cur.close()

def categoryid_tostring(argument):
    match argument:
        case "1":
            return "Programming"
        case "2":
            return "Databases"
        case "3":
            return "HTML & Web design"
        case default:
            return ""

def sortedbyid_tostring(argument):
    match argument:
        case "1":
            return "book_date"
        case default:
            return "recomendation"

def summariesid_tostring(argument):
    match argument:
        case "1":
            return "with"
        case default:
            return "without"

def subtract_time(weeks=0, months=0, years=0):

    # Assuming you have a datetime object
    base_date = datetime.now()

     # Calculate the total number of days to subtract
    total_days = weeks * 7 + months * 30 + years * 365

    # Create a timedelta with the total number of days
    delta = timedelta(days=total_days)

    # Subtract the delta from the base date
    result_date = base_date - delta

    # Format the result date as a string
    result_date_str = result_date.strftime("%Y-%m-%d")

    return result_date_str

def get_date_range(argument):
    match argument:
        case "7":
            return subtract_time(weeks=1)
        case "14":
            return subtract_time(weeks=2)
        case "30":
            return subtract_time(months=1)
        case "60":
            return subtract_time(months=2)
        case "90":
            return subtract_time(months=3)
        case "180":
            return subtract_time(months=6)
        case "365":
            return subtract_time(years=1)
        case "730":
            return subtract_time(years=2)
        case default:
            return "-1"

def specific_date(dsd, dsm, dsy, ded, dem, dey):

    current_date = datetime.now()

    if dsd == "0":
        dsd = "1"
    if dsm == "0":
        dsm = "1"
    if dsy == "":
        dsy ="2000"

    if ded == "0":
        ded = str(current_date.day)
    elif int(dey)>current_date.year:
        ded = str(current_date.day)
    elif int(dey)==current_date.year:
        if int(dem)>current_date.month:
            ded = str(current_date.day)
        elif int(dem)==current_date.month:
            if int(ded) > current_date.day:
                ded = str(current_date.day)

    if dem == "0":
        dem = str(current_date.month)
    elif int(dey)>current_date.year:
        dem = str(current_date.month)
    elif int(dey)==current_date.year:
        if int(dem)>current_date.month:
            dem = str(current_date.month)

    if dey == "" or int(dey)>current_date.year:
        dey = str(current_date.year)

    # Create datetime objects directly from the inputs
    date_start_object = datetime(int(dsy), int(dsm), int(dsd))
    date_end_object = datetime(int(dey), int(dem), int(ded))

    # Format the datetime objects as strings
    date_start_string = date_start_object.strftime("%Y-%m-%d")
    date_end_string = date_end_object.strftime("%Y-%m-%d")
    
    return date_start_string, date_end_string

def basic_search(date_range, sortedby, title, authors, category, pricemin, pricemax):
    statement = "SELECT * FROM books WHERE 1=1"
    values = []

    if date_range == "-1":
        if title != "":
            statement += ' AND title = %s'
            values.append(title)
        if authors != "":
            statement += ' AND authors = %s'
            values.append(authors)
        if category != "":
            statement += ' AND category = %s'
            values.append(category)
        if pricemin != "":
            statement += ' AND price >= %s'
            values.append(pricemin)
        if pricemax != "":
            statement += ' AND price <= %s'
            values.append(pricemax)

        if sortedby == "recomendation":
            statement += ' ORDER BY recomendation DESC'
        else:
            statement += ' ORDER BY book_date'

    else:
        if title != "":
            statement += ' AND title = %s'
            values.append(title)
        if authors != "":
            statement += ' AND authors = %s'
            values.append(authors)
        if category != "":
            statement += ' AND category = %s'
            values.append(category)
        if pricemin != "":
            statement += ' AND price >= %s'
            values.append(pricemin)
        if pricemax != "":
            statement += ' AND price <= %s'
            values.append(pricemax)

        if sortedby == "recomendation":
            statement += ' AND book_date >= %s ORDER BY recomendation DESC'
        else:
            statement += ' AND book_date >= %s ORDER BY book_date'
        values.append(date_range)
    return statement, tuple(values)

def basic_search2(sortedby, title, authors, category, pricemin, pricemax, date_start, date_end):
    statement = "SELECT * FROM books WHERE 1=1"
    values = []

    if title != "":
        statement += ' AND title = %s'
        values.append(title)
    if authors != "":
        statement += ' AND authors = %s'
        values.append(authors)
    if category != "":
        statement += ' AND category = %s'
        values.append(category)
    if pricemin != "":
        statement += ' AND price >= %s'
        values.append(pricemin)
    if pricemax != "":
        statement += ' AND price <= %s'
        values.append(pricemax)

    if sortedby == "recomendation":
        statement += ' AND book_date BETWEEN %s AND %s ORDER BY recomendation DESC'
    else:
        statement += ' AND book_date BETWEEN %s AND %s ORDER BY book_date'
    values.extend([date_start, date_end])

    return statement, tuple(values)

def advanced_search(date_range, sortedby, searchfor, searchfield):
    statement = "SELECT * FROM books WHERE"
    values = []

    if date_range == "-1":
        if searchfield == "any":
            statement += ' title=%s OR authors=%s OR description=%s OR keywords=%s OR notes=%s'
            values.extend([searchfor, searchfor, searchfor, searchfor, searchfor])

        elif searchfield == "title":
            statement += ' title = %s'
            values.append(searchfor)
        elif searchfield == "authors":
            statement += ' authors = %s'
            values.append(searchfor)
        elif searchfield == "description":
            statement += ' description = %s'
            values.append(searchfor)
        elif searchfield == "keywords":
            statement += ' keywords = %s'
            values.append(searchfor)
        elif searchfield == "notes":
            statement += ' notes = %s'
            values.append(searchfor)

        if sortedby == "recomendation":
            statement += ' ORDER BY recomendation DESC'
        else:
            statement += ' ORDER BY book_date'

    else:
        if searchfield == "any":
            statement += ' (title=%s OR authors=%s OR description=%s OR keywords=%s OR notes=%s)'
            values.extend([searchfor, searchfor, searchfor, searchfor, searchfor])

        elif searchfield == "title":
            statement += ' title = %s'
            values.append(searchfor)
        elif searchfield == "authors":
            statement += ' authors = %s'
            values.append(searchfor)
        elif searchfield == "description":
            statement += ' description = %s'
            values.append(searchfor)
        elif searchfield == "keywords":
            statement += ' keywords = %s'
            values.append(searchfor)
        elif searchfield == "notes":
            statement += ' notes = %s'
            values.append(searchfor)

        if sortedby == "recomendation":
            statement += ' AND book_date >= %s ORDER BY recomendation DESC'
        else:
            statement += ' AND book_date >= %s ORDER BY book_date'
        values.append(date_range)
    return statement, tuple(values)

def advanced_search2(sortedby, searchfor, searchfield, date_start, date_end):
    statement = "SELECT * FROM books WHERE"
    values = []

    if searchfield == "any":
            statement += ' title=%s OR authors=%s OR description=%s OR keywords=%s OR notes=%s'
            values.extend([searchfor, searchfor, searchfor, searchfor, searchfor])

    elif searchfield == "title":
        statement += ' title = %s'
        values.append(searchfor)
    elif searchfield == "authors":
        statement += ' authors = %s'
        values.append(searchfor)
    elif searchfield == "description":
        statement += ' description = %s'
        values.append(searchfor)
    elif searchfield == "keywords":
        statement += ' keywords = %s'
        values.append(searchfor)
    elif searchfield == "notes":
        statement += ' notes = %s'
        values.append(searchfor)

    if sortedby == "recomendation":
        statement += ' AND book_date BETWEEN %s AND %s ORDER BY recomendation DESC'
    else:
        statement += ' AND book_date BETWEEN %s AND %s ORDER BY book_date'
    values.extend([date_start, date_end])

    return statement, tuple(values)

def advanced_search3(date_range, sortedby, searchfor, searchfield):
    statement = "SELECT * FROM books WHERE"
    values = []

    if date_range == "-1":
        if searchfield == "any":
            statement += ' title like %s OR authors like %s OR description like %s OR keywords like %s OR notes like %s'
            values.extend(["%" + searchfor + "%", "%" + searchfor + "%", "%" + searchfor + "%", "%" + searchfor + "%", "%" + searchfor + "%"])

        elif searchfield == "title":
            statement += ' title like %s'
            values.append("%" + searchfor + "%")
        elif searchfield == "authors":
            statement += ' authors like %s'
            values.append("%" + searchfor + "%")
        elif searchfield == "description":
            statement += ' description like %s'
            values.append("%" + searchfor + "%")
        elif searchfield == "keywords":
            statement += ' keywords like %s'
            values.append("%" + searchfor + "%")
        elif searchfield == "notes":
            statement += ' notes like %s'
            values.append("%" + searchfor + "%")

        if sortedby == "recomendation":
            statement += ' ORDER BY recomendation DESC'
        else:
            statement += ' ORDER BY book_date'

    else:
        if searchfield == "any":
            statement += ' (title like %s OR authors like %s OR description like %s OR keywords like %s OR notes like %s)'
            values.extend(["%" + searchfor + "%", "%" + searchfor + "%", "%" + searchfor + "%", "%" + searchfor + "%", "%" + searchfor + "%"])
            
        elif searchfield == "title":
            statement += ' title like %s'
            values.append("%" + searchfor + "%")
        elif searchfield == "authors":
            statement += ' authors like %s'
            values.append("%" + searchfor + "%")
        elif searchfield == "description":
            statement += ' description like %s'
            values.append("%" + searchfor + "%")
        elif searchfield == "keywords":
            statement += ' keywords like %s'
            values.append("%" + searchfor + "%")
        elif searchfield == "notes":
            statement += ' notes like %s'
            values.append("%" + searchfor + "%")

        if sortedby == "recomendation":
            statement += ' AND book_date >= %s ORDER BY recomendation DESC'
        else:
            statement += ' AND book_date >= %s ORDER BY book_date'
        values.append(date_range)
    return statement, tuple(values)

def advanced_search4(sortedby, searchfor, searchfield, date_start, date_end):
    statement = "SELECT * FROM books WHERE"
    values = []

    if searchfield == "any":
        statement += ' title like %s OR authors like %s OR description like %s OR keywords like %s OR notes like %s'
        values.extend(["%" + searchfor + "%", "%" + searchfor + "%", "%" + searchfor + "%", "%" + searchfor + "%", "%" + searchfor + "%"])

    elif searchfield == "title":
        statement += ' title like %s'
        values.append("%" + searchfor + "%")
    elif searchfield == "authors":
        statement += ' authors like %s'
        values.append("%" + searchfor + "%")
    elif searchfield == "description":
        statement += ' description like %s'
        values.append("%" + searchfor + "%")
    elif searchfield == "keywords":
        statement += ' keywords like %s'
        values.append("%" + searchfor + "%")
    elif searchfield == "notes":
        statement += ' notes like %s'
        values.append("%" + searchfor + "%")

    if sortedby == "recomendation":
        statement += ' AND book_date BETWEEN %s AND %s ORDER BY recomendation DESC'
    else:
        statement += ' AND book_date BETWEEN %s AND %s ORDER BY book_date'
    values.extend([date_start, date_end])

    return statement, tuple(values)

def basic_search_vulnerable(date_range, sortedby, title, authors, category, pricemin, pricemax):
    statement = "SELECT * FROM books WHERE 1=1"

    if date_range == "-1":
        if title != "":
            statement += " AND title = '" + title + "'"
        if authors != "":
            statement += " AND authors = '" + authors + "'"
        if category != "":
            statement += " AND category = '" + category + "'"
        if pricemin != "":
            statement += " AND price >= '" + pricemin + "'"
        if pricemax != "":
            statement += " AND price <= '" + pricemax + "'"

        if sortedby == "recomendation":
            statement += ' ORDER BY recomendation DESC'
        else:
            statement += ' ORDER BY book_date'

    else:
        if title != "":
            statement += " AND title = '" + title + "'"
        if authors != "":
            statement += " AND authors = '" + authors + "'"
        if category != "":
            statement += " AND category = '" + category + "'"
        if pricemin != "":
            statement += " AND price >= '" + pricemin + "'"
        if pricemax != "":
            statement += " AND price <= '" + pricemax + "'"

        if sortedby == "recomendation":
            statement += " AND book_date >= '"+ date_range + "' ORDER BY recomendation DESC"
        else:
            statement += " AND book_date >= '"+ date_range + "' ORDER BY book_date"
    return statement

def basic_search2_vulnerable(sortedby, title, authors, category, pricemin, pricemax, date_start, date_end):
    statement = "SELECT * FROM books WHERE 1=1"

    if title != "":
        statement += " AND title = '" + title + "'"
    if authors != "":
        statement += " AND authors = '" + authors + "'"
    if category != "":
        statement += " AND category = '" + category + "'"
    if pricemin != "":
        statement += " AND price >= '" + pricemin + "'"
    if pricemax != "":
        statement += " AND price <= '" + pricemax + "'"

    if sortedby == "recomendation":
        statement += " AND book_date BETWEEN '" + date_start + "' AND '" + date_end + "' ORDER BY recomendation DESC"
    else:
        statement += " AND book_date BETWEEN '" + date_start + "' AND '" + date_end + "' ORDER BY book_date"
    
    return statement

def advanced_search_vulnerable(date_range, sortedby, searchfor, searchfield):
    statement = "SELECT * FROM books WHERE"

    if date_range == "-1":
        if searchfield == "any":
            statement += " title='"+ searchfor +"' OR authors='"+ searchfor +"' OR description='"+ searchfor +"' OR keywords='"+ searchfor +"' OR notes='"+ searchfor +"'"

        elif searchfield == "title":
            statement += " title = '"+ searchfor +"'"
        elif searchfield == "authors":
            statement += " authors = '"+ searchfor +"'"
        elif searchfield == "description":
            statement += " description = '"+ searchfor +"'"
        elif searchfield == "keywords":
            statement += " keywords = '"+ searchfor +"'"
        elif searchfield == "notes":
            statement += " notes = '"+ searchfor +"'"

        if sortedby == "recomendation":
            statement += " ORDER BY recomendation DESC"
        else:
            statement += " ORDER BY book_date"

    else:
        if searchfield == "any":
            statement += " title='"+ searchfor +"' OR authors='"+ searchfor +"' OR description='"+ searchfor +"' OR keywords='"+ searchfor +"' OR notes='"+ searchfor +"'"

        elif searchfield == "title":
            statement += " title = '"+ searchfor +"'"
        elif searchfield == "authors":
            statement += " authors = '"+ searchfor +"'"
        elif searchfield == "description":
            statement += " description = '"+ searchfor +"'"
        elif searchfield == "keywords":
            statement += " keywords = '"+ searchfor +"'"
        elif searchfield == "notes":
            statement += " notes = '"+ searchfor +"'"

        if sortedby == "recomendation":
            statement += " AND book_date >= '"+ date_range +"' ORDER BY recomendation DESC"
        else:
            statement += " AND book_date >= '"+ date_range +"' ORDER BY book_date"
    return statement

def advanced_search2_vulnerable(sortedby, searchfor, searchfield, date_start, date_end):
    statement = "SELECT * FROM books WHERE"

    if searchfield == "any":
        statement += " title='"+ searchfor +"' OR authors='"+ searchfor +"' OR description='"+ searchfor +"' OR keywords='"+ searchfor +"' OR notes='"+ searchfor +"'"

    elif searchfield == "title":
        statement += " title = '"+ searchfor +"'"
    elif searchfield == "authors":
        statement += " authors = '"+ searchfor +"'"
    elif searchfield == "description":
        statement += " description = '"+ searchfor +"'"
    elif searchfield == "keywords":
        statement += " keywords = '"+ searchfor +"'"
    elif searchfield == "notes":
        statement += " notes = '"+ searchfor +"'"

    if sortedby == "recomendation":
        statement += " AND book_date BETWEEN '"+ date_start +"' AND '"+ date_end +"' ORDER BY recomendation DESC"
    else:
        statement += " AND book_date BETWEEN '"+ date_start +"' AND '"+ date_end +"' ORDER BY book_date"
    
    return statement

def advanced_search3_vulnerable(date_range, sortedby, searchfor, searchfield):
    statement = "SELECT * FROM books WHERE"

    if date_range == "-1":
        if searchfield == "any":
            statement += " title like '"+ "%" + searchfor + "%" + "' OR authors like '"+ "%" + searchfor + "%" + "' OR description like '"+ "%" + searchfor + "%" + "' OR keywords like '"+ "%" + searchfor + "%" + "' OR notes like '"+ "%" + searchfor + "%" + "'"

        elif searchfield == "title":
            statement += " title like '"+ "%" + searchfor + "%" + "'"
        elif searchfield == "authors":
            statement += " authors like '"+ "%" + searchfor + "%" + "'"
        elif searchfield == "description":
            statement += " description like '"+ "%" + searchfor + "%" + "'"
        elif searchfield == "keywords":
            statement += " keywords like '"+ "%" + searchfor + "%" + "'"
        elif searchfield == "notes":
            statement += " notes like '"+ "%" + searchfor + "%" + "'"

        if sortedby == "recomendation":
            statement += " ORDER BY recomendation DESC"
        else:
            statement += " ORDER BY book_date"

    else:
        if searchfield == "any":
            statement += " title like '"+ "%" + searchfor + "%" + "' OR authors like '"+ "%" + searchfor + "%" + "' OR description like '"+ "%" + searchfor + "%" + "' OR keywords like '"+ "%" + searchfor + "%" + "' OR notes like '"+ "%" + searchfor + "%" + "'"

        elif searchfield == "title":
            statement += " title like '"+ "%" + searchfor + "%" + "'"
        elif searchfield == "authors":
            statement += " authors like '"+ "%" + searchfor + "%" + "'"
        elif searchfield == "description":
            statement += " description like '"+ "%" + searchfor + "%" + "'"
        elif searchfield == "keywords":
            statement += " keywords like '"+ "%" + searchfor + "%" + "'"
        elif searchfield == "notes":
            statement += " notes like '"+ "%" + searchfor + "%" + "'"

        if sortedby == "recomendation":
            statement += " AND book_date >= '"+ date_range +"' ORDER BY recomendation DESC"
        else:
            statement += " AND book_date >= '"+ date_range +"' ORDER BY book_date"

    return statement

def advanced_search4_vulnerable(sortedby, searchfor, searchfield, date_start, date_end):
    statement = "SELECT * FROM books WHERE"

    if searchfield == "any":
        statement += " title like '"+ "%" + searchfor + "%" + "' OR authors like '"+ "%" + searchfor + "%" + "' OR description like '"+ "%" + searchfor + "%" + "' OR keywords like '"+ "%" + searchfor + "%" + "' OR notes like '"+ "%" + searchfor + "%" + "'"

    elif searchfield == "title":
        statement += " title like '"+ "%" + searchfor + "%" + "'"
    elif searchfield == "authors":
        statement += " authors like '"+ "%" + searchfor + "%" + "'"
    elif searchfield == "description":
        statement += " description like '"+ "%" + searchfor + "%" + "'"
    elif searchfield == "keywords":
        statement += " keywords like '"+ "%" + searchfor + "%" + "'"
    elif searchfield == "notes":
        statement += " notes like '"+ "%" + searchfor + "%" + "'"

    if sortedby == "recomendation":
        statement += " AND book_date BETWEEN '"+ date_start +"' AND '"+ date_end +"' ORDER BY recomendation DESC"
    else:
        statement += " AND book_date BETWEEN '"+ date_start +"' AND '"+ date_end +"' ORDER BY book_date"

    return statement

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/part1.html", methods=['GET'])
def login():
    if "user" in session:
        return redirect(url_for('part2'))
    return render_template("part1.html")

#Function to logout
@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", None)
        logger.info("Logout successful!")
    return redirect(url_for("login"))


@app.route("/part1Register.html", methods=['GET', 'POST'])
def register():
    return render_template("part1Register.html")

@app.route("/handle_register", methods=['GET', 'POST'])
def handle_register():
    logger.info("---- Register ----")

    if request.method == 'GET':
        new_password = request.args.get('new_password')
        new_username = request.args.get('new_username')
        confirm_password = request.args.get('confirm_new_password')
    else:
        new_password = request.form['new_password']
        new_username = request.form['new_username']
        confirm_password = request.form['confirm_new_password']

    logger.info('POST /Users')

    logger.info("new_username -> " + new_username)
    logger.info("new_password -> " + ph.hash(new_password))
    logger.info("confirm_new_password -> " + ph.hash(confirm_password))

    #Connection to db
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute('Select username from users where username = (%s)', (new_username,))
        checkUsername = cur.fetchone()
        #Check if it exists the input username
        if checkUsername == None:
            if new_password == confirm_password:
                # parameterized queries, good for security and performance
                statement = 'INSERT INTO users (username, password, secret_key) VALUES (%s, %s, %s)'
                # generating random secret key for authentication
                secret = pyotp.random_base32()
                logger.info("secret_key -> "+ secret)
                #hashed_secret = ph.hash(secret)
                hashed_password = ph.hash(new_password)
                values = (new_username, hashed_password, secret)
                cur.execute(statement, values)
                # commit the transaction
                conn.commit()

                return render_template("2fa.html", secret=secret)
            else:
                flash("Passwords need to be identical!", "register_error")
                return render_template("part1Register.html")        
        else:
            flash("Can't use that username!", "register_error")
            return render_template("part1Register.hmtl")

    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred, rollback
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return render_template("part1Register.html")

@app.route("/handle_register2", methods=['GET', 'POST'])
def handle_register2():
    logger.info("---- Register ----")

    if request.method == 'GET':
        new_password = request.args.get('new_v_password')
        new_username = request.args.get('new_v_username')
        confirm_password = request.args.get('confirm_new_v_password')
    else:
        new_password = request.form['new_v_password']
        new_username = request.form['new_v_username']
        confirm_password = request.form['confirm_new_v_password']

    logger.info('POST /Users')

    logger.info("new_username -> " + new_username)
    logger.info("new_password -> " + new_password)
    logger.info("confirm_new_password -> " + confirm_password)

    #Connection to db
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("Select username from users_vulnerable where username = '" + new_username + "'")
        checkUsername = cur.fetchone()
        #Check if it exists the input username
        if checkUsername == None:
            if new_password == confirm_password:
                cur.execute("INSERT INTO users_vulnerable (username, password) VALUES ('" + new_username + "','" + new_password + "')")
                # commit the transaction
                conn.commit()

                return redirect(url_for("login"))
            else:
                flash("Passwords need to be identical!", "register2_error")
                return render_template("part1Register.html")        
        else:
            flash("Username already exists!", "register2_error")
            return render_template("part1Register.hmtl")

    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred, rollback
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return render_template("part1Register.html")

@app.route("/part1_vulnerable", methods=['GET', 'POST'])
def part1_vulnerable():
    logger.info("---- part1_vulnerable ----")

    if request.method == 'GET':
        password = request.args.get('v_password') 
        username = request.args.get('v_username') 
        remember = request.args.get('v_remember') 
    else:
        password = request.form['v_password']
        username = request.form['v_username']
        remember = request.form['v_remember']
        
    

    logger.info("v_password  -> " + password)
    logger.info("v_username  -> " + username)
    
    #Connection to db
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("Select password from users_vulnerable where username = '" + username + "'")
        checkUsername = cur.fetchone()
        #Check if it exists the input username
        if checkUsername == None:
            flash("User doesn't exist!","register2_error")
            return redirect(url_for('login'))
        else:
            if (password == checkUsername[0]):
                session["user"] = username

                #Activate the session time
                if remember == "on":
                    session.permanent = True

                logger.info("Login success!")
                return redirect(url_for("part2"))
            else:
                flash("Password is wrong!","register2_error")
                return redirect(url_for('login'))

    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred, rollback
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return redirect(url_for('login'))


@app.route("/part1_correct", methods=['GET', 'POST'])
def part1_correct():
    logger.info("---- part1_correct ----")

    if request.method == 'GET':
        password = request.args.get('c_password') 
        username = request.args.get('c_username') 
        remember = request.args.get('c_remember')
        token = request.args.get('c_token') 
    else:
        password = request.form['c_password']
        username = request.form['c_username']
        remember = request.form['c_remember']
        token = request.form['c_token']
    
        
    logger.info("c_username  -> " + username)
    logger.info("c_password -> " + ph.hash(password))
    logger.info("c_token  -> " + ph.hash(token))

    #Connection to db
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute('Select username from users where username = (%s)', (username,))
        checkUsername = cur.fetchone()
        #Check if it exists the input username
        if checkUsername == None:
            flash("Credentials Wrong!","register_error")
            return redirect(url_for('login'))
        else:
            if (verify_login(conn, username, password)):
                if(verify_token(conn, username, token)):

                    session["user"] = username

                    #Activate the session time
                    if remember == "on":
                        session.permanent = True

                    logger.info("Authentication success!")
                    return redirect(url_for("part2"))
                else:
                    # inform users if OTP is invalid
                    flash("Credentials Wrong!","register_error")
                    return redirect(url_for('login'))
            else:
                flash("Credentials Wrong!","register_error")
                return redirect(url_for('login'))

    except (Exception, psycopg2.DatabaseError) as error:
        # an error occurred, rollback
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return redirect(url_for('login'))


@app.route("/part2.html", methods=['GET'])
def part2():

    if "user" in session:
        logger.info('GET /Messages')

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute('SELECT author, message FROM messages')
            rows = cur.fetchall()

            logger.debug('GET /Messages - parse')
            Results = []
            for row in rows:
                logger.debug(row)
                content = {'author': row[0], 'message': row[1]}
                Results.append(content)  # appending to the payload to be returned


        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'GET /Messages - error: {error}')

        finally:
            if conn is not None:
                conn.close()

        return render_template("part2.html", results=Results)
    else:
        return redirect(url_for("login"))


@app.route("/part2_vulnerable", methods=['GET', 'POST'])
def part2_vulnerable():
    if "user" in session:
        logger.info("---- part2_vulnerable ----")

        if request.method == 'GET':
            new_text = request.args.get('v_text') 
        else:
            new_text = request.form['v_text']
        
        logger.info("POST /Message")
        logger.info("v_text  -> " + new_text)

        #Connection to db
        conn = get_db()
        cur = conn.cursor()
        
        username = session["user"]
                                                               

        try:
            cur.execute("INSERT INTO messages (author, message) VALUES ('" + username + "', '" + new_text + "')")
            # commit the transaction
            conn.commit()
            return redirect(url_for('part2'))

        except (Exception, psycopg2.DatabaseError) as error:
            # an error occurred, rollback
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()    

        return render_template("part2.html")
    else:
        return redirect(url_for("login"))


@app.route("/part2_correct", methods=['GET', 'POST'])
def part2_correct():

    if "user" in session:
        logger.info("---- part2_correct ----")

        if request.method == 'GET':
            new_text = request.args.get('c_text') 
        else:
            new_text = request.form['c_text']
        
        logger.info("POST /Message")
        logger.info("c_text  -> " + new_text)

        #Connection to db
        conn = get_db()
        cur = conn.cursor()
        
        username = session["user"]

        statement = 'INSERT INTO messages (author, message) VALUES (%s, %s)'
        values = (username, new_text)

        try:
            cur.execute(statement, values)
            # commit the transaction
            conn.commit()
            return redirect(url_for('part2'))

        except (Exception, psycopg2.DatabaseError) as error:
            # an error occurred, rollback
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()    

        return render_template("part2.html")
    else:
        return redirect(url_for("login"))


@app.route("/part3.html", methods=['GET'])
def part3():

    return render_template("part3.html")


@app.route("/part3_vulnerable", methods=['GET', 'POST'])
def part3_vulnerable():
    logger.info('GET Vulnerable/Books')

    if request.method == 'GET':
        title = request.args.get('v_name') 
        authors = request.args.get('v_author') 
        category_id = request.args.get('v_category_id')
        pricemin = request.args.get('v_pricemin')
        pricemax = request.args.get('v_pricemax')
        searchfor = request.args.get('v_search_input')
        searchfield = request.args.get('v_search_field')
        advanced_match = request.args.get('v_radio_match')
        sortedby_id = request.args.get('v_sp_s')
        show_n_books = int(request.args.get('v_sp_c'))
        summaries_id =  request.args.get('v_sp_m')
        typeofdate = request.args.get('v_sp_d')
        
    else:
        title = request.form['v_name']
        authors = request.form['v_author']
        category_id = request.form['v_category_id']
        pricemin = request.form['v_pricemin']
        pricemax = request.form['v_pricemax']
        searchfor = request.form['v_search_input']
        searchfield = request.form['v_search_field']
        advanced_match = request.form['v_radio_match']
        sortedby_id = request.form['v_sp_s']
        show_n_books = int(request.form['v_sp_c'])
        summaries_id =  request.form['v_sp_m']
        typeofdate = request.form['v_sp_d']
    
    advanced_search_flag = False

    words_list = []

    # Split by both spaces and commas, and filter out empty strings
    if searchfor !="":
        words_list = [word for word in re.split(r'[,\s]+', searchfor) if word]
        advanced_search_flag = True

    #takes care of the advanced search input
    if advanced_search_flag:
        if words_list:
            if advanced_match!="phrase":
                logger.info("v_search_input -> " + str(words_list))
            else:
                words_list.clear()
                logger.info("v_search_input -> " + searchfor)
            logger.info("v_search_field -> " + searchfield)
            logger.info("v_radio_match -> " + advanced_match)
        else:
            advanced_search_flag = False

    category = categoryid_tostring(category_id)
    sortedby = sortedbyid_tostring(sortedby_id)
    summaries = summariesid_tostring(summaries_id)

    if not advanced_search_flag:
        logger.info('v_name -> ' + title)
        logger.info('v_author -> '+ authors)
        logger.info('v_category -> '+ category)
        logger.info('v_pricemin -> '+ pricemin)
        logger.info('v_pricemax -> '+ pricemax)
    logger.info('v_sp_s -> '+ sortedby)
    logger.info('v_sp_c -> '+ str(show_n_books))
    logger.info('v_sp_m -> '+ summaries)


    #takes care of the input dates
    if typeofdate == "custom":
        if request.method == 'GET':
            date_range = request.args.get('v_sp_date_range') 
        else:
            date_range = request.form['v_sp_date_range']
        date_range = get_date_range(date_range)
        logger.info('v_sp_date_range -> '+ date_range)
    else:
        if request.method == 'GET':
            date_start_month = request.args.get('v_sp_start_month')
            date_start_day = request.args.get('v_sp_start_day')
            date_start_year = request.args.get('v_sp_start_year')
            date_end_month = request.args.get('v_sp_end_month')
            date_end_day = request.args.get('v_sp_end_day')
            date_end_year = request.args.get('v_sp_end_year')
        else:
            date_start_month = request.form['v_sp_start_month']
            date_start_day = request.form['v_sp_start_day']
            date_start_year = request.form['v_sp_start_year']
            date_end_month = request.form['v_sp_end_month']
            date_end_day = request.form['v_sp_end_day']
            date_end_year = request.form['v_sp_end_year']
        date_start, date_end = specific_date(date_start_day, date_start_month, date_start_year, date_end_day, date_end_month, date_end_year)
        logger.info("v_start_date -> " + date_start)
        logger.info("v_end_date -> " + date_end)

        current_date = datetime.now()
        
        # Convert the string date to a datetime object
        parsed_date = datetime.strptime(date_start, "%Y-%m-%d")

        if parsed_date > current_date:
            flash("Can't travel to the future!", "register2_error")
            return redirect(url_for("part3"))
        else:
            if date_start > date_end:
                flash("The first date can't be later than the second one!", "register2_error")
                return redirect(url_for("part3"))

    conn = get_db()
    cur = conn.cursor()

    if not advanced_search_flag:
        if typeofdate == "custom":
            statement = basic_search_vulnerable(date_range, sortedby, title, authors, category, pricemin, pricemax)
        else:
            statement = basic_search2_vulnerable(sortedby, title, authors, category, pricemin, pricemax, date_start, date_end)
    else:
        if advanced_match == "phrase":
            if typeofdate == "custom":
                statement = advanced_search_vulnerable(date_range, sortedby, searchfor, searchfield)
            else:
                statement = advanced_search2_vulnerable(sortedby, searchfor, searchfield, date_start, date_end)
        else:
            if len(words_list) == 1:
                if typeofdate == "custom":
                    statement = advanced_search3_vulnerable(date_range, sortedby, words_list[0], searchfield)
                else:
                    statement = advanced_search4_vulnerable(sortedby, words_list[0], searchfield, date_start, date_end)
            

    counter = 0

    if (len(words_list)<=1):
        try:
            cur.execute(statement)
            rows = cur.fetchall()

            logger.debug('GET Vulnerable/Books - parse')
            Results = []
            for row in rows:
                if counter < show_n_books:
                    if summaries == "with":
                        counter +=1
                        content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'description':row[6], 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                    else:
                        counter +=1
                        content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                    
                    Results.append(content)  # appending to the payload to be returned
                    logger.debug(content)
                else:
                    break

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'GET Vulnerable/books - error: {error}')

        finally:
            if conn is not None:
                conn.close()
    else:
        logger.debug('GET Vulnerable/Books - parse')
        Results = []
        if advanced_match == "any":
            for word in words_list:

                conn = get_db()
                cur = conn.cursor()

                if typeofdate == "custom":
                    statement = advanced_search3_vulnerable(date_range, sortedby, word, searchfield)
                else:
                    statement = advanced_search4_vulnerable(sortedby, word, searchfield, date_start, date_end)

                counter = 0
                try:
                    cur.execute(statement)
                    rows = cur.fetchall()
                    for row in rows:
                        if counter < show_n_books:
                            if summaries == "with":
                                counter +=1
                                content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'description':row[6], 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                                
                            else:
                                counter +=1
                                content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                                
                            # Convert content to a string for comparison
                            content_str = str(content)
                            # Check if content_str is not in Results
                            if content_str not in [str(result) for result in Results]:
                                Results.append(content)  # appending to the payload to be returned
                            logger.debug(content)
                        else:
                            break

                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(f'GET /books - error: {error}')

                finally:
                    if conn is not None:
                        conn.close()
        else:
            for word in words_list:

                conn = get_db()
                cur = conn.cursor()

                if typeofdate == "custom":
                    statement = advanced_search3_vulnerable(date_range, sortedby, word, searchfield)
                else:
                    statement = advanced_search4_vulnerable(sortedby, word, searchfield, date_start, date_end)

                try:
                    cur.execute(statement)
                    rows = cur.fetchall()

                    word_results = []  # List to store results for the current word
                    for row in rows:
                        if summaries == "with":
                            content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'description':row[6], 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                        else:
                            content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                        word_results.append(content)
                    Results.append(word_results)
                        

                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(f'GET /books - error: {error}')

                finally:
                    if conn is not None:
                        conn.close()

            # Find the intersection of the book arrays
            common_books = set.intersection(*(set(map(str, word_results)) for word_results in Results))

            # Convert the intersection set back to a list of dictionaries
            Results = [eval(book) for book in common_books]

            # Discard any excess books beyond show_n_books
            Results = Results[:show_n_books]

            for content in Results:
                logger.debug(content)
    
    return render_template("part3Books.html", results=Results)


@app.route("/part3_correct", methods=['GET', 'POST'])
def part3_correct():
    logger.info('GET /Books')

    if request.method == 'GET':
        title = request.args.get('c_name') 
        authors = request.args.get('c_author') 
        category_id = request.args.get('c_category_id')
        pricemin = request.args.get('c_pricemin')
        pricemax = request.args.get('c_pricemax')
        searchfor = request.args.get('c_search_input')
        searchfield = request.args.get('c_search_field')
        advanced_match = request.args.get('c_radio_match')
        sortedby_id = request.args.get('c_sp_s')
        show_n_books = int(request.args.get('c_sp_c'))
        summaries_id =  request.args.get('c_sp_m')
        typeofdate = request.args.get('c_sp_d')
        
    else:
        title = request.form['c_name']
        authors = request.form['c_author']
        category_id = request.form['c_category_id']
        pricemin = request.form['c_pricemin']
        pricemax = request.form['c_pricemax']
        searchfor = request.form['c_search_input']
        searchfield = request.form['c_search_field']
        advanced_match = request.form['c_radio_match']
        sortedby_id = request.form['c_sp_s']
        show_n_books = int(request.form['c_sp_c'])
        summaries_id =  request.form['c_sp_m']
        typeofdate = request.form['c_sp_d']
    
    advanced_search_flag = False

    words_list = []

    # Split by both spaces and commas, and filter out empty strings
    if searchfor !="":
        words_list = [word for word in re.split(r'[,\s]+', searchfor) if word]
        advanced_search_flag = True

    #takes care of the advanced search input
    if advanced_search_flag:
        if words_list:
            if advanced_match!="phrase":
                logger.info("c_search_input -> " + str(words_list))
            else:
                words_list.clear()
                logger.info("c_search_input -> " + searchfor)
            logger.info("c_search_field -> " + searchfield)
            logger.info("c_radio_match -> " + advanced_match)
        else:
            advanced_search_flag = False

    category = categoryid_tostring(category_id)
    sortedby = sortedbyid_tostring(sortedby_id)
    summaries = summariesid_tostring(summaries_id)

    if not advanced_search_flag:
        logger.info('c_name -> ' + title)
        logger.info('c_author -> '+ authors)
        logger.info('c_category -> '+ category)
        logger.info('c_pricemin -> '+ pricemin)
        logger.info('c_pricemax -> '+ pricemax)
    logger.info('c_sp_s -> '+ sortedby)
    logger.info('c_sp_c -> '+ str(show_n_books))
    logger.info('c_sp_m -> '+ summaries)


    #takes care of the input dates
    if typeofdate == "custom":
        if request.method == 'GET':
            date_range = request.args.get('c_sp_date_range') 
        else:
            date_range = request.form['c_sp_date_range']
        date_range = get_date_range(date_range)
        logger.info('c_sp_date_range -> '+ date_range)
    else:
        if request.method == 'GET':
            date_start_month = request.args.get('c_sp_start_month')
            date_start_day = request.args.get('c_sp_start_day')
            date_start_year = request.args.get('c_sp_start_year')
            date_end_month = request.args.get('c_sp_end_month')
            date_end_day = request.args.get('c_sp_end_day')
            date_end_year = request.args.get('c_sp_end_year')
        else:
            date_start_month = request.form['c_sp_start_month']
            date_start_day = request.form['c_sp_start_day']
            date_start_year = request.form['c_sp_start_year']
            date_end_month = request.form['c_sp_end_month']
            date_end_day = request.form['c_sp_end_day']
            date_end_year = request.form['c_sp_end_year']
        date_start, date_end = specific_date(date_start_day, date_start_month, date_start_year, date_end_day, date_end_month, date_end_year)
        logger.info("c_start_date -> " + date_start)
        logger.info("c_end_date -> " + date_end)

        current_date = datetime.now()
        
        # Convert the string date to a datetime object
        parsed_date = datetime.strptime(date_start, "%Y-%m-%d")

        if parsed_date > current_date:
            flash("Can't travel to the future!", "register_error")
            return redirect(url_for("part3"))
        else:
            if date_start > date_end:
                flash("The first date can't be later than the second one!", "register_error")
                return redirect(url_for("part3"))


    conn = get_db()
    cur = conn.cursor()

    if not advanced_search_flag:
        if typeofdate == "custom":
            statement, values = basic_search(date_range, sortedby, title, authors, category, pricemin, pricemax)
        else:
            statement, values = basic_search2(sortedby, title, authors, category, pricemin, pricemax, date_start, date_end)
    else:
        if advanced_match == "phrase":
            if typeofdate == "custom":
                statement, values = advanced_search(date_range, sortedby, searchfor, searchfield)
            else:
                statement, values = advanced_search2(sortedby, searchfor, searchfield, date_start, date_end)
        else:
            if len(words_list) == 1:
                if typeofdate == "custom":
                    statement, values = advanced_search3(date_range, sortedby, words_list[0], searchfield)
                else:
                    statement, values = advanced_search4(sortedby, words_list[0], searchfield, date_start, date_end)
            

    counter = 0

    if (len(words_list)<=1):
        try:
            cur.execute(statement, values)
            rows = cur.fetchall()

            logger.debug('GET /Books - parse')
            Results = []
            for row in rows:
                if counter < show_n_books:
                    if summaries == "with":
                        counter +=1
                        content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'description':row[6], 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                    else:
                        counter +=1
                        content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                    
                    Results.append(content)  # appending to the payload to be returned
                    logger.debug(content)
                else:
                    break

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'GET /books - error: {error}')

        finally:
            if conn is not None:
                conn.close()
    else:
        logger.debug('GET /Books - parse')
        Results = []
        if advanced_match == "any":
            for word in words_list:

                conn = get_db()
                cur = conn.cursor()

                if typeofdate == "custom":
                    statement, values = advanced_search3(date_range, sortedby, word, searchfield)
                else:
                    statement, values = advanced_search4(sortedby, word, searchfield, date_start, date_end)

                counter = 0
                try:
                    cur.execute(statement, values)
                    rows = cur.fetchall()
                    for row in rows:
                        if counter < show_n_books:
                            if summaries == "with":
                                counter +=1
                                content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'description':row[6], 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                                
                            else:
                                counter +=1
                                content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                                
                            # Convert content to a string for comparison
                            content_str = str(content)
                            # Check if content_str is not in Results
                            if content_str not in [str(result) for result in Results]:
                                Results.append(content)  # appending to the payload to be returned
                            logger.debug(content)
                        else:
                            break

                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(f'GET /books - error: {error}')

                finally:
                    if conn is not None:
                        conn.close()
        else:
            for word in words_list:

                conn = get_db()
                cur = conn.cursor()

                if typeofdate == "custom":
                    statement, values = advanced_search3(date_range, sortedby, word, searchfield)
                else:
                    statement, values = advanced_search4(sortedby, word, searchfield, date_start, date_end)

                try:
                    cur.execute(statement, values)
                    rows = cur.fetchall()

                    word_results = []  # List to store results for the current word
                    for row in rows:
                        if summaries == "with":
                            content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'description':row[6], 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                        else:
                            content = {'book_id':str(row[0]), 'title': row[1], 'authors': row[2], 'category':row[3], 'price': str(row[4]), 'book_date': str(row[5]), 'keywords': row[7], 'notes': row[8], 'recomendation':str(row[9])}
                        word_results.append(content)
                    Results.append(word_results)
                        

                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(f'GET /books - error: {error}')

                finally:
                    if conn is not None:
                        conn.close()

            # Find the intersection of the book arrays
            common_books = set.intersection(*(set(map(str, word_results)) for word_results in Results))

            # Convert the intersection set back to a list of dictionaries
            Results = [eval(book) for book in common_books]

            # Discard any excess books beyond show_n_books
            Results = Results[:show_n_books]

            for content in Results:
                logger.debug(content)

    return render_template("part3Books.html", results=Results)


@app.route("/demo", methods=['GET', 'POST'])
def demo():
    logger.info(" DEMO \n");   

    conn = get_db()
    cur = conn.cursor()

    logger.info("---- users  ----")
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()

    for row in rows:
        logger.info(row)


    logger.info("---- users_vulnerable ----")
    cur.execute("SELECT * FROM users_vulnerable")
    rows = cur.fetchall()

    for row in rows:
        logger.info(row)

    logger.info("---- messages ----")
    cur.execute("SELECT * FROM messages")
    rows = cur.fetchall()
 
    for row in rows:
        logger.info(row)

    logger.info("---- books ----")
    cur.execute("SELECT * FROM books")
    rows = cur.fetchall()
 
    for row in rows:
        logger.info(row)

    conn.close ()
    logger.info("\n---------------------\n\n") 

    return "/demo"


##########################################################
## DATABASE ACCESS
##########################################################

def get_db():
    db = psycopg2.connect(user = "ddss-database-assignment-2",
                password = "ddss-database-assignment-2",
                host = "db",
                port = "5432",
                database = "ddss-database-assignment-2")
    return db





##########################################################
## MAIN
##########################################################
if __name__ == "__main__":
    logging.basicConfig(filename="log_file.log")

    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:  %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    logger.info("\n---------------------\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)





