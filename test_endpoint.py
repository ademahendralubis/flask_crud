from apps import app, db_connection
import base64
import pytest

db = db_connection()

credentialsTrue = base64.b64encode(b"admin:123").decode('utf-8')
credentialsFalse = base64.b64encode(b"superadmin:1234").decode('utf-8')

def delete_all_books(conn):
    """
    Delete all rows in the tasks table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM book'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    
@pytest.fixture(autouse=True)
def delete_db():
    delete_all_books(db)

def test_authentication_success():
    with app.test_client() as c:
        response = c.get('books', headers={"Authorization": "Basic {}".format(credentialsTrue)})
        assert response.status_code==200
        
def test_authentication_failed():
    with app.test_client() as c:
        response = c.get('books', headers={"Authorization": "Basic {}".format(credentialsFalse)})
        assert response.status_code==401
        
def test_insert_book_success():
    with app.test_client() as c:
        response = c.get('books', headers={"Authorization": "Basic {}".format(credentialsTrue)})
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == []
        
        c.post('books', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaa"})
        
        response = c.get('books', headers={"Authorization": "Basic {}".format(credentialsTrue)})
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == [{"author":"bbb","id":1,"language":"ccc","title":"aaa"}]

def test_insert_book_failed():
    with app.test_client() as c:
        response = c.post('books', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc"})
        assert response.status_code == 500
        response = c.get('books', headers={"Authorization": "Basic {}".format(credentialsTrue)})
        json_response = response.get_json()
        assert json_response == []
        
def test_get_all_books():
    with app.test_client() as c:
        c.post('books', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaa"})
        response = c.get('books', headers={"Authorization": "Basic {}".format(credentialsTrue)})
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == [{"author":"bbb","id":1,"language":"ccc","title":"aaa"}]
        
def test_get_single_book_found():
    with app.test_client() as c:
        c.post('books', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaa"})
        response = c.get('book/1', headers={"Authorization": "Basic {}".format(credentialsTrue)})
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == {"author":"bbb","id":1,"language":"ccc","title":"aaa"}

def test_get_single_book_not_found():
    with app.test_client() as c:
        c.post('books', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaa"})
        response = c.get('book/2', headers={"Authorization": "Basic {}".format(credentialsTrue)})
        assert response.status_code == 404
        json_response = response.get_json()
        assert json_response == {"message": "Book not exist"}
        
def test_update_single_book_success():
    with app.test_client() as c:
        c.post('books', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaa"})
        response = c.put('book/1', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaaa"})
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == {"author":"bbb","id":1,"language":"ccc","title":"aaaa"}
        
def test_update_single_book_failed():
    with app.test_client() as c:
        c.post('books', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaa"})
        response = c.put('book/3', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaaa"})
        assert response.status_code == 404
        json_response = response.get_json()
        assert json_response == {"message": "Book not exist"}
        
def test_delete_single_book_success():
    with app.test_client() as c:
        c.post('books', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaa"})
        response = c.delete('book/1', headers={"Authorization": "Basic {}".format(credentialsTrue)})
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == {"message": "The book with id: 1 has been deleted."}
        
def test_delete_single_book_failed():
    with app.test_client() as c:
        c.post('books', headers={"Authorization": "Basic {}".format(credentialsTrue)}, json={"author":"bbb","language":"ccc","title":"aaa"})
        response = c.delete('book/2', headers={"Authorization": "Basic {}".format(credentialsTrue)})
        assert response.status_code == 404
        json_response = response.get_json()
        assert json_response == {"message": "Delete Failed, Book not exist"}