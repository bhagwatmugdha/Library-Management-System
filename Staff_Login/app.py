from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

app.config.from_pyfile('/home/mugdha/Projects/Library_Management_System/config.py')

# Initializing MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Register Form Class
class RegisterForm(Form):
    staffName = StringField("Name", [validators.Length(min=1, max=100)])
    username = StringField('Username', [validators.Length(min=1, max=100)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
        ])
    confirm = PasswordField('Confirm Password')

#User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            staffName = form.staffName.data
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))

            # Creating the cursor
            cur = mysql.connection.cursor()

            # Executing Query
            cur.execute("INSERT INTO staff( staffName, username, password) VALUES(%s, %s, %s)", (staffName, username, password))

            # Commit to database
            mysql.connection.commit()

            # Close connection
            cur.close()

            flash("You are now registered.", 'success')

            return redirect(url_for('login'))

        return render_template('register.html', form= form )

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        #Get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Get user by Username
        result = cur.execute("SELECT * FROM staff WHERE username = %s", [username])

        if result > 0:

            # Get the stored hash
            data = cur.fetchone()
            password = data['password']

            # Comparing the Passwords
            if sha256_crypt.verify(password_candidate, password):

                # Password matched
                session['logged_in'] = True
                session['username'] = username

                flash('You have successfully logged in', 'success')
                return redirect(url_for('bookslist'))

            else:
                error = 'Invalid login.'
                return render_template('login.html', error = error)

            #Close connection
            cur.close()

        else:
            error = 'Username not found.'
            return render_template('login.html', error = error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized, please Login.', 'danger')
            return redirect(url_for('login'))
    return wrap

# Creating the Books list
@app.route('/bookslist')
# @is_logged_in
def bookslist():

    # Create Cursor
    cur = mysql.connection.cursor()

    # Execute
    result = cur.execute("SELECT bookName, count(bookName) AS count FROM books GROUP BY bookName")

    books = cur.fetchall()

    if result > 0:
        return render_template('bookslist.html', books = books)
    else:
        msg = 'No books found'
        return render_template('bookslist.html', msg= msg)

    # Close connection
    cur.close()

# Report Form Class
class ReportForm(Form):
    student_id = StringField("Student ID", [validators.Length(min=1)])
    staff_id = StringField('Enter your ID to authenticate', [validators.Length(min=1)])
    book_id = StringField("Book ID")

# Add Report Form
@app.route('/issue_books', methods=['GET', 'POST'])
@is_logged_in
def issue_books():
    form = ReportForm(request.form)

    if request.method == 'POST' and form.validate():
        student_id = form.student_id.data
        staff_id  = form.staff_id.data
        book_id = form.book_id.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO transactions( student_id, staff_id, book_id) VALUES(%d, %d, %d)",(student_id, staff_id, book_id))#, session['username']))

        # Commit to MySQL
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Book Issued', 'success')

        return redirect(url_for('bookslist'))

    return render_template('issue_books.html', form= form)

# Creating the Hospital List
@app.route('/hospitallist')
# @is_logged_in
def hospitallist():

    # Create Cursor
    cur = mysql.connection.cursor()

    # Execute
    result = cur.execute("SELECT * FROM hospital ORDER BY location")

    hospitals = cur.fetchall()

    if result > 0:
        return render_template('hospitallist.html', hospitals = hospitals)
    else:
        msg = 'No hospitals found'
        return render_template('hospitallist.html', msg= msg)

    # Close connection
    cur.close()

# Creating the blood bank
@app.route('/bloodbank')

def bloodbank():

    # Create Cursor
    cur = mysql.connection.cursor()

    # Execute
    result = cur.execute("SELECT * FROM bloodbank NATURAL JOIN hospital ORDER BY bb_name, bb_quantity DESC")

    bloodbanks = cur.fetchall()

    if result > 0:
        return render_template('bloodbank.html', bloodbanks = bloodbanks)
    else:
        msg = 'No Stock'
        return render_template('bloodbank.html', msg= msg)

    # Close connection
    cur.close()

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You have logged out.', 'success')
    return redirect(url_for('login'))

# Report Form Class
class ReportForm(Form):
    test_name = StringField("Test Name", [validators.Length(min=1)])
    aadharNo = StringField('Aadhar Number', [validators.Length(min=1)])
    test_data = TextAreaField("Test Data")

# Add Report Form
@app.route('/addReport', methods=['GET', 'POST'])
@is_logged_in
def addReport():
    form = ReportForm(request.form)

    if request.method == 'POST' and form.validate():
        test_name = form.test_name.data
        aadharNo  = form.aadharNo.data
        test_data = form.test_data.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO data( test_name, test_data, aadharNo, username) VALUES(%s, %s, %s, %s)",(test_name, test_data, aadharNo, session['username']))

        # Commit to MySQL
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Report created.', 'success')

        return redirect(url_for('reportlist'))

    return render_template('addReport.html', form= form)

# Creating the Report list
@app.route('/reportlist')
@is_logged_in
def reportlist():

    # Create Cursor
    cur = mysql.connection.cursor()

    # Execute
    result = cur.execute("SELECT * FROM data WHERE username= %s ORDER BY date_of_test desc", (session['username'],))

    reports = cur.fetchall()

    if result > 0:
        return render_template('reportlist.html', reports = reports)
    else:
        msg = 'No reports found'
        return render_template('reportlist.html', msg= msg)

    # Close connection
    cur.close()

# Displaying each individual report
@app.route('/viewReport/<string:test_id>/')
def viewReport(test_id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get Article
    result = cur.execute("SELECT * FROM data WHERE test_id= %s", [test_id])

    report = cur.fetchone()

    #if result > 0:
    return render_template('viewReport.html', report=report)
    # Close connection
    #cur.close()

# Creating the Report list
@app.route('/addbb')
@is_logged_in
def addbb():

    # Create Cursor
    cur = mysql.connection.cursor()

    # Execute
    result = cur.execute("SELECT * FROM bloodbank NATURAL JOIN hospital WHERE username= %s ORDER BY bb_name", (session['username'],))

    bbs = cur.fetchall()

    if result > 0:
        return render_template('addbb.html', bbs = bbs)
    else:
        msg = 'No stock'
        return render_template('addbb.html', msg= msg)

    # Close connection
    cur.close()

# Blood bank Form Class
class BBForm(Form):
    bb_name = StringField("Parameter Name", [validators.Length(min=1)])
    bb_quantity = StringField('Quantity')
    hospital_name = StringField("Hospital Name")

# Edit Blood Bank
@app.route('/editbb/<string:bb_id>', methods=['GET', 'POST'])
@is_logged_in
def editbb(bb_id):

    # Create Cursor
    cur = mysql.connection.cursor()

    # Get Article
    result = cur.execute("SELECT * FROM bloodbank NATURAL JOIN hospital WHERE bb_id= %s", [ bb_id ])

    bb = cur.fetchone()

    # Get form
    form = BBForm(request.form)

    # Populate the article form fields
    form.bb_name.data = bb['bb_name']
    form.bb_quantity.data = bb['bb_quantity']
    form.hospital_name.data = bb['hospital_name']

    if request.method == 'POST' and form.validate():
        bb_quantity = request.form['bb_quantity']


        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("UPDATE bloodbank SET bb_quantity = %s WHERE bb_id=%s", (bb_quantity, [bb_id]))

        # Commit to MySQL
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Blood Bank Updated', 'success')

        return redirect(url_for('addbb'))

    return render_template('editbb.html', form= form)


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
