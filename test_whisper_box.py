import requests

# URL API to fetch data from
listen_url = "https://localhost:8089/recstart"
stop_url = "https://localhost:8089/recstop"

data = {
    "stats":{
        "p_last_action": "",
        "p_lifepath": "Corpo",
        "p_time": "",
        "p_health_armor": {
            "health" : 100,
            "maxHealth" : 100,
            "armor" : 100,
        },
        "p_gender" : "Male",
        "p_location" : {
            "name": "Afterlife",
            "x" : 0,
            "y" : 0,
            "z" : 0
        },
        "p_quest": {
            "name": "New Job",
            "objective": "Find th fixer Mr.Hands"
        },
        "p_district": {
            "main": "Watson",
            "sub": "Watson",
        },
        "p_stats": {
            "food": 0,
            "hydration": 0,
            "fun": 0,
            "relationship": 0        
        },
        "p_combat_state" : {
            "state" : "normal",
            "time": "",
            "last_combat": "",
            "combat_duration": "",
        }
    },    
    "npc": {
        "id_hash": "26452346",
        "record_id_hash":"26452346",
        "class_name":"jackie welles",
        "display_name": "jackie welles",
        "tweaks_name": "jackie welles",
        "appearance": "jackie_normal_leather_jacket",
    }
}
actions_array = [
    "0. listen",
    "1. stop",
]

i=0

for action in actions_array:
    print(str(i) + ":" + action)
    i+=1

# listen first
# response = requests.post(listen_url, verify=False, json=data)
while True:
    selection = int(input("\033[93m"+"Select an action:"))
    if len(actions_array) < selection:
        print("bruh .. what are you doing?")
        continue
    
    print(f"Selected action: {actions_array[selection]}")
    
    if(selection == 0):
        response = requests.post(listen_url, verify=False, json=data)
    elif (selection == 1):
        response = requests.post(stop_url, verify=False, json=data)
    elif (selection == 2):
        response = requests.post(stat_url, verify=False, json=data)

    response_json = response.json()
    
    print(response.json())    

    i=0
    for action in actions_array:
        print("\033[96m" + str(i) + ":" + action)
        i+=1
    
