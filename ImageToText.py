import os
import pytesseract
import requests
import pandas as pd
from PIL import Image
from typing import List
from langdetect import detect
from iso639 import languages
import time
from textblob import TextBlob
from copy import deepcopy

#Checks if csv file exists, if not creates it then loads a dataframe from it
def check_csv(filepath : str) -> pd.DataFrame:
    if not os.path.isfile(filepath):
        pd.DataFrame(columns=["Image URL", "Raw Text", "Language", "Polarity", "Subjectivity","Lang Code"]).to_csv(filepath)
    return pd.read_csv(filepath).drop("Unnamed: 0", axis=1)

#Returns list of all URLs
def get_urls(filepath : str) -> List[str]:
    return [url.strip() for url in open(filepath, "r").read().split("\n")]


#Extracting text from image
def get_text(img : Image) -> str:
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 140 else 255)
    return pytesseract.image_to_string(img).replace("\n", " ")

#Performs some basic nlp on text
def analyse_text(text: str) -> List:
    blob = TextBlob(text)
    lang_code = detect(text)
    language = languages.get(alpha2=lang_code).name
    polarity, subjectivity = "", ""
    if language == "English":
        polarity = blob.polarity
        subjectivity= blob.subjectivity
    return [text, language, polarity, subjectivity, lang_code]

#Method to get data from every url in the sheet
def analyse_all_urls(image_url : List[str], dataframe : pd.DataFrame) -> None:
    print("Starting to scan!")
    counter, total = 0, len(image_url)
    for url in image_url:
        counter+=1
        if counter % 20 == 0:
            print(f"Currently on image: {counter} out of {total}")
        img = requests.get(url, stream=True, headers=headers)
        if img.status_code == 200:
            row = [url] + analyse_text(get_text(Image.open(img.raw)))
            dataframe.loc[len(dataframe)] = row
        else:
            print("Error" + img.status_code + "\n" + img.text)
        time.sleep(0.5)

#Saves dataframe to a csv file
def save_dataframe(filename : str, dataframe : pd.DataFrame) -> None:
    dataframe.to_csv(filename)
    print("Data Saved to " + filename)


#Main method
if __name__ == "__main__":
    url_filename = "./images.txt"
    csv_filename = "./data.csv"

    image_data_df = check_csv(csv_filename)
    image_urls = get_urls(url_filename)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    analyse_all_urls(image_url=image_urls, dataframe=image_data_df)
    print("Done!, saving to file.")
    save_dataframe(filename=csv_filename, dataframe=image_data_df)


