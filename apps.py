from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_swagger_ui import get_swaggerui_blueprint
import sqlite3

app = Flask(__name__)
auth = HTTPBasicAuth()

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)

app.register_blueprint(swaggerui_blueprint)

USER_DATA = {
        "admin" : "123"
    }

@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("books.sqlite")
    except sqlite3.error as e:
        print(e)
    return conn


@app.route("/books", methods=["GET", "POST"])
@auth.login_required
def books():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor = conn.execute("SELECT * FROM book")
        books = [
            dict(id=row[0], author=row[1], language=row[2], title=row[3])
            for row in cursor.fetchall()
        ]
        if books is not None:
            return jsonify(books)

    if request.method == "POST":
        content = request.get_json()
        
        new_author = content['author']
        new_lang = content['language']
        new_title = content['title']
        sql = """INSERT INTO book (author, language, title)
                 VALUES (?, ?, ?)"""
        cursor = cursor.execute(sql, (new_author, new_lang, new_title))
        conn.commit()
        return {"message" :"Book inserted successfully"}, 201


@app.route("/book/<int:id>", methods=["GET", "PUT", "DELETE"])
@auth.login_required
def single_book(id):
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == "GET":
        cursor.execute("SELECT * FROM book WHERE id=?", (id,))
        
        data = cursor.fetchone()
        
        if data is not None:
            response = {
                "id": data[0],
                "author": data[1],
                "language": data[2],
                "title": data[3],
            }
            return jsonify(response), 200
        else:
            return {"message": "Book not exist"}, 404

    if request.method == "PUT":
        cursor.execute("SELECT * FROM book WHERE id=?", (id,))
        data = cursor.fetchone()
        
        sql = """UPDATE book
                SET title=?,
                    author=?,
                    language=?
                WHERE id=? """
        content = request.get_json()        
        author = content['author']
        language = content['language']
        title = content['title']
        updated_book = {
            "id": id,
            "author": author,
            "language": language,
            "title": title,
        }
        conn.execute(sql, (title, author, language, id))
        conn.commit()
        if data is not None:
            return jsonify(updated_book)
        else:
            return {"message": "Book not exist"}, 404

    if request.method == "DELETE":
        cursor.execute("SELECT * FROM book WHERE id=?", (id,))
        
        data = cursor.fetchone()
        
        sql = """ DELETE FROM book WHERE id=? """
        conn.execute(sql, (id,))
        conn.commit()
        if data is not None:
            message = "The book with id: {} has been deleted.".format(id)
            return {"message" : message}, 200
        else:
            return {"message": "Delete Failed, Book not exist"}, 404


if __name__ == "__main__":
    app.run(debug=True)