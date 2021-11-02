# https://myafu-python.com/todo/
# https://tech-diary.net/flask-introduction/
# flask(フラスク)とは？: pythonのwebアプリケーションフレームワーク
# 小規模向けの簡単なwebアプリケーションを作成するのに最適
# Djangoの簡易版
# https://aiacademy.jp/media/?p=57

import datetime
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy


# Flaskのインスタンス
app = Flask(__name__)

# データベース
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db' #データベースの作成。データベースsqliteを使って、名前はtodo.dbにする
db = SQLAlchemy(app) # データベースを操作するインスタンスの作成
class Post(db.Model): # db.Modelを継承して、データベース（どのようなデータか）を設定
    # todoアプリなので、todoごとのid, タイトル、詳細、期限を指定したい
    id = db.Column(db.Integer, primary_key=True) # idの設定。整数の指定。主キーにする。
    title = db.Column(db.String(30), nullable=False) # タイトル。30までにしてい。空はダメ、つまり必須。
    detail = db.Column(db.String(100)) # 詳細。100文字まで
    due = db.Column(db.DateTime, nullable=False) # 期限。日付を表示。必須に指定

###############################
# ルーティング
###############################

# ホーム画面
@app.route('/', methods=['GET', 'POST']) # index関数の場所を指定。メソッドGETとPOSTを継承。
def index(): # 表示する内容
    if request.method == 'GET': #リクエスト方法がGETなら(アクセスしただけ)
        posts = Post.query.all() # データベースから投稿したものすべてを取り出す
        sortdedposts = sorted(posts, key=lambda x: x.due) # postsを日付順にソート
        today = datetime.datetime.now()
        return render_template('index.html', posts=sortdedposts, today=today) # ここの内容を表示する。index.htmlとposts（データベースから受け取ったデータ）。
    else: # リクエスト方法がPOSTなら
        title = request.form.get('title') # formから受け取ったtitle
        detail = request.form.get('detail')
        due = request.form.get('due')
        due = datetime.datetime.strptime(due, '%Y-%m-%d') # 表記法を変更
        #print(due)
        new_post = Post(title=title, detail=detail, due=due) # 新しく来た投稿を作成

        db.session.add(new_post) # データベースに保存
        db.session.commit()

        return redirect('/')

# タスク作成
@app.route('/create')
def create(): 
    return render_template('create.html') 

# タスク削除
@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

# タスク編集
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get(id)
    if request.method == 'GET': # /edit/idにアクセスしたら
        return render_template('edit.html', post=post)
    else: # 編集したら
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = request.form.get('due')
        post.due = datetime.datetime.strptime(post.due, '%Y-%m-%d')

        db.session.commit()

        return redirect('/')

# 今日のTODO
@app.route('/day')
def day():
    posts = Post.query.all() # データベースから投稿したものすべてを取り出す
    dayposts = []
    for post in posts:
        if post.due.date() == datetime.date.today():
            dayposts.append(post)
    sortdedposts = sorted(dayposts, key=lambda x: x.due) # postsを日付順にソート
    today = datetime.datetime.now()
    return render_template('day.html', posts=sortdedposts, today=today)

# 今週のTODO
@app.route('/week')
def week():
    posts = Post.query.all()
    weekposts = []
    today = datetime.date.today()
    weekday = today + datetime.timedelta(days=7)
    for post in posts:
        if post.due.date() < weekday:
            weekposts.append(post)
    sortdedposts = sorted(weekposts, key=lambda x: x.due) # postsを日付順にソート
    today = datetime.datetime.now()
    return render_template('week.html', posts=sortdedposts, today=today)
    

# 使い方説明
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# main
if __name__ == '__main__':
    app.run(debug=True)