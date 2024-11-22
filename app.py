from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Thay bằng secret key an toàn hơn
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# Model người dùng
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Model sách
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)

# Khởi tạo cơ sở dữ liệu
with app.app_context():
    db.create_all()
    # Thêm người dùng mặc định nếu chưa tồn tại
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', password=generate_password_hash('password'))
        db.session.add(admin_user)
        db.session.commit()

# Trang đăng nhập
@app.route('/')
def home():
    return render_template('login.html')

# Xử lý đăng nhập
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['username'] = username
        return redirect(url_for('main'))
    else:
        flash('Sai tên đăng nhập hoặc mật khẩu.')
        return redirect(url_for('home'))

# Trang chính sau khi đăng nhập thành công
@app.route('/main')
def main():
    if 'username' not in session:
        return redirect(url_for('home'))
    books = Book.query.all()
    return render_template('main.html', books=books)


# Tìm kiếm sách
@app.route('/search_books', methods=['POST'])
def search_books():
    keyword = request.form['keyword']
    results = Book.query.filter(
        (Book.title.ilike(f'%{keyword}%')) | (Book.author.ilike(f'%{keyword}%'))
    ).all()

    if not results:
        flash('Không tìm thấy sách phù hợp!')
    return render_template('search_results.html', books=results)


# Thêm sách
@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    if not title or not author:
        flash('Vui lòng nhập đầy đủ thông tin!')
        return redirect(url_for('main'))

    new_book = Book(title=title, author=author)
    db.session.add(new_book)
    db.session.commit()
    flash(f'Đã thêm sách: {title} của tác giả {author}')
    return redirect(url_for('main'))
# Xóa sách
@app.route('/delete_book/<int:book_id>', methods=['GET'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        flash(f'Đã xóa sách: {book.title}')
    else:
        flash('Không tìm thấy sách để xóa!')
    return redirect(url_for('main'))
# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Đã thoát khỏi ứng dụng.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
