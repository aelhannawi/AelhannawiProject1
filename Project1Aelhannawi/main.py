import sys

import requests
import secrets
import sqlite3
from typing import Tuple


def get_top_250_data() -> list[dict]:
    all_data = []
    api_query = f"https://imdb-api.com/en/API/Top250TVs/{secrets.secret_key}"
    response = requests.get(api_query)
    if response.status_code != 200:  # if we don't get an ok response we have trouble
        print(f"Failed to get data, response code:{response.status_code} and error message: {response.reason} ")
        sys.exit(-1)
    # jsonresponse is a kinda useless dictionary, but the items element has what we need
    jsonresponse = response.json()
    show_list = jsonresponse["items"]
    return show_list


def report_results(data_to_write: list[dict]):
    with open("Output.txt", mode='a') as outputFile:  # open the output file for appending
        for show in data_to_write:
            print(show, file=outputFile)  # write each data item to file
            print("\n", file=outputFile)
            print("===================================================================", file=outputFile)


def get_ratings(top_show_data: list[dict]) -> list[dict]:
    results = []
    api_queries = []
    base_query = f"https://imdb-api.com/en/API/UserRatings/{secrets.secret_key}/"
    wheel_of_time_query = f"{base_query}tt1375666"
    api_queries.append(wheel_of_time_query)
    first_query = f"{base_query}{top_show_data[0]['id']}"
    api_queries.append(first_query)
    fifty_query = f"{base_query}{top_show_data[49]['id']}"
    api_queries.append(fifty_query)
    hundred_query = f"{base_query}{top_show_data[99]['id']}"
    api_queries.append(hundred_query)
    two_hundered = f"{base_query}{top_show_data[199]['id']}"
    api_queries.append(two_hundered)
    for query in api_queries:
        response = requests.get(query)
        if response.status_code != 200:  # if we don't get an ok response we have trouble, skip it
            print(f"Failed to get data, response code:{response.status_code} and error message: {response.reason} ")
            continue
        rating_data = response.json()
        results.append(rating_data)
    return results


def get_data():
    all_data = []
    response = requests.get(f"https://imdb-api.com/en/API/Top250TVs/k_8rtu00s8")
    first_page = response.json()
    if response.status_code != 200:
        print(F"Error Getting Data from API: {response.raw}")
        return []
    total_results = first_page['metadata']['total']
    page = 0
    per_page = first_page['metadata']['per_page']
    all_data.extend(first_page['results'])
    while (page + 1) * per_page < total_results:
        page += 1
        response = requests.get(
            f"https://imdb-api.com/en/API/Top250TVs/k_8rtu00s8")
        if response.status_code != 200:  # if we didn't get good data keep going
            continue
        current_page = response.json()
        all_data.extend(current_page['results'])

    return all_data


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(filename)  # connect to existing DB or create new one
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()


def make_tables(cursor: sqlite3.Cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS show_data(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    full_title NOT NULL,
    crew TEXT,
    IMDbrating INT,
    IMDbrating_counts INT);''')


def save_data(all_data, cursor):
    for show_data in all_data:
        cursor.execute("""
        INSERT INTO show_data(id, title, fulltitle, crew,imDbRating ,
         imDbRatingCount)
         VALUES (?,?,?,?,?,?);
        """, (show_data['id '], show_data['title '], show_data['fulltitle '],
              show_data['crew '], show_data['imDbRating '],
              show_data['imDbRatingCount ']))


def main():
    top_show_data = get_top_250_data()
    ratings_data = get_ratings(top_show_data)
    report_results(ratings_data)
    report_results(top_show_data)
    all_data = get_data()
    conn, cursor = open_db("comp490.sqlite")
    make_tables(cursor)
    save_data(all_data, cursor)
    close_db(conn)


if __name__ == '__main__':
    main()
