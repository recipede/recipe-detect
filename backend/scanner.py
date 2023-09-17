from collections import Counter
from typing import List
from google.cloud import vision
import cohere  
import os
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

def is_food(flyer_text: str) -> bool:
    if COHERE_API_KEY == None:
        raise Exception("API key not found.")
    co = cohere.Client(COHERE_API_KEY)
    prompt = "The following is text from a grocery store flyer that sells conventional household goods and food. Determine if this item on the flyer is a food or not: " + flyer_text
    prompt += "\n\nPlease respond with only 'true' or 'false' based on whether the item is a food or not."
    response = co.generate(  
        model='command-nightly',  
        prompt = prompt,  
        max_tokens=200,  
        temperature=0.75)

    if response.generations == None:
        raise Exception("No response from API.")

    return response.generations[0].text.strip() == "true"

def extract_grocery(flyer_text: str) -> str:
    if COHERE_API_KEY == None:
        raise Exception("API key not found.")
    co = cohere.Client(COHERE_API_KEY)
    prompt = "The following is text from a grocery store flyer that sells conventional household goods and food. Determine what the product name is: " +flyer_text
    prompt += "\n\nPlease respond with only the name of the product." #kind of food or product that the item is."#"
    response = co.generate(  
        model='command-nightly',  
        prompt = prompt,  
        max_tokens=200,  
        temperature=0.75)

    if response.generations == None:
        raise Exception("No response from API.")

    return response.generations[0].text.strip()

def extract_flyer(image_uri: str) -> str:
    client = vision.ImageAnnotatorClient()
    response = client.annotate_image({
      'image': {'source': { 'image_uri': image_uri }},
      'features': [{'type_': vision.Feature.Type.TEXT_DETECTION}]
    })
    return str(response.text_annotations[0].description)

def extract_cost(flyer_text: str) -> float:
    flyer_text = flyer_text.replace("\\\n", " ")
    flyer_text = flyer_text.replace("\n", " ")
    flyer_words = flyer_text.split(" ")
    costs = [ float(w) for w in flyer_words if (len(w) >= 3 and w[-1] == '9') ]
    return costs[0] / 100

if __name__ == "__main__":
    flyer_text = extract_flyer("https://raw.githubusercontent.com/recipede/recipe-detect/main/backend/grocery/crop_14.jpg")
    print(extract_cost(flyer_text))
