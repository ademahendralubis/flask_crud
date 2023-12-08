from apps import app

def test_get_books():
    with app.test_client() as c:
        response = c.get('books')
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == [{"author":"bbb","id":1,"language":"ccc","title":"aaa"}]
        
def test_get_books():
    with app.test_client() as c:
        response = c.get('single_book/1')
        assert response.status_code == 200
        json_response = response.get_json()
        assert json_response == [{"author":"bbb","id":1,"language":"ccc","title":"aaa"}]