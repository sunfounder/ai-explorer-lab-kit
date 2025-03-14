from fusion_hat import RC522
import json

rc = RC522()
rc.Pcd_start()

users_db = "users.json"  # the file to store user data

# load the existing user data from the file
try:
    with open(users_db, "r") as file:
        users = json.load(file)
except FileNotFoundError:
    users = {}

def register_card():
    print("Please place the card to register...")
    uid,message = rc.read(2)
    if uid:
        user_name = input("Enter the name of the cardholder: ")
        users[uid] = user_name
        with open(users_db, "w") as file:
            json.dump(users, file)
        print(f"Card registered successfully for {user_name}.")
    else:
        print("Failed to read the card.")

if __name__ == "__main__":
    while True:
        register_card()
        if input("Register another card? (y/n): ").lower() != 'y':
            break
