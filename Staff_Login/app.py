from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, IntegerField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import datetime
import time
from datetime import timedelta

app = Flask(__name__)

app.config.from_pyfile(
    '/home/mugdha/Projects/Library_Management_System/config.py')

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
    staffUsername = StringField(
        'Staff Username', [validators.Length(min=1, max=100)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
        ])
    confirm = PasswordField('Confirm Password')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            staffName = form.staffName.data
            staffUsername = form.staffUsername.data
            password = sha256_crypt.encrypt(str(form.password.data))

            # Creating the cursor
            cur = mysql.connection.cursor()

            # Executing Query
            cur.execute("INSERT INTO staff( staffName, staffUsername, password) VALUES(%s, %s, %s)",
                        (staffName, staffUsername, password))

            # Commit to database
            mysql.connection.commit()

            # Close connection
            cur.close()

            flash("You are now registered.", 'success')

            return redirect(url_for('login'))

        return render_template('register.html', form=form)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        # Get form fields
        staffUsername = request.form['staffUsername']
        password_candidate = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Get user by Username
        result = cur.execute(
            "SELECT * FROM staff WHERE staffUsername = %s", [staffUsername])

        if result > 0:

            # Get the stored hash
            data = cur.fetchone()
            password = data['password']

            # Comparing the Passwords
            if sha256_crypt.verify(password_candidate, password):

                # Password matched
                session['logged_in'] = True
                session['staffUsername'] = staffUsername

                flash('You have successfully logged in', 'success')
                return redirect(url_for('bookslist'))

            else:
                error = 'Invalid login.'
                return render_template('login.html', error=error)

            # Close connection
            cur.close()

        else:
            error = 'Username not found.'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please Login.', 'danger')
            return redirect(url_for('login'))
    return wrap

# Creating the Books list
@app.route('/bookslist', methods=['GET', 'POST'])
# @is_logged_in
def bookslist():

    # Create Cursor
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        searchbook = request.form['search']

        data = cur.execute("select * from books where bookName = '" + str(searchbook)+"' and available = 1 ")

        if data > 0:
            return redirect(url_for('issue_books', bookName=searchbook))
        else:
            msg = 'This book is not available right now'
            return render_template('bookslist.html', msg=msg)
    # Execute
    # where available <> 0
    result = cur.execute(
        "SELECT bookName, author, count(bookName) AS count, sum(available) as available FROM books GROUP BY bookName, author ORDER BY count(bookName) DESC")

    books = cur.fetchall()

    if result > 0:
        return render_template('bookslist.html', books=books)
    else:
        msg = 'No books found'
        return render_template('bookslist.html', msg=msg)

    # Close connection
    cur.close()

# Issue books Form Class


class IssueForm(Form):
    bookName = StringField("Name of the book to be issued")
    studentUsername = StringField(
        "Student ID number", [validators.Length(min=1)])
    staffUsername = StringField('Enter your ID to authenticate', [
                                validators.Length(min=1)])

# Add Report Form


@app.route('/issue_books/<string:bookName>', methods=['GET', 'POST'])
@is_logged_in
def issue_books(bookName):
    # Create Cursor
    cur = mysql.connection.cursor()

    result = cur.execute(
        "SELECT * FROM books WHERE bookName = %s AND available = 1 LIMIT 1", [bookName])

    book = cur.fetchone()

    # Get form
    form = IssueForm(request.form)

    # Populate form
    form.bookName.data = bookName

    if request.method == 'POST' and form.validate():
        student_id = form.studentUsername.data
        staff_id = form.staffUsername.data
        bookName = form.bookName.data

        # Execute
        cur.execute("INSERT INTO transactions( studentUsername, staffUsername, bookName, book_id) VALUES(%s, %s, %s, %s)",
                    (student_id, session['staffUsername'], bookName, book['book_id']))  # , session['username']))
        cur.execute(
            "UPDATE books SET available = 0 WHERE book_id = "+str(book['book_id'])+"")
        # Commit to MySQL
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Book Issued', 'success')

        return redirect(url_for('bookslist'))

    return render_template('issue_books.html', form=form)


# Return books
class ReturnForm(Form):
    book_name = StringField("Name of the book to be returned")
    studentUsername = StringField(
        "Student ID number", [validators.Length(min=1)])


