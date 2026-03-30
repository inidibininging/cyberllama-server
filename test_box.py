import requests

# URL API to fetch data from
url = "https://127.0.0.1:8089/promptcontinue"
npc_data = {
    "id_hash": "26452346",
    "record_id_hash":"26452346",
    "class_name":"someone welles",
    "display_name": "someone welles",
    "tweaks_name": "someone welles",
    "appearance": "ma_someone_normal_leather_jacket",
}
stats = {
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
}
data = {
    "prompt": "Hey Someone, wanna hit the after life club tonight?",
    "stats": stats,
    "npc": npc_data
}

# Fetch array of actions from API
response = requests.post(url, verify=False, json=data)
actions_array = response.json()["actions"]

i=0

for action in actions_array:
    print(str(i) + ":" + action)
    i+=1
 
while True:
    selection = int(input("\033[93m"+"Select an action:"))
    if len(actions_array) < selection:
        print("bruh .. what are you doing?")
        continue
    
    print(f"Selected action: {actions_array[selection]}")

    data = {"prompt": actions_array[selection]}
    data["npc"] = npc_data 
    data["stats"] = stats
    response = requests.post(url, verify=False, json=data)
    print(response.json())
    actions_array = response.json()["actions"]

    i=0
    for action in actions_array:
        print("\033[96m" + str(i) + ":" + action)
        i+=1
    
