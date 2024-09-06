import requests, os, json
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
NTFY_BASE_URL = os.getenv("NTFY_BASE_URL")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")


def ntfy(data, headers):
    print("Making request to NTFY...")
    
    r1 = requests.post(f"{NTFY_BASE_URL}/{NTFY_TOPIC}",
                        data=data,
                        headers=headers)
    
    # Print status code
    print("Status code:", r1.status_code)

    if r1.status_code == 200:
        print("Notification sent successfully")
    else:
        print(f"Error sending notification: {r1.status_code}")


def main():
    print("Making request to EcoFlow API...")
    r = requests.get("https://api.ecoflow.com/iot-service/open/api/device/queryDeviceQuota", 
                     headers={
                        "Content-Type": "application/json",
                        "appKey": os.getenv("ECOFLOW_APP_KEY"),
                        "secretKey": os.getenv("ECOFLOW_SECRET_KEY")
                    }, 
                     params={
                        "sn": os.getenv("ECOFLOW_SN")
                    })
    
    # Print status code
    print("Status code:", r.status_code)

    # Print response body
    if r.status_code == 200:
        print("Request successful")
    else:
        print("Error, status code:", r.status_code)
        return
    
    ecoflow_data = r.json()["data"]

    # check current state
    current_state = {
        "battery_low": True if ecoflow_data["soc"] < 20 else False if ecoflow_data["soc"] >= 99 else None,
        "overload": True if ecoflow_data["wattsOutSum"] > 1500 else False,
        "blackout": False if ecoflow_data["wattsInSum"] > 0 else True if ecoflow_data["wattsOutSum"] - ecoflow_data["wattsInSum"] > 0 else None
    }

    # check previous state
    none_state = {
        "battery_low": None,
        "overload": None,
        "blackout": None
    }
    # Creates empty file if it doesn't exist
    if not os.path.isfile("ecoflow_state.txt"):
        with open("ecoflow_state.txt", "w") as f:
            json.dump(none_state, f)
    
    with open("ecoflow_state.txt", "r") as f:
        previous_state = json.load(f)

    # compare states and send notification
    if current_state["battery_low"] != None and current_state["battery_low"] != previous_state["battery_low"]:
        if current_state["battery_low"]:
            print("Sending battery low notification...")
            headers = {
                "Title": "EcoFlow-1 battery is low",
                "Priority": "default",
                "Tags": "battery, warning",
                "Authorization": f"Bearer {os.getenv('NTFY_TOKEN')}"
            }
        else:
            print("Sending battery fully charged notification...")
            headers = {
                "Title": "EcoFlow-1 battery fully charged",
                "Priority": "default",
                "Tags": "battery, ok",
                "Authorization": f"Bearer {os.getenv('NTFY_TOKEN')}"
            }
        data = json.dumps(ecoflow_data, indent=4)
        ntfy(data, headers)
    else:
        print("Battery state not changed.")
    
    if current_state["overload"] != None and current_state["overload"] != previous_state["overload"]:
        if current_state["overload"]:
            print("Sending overload notification...")
            headers = {
                "Title": "EcoFlow-1 overload",
                "Priority": "default",
                "Tags": "fire, warning",
                "Authorization": f"Bearer {os.getenv('NTFY_TOKEN')}"
            }
        else:
            print("Sending overload cleared notification...")
            headers = {
                "Title": "EcoFlow-1 overload cleared",
                "Priority": "default",
                "Tags": "fire, ok",
                "Authorization": f"Bearer {os.getenv('NTFY_TOKEN')}"
            }
        data = json.dumps(ecoflow_data, indent=4)
        ntfy(data, headers)
    else:
        print("Overload state not changed.")

    if current_state["blackout"] != None and current_state["blackout"] != previous_state["blackout"]:
        if current_state["blackout"]:
            print("Sending blackout notification...")
            headers = {
                "Title": "EcoFlow-1 blackout",
                "Priority": "default",
                "Tags": "zap, warning",
                "Authorization": f"Bearer {os.getenv('NTFY_TOKEN')}"
            }
        else:
            print("Sending blackout cleared notification...")
            headers = {
                "Title": "EcoFlow-1 lights are back!",
                "Priority": "default",
                "Tags": "zap, ok",
                "Authorization": f"Bearer {os.getenv('NTFY_TOKEN')}"
            }
        data = json.dumps(ecoflow_data, indent=4)
        ntfy(data, headers)
    else:
        print("Blackout state not changed.")


    # update previous state
    with open("ecoflow_state.txt", "w") as f:
        json.dump(current_state, f)

if __name__ == "__main__":
    main()
