import sqlite3
import flask
import json
from flask import Flask


def run_sql(sql):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row  # вывод в строке
        result = []
        for item in connection.execute(sql).fetchall():
            result.append(dict(item))

        return result  # fetchall()[0] = fetchone()


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # как и ensure_ascii=False для кириллицы


@app.get('/movie/<title>')  # app.get() = app.route("/", methods=["GET", "POST"]
def get_movie_information(title):
    sql = f""" 
            Select title, country, release_year, listed_in as genre, description 
            from netflix
            where title like '%{title}%'
            order by date_added desc 
            limit 1  
            """
    result = run_sql(sql)
    if result:
        result = result[0]

    return flask.jsonify(result)
    # return app.response_class(json.dump(result, ensure_ascii=False indent=8), mimetype="application/json")


@app.get("/movie/<int:year1>/to/<int:year2>")
def get_by_year(year1, year2):
    sql = f""" 
            select title, release_year from netflix 
            where release_year between {year1} and {year2}
            order by release_year
            limit 100 """

    return flask.jsonify(run_sql(sql))


@app.get("/rating/<rating>")
def get_by_rating(rating):
    watch_groups = {
        "children": ("G", "G"),
        "family": ("G", "PG", "PG-13"),
        "adult": ("R", "NC-17")
    }

    sql = f'''
            select title, rating, description from netflix
            where rating in {watch_groups.get(rating, ('PG-13', 'NC-17'))}
            '''
    return flask.jsonify(run_sql(sql))


@app.get("/genre/<genre>")
def get_by_genre(genre):
    sql = f'''
            select title, description from netflix
            where listed_in like  '%{genre.title()}%'
           '''
    return flask.jsonify(run_sql(sql))


def step_5(name1='Rose McIver', name2='Ben Lamb'):
    sql = '''
           select "cast" from netflix
           where "cast" like '%{name1}%' and '%{name2}%'
          '''
    result = run_sql(sql)
    print(result)

    main_name = {}

    for item in result:
        names = item.get('cast').split(", ")
        for name in names:
            # if name in main_name.keys():
            #     main_name[name] += 1
            # else:
            #     main_name[name] = 1
            main_name[name] = main_name.get(name, 0) + 1
    print(main_name)
    result = []
    for item in main_name:
        if item not in (name1, name2) and main_name[item] > 2:
            result.append(item)

    return result


def step_6(types='TV Show', release_year=2021, genre='TV'):
    sql = '''
           select type, release_year, listed_in from netflix
           where type = '%{types}%'
           and release_year = '%{release_year}%'
           and listed_in like  '%{genre}%'
          '''
    return json.dumps(run_sql(sql), indent=4, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)
