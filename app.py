from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
import base64
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from geopy.geocoders import Nominatim
from random import randint
from con import *


@app.route('/')
def index():
    s = ""
    s += f"SELECT id, img, title, creator_name FROM main WHERE id>={str(0)} AND id<={str(10)};"

    db_cursor.execute(s)

    array_users = db_cursor.fetchall()
    array_users = array_users[::-1]

    return render_template('index.html', array_us=array_users, method='utf-8')
    
@app.route('/page/<int:id>')
def main_pages(id):
    s = ""
    s += f"SELECT id, img, title, ad, prew_img, creator_id FROM main WHERE id>={str(id)} AND id<={str(int(id)+10)};"

    db_cursor.execute(s)
    array_users = db_cursor.fetchall()
    print(array_users)

    return render_template('index.html', array_us=array_users, method='utf-8')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    captcha_response = request.form['g-recaptcha-response']
    if str(captcha_response)=='':
        return redirect('/login')
    user = User.query.filter_by(email=email).first()
    if check_password_hash(user.password, password) == False:
        flash('Пароль или email введён неверно')
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    time.sleep(3)
    return redirect(url_for('index'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    main_num = request.form.get('main_num')
    prew_img = request.files['prew_img']
    captcha_response = request.form['g-recaptcha-response']
    if str(captcha_response)=='':
        return redirect('/signup')
    user = User.query.filter_by(email=email).first()
    num = User.query.filter_by(main_num=main_num).first()
    login = User.query.filter_by(name=name).first()
    if num:
        flash('Тел.номер занят')
        return redirect(url_for('signup'))

    if user:
        flash('Email занят')
        return redirect(url_for('signup'))

    if login:
        flash('Login занят')
        return redirect(url_for('signup'))

    if len(password) < 8:
        flash('Пароль меньше 8 символов')
        return redirect(url_for('signup'))

    if prew_img.filename == '':
        prew_img.filename = 'Без_названия.png'
    else:
        prew_form = prew_img.filename
        prew_form = str.split(prew_form, '.')
        if str(prew_form[-1])=='png' or str(prew_form[-1])=='jpg':
            prew_img.save(os.path.join(app.config['UPLOAD_FOLDER'], str(email) + str(name) + str(main_num)) + '.' + str(prew_form[-1]))
        else:
            flash('Неправильный формат файла. Нужен jpg(jpeg) или png')
    new_user = User(main_num=main_num, email=email, name=name, password=generate_password_hash(password, method='sha256'), prew_img=prew_img.filename)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/view/<int:id>', methods=['POST', 'GET'])
def view(id):
   its = Item.query.get(id)
   if request.method == 'POST':
       captcha_response = request.form['g-recaptcha-response']
       if str(captcha_response)=='':
            return redirect(f'/send_service/{id}')
       comment = request.form['comment']
       name = current_user.name
       phone = current_user.main_num
       mail = current_user.email
       mess = str(f'(Имя : {name} ),( Телефон : {phone} ),( Почта : {mail} ),( Коментарий : {comment}),( Услуга : {its.title}),(ссылка на профиль : /profile/{current_user.id}/)')
       send = Service(mess=mess, us=its.creator_id)
       db.session.add(send)
       db.session.commit()
       return redirect(f'/view/{id}')
   else:
       for i in its.img:
           print(str(i))
       return render_template('view.html', dt=its, dt_len=len(its.img))


@app.route("/",methods=["POST"])
def result():
    searchbox = request.form.get("search")
    List1 = []
    results = db.session.query(Item).all()
    for i in results:
        if (searchbox in i.title) is True:
            List1.append([i.title, i.creator_id, i.id, i.prew_img])
    return render_template('result.html', count=len(List1), result=List1)

@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic
    api_key = request.headers.get('orization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

@app.route('/create', methods=['POST', 'GET'])
#@login_required
def create():
    if request.method == "POST":
    #and current_user.is_authenticated
        title = request.form['title']
        captcha_response = request.form['g-recaptcha-response']
        if str(captcha_response)=='':
            return redirect('/create')
        img = request.files.getlist('img[]')
        text = request.form['text']
        prew_img = request.files['prew_img']
        fname = []
        for im in img:
            imm = str(title) + str(current_user.name) + str(randint(0, 10000))
            im.save(os.path.join(app.config['UPLOAD_FOLDER'], imm))
            fname.append(imm)
        print(str(title), fname, text, current_user.name)
        item = Item(title=str(title), img=fname, text=text, creator_name=current_user.name)
        db.session.add(item)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create.html')

app.secret_key = 'some_secret_key'
if __name__ == "__main__":
    app.run(debug=False, host='192.168.43.94')
