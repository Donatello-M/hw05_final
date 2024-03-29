from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

POSTS_ON_PAGE = 10


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_num = request.GET.get("page")
    page = paginator.get_page(page_num)
    return render(
        request, "posts/index.html",
        {"page": page}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_num = request.GET.get("page")
    page = paginator.get_page(page_num)
    return render(
        request,
        "group.html",
        {"group": group, "page": page}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:index")

    return render(
        request, "posts/new_post.html",
        {"form": form, "create": True}
    )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    num = posts.count()
    followers = user.following.count()
    follows = user.follower.count()
    following = (request.user.is_authenticated
                 and Follow.objects.filter(author=user,
                                           user=request.user).exists())
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_num = request.GET.get("page")
    page = paginator.get_page(page_num)
    return render(
        request, "posts/profile.html", context={
            "author": user, "num_of_posts": num,
            "page": page, "following": following,
            "followers": followers, "follows": follows
        }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post,
        pk=post_id,
        author__username=username
    )
    if request.user.username != username:
        return redirect("posts:post_view", post_id=post_id, username=username)
    form = PostForm(
        request.POST or None, files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_view", post_id=post_id, username=username)
    return render(request, "posts/new_post.html", {"form": form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_view", post_id=post_id, username=username)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    num = post.author.posts.count()
    followers = post.author.following.count()
    follows = post.author.follower.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    return render(
        request, "posts/post.html", context={
            "author": post.author, "num_of_posts": num,
            "post": post, "comments": comments, 'form': form, "on_post": True,
            "followers": followers, "follows": follows
        }
    )


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_num = request.GET.get("page")
    page = paginator.get_page(page_num)
    return render(
        request,
        "posts/follow.html", {"page": page}
    )


@login_required
def profile_follow(request, username):
    follow_author = get_object_or_404(User, username=username)
    if request.user != follow_author:
        Follow.objects.get_or_create(author=follow_author, user=request.user)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    unfollow_author = get_object_or_404(User, username=username)
    if request.user != unfollow_author:
        unfollow = Follow.objects.filter(
            user=request.user, author=unfollow_author
        )
        unfollow.delete()
    return redirect("posts:profile", username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
