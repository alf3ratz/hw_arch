from locust import HttpUser, task, between


# locust -f locustfile.py --host=http://localhost:5000
class StudentServiceUser(HttpUser):
    wait_time = between(1, 5)

    @task(1)
    def search_students(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "0",
            "method": "search_students",
            "params": {
                "params": {
                    "name": "Иван"
                }
            }
        }
        self.client.post("/api/v1/jsonrpc/search_students", json=payload)
