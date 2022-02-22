from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


PR_POSTS = 10


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PR_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post = Post.objects.filter(group=group)
    paginator = Paginator(post, PR_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author_1 = User.objects.get(username=username)
    posts = author_1.posts.all()
    count_posts = author_1.posts.count()
    paginator = Paginator(posts, PR_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = Follow.objects.filter(author=author_1).exists()
    context = {
        'count_posts': count_posts,
        'page_obj': page_obj,
        'author': author_1,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    image = post.image
    count_posts = author.posts.count()
    context = {
        'count_posts': count_posts,
        'post': post,
        'author': author,
        'image': image,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    username = request.user.username
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, template, {'form': form, 'username': username})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'form': form,
        'post': post,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    user = request.user
    author = user.follower.values_list('author', flat=True)
    authors = User.objects.filter(id__in=author)
    post = Post.objects.filter(author__following__user=user)
    template = 'posts/follow.html'
    paginator = Paginator(post, PR_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'authors': authors,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author_1 = get_object_or_404(User, username=username)
    if author_1 != request.user:
        Follow.objects.get_or_create(author=author_1, user=request.user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author_1 = get_object_or_404(User, username=username)
    author = Follow.objects.filter(author=author_1, user=request.user)
    author.delete()
    return redirect('posts:profile', username=username)
