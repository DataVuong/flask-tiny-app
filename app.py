from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Model User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)  # Thêm trạng thái khóa
    role = db.Column(db.String(10), default='user')  # 'admin' hoặc 'user'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    posts = [{"title": "Bài viết 1", "content": "Nội dung bài viết 1"}]
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user:
            if user.is_blocked:
                flash('Tài khoản của bạn đã bị khóa!')
                return redirect(url_for('login'))
            if user.password == request.form['password']:
                login_user(user)
                return redirect(url_for('home'))
        flash('Sai tên đăng nhập hoặc mật khẩu!')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!')
        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Đăng ký thành công!')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Trang Admin
@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Bạn không có quyền truy cập trang này!')
        return redirect(url_for('home'))
    
    users = User.query.all()
    return render_template('admin.html', users=users)

# Khóa/Mở khóa user
@app.route('/block_user/<int:user_id>')
@login_required
def block_user(user_id):
    if current_user.role != 'admin':
        flash('Bạn không có quyền thực hiện hành động này!')
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    if user:
        user.is_blocked = not user.is_blocked  # Đảo trạng thái khóa/mở khóa
        db.session.commit()
        flash(f'User {user.username} {"bị khóa" if user.is_blocked else "đã mở khóa"}!')
    
    return redirect(url_for('admin'))

# Reset mật khẩu
@app.route('/reset_password/<int:user_id>')
@login_required
def reset_password(user_id):
    if current_user.role != 'admin':
        flash('Bạn không có quyền thực hiện hành động này!')
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    if user:
        user.password = '123456'  # Đặt lại mật khẩu mặc định
        db.session.commit()
        flash(f'Mật khẩu của {user.username} đã được đặt lại!')
    
    return redirect(url_for('admin'))

# Tạo admin mặc định
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', password='admin123', role='admin')
        db.session.add(admin_user)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