@app.route('/return_books', methods=['GET', 'POST'])
@is_logged_in
def return_books():
    cur_start = mysql.connection.cursor()
    result = cur_start.execute(
        "select bookName from books where available = 0 group by bookName")
    books = cur_start.fetchall()
    form = ReturnForm(request.form)
    if result > 0:

        if request.method == 'POST' and form.validate():
            student_id = form.studentUsername.data
            book_name = form.book_name.data

            cur = mysql.connection.cursor()
            result = cur.execute("select book_id from transactions where studentUsername= "+str(
                student_id)+" and bookName= '"+str(book_name)+"' ")
            data = cur.fetchone()
            if result > 0:
                book_id = data['book_id']

                cur.execute(
                    "update books set available = 1 where book_id = "+str(book_id)+" ")

                mysql.connection.commit()
                cur.execute("update transactions set Done = 1  where book_id = " +
                            str(book_id)+" and studentUsername= "+str(student_id)+" ")

                mysql.connection.commit()

                cur.execute("select returnDate from transactions where studentUsername = " +
                            str(student_id)+" and book_id= "+str(book_id)+" ")
                data = cur.fetchone()

                returndate = str(data['returnDate'])
                current_time = time.strftime(
                    r"%Y-%m-%d %H:%M:%S", time.localtime())

                if current_time > returndate:
                    returndate = time.strftime(returndate)

                    datetimeFormat = '%Y-%m-%d %H:%M:%S'
                    diff = datetime.datetime.strptime(current_time, datetimeFormat)\
            - datetime.datetime.strptime(returndate, datetimeFormat)
                    amount_to_be_added_to_fine = (diff.days)*10

                    cur.execute("update transactions set fine=fine+ "+str(
                        amount_to_be_added_to_fine)+" studentUsername= "+str(student_id)+"  ")
                    mysql.connection.commit()

                else:
                    returndate = time.strftime(returndate)
                    datetimeFormat = '%Y-%m-%d %H:%M:%S'
                    diff = datetime.datetime.strptime(current_time, datetimeFormat)\
            - datetime.datetime.strptime(returndate, datetimeFormat)
                    # should be negative
                    print(diff.days)
                flash('Book Returned', 'success')
                return redirect(url_for('bookslist'))

            else:
                flash('Book already returned', 'success')
                return redirect(url_for('bookslist'))
            cur.close()

    else:
        flash('No books found', 'success')

    return render_template('return_books.html', form=form, books=books)

# Check fine form


class GetUsernameForm(Form):
    studentUsername = StringField(
        "Student ID number", [validators.Length(min=1)])
    amountpaid = StringField("Student ID number")


@app.route('/check_fine', methods=['GET', 'POST'])
@is_logged_in
def check_fine():
    cur = mysql.connection.cursor()

    # Execute
    result = cur.execute(
        "SELECT studentUsername, fine  FROM transactions where fine > 0 GROUP BY studentusername,fine")

    books = cur.fetchall()

    if result > 0:
        return render_template('check_fine.html', books=books)
    else:
        msg = 'No outstanding fines'
        return render_template('check_fine.html', msg=msg)

    # Close connection
    cur.close()

# Pay Fine


@app.route('/pay_fine', methods=['GET', 'POST'])
@is_logged_in
def pay_fine():
    form = GetUsernameForm(request.form)
    data = 0
    newfine = 0

    if request.method == 'POST' and form.validate():
        student_id = form.studentUsername.data
        cur = mysql.connection.cursor()
        cur.execute(
            "select fine from transactions where studentUsername="+str(student_id)+"  ")
        data = cur.fetchone()
        amountpaid = form.amountpaid.data
        if amountpaid and int(data['fine']) > 0:

            originalfine = int(data['fine'])
            newfine = 0
            newfine = originalfine-int(amountpaid)
            print(newfine)
            cur.execute("update transactions set fine="+str(newfine) +
                        " where studentUsername="+str(student_id)+" ")

            mysql.connection.commit()

            flash('Amount was paid', 'success')

    return render_template('pay_fine.html', form=form, data=data, newfine=newfine)


@app.route('/analyse', methods=['GET', 'POST'])
@is_logged_in
def analyse():
    cur = mysql.connection.cursor()
    cur.execute("select studentUsername,count(*) as num from transactions group by studentUsername,fine order by fine  desc, num desc limit 5")
    data = cur.fetchall()
    print data
    mysql.connection.commit()
    return render_template('analyse.html', data=data)


# Add books Form Class
class AddBooksForm(Form):
    bookName = StringField("Name of the book to be added")
    author = StringField("Name of the Author")
    quantity = IntegerField("Enter the quantity to be added")

# Add Report Form


@app.route('/add_books', methods=['GET', 'POST'])
@is_logged_in
def add_books():
    
    # Get form
    form = AddBooksForm(request.form)

    if request.method == 'POST' and form.validate():
        bookName = form.bookName.data
        author = form.author.data
        quantity = form.quantity.data
        
        while quantity:
            cur = mysql.connection.cursor()
     
            # Execute
            cur.execute("INSERT INTO books( bookName, author) VALUES(%s, %s)",(bookName, author)) 
            # Commit to MySQL
            mysql.connection.commit()

            # Close connection
            cur.close()

            quantity-=1

        flash('Books Added', 'success')

        return redirect(url_for('bookslist'))

    return render_template('add_books.html', form= form)



# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You have logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
