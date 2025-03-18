import playwright.sync_api as playwright

def test_get_request():
    with playwright.sync_playwright() as p:
        # Create a new request context
        request = p.request.new_context()

        # Send a GET request
        response = request.get("https://jsonplaceholder.typicode.com/posts/1")

        # Validate the response
        assert response.status == 200
        assert response.ok
        assert response.json()["id"] == 1
        assert response.json()["title"] == "sunt aut facere repellat provident occaecati excepturi optio reprehenderit"

        print("GET Request Test Passed!")

def test_post_request():
    with playwright.sync_playwright() as p:
        # Create a new request context
        request = p.request.new_context()

        # Send a POST request with JSON payload
        payload = {
            "title": "foo",
            "body": "bar",
            "userId": 1
        }
        response = request.post("https://jsonplaceholder.typicode.com/posts", data=payload)

        # Validate the response
        assert response.status == 201
        assert response.ok
        assert response.json()["id"] == 101
        assert response.json()["title"] == "foo"


        print("POST Request Test Passed!")


def test_put_request():
    with playwright.sync_playwright() as p:
        # Create a new request context
        request = p.request.new_context()
        response = request.put("https://jsonplaceholder.typicode.com/posts/1", data={"title": "cool"})
        assert response.status == 200  
        assert response.json()["title"] == "cool" 
        print("PUT Request Test Passed!")
        print("The updated title is " + response.json()["title"])

    
def test_delete_request():
    with playwright.sync_playwright() as p:
        # Create a new request context
        request = p.request.new_context()

        # Send a DELETE request
        response = request.delete("https://jsonplaceholder.typicode.com/posts/1")

        # Validate the response
        assert response.status == 200
        assert response.ok
        assert response.json() == {}

        print("DELETE Request Test Passed!")

# Run the tests
test_get_request()
test_post_request()
test_put_request()
test_delete_request()