import random;random.seed(111)
import pandas as pd
import problem_bank_helpers as pbh

def generate(data):
    data2 = pbh.create_data2()
    
    # define or load names/items/objects from server files
    names = pd.read_csv(data["options"]["client_files_course_path"]+"/data/names.csv")["Names"].tolist()
    manual_vehicles = pd.read_csv(data["options"]["client_files_course_path"]+"/data/manual_vehicles.csv")["Manual Vehicles"].tolist()
    
    # store phrases etc
    data2["params"]["vars"]["title"] = 'Kinematics'
    data2["params"]["vars"]["name"] = random.choice(names)
    data2["params"]["vars"]["vehicle"] = random.choice(manual_vehicles)
    data2["params"]["vars"]["units"] = "m/s"
    
    # Randomize Variables
    v = random.randint(2,7)
    t = random.randint(5,10)
    
    # store the variables in the dictionary "params"
    data2["params"]["v"] = v
    data2["params"]["t"] = t
    
    # define possible answers
    data2["params"]["part1"]["ans1"]["value"] = pbh.roundp(42)
    data2["params"]["part1"]["ans1"]["correct"] = False
    
    data2["params"]["part1"]["ans2"]["value"] = pbh.roundp(v*t)
    data2["params"]["part1"]["ans2"]["correct"] = True
    
    data2["params"]["part1"]["ans3"]["value"] = pbh.roundp(v+t)
    data2["params"]["part1"]["ans3"]["correct"] = False
    
    data2["params"]["part1"]["ans4"]["value"] = pbh.roundp(v/t)
    data2["params"]["part1"]["ans4"]["correct"] = False
    
    data2["params"]["part1"]["ans5"]["value"] = pbh.roundp(v-t)
    data2["params"]["part1"]["ans5"]["correct"] = False
    
    data2["params"]["part1"]["ans6"]["value"] = pbh.roundp(1.3*(v-t))
    data2["params"]["part1"]["ans6"]["correct"] = False
    
    # Update the data object with a new dict
    data.update(data2)
    
def prepare(data):
    pass
    
def parse(data):
    pass
    
def grade(data):
    pass
    
