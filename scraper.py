import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_myanimelist():
    base_url = "https://myanimelist.net/anime/genre/{}/{}?page={}"
    df = pd.read_csv("anime_genres.csv",index_col=0)
    genres = {
        index : row["genre_name"] for index, row in df.iterrows()
    }
    seen_titles = set()
    all_anime_data = []
    for genre_id, genre_name in genres.items():
        page_number = 1
        while True:
            print("---------------------")
            print(f"Scraping genre: {genre_name}, Page: {page_number}")
            url = base_url.format(genre_id, genre_name, page_number)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            anime_items = soup.find("div", class_="seasonal-anime-list")
            if not anime_items:
                break
            for item in anime_items.find_all("div", class_="js-seasonal-anime"):
                print("scraping item...")
                title_tag = item.find("span", class_="js-title")
                if title_tag.text.strip() in seen_titles:
                    continue
                type_tag = item.find("div", class_="info").find_next("span",class_="item").text.strip()
                score_tag = item.find("span", class_="js-score")
                members_tag = item.find("span", class_="js-members")
                genres = [genre.text.strip() for genre in item.find("div", class_="js-genre").find_all("span", class_="genre")]
                studio_tag = item.find("div", class_="js-synopsis").find_next("span",class_="item").text.strip()
                themes_caption = item.find("span", class_="caption", string=re.compile(r"Theme[s]?"))
                themes = [theme.text.strip() for theme in themes_caption.find_next_siblings("span", class_="item")] if themes_caption else []
                demo_caption = item.find("span", class_="caption", string=re.compile(r"Demographic[s]?"))
                demographics = [demo.text.strip() for demo in demo_caption.find_next_siblings("span", class_="item")] if demo_caption else []
                anime_data = {
                    "title": title_tag.text.strip() if title_tag else None,
                    "type": type_tag[:type_tag.index(",") if "," in type_tag else -1] if type_tag else None,
                    "score": score_tag.text.strip() if score_tag else None,
                    "members": members_tag.text.strip() if members_tag else None,
                    "genres": ", ".join(genres) if genres else "",
                    "studio": studio_tag,
                    "themes": ", ".join(themes) if themes else "",
                    "demographics": ", ".join(demographics) if demographics else ""
                }
                print(anime_data)
                print("---------------------")
                all_anime_data.append(anime_data)
                seen_titles.add(title_tag.text.strip())
                # print("waiting for 1 second...")
                # time.sleep(1)
            page_number += 1
    df = pd.DataFrame(all_anime_data,columns=["title","score","members","genres","studio","themes","demographics"])
    df.to_csv("anime_data.csv", index=False)

scrape_myanimelist()