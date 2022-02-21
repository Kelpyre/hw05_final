from typing import Union

from django.shortcuts import redirect, render, get_object_or_404
from django.db.models.query import QuerySet
from django.http import HttpRequest, Http404, HttpResponse
from django.core.paginator import Paginator, Page
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User, Comment
from .forms import PostForm, CommentForm

WORD_COUNT = 30
POST_COUNT = 10


def index(request: HttpRequest) -> HttpResponse:
    """Функция вызова главной страницы."""
    template: str = 'posts/index.html'
    title: str = 'Последние обновления на сайте'
    description: str = 'Главная страница проекта Yatube'
    posts: QuerySet = Post.objects.select_related('author')
    paginator: Paginator = Paginator(posts, POST_COUNT)
    page_number: Union[str, None] = request.GET.get('page')
    page_obj: Page = paginator.get_page(page_number)
    context: dict[str, Union[str, Page]] = {
        'title': title,
        'description': description,
        'page_obj': page_obj,
    }
    return render(
        request,
        template,
        context,
    )


def group_list(request: HttpRequest, slug: str) -> HttpResponse:
    """Функция вызова страницы группы."""
    group_name: Union[Group, Http404] = get_object_or_404(
        Group,
        slug=slug
    )
    template: str = 'posts/group_list.html'
    title: Group = group_name
    posts: QuerySet = group_name.posts.all()
    description: str = group_name.description
    paginator: Paginator = Paginator(posts, POST_COUNT)
    page_number: Union[str, None] = request.GET.get('page')
    page_obj: Page = paginator.get_page(page_number)
    context: dict[str, Union[str, Page, Group]] = {
        'title': title,
        'description': description,
        'group_name': group_name,
        'page_obj': page_obj,
    }
    return render(
        request,
        template,
        context
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Функция вызова страницы пользователя."""
    template: str = 'posts/profile.html'
    author: Union[User, Http404] = get_object_or_404(User, username=username)
    posts: QuerySet = author.posts.all()
    title: str = f'Профайл пользователя {username}'
    paginator: Paginator = Paginator(posts, POST_COUNT)
    page_number: Union[str, None] = request.GET.get('page')
    page_obj: Page = paginator.get_page(page_number)
    context: dict[str, Union[str, Page, User]] = {
        'title': title,
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Функция вызова страницы поста."""
    template: str = 'posts/post_detail.html'
    post: Union[Post, Http404] = get_object_or_404(Post, pk=post_id)
    author: str = post.author
    posts_count: int = author.posts.all().count()
    title: str = f'Пост {post.text[:WORD_COUNT]}'
    form: CommentForm = CommentForm(request.POST or None)
    comments: Comment = post.comments.all()
    context: dict[str, Union[str, Post, int, CommentForm, Comment]] = {
        'title': title,
        'post': post,
        'posts_count': posts_count,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Функция вызова страницы создания поста."""
    template: str = 'posts/create_post.html'
    title: str = 'Добавить запись'
    form: PostForm = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        added_post = form.save(commit=False)
        added_post.author = request.user
        added_post.save()
        return redirect('posts:profile', added_post.author)
    context: dict[str, Union[str, PostForm]] = {
        'form': form,
        'title': title,
    }
    return render(request, template, context)


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Функция вызова страницы редактирования поста."""
    template: str = 'posts/create_post.html'
    title: str = 'Редактировать запись'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form: PostForm = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context: dict[str, Union[str, bool, PostForm, int]] = {
        'form': form,
        'title': title,
        'is_edit': True,
        'post_id': post_id
    }
    return render(request, template, context)


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Функция добавления комментария к посту."""
    post: Post = Post.objects.get(pk=post_id)
    form: CommentForm = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
