#imports necessary components
from flask import Flask, render_template, g, request, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
app = Flask(__name__)


#defines the databse as DATABASE
DATABASE = 'game_database.db'

#access database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


#home page shows all games
@app.route('/')
def content():
    cursor = get_db().cursor()
    sql = "SELECT  content.id,content.image, content.Genre,content.name FROM content "
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor = get_db().cursor()
    sql = "SELECT genre.id,genre.genreName FROM genre "
    cursor.execute(sql)
    Genres = cursor.fetchall()
    return render_template("content.html", results=results, Genres=Genres)



#shows all games of a certain genre
@app.route('/Genre/<int:id>')
def genre(id):
    cursor = get_db().cursor()
    sql = "SELECT content.name,content.image, genre.genreName,content.id FROM content JOIN genre ON content.Genre = genre.id WHERE content.Genre = ?"
    cursor.execute(sql,(id,))
    results = cursor.fetchall()
    if len(results) > 0:
        sql = "SELECT genre.id,genre.genreName FROM genre "
        cursor.execute(sql)
        Genres = cursor.fetchall()
        return render_template("Genre.html", results=results,Genre=results[0][2], Genres=Genres)
    else:
        return redirect (url_for("NoGame"))

#runs game info route
@app.route('/Game/<int:id>')
def game(id):
    cursor = get_db().cursor()
    sql = "SELECT content.name, content.image, content.description,content.date FROM content WHERE id = ?"
    cursor.execute(sql,(id,))
    results = cursor.fetchall()
    sql = "SELECT genre.id,genre.genreName FROM genre "
    cursor.execute(sql)
    Genres = cursor.fetchall()
    return render_template("game.html", results=results,Desc=results[0][2],Title=results[0][0],Date=results[0][3],Genres=Genres)

#upload game route user inputs information into html form and it is sent here
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    cursor = get_db().cursor()
    sql = "SELECT genre.id, genre.genreName FROM genre"
    cursor.execute(sql)
    results = cursor.fetchall()
    if request.method == 'POST':   
        t = request.form.get('title_name')
        d = request.form.get('desc_name')
        D = request.form.get('date_name')
        g = request.form.get('genre_name')
        f = request.files['file_name']
        pw = request.form.get('password')
        filename = secure_filename(f.filename)
        f.save('static/images/' + filename)
        #checks if paswsord is correct
        if pw == "admin":    
            cursor = get_db().cursor()
            sql = "INSERT INTO content (name,description,date,Genre,image) VALUES (?,?,?,?,?)"
            print(filename)
            print(f)
            print(t,d,D,g,filename)
            data = (t,d,D,g,str(filename))
            cursor.execute(sql,data)
            get_db().commit()
            return redirect (url_for("content"))
        else:
            return redirect (url_for("content"))
    cursor = get_db().cursor()
    sql = "SELECT genre.id,genre.genreName FROM genre "
    cursor.execute(sql)
    Genres = cursor.fetchall()
    return render_template ("uploadForm.html", results=results, Genres=Genres)

#runs the uplaod genre route
@app.route('/uploadGenre', methods=['GET','POST'])
def upload_Genre():
    if request.method == 'POST':  
        pww = request.form.get('password')
        Genre = request.form.get('genre') 
        #checks if paswsord is correct
        if pww == "admin":
            cursor = get_db().cursor()
            sql = "INSERT INTO genre (genreName) VALUES (?)"
            cursor.execute(sql,(Genre,))
            get_db().commit()
            return redirect (url_for("content"))
        else:
            return redirect (url_for("content"))
    cursor = get_db().cursor()
    sql = "SELECT genre.id,genre.genreName FROM genre "
    cursor.execute(sql)
    Genres = cursor.fetchall()
    return render_template ("uploadGenreForm.html", Genres=Genres)

#shows user all games so they can slecet one to delete
@app.route('/CDG' , methods=['GET','POST'])
def choose_delete_game():
    cursor = get_db().cursor()
    sql = "SELECT  content.id,content.image, content.Genre,content.name FROM content "
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor = get_db().cursor()
    sql = "SELECT genre.id,genre.genreName FROM genre "
    cursor.execute(sql)
    Genres = cursor.fetchall()
    return render_template("ChooseGameDelete.html", results=results, Genres=Genres)
#confirms if the user wants to delete a certain game
@app.route('/Delete/<int:id>', methods=['GET','POST'])
def delete(id): 
    cursor = get_db().cursor()
    sql = "SELECT  content.id,content.image, content.Genre,content.name FROM content WHERE id =?"
    cursor.execute(sql,(id,))
    results = cursor.fetchall()
    
    if request.method == 'POST':  
        password = request.form.get('password')
        #checks if paswsord is correct
        if password == "admin": #;)
            cursor = get_db().cursor()
            sql = "DELETE FROM content WHERE id =?"
            cursor.execute(sql,(id,))
            get_db().commit()
            return redirect (url_for("content"))
        else:
             return redirect (url_for("choose_delete_game"))
    cursor = get_db().cursor()
    sql = "SELECT genre.id,genre.genreName FROM genre "
    cursor.execute(sql)
    Genres = cursor.fetchall()
    return render_template("delete.html", results=results,name=results[0][3],id = id, Genres=Genres)

    



if __name__ == "__main__":
    app.run(debug=True)