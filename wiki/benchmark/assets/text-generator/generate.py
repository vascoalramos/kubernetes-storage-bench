import json
import string
import random
import requests

DEEP_AI_URL = "https://api.deepai.org/api/text-generator"
API_KEY = ""
TEXT_OUTPUT_FOLDER = "output"

def generateTextFromKeywords(iterations=1, keywords_size=3):    
    for _ in range(iterations):
        with open("dataset.json") as dataset_file:
            dataset = json.loads(dataset_file.read())

        keywords = [random.choice(dataset) for _ in range(keywords_size)]
        filename = "_".join(keywords)

        generated_text = requests.post(DEEP_AI_URL, data={'text': " ".join(keywords)}, headers={'api-key': API_KEY}).json()["output"]

        with open("{}/{}.txt".format(TEXT_OUTPUT_FOLDER, filename), "w") as output_file:
            output_file.write(generated_text)


if __name__ == "__main__":
    generateTextFromKeywords(iterations=100, keywords_size=1)
