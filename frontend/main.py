"""
Taipy frontend for application.
"""
import taipy
from taipy.gui import notify
import requests
import os
import pandas as pd
from pymongo import MongoClient
from models.ingredient import Ingredient

CONNECTION_STRING = "mongodb+srv://j2795wan:hackthenorth2023@cluster0.mibkmem.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)
mydb = client['Cluster0']
pantry = mydb["pantry"]

# state
file_path = None
path = None
status = []
generated_ingredients = []
data = pd.DataFrame([])
current_ingredient = Ingredient()

# bindings
value = None
number = None
show_recipe_modal = False
selected_recipe = {}
selected_name = None
selected_ingredients = []
selected_steps = []

markdown = """
# Recipe Architech

## My Pantry
<|card|
<|{value}|input|label=Ingredient Name|on_change=on_ingredient_change|>
<|Add Ingredient|button|on_action=add_ingredient|>
|>

## Prepare to Cook
<|card|
<|{path}|file_selector|label=Upload Flyer|extensions=.png,.jpg|on_action=load_file|>
<|Let it cook!|button|on_action=generate_recipes|>
|>

## Recipes
<|card|
<|{data}|table|columns=Name|show_all|rebuild|on_action=on_recipe_click|>
|>

<|{"https://media4.giphy.com/media/WRXNJYnmTfaCUsU4Sw/giphy.gif?cid=6c09b952mdjomg6udjcjs7f2ybbepnrcks3zk55ymzfnt7u6&ep=v1_internal_gif_by_id&rid=giphy.gif&ct=s"}|image|>
<|{show_recipe_modal}|dialog|on_action=display_recipe_modal|title=Recipe Display|labels=Save Recipe;Cancel|
<|
<|{selected_name}|>\n
Ingredients\n
Steps
|>
|>
"""

# state modification
def on_ingredient_change(state):
    current_ingredient.set_name(state.value)

def display_recipe_modal(state, action, payload):
    print("attempt")
    with state as st:
        print(st, action, payload)
        print("AMONGUS", dict(st.selected_recipe))
        data_display = dict(st.selected_recipe)
        st.show_recipe_modal = False
    

def update_ingredient_display(new_ingredients: 'list[Ingredient]'):
    global status
    status = [(("info", ingredient.name)) for ingredient in new_ingredients]

def add_ingredient():
    if Ingredient.from_existing(current_ingredient).get_name() == "":
        return
    mydict = {"name":Ingredient.from_existing(current_ingredient).get_name()}
    pantry.insert_one(mydict)
    # current_ingredient.reset()
    cursor = pantry.find({}).distinct('names')
    for item in cursor:
        print(item)

def load_file(state):
    global file_path
    file_path = state.path

def on_recipe_click(state, var_name, action, payload):
    try:
        print(payload)
        idx = payload["index"]
        row = state.data.iloc[idx].to_dict()
        print(row)
        state.selected_recipe = row
        state.selected_name = row["Name"]
        state.selected_ingredients = row["Ingredients"]
        state.selected_steps = row["Steps"]
        state.show_recipe_modal = True
    except Exception as e:
        print("Recipe Error Click", str(e))

def generate_recipes(state):
    pantry_items = []
    cursor = pantry.find({}).distinct('names')
    for item in cursor:
        pantry_items.append(item)
    print(pantry_items)
    global file_path
    payload = {
        "path": file_path,
        "pantry": pantry_items
    }
    try:
        recipes_response = requests.post("http://localhost:8080/process", json=payload)
        recipe_data = recipes_response.json()
        recipes_result = recipe_data.get('result')

        recipe_display = {
            "Name": [],
            "Ingredients": [],
            "Steps": []
        }
        print(recipes_result)
        for recipe in recipes_result:
            name = recipe.get("name", "")

            ingredients = recipe.get("ingredients", [])
            steps = recipe.get("steps", [])
            print(name, ingredients)
            if name is None or name == "":
                continue
            recipe_display["Name"].append(name)
            recipe_display["Ingredients"].append(ingredients)
            recipe_display["Steps"].append(steps)
        data = pd.DataFrame(recipe_display)
        state.data = data
    except Exception as e:
        notify(state, "error", str(e))
    

taipy.Gui(page=markdown).run(
    title="Let us cook",
    host='0.0.0.0',
    port=os.environ.get('PORT', '5000'),
    use_reloader=True,
    stylekit={
        "color-secondary": "#4051B5",
    },
    css_file="main.css",
    dark_mode=False,
)