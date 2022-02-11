import main
import pytest


@pytest.fixture
def get_db():
    conn, cursor = main.open_db('testdb.sqlite')
    return conn, cursor


def test_get_data():
    data = main.get_data()
    assert len(data) > 3000


def test_data_save(get_db):
    # first lets add test data
    conn, cursor = get_db
    main.make_tables(cursor)
    test_data = {
        "items": [{"id": "tt1375666", "rank": "40", "title": "The Office", "fullTitle": "The Office (2005)",
                   "year": "2005", "crew": " Steve Carell, Jenna Fischer ", "imDbRating": "8.9",
                   "imDbRatingCount": "515389"}]}
    main.save_data(test_data, cursor)
    main.close_db(conn)
    # test data is saved - now lets see if it is there
    conn, cursor = main.open_db('testdb.sqlite')
    # the sqlite_master table is a metadata table with information about all the tables in it
    cursor.execute('''SELECT name FROM sqlite_master
    WHERE type ='table' AND name LIKE 'show_%';''')  # like does pattern matching with % as the wildcard
    results = cursor.fetchall()
    assert len(results) == 1
    cursor.execute(''' SELECT title FROM topShow_data''')
    results = cursor.fetchall()
    test_record = results[0]
    assert test_record[0] == 'items'