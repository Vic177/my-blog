from flask import render_template, session, redirect, url_for, flash, request, \
    current_app
from ..models import User, Role, Post, Permission, Comment, Category, Reply, \
                     Message
from .forms import EditProfileForm, PostForm, CommentForm, EditProfileAdminForm, ReplyForm, \
                   MessageForm
from flask_login import login_required, current_user
from ..decorators import admin_required
from .. import db

from . import main 

@main.route('/', methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    category=Category.query.get(form.category.data),
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    admin = User.query.filter(Role.name=="Administrator").first()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
        per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, admin=admin, pagination=pagination, form=form)
    
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)
    
@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
    
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    replyform = ReplyForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object(),
                          )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, replyform=replyform,
                           comments=comments, pagination=pagination)
    
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html', form=form)
    
@main.route('/post/<int:id>/delete')
@login_required
def post_delete(id):
    post = Post.query.get_or_404(id)
    if current_user == post.author or current_user.can(Permission.ADMINISTER):
        post.post_delete(id)
    return redirect(url_for('.index'))

@main.route('/category/<name>')
def category(name):
    category = Category.query.filter_by(name=name).first()
    posts = Post.query.filter_by(category=category).order_by(Post.timestamp.desc()).all()
    return render_template('category.html', posts=posts, category=category)


@main.route('/replyto_comment/<int:id>', methods=['POST'])
@login_required
def replyto_comment(id):
    comment = Comment.query.get_or_404(id)
    if request.method == 'POST':
        reply = Reply(body=request.form.get('body'),
                      comment=comment,
                      author=current_user._get_current_object(),
                      replyto_id=comment.id,
                      replyto_user=comment.author,
                      )
        db.session.add(reply)
        db.session.commit()
        if comment.post:
            return redirect(url_for('.post', id=comment.post.id))
        else:
            return redirect(url_for('.message'))

@main.route('/replyto_reply/<int:id>', methods=['GET', 'POST'])
@login_required
def replyto_reply(id):
    reply = Reply.query.get_or_404(id)
    if request.method == 'POST':
        replyto = Reply(body=request.form.get('body'),
                        comment=reply.comment,
                        author=current_user._get_current_object(),
                        replyto_id=reply.id,
                        replyto_user=reply.replyto_user,
                        reply_type='reply')
        db.session.add(replyto)
        if reply.comment.post:  
            return redirect(url_for('.post', id=reply.comment.post_id))
        else:
            return redirect(url_for('.message'))

@main.route('/write_post/', methods=['GET', 'POST'])
def write_post():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    category=Category.query.get(form.category.data),
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('write_post.html', form=form)


@main.route('/message_page', methods=['GET', 'POST'])
def message():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(body=form.body.data,
                          author=current_user._get_current_object()
                          )
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('.message'))
    return render_template('message_page.html', form=form, messages=messages)

@main.route('/comment-message/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_message(id):
    message = Message.query.get_or_404(id)
    if request.method == 'POST':
        comment = Comment(body=request.form.get('body'),
                          author=current_user._get_current_object(),
                          message=message)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('.message'))