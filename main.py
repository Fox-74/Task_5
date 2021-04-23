from flask import Flask, request, jsonify
import sqlite3 as lite
from newsapi import NewsApiClient
from config import newsApi_token
usc = 0

app = Flask(__name__)
#Создание БД
con = lite.connect('news_bd.db', check_same_thread=False)
cur = con.cursor()
def add_user(user_id):
    global usc
    usc = user_id
    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,'' f_name varchar(50), l_name varchar(50));')
    cur.execute('CREATE TABLE IF NOT EXISTS categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT,''cat_name varchar(100), user_id INTEGER)')
    cur.execute('CREATE TABLE IF NOT EXISTS keywords (keyword_id integer primary key AUTOINCREMENT,''word_name varchar(100), user_id INTEGER)')
    user_data = cur.execute(f"SELECT * FROM users WHERE user_id = {user_id}").fetchone()
    if user_data is None:
        cur.execute(f"INSERT INTO users (user_id) VALUES "f" ({user_id})")
        con.commit()
        return "Готово, добавлен"
    return f"Добрый день {user_id}"
def add_category(category):
    сdata = cur.execute(f"SELECT * FROM categories WHERE cat_name = '{category}' "f"AND user_id = {usc}").fetchone()
    print(сdata)
    if сdata is None:
        cur.execute(f"INSERT INTO categories (cat_name, user_id) VALUES "f" ('{category}',"f" {usc})")
        con.commit()
        return "(^-^)"
    else:
        return "(Оо)"


def add_keyword(message):
    kdata = cur.execute(f"SELECT * FROM keywords WHERE word_name = '{message}' "f"AND user_id = {usc}").fetchone()
    if kdata is None:
        cur.execute(f"INSERT INTO keywords (word_name, user_id) VALUES "f" ('{message}',"f" {usc})")
        con.commit()
        return "Слово (^-^)"
    else:
        return "Слово (оО)"

def show_categories():
    cats = cur.execute(f"SELECT cat_name FROM categories WHERE user_id = {usc}").fetchall()
    if cats is None:
        return "\-(oO)-/"
    else:
        return f"Категории: {cats}"


def show_keywords():
    keyw = cur.execute(f"SELECT word_name FROM keywords WHERE user_id = {usc}").fetchall()
    if keyw is None:
        return "(Оо)"
    else:
        return f"Ключевые слова: {keyw}"


def remove_category(cn):
    cur.execute(f"DELETE FROM categories WHERE cat_name = '{cn}'")
    con.commit()


def remove_keyword(wn):
    cur.execute(f"DELETE FROM keywords WHERE word_name = '{wn}'")
    con.commit()


@app.route('/subscriptions/categories/<category>', methods=['GET', 'PUT', 'DELETE'])
def categories(category):
    if request.method == 'GET':
        cats = show_categories()
        return jsonify(f'{cats}')
    if request.method == 'PUT':
        add_category(category)
        return jsonify(f'Категория добавлена')
    if request.method == 'DELETE':
        remove_category(category)
        return f'Категория {category} удалена'


@app.route('/subscriptions/keywords/<keyword>', methods=['GET', 'PUT', 'DELETE'])
def keywords(keyword):
    if request.method == 'GET':
        keywords = show_keywords()
        return jsonify(keywords)
    if request.method == 'PUT':
        add_keyword(keyword)
        return jsonify(f'Ключевое слово добавлено')
    if request.method == 'DELETE':
        remove_keyword(keyword)
        return f'Ключевое слово {keyword} удалено'


@app.route('/users/<user_id>', methods=['GET'])
def users(user_id):
    if request.method == 'GET':
        ret = add_user(user_id)
        return jsonify(ret)
    return jsonify("Ошибочка")


@app.route('/news/', methods=['GET'])
def get_news():
    newsapi = NewsApiClient(api_key=newsApi_token)
    if request.method == 'GET':
        cats = cur.execute(f"SELECT cat_name FROM categories WHERE user_id = {usc}").fetchall()
        keyw = cur.execute(f"SELECT word_name FROM keywords WHERE user_id = {usc}").fetchall()

        category_list = [item for t in cats for item in t]
        keyword_list = [item for t in keyw for item in t]
        links = []
        titles = []
        for cat in category_list:
            for keyword in keyword_list:
                top_headlines = newsapi.get_top_headlines(q=keyword,
                                                          category=cat,
                                                          page_size=10,
                                                          page=1)
                print( f"Категории \"{cat}\"\n ключевые слова \"{keyword}\"\n")
                articles = []
                articles = top_headlines['articles']
                if articles:
                    if len(articles) > 10:
                        cnt = 10
                    else:
                        cnt = len(articles)
                    for i in range(cnt):
                        print( f"-{i}-\n")
                        print("cnt = ", cnt)
                        print(top_headlines)
                        links.append(top_headlines['articles'][i]['url'])
                        titles.append(top_headlines['articles'][i]['title'])
                else:
                    print("(оО)\n")

        return jsonify(ok = 200, link = links)
    return jsonify("ok")

if __name__ == '__main__':
    app.run("127.0.0.1", port=8080)

