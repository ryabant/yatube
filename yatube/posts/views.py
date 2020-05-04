from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.POST and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    if profile != request.user:
        return redirect("post", username=request.user.username, post_id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if request.POST and form.is_valid():
        form.save()
        return redirect("post", username=request.user.username, post_id=post_id)

    return render(request, "new_post.html", {'form': form, 'post': post})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(
        author=user).order_by("-pub_date").all()

    number_of_posts = post_list.count()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {"profile": user, 'page': page, 'paginator': paginator,
                                            'number_of_posts': number_of_posts})


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    number_of_posts = Post.objects.filter(author=profile).count()

    comments = Comment.objects.filter(post=post).all()
    form = CommentForm(request.POST)
    return render(request, "post.html", {'post': post, "profile": profile,
                                         'number_of_posts': number_of_posts, 'form': form, 'items': comments})


def add_comment(request, username, post_id):

    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if request.POST and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, "comments.html", {'form': form, 'post': post_id})


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
