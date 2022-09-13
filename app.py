from flask import Flask, render_template, request, session, redirect, render_template_string
from dotenv import load_dotenv
from datetime import datetime
import json
import os
import sqlite3
import hashlib
import socket
import pickle
import base64

app = Flask(__name__, static_folder='./static/')
app.secret_key = os.urandom(16)
load_dotenv(verbose=True)


@app.route('/', methods=["GET"])
def init():
    if "user" in session:
        print(session["user"])
        html = '''
            <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>텍스트 사서함</title>
            <link href="https://hangeul.pstatic.net/hangeul_static/css/nanum-square-round.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css" rel="stylesheet"
                integrity="sha384-iYQeCzEYFbKjA/T2uDLTpkwGzCiq6soy8tYaI1GyVh/UjpbCx/TYkiZhlZB6+fzT" crossorigin="anonymous">
        </head>
        <style>
            body {
                font-family: "NanumSquareRound";
                text-align: center;
                max-width: 580px;
                margin: 0 auto;
            }

            h1 {
                margin-top: 10px;
            }
        </style>

        <body>
            <h1>텍스트 사서함</h1>
            <p>%s 님 환영합니다.</p>
            <form action="/submit" method="post">
                <div class=" input-group">
                    <span class="input-group-text">메시지</span>
                    <textarea class="form-control" aria-label="메시지" rows="10" name="msg"></textarea>
                </div>
                <br>
                <input type="submit" value="전송" class="btn btn-primary" />
            </form><br>
            <a href="/logout"><button class="btn btn-primary">로그아웃</button></a>
        </body>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-u1OknCvxWvY5kfmNBILK2hRnQC3Pr17a+RTT6rIHI7NnikvbZlHgTPOOmMi466C8"
            crossorigin="anonymous"></script>

        </html>
        ''' % session["user"]
        return render_template_string(html)
    return render_template("index.html")


@app.route('/login', methods=["POST"])
def login():
    session["user"] = request.form["id"]
    print(session["user"])
    return redirect("/")
    # con = sqlite3.connect('./db/account.db')
    # cur = con.cursor()
    # cur.execute(f'SELECT pw FROM account WHERE id = "{request.form["id"]}"')
    # try:
    #     if cur.fetchall()[0][0] == hashlib.sha256(request.form["pw"].encode()).hexdigest():
    #         session["user"] = request.form["id"]
    #         return redirect("/")
    # except:
    #     return "<script>alert('아이디 또는 비밀번호가 일치하지 않습니다.');window.history.back();</script>"
    # return "<script>alert('아이디 또는 비밀번호가 일치하지 않습니다.');window.history.back();</script>"


@app.route('/register', methods=["POST"])
def register():
    for i in ["os", "request", "%", "config"]:
        if i in request.form["register_id"]:
            return "<script>alert('올바르지 않은 문자열이 포함되어 있습니다.');window.history.back();</script>"
    if request.form["register_pw"] != request.form["register_pw2"]:
        return "<script>alert('비밀번호가 일치하지 않습니다.');window.history.back();</script>"
    con = sqlite3.connect('./db/account.db')
    cur = con.cursor()
    id = request.form["register_id"]
    pw = request.form["register_pw"]
    cur.execute(f'SELECT pw FROM account WHERE id = "{id}"')
    res = cur.fetchall()
    print(res)
    if res != []:
        return "<script>alert('이미 존재하는 아이디입니다.');window.history.back();</script>"
    cur.execute(
        f'INSERT INTO account (id,pw) VALUES ("{id}","{hashlib.sha256(pw.encode()).hexdigest()}")')
    con.commit()
    return redirect("/")


@app.route('/submit', methods=["POST"])
def submit():
    udp_port = 8081
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    now = datetime.now()
    msg = '{"msg":' + f"\"{request.form['msg']}\"" + ',"time":' + \
        f'"{str(now.hour).zfill(2)}:{str(now.minute).zfill(2)}:{str(now.second).zfill(2)}"' + \
        ',"user":' + f'"{session["user"]}"' + "}"
    enc = base64.b64encode(pickle.dumps(msg)).decode()
    sock.sendto(enc.encode(), (os.getenv('SERVER'), udp_port))
    data, addr = sock.recvfrom(1024)
    print(data.decode())
    sock.close()
    return "<script>alert('전송 완료!');window.history.back();</script>"


@app.route('/logout', methods=["GET"])
def logout():
    session.pop('user', None)
    return redirect("/")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT', 5001), debug=1)
