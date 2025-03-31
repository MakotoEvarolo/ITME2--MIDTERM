from flask import Flask, render_template, redirect, request, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

app = Flask(__name__)

app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mak.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  

bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)

class Post(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    comments = relationship("Comment", backref="post", cascade="all, delete-orphan")

class Comment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    content: Mapped[str] = mapped_column(Text)


@app.route("/")
def home():
    posts = Post.query.all()
    return render_template("blog/home.html", posts=posts)


@app.route("/post/create", methods=["GET", "POST"])
def create_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("create_post"))

        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully.", "success")
        return redirect(url_for("home"))

    return render_template("blog/post.html")

@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("home"))
    
    return render_template("blog/view.html", post=post)

@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
def update_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("Title and content cannot be empty.", "danger")
            return redirect(url_for("update_post", post_id=post_id))

        post.title = title
        post.content = content
        db.session.commit()
        flash("Post updated successfully.", "success")
        return redirect(url_for("view_post", post_id=post_id))

    return render_template("blog/update.html", post=post)

@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("home"))

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully.", "success")

    return redirect(url_for("home"))

@app.route("/post/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("home"))
    
    content = request.form.get("content")
    if not content:
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for("view_post", post_id=post_id))

    comment = Comment(content=content, post_id=post.id)
    db.session.add(comment)
    db.session.commit()
    flash("Comment added successfully.", "success")

    return redirect(url_for("view_post", post_id=post_id))

if __name__ == "__main__":
    app.run(debug=True)
