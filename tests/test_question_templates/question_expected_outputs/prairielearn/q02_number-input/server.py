import random;random.seed(111)
import pandas as pd
import problem_bank_helpers as pbh

def generate(data):
    data2 = pbh.create_data2()
    
    # define or load names/items/objects
    names = pd.read_csv(data["options"]["client_files_course_path"]+"/data/names.csv")["Names"].tolist()
    manual_vehicles = pd.read_csv(data["options"]["client_files_course_path"]+"/data/manual_vehicles.csv")["Manual Vehicles"].tolist()
    
    # store phrases etc
    data2["params"]["vars"]["name"] = random.choice(names)
    data2["params"]["vars"]["vehicle"] = random.choice(manual_vehicles)
    data2["params"]["vars"]["title"] = "Distance travelled"
    data2["params"]["vars"]["units"] = "m/s"
    
    # define bounds of the variables
    v = random.randint(2,7)
    t = random.randint(5,10)
    
    # store the variables in the dictionary "params"
    data2["params"]["v"] = v
    data2["params"]["t"] = t
    
    # define correct answers
    data2["correct_answers"]["part1_ans"] = v*t
    
    # Update the data object with a new dict
    data.update(data2)
    
def prepare(data):
    pass
    
def parse(data):
    pass
    
def grade(data):
    pass
    
