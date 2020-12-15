from flask import Flask,render_template, redirect,session,url_for,request #packages installed for the module
from flask_mysqldb import MySQL
import MySQLdb
from twilio.rest import Client
import random


app=Flask(__name__, template_folder='template')
app.secret_key=" "


app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "newrootpassword"
app.config["MYSQL_DB"] = "login"

db = MySQL(app)

@app.route('/')  #URL pattern
def home():
    return render_template('portalpage.html') #returns the portal page, to enter mobile number

#getOTP from portal page
@app.route('/getOTP', methods=['POST'])
def getOTP():
    number = request.form['number']
    val = getOTPApi(number)
    if val:
        return render_template('enterOTP.html')

#validates the entered OTP
@app.route('/validateOTP', methods=['POST'])
def validateOTP():
    otp = request.form['otp']
    if 'response' in session:
        s = session['response']
        session.pop('response',None)
        if s == otp:
            return render_template("login.html")

        else:
            return 'Incorrect OTP'



def generateOTP():
    return random.randrange(100000,999999) #using rand function, OTP is generated in the given range

#using twilio API, message is sent
def getOTPApi(number):
    account_sid = 'AC0434a5b942125715b8d05b655cee4e35'
    auth_token = ' '
    client = Client(account_sid,auth_token)
    otp= generateOTP()
    session['response']= str(otp)
    body = 'Your OTP is ' + str(otp)
    message = client.messages.create(
                                from_='+14086281466',
                                body =body,
                                to= number
                                )
    if message.sid:
        return True
    else:
        return False

#routes the login page, to enter email and password
@app.route('/newlogin', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("select * from logininfo where email=%s and password=%s",(email,password))
            info = cursor.fetchone()
            print(info)
            if info is not None:
                if info['email']==email and info['password']==password:
                    session['loginsuccess']=True
                    return redirect(url_for('profile'))
            else:
                return redirect(url_for('index'))
    return render_template("login.html")


#registers the new user by storing the data into the database
@app.route('/new',methods=['GET','POST'])
def new_user():
    if request.method == "POST":
        if "one" in request.form and "two" in request.form and "three" in request.form:
            name = request.form['one']
            email = request.form['two']
            password = request.form['three']
            cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("insert into login.logininfo(name,email,password)values(%s,%s,%s)",(name,email,password))
            db.connection.commit()
            return redirect(url_for('index'))

    return render_template("register.html")


@app.route('/new/profile') #to the profile page
def profile():
    if session['loginsuccess']== True:
        return render_template("profile.html")


if __name__ == '__main__':
    app.run(debug=True)
