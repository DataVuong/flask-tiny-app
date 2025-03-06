from flask import Flask, render_template

app = Flask(__name__)

# Danh sách bài blog (giả lập)
blogs = [
    {"title": "Bài viết đầu tiên", "content": "Nội dung bài viết 1"},
    {"title": "Bài viết thứ hai", "content": "Nội dung bài viết 2"}
]

# Danh sách việc cần làm (giả lập)
todos = ["Học Flask", "Viết code", "Push lên GitHub"]

@app.route('/')
def home():
    return render_template('index.html', blogs=blogs)

@app.route('/todo')
def todo():
    return render_template('todo.html', todos=todos)

if __name__ == '__main__':
    app.run(debug=True)