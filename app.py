from flask import Flask, request, render_template, flash, get_flashed_messages, url_for, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "demoapp"

def init_db():
    #Call sqlite3.connect() to create a connection to the database tutorial.db in the current working directory, implicitly creating it if it does not exist.
    conn = sqlite3.connect("todo.db")

    #In order to execute SQL statements and fetch results from SQL queries, we will need to use a database cursor.
    cur = conn.cursor()

    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
            EMAIL TEXT UNIQUE NOT NULL PRIMARY KEY,
            FULL_NAME TEXT NOT NULL,
            PASSWORD TEXT NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            TASKS TEXT,
            EMAIL TEXT,
            STATUS TEXT,
            FOREIGN KEY (EMAIL) REFERENCES users(EMAIL)
            )
        ''')
    except Exception as e:
        print(f"Error: {e}")
        
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def load_user_registeration_page():
    return render_template('registerUser.html')

@app.route('/login')
def load_user_login_page():
    print(session)
    if 'email' in session:
        return redirect('/userlogin')
    else:
        return render_template('userlogin.html')

@app.route('/addUser', methods=['POST'])
def adduser():
    email = request.form.get('email')
    fullname = request.form.get('fullname')
    passwd = request.form.get('password')
    print(email, fullname, passwd)
    conn = sqlite3.connect("todo.db")
    cur = conn.cursor()
    try:
        res = cur.execute('SELECT * FROM users WHERE EMAIL==?',(email,))
        user = cur.fetchone()
        if not user:
            cur.execute('INSERT INTO users (EMAIL, FULL_NAME, PASSWORD) VALUES (?,?,?)',(email,fullname,passwd))
            conn.commit()
            flash("User registered successfully, Please login")
            return redirect('/login')
        else:
            return "user already exist", 409
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()


@app.route('/userlogin', methods=['GET','POST'])
def loginuser():
    if 'email' in session:
        user_email = session['email']
        conn = sqlite3.connect("todo.db")
        cur = conn.cursor()
        print(user_email)
        try:
            cur.execute('SELECT TASKS,STATUS FROM tasks WHERE EMAIL == ?', (user_email,))
            tasks = cur.fetchall()
            cur.execute('SELECT FULL_NAME FROM users WHERE EMAIL == ?', (user_email,))
            fullname = cur.fetchone()[0]
            print(tasks)
            print(fullname)
        except Exception as e:
            print(f"Task retrieval error: {e}")
        finally:
            conn.close()
        return render_template('userhome.html', username=fullname, tasks=tasks or [])
    else:
        email = request.form.get('login-email')
        password = request.form.get('login-password')

        conn = sqlite3.connect("todo.db")
        cur = conn.cursor()

        try:
            # Step 1: Fetch user info
            cur.execute('SELECT PASSWORD, FULL_NAME FROM users WHERE EMAIL = ?', (email,))
            result = cur.fetchone()

            if result is None:
                return "User not found", 404

            user_passwd, fullname = result

            if user_passwd != password:
                return "User login failed", 401
        
            # If the code reaches here that means user is authenticated, hence set the cookie
            session['email'] = email

            # Step 2: Fetch user tasks (safely)
            try:
                cur.execute('SELECT TASKS,STATUS FROM tasks WHERE EMAIL = ?', (email,))
                tasks = cur.fetchall()
                print(tasks)
            except Exception as e:
                print(f"Task retrieval error: {e}")
                tasks = [] 

            # Step 3: Always return something
            return render_template('userhome.html', username=fullname, tasks=tasks or [])

        except Exception as e:
            print(f"Login error: {e}")
            return f"Error occurred: {e}", 500

        finally:
            conn.close()


@app.route("/addtask", methods=["POST"])
def addtask():
    conn = sqlite3.connect("todo.db")
    cur = conn.cursor()
    
    task = request.form.get("task")
    email = session['email']
    status = 'pending'
    #add task to tasks table
    try:
        cur.execute('INSERT INTO tasks(TASKS, EMAIL, STATUS) VALUES (?,?,?)',(task, email, status))
        flash("Task added successfully!! ")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.commit()
        conn.close()


    return redirect('/userlogin')

@app.route('/completetask', methods=["GET", "POST"])
def completetask():
    task = request.form.get("task")
    email = session['email']
    status = 'completed'
    conn = sqlite3.connect("todo.db")
    cur = conn.cursor()
    
    try:
        cur.execute('UPDATE tasks SET STATUS = ? WHERE TASKS == ? AND EMAIL == ?',(status, task, email))
        flash("Task marked as completed ")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.commit()
        conn.close()
    
    return redirect('/userlogin')

@app.route('/deletetask', methods=["GET","POST"])
def deletetask():
    task = request.form.get("task")
    email = session['email']
    conn = sqlite3.connect("todo.db")
    cur = conn.cursor()

    try:
        cur.execute('DELETE FROM tasks WHERE TASKS == ? AND EMAIL == ?',( task, email))
        flash("Task deleted!! ")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.commit()
        conn.close()

    return redirect('/userlogin')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0')

