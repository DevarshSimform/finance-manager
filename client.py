import requests 

BASE_URL = "http://127.0.0.1:5000/api/v1"

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None

    def login(self, email, password):
        """Login and store access & refresh tokens"""
        url = f"{BASE_URL}/login/"
        data = {"email": email, "password": password}
        response = self.session.post(url, json=data)
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get("access")
            self.refresh_token = tokens.get("refresh")
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
        return response.json()

    def refresh_token(self):
        """Refresh the access token"""
        url = f"{BASE_URL}/token/refresh/"
        data = {"refresh": self.refresh_token}
        response = self.session.post(url, json=data)

        if response.status_code == 200:
            self.access_token = response.json().get("access")
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
        return response.json()

    def get_transactions(self):
        """Get all transactions"""
        url = f"{BASE_URL}/transactions/"
        response = self.session.get(url)
        return response.json()

    def get_transaction(self, transaction_id):
        """Get a single transaction by ID"""
        url = f"{BASE_URL}/transactions/{transaction_id}/"
        response = self.session.get(url)
        return response.json()

    def create_transaction(self, user_id, category_id, amount, type, description=""):
        """Create a new transaction"""
        url = f"{BASE_URL}/transactions/"
        data = {
            "user_id": user_id,
            "category_id": category_id,
            "amount": amount,
            "type": type,
            "description": description,
        }
        response = self.session.post(url, json=data)
        return response.json()

    def update_transaction(self, transaction_id, amount, type, description=""):
        """Update a transaction"""
        url = f"{BASE_URL}/transactions/{transaction_id}/"
        data = {
            "amount": amount,
            "type": type,
            "description": description,
        }
        response = self.session.put(url, json=data)
        return response.json()

    def delete_transaction(self, transaction_id):
        """Soft delete a transaction"""
        url = f"{BASE_URL}/transactions/{transaction_id}/"
        response = self.session.delete(url)
        return response.status_code  # Should return 204 for successful deletion

# Example usage
if __name__ == "__main__":
    client = APIClient()

    # Login and get tokens
    print("Logging in...")
    print(client.login("dhruv@gmail.com", "Admin@123"))
    # print(client.session.headers)

    # Refresh token
    # print("\nRefreshing token...")
    # print(client.refresh_token())

    # Fetch all transactions
    # print("\nFetching transactions...")
    # print(client.get_transactions())

    # Fetch a specific transaction
    # transaction_id = "6a5f18bb-b527-44d2-a9bc-03a3ea6b8055"
    # print(f"\nFetching transaction {transaction_id}...")
    # print(client.get_transaction(transaction_id))

    # Logout (optional)
    # print("\nLogging out...")
    # print(client.logout())
