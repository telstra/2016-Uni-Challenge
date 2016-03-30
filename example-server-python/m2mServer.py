"""
    M2M Server

    Sample M2M Server code for the university challenge.
    This code is based off of the Flask tutorial by Armin Ronacher, found here:
       http://flask.pocoo.org/docs/tutorial/

    :license: BSD, see LICENSE for more details.
"""

#################################
#            Imports     	#
#################################


from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify, make_response, Response, current_app
import json, datetime, os
from functools import wraps
#from OpenSSL import SSL


app = Flask(__name__)

# Load default config or override config from an environment variable, if it exists
app.config.update(dict(
    DATABASE=os.path.join(os.path.dirname(os.path.realpath(__file__)), "M2M.db"),
    DEBUG=False,
    SECRET_KEY='someRandomKey',
    USERNAME='admin',
    PASSWORD='password'
))
app.config.from_envvar('M2M_SETTINGS', silent=True)

#################################
#       Database methods        #
#################################


def connect_db():
    """Connects to the database defined in config."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#######################################
#        Basic auth functions     	   #
#######################################

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'TUC2016' and password == 'M2M'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

#################################
#       Route definitions       #
#################################

@app.route('/')
def show_records():
    db = get_db()
    cur = db.execute('select device_ID, team_code, team_name, device_reading, time_stamp from records order by id desc')
    records = cur.fetchall()
    return render_template('show_records.html', records=records)



@app.route('/map')
def show_map_test():
    return render_template('map_test.html')

# This method uses the python google-maps api to add marker to the google map
# not updated for 2016 due to lack of GPS module
@app.route('/map_old')
def show_map():
    db = get_db()
    cur = db.execute('select device_ID, team_code, team_name, device_reading from records order by id desc')
    records = cur.fetchall()
    
    # create list of markers from the lat/lng values for each records in the DB
    markerList = []
    for item in records:
        markerList.append((float(item[2]), float(item[3])))
    print markerList
    
    # create the map object
    mymap = Map(
        identifier="mymap",
        lat=-28,
        lng=135,
        zoom=4,
        markers=markerList,
	style="height:600px;width:800px;"
    )

    return render_template('map.html', mymap=mymap)

@app.route('/api/position', methods=['GET', 'POST', 'OPTIONS'])
def add_record():
    keys = ('device_ID','team_code','team_name', 'device_reading', 'time_stamp')
    db = get_db()
    if request.method == 'POST':
        jsonData = request.get_json(force=True)
        print "REQ DATA", jsonData
        db.execute('insert into records (device_ID, team_code, team_name, device_reading, time_stamp) values (?, ?, ?, ?, ?)',
[jsonData['cpuID'], jsonData['TUC2016TEAMCODE'], jsonData['TEAMNAME'], jsonData['cpuTEMP'], datetime.datetime.now()])
        db.commit()
        return '200 OK'
    
    if request.method == 'GET':
        cur = db.execute('select device_ID, team_code, team_name, device_reading, time_stamp from records order by id desc')
        records = cur.fetchall()
        
        if len(records) > 0:
            outputList = []
            for record in records:
                outputList.append(dict(zip(keys, record)))
                
            # craft response    
            resp2 = Response(json.dumps(outputList),  mimetype='application/json')			
            resp2.headers.add('Access-Control-Allow-Origin', '*')
            return resp2
        else:
            resp2 = Response('no records posted',  mimetype='text/html')			
            resp2.headers.add('Access-Control-Allow-Origin', '*')
            return resp2

    if request.method == 'OPTIONS':
            resp = make_response()          
            resp.headers.add('Access-Control-Allow-Headers', 'origin, content-type, accept')
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp

@app.route('/api/uniInfo', methods=['GET', 'OPTIONS'])
def get_uni_info():
    keys = ('code','teamName','uni', 'lat', 'lon')
    db = get_db()

    if request.method == 'GET':
        cur = db.execute('select code, teamName, uni, lat, lon from uniInfo')
        records = cur.fetchall()
        
        if len(records) > 0:
            outputList = []
            for record in records:
                outputList.append(dict(zip(keys, record)))
                
            # craft response    
            resp2 = Response(json.dumps(outputList),  mimetype='application/json')			
            resp2.headers.add('Access-Control-Allow-Origin', '*')
            return resp2
        else:
            resp2 = Response('no records posted',  mimetype='text/html')			
            resp2.headers.add('Access-Control-Allow-Origin', '*')
            return resp2

    if request.method == 'OPTIONS':
            resp = make_response()          
            resp.headers.add('Access-Control-Allow-Headers', 'origin, content-type, accept')
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp
            
#######################################
#    login/logout route functions     #
#######################################
# These aren't really needed, but could be of use to the teams. 

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You are now logged in')
            return redirect(url_for('show_records'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_records'))



if __name__ == '__main__':
    #init_db() 
    # Uncommenting the above line will make the server reinitialise the db each time it's run,
    # removing any previous records, leave commented for a persistent DB
    
    app.run(host='0.0.0.0', port=80, debug=True)  # Make server publicly available on port 80
    #app.run() # Make the server only available locally on port 5000 (127.0.0.1:5000)
	
	
