import sys

import requests
##import secrets
import sqlite3
from typing import Tuple


def get_top_250_data() -> list[dict]:
    all_data = []
    api_query = f"https://imdb-api.com/en/API/Top250TVs/k_8rtu00s8"
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
    base_query = f"https://imdb-api.com/en/API/UserRatings/k_8rtu00s8/tt1375666"
    ##wheel_of_time_query = f"{base_query}tt1375666"
    ##api_queries.append(wheel_of_time_query)
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


def get_show():
    show_data = []
    response = requests.get(
        f'https://imdb-api.com/en/API/Top250TVs/k_8rtu00s8')
    first_page = response.json()
    if response.status_code != 200:
        print(F"Error Getting Data from API: {response.raw}")
        return []
    total_results = first_page['metadata']['total']
    page = 0
    per_page = first_page['metadata']['per_page']
    show_data.extend(first_page['results'])
    while (page + 1) * per_page < total_results:
        page += 1
        response = requests.get(
            f'https://imdb-api.com/en/API/Top250TVs/k_8rtu00s8')
        if response.status_code != 200:  # if we didn't get good data keep going
            continue
        current_page = response.json()
        show_data.extend(current_page['results'])

    return show_data


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(filename)  # connect to existing DB or create new one
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()


def make_tables(cursor: sqlite3.Cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS topShow_data(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    fullTile  NOT NULL,
    year INT,
    crew TEXT,
    imdbRating INT,
    imdbRatingCount INT);''')


def save_data(show_data, cursor):
    for show_detail in show_data:
        cursor.execute("""
        INSERT INTO topShow_data(id, title, fullTitle,year, crew, imdbRating,
         imdbRatingCount)
         VALUES (?,?,?,?,?,?.?);
        """, (show_detail['id'], show_detail['title'], show_detail['full.title'],
              show_detail['year'], show_detail['crew'], show_detail['imDbRating'],
              show_detail['imDbRatingCount']))


def main():
    top_show_data = get_top_250_data()
    ratings_data = get_ratings(top_show_data)
    report_results(ratings_data)
    report_results(top_show_data)
    show_data = get_show()
    conn, cursor = open_db("comp490.sqlite")
    make_tables(cursor)
    save_data(show_data, cursor)
    close_db(conn)


if __name__ == '__main__':
    main()
