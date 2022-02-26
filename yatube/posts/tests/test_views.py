from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models.fields.files import ImageFieldFile
from django.shortcuts import redirect
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, Comment, Follow
from posts.forms import PostForm

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.other_group = Group.objects.create(
            title='Тестовый заголовок 2',
            description='Тестовый текст 2',
            slug='test_2-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый заголовок',
            pub_date='12.02.2022',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комментарий'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_index = reverse('posts:index')
        self.post_group = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )
        self.post_other_group = reverse(
            'posts:group_list',
            kwargs={'slug': self.other_group.slug}
        )
        self.post_profile = reverse(
            'posts:profile',
            kwargs={'username': self.user}
        )
        self.post_posts = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        )
        self.post_create = reverse('posts:post_create')
        self.post_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        )
        self.post_comment = reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id},
        )

    def test_views_correct_template(self):
        """Проверяем соответствие view-функций адресам."""
        templates_names = {
            self.post_index: 'posts/index.html',
            self.post_group: 'posts/group_list.html',
            self.post_profile: 'posts/profile.html',
            self.post_posts: 'posts/post_detail.html',
            self.post_create: 'posts/create_post.html',
            self.post_edit: 'posts/create_post.html',
        }
        for address, template in templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_views_correct_context_index(self):
        """Проверяем соответствие контекста index."""
        response = self.authorized_client.get(self.post_index)
        page_object = response.context['page_obj'][0]
        self.assertEqual(page_object, self.post)

    def test_views_correct_context_group_list(self):
        """Проверяем соответствие контекста group_list."""
        response = self.authorized_client.get(self.post_group)
        page_object = response.context['page_obj'][0]
        group_object = page_object.group
        self.assertEqual(page_object, self.post)
        self.assertEqual(group_object, self.group)

    def test_views_correct_context_profile(self):
        """Проверяем соответствие контекста profile."""
        response = self.authorized_client.get(self.post_group)
        page_object = response.context['page_obj'][0]
        author_object = page_object.author
        self.assertEqual(page_object, self.post)
        self.assertEqual(author_object, self.post.author)

    def test_views_correct_context_post_detail(self):
        """Проверяем соответствие контекста post_detail."""
        response = self.authorized_client.get(self.post_posts)
        post_object = response.context['post']
        pk_object = response.context.get('post').pk
        self.assertEqual(post_object, self.post)
        self.assertEqual(pk_object, self.post.pk)

    def test_views_correct_context_post_edit(self):
        """Проверяем соответствие контекста post_edit."""
        response = self.authorized_client.get(self.post_edit)
        form_object = response.context['form']
        post_id_object = response.context['post_id']
        is_edit_object = response.context['is_edit']
        self.assertIsInstance(form_object, PostForm)
        self.assertEqual(post_id_object, self.post.pk)
        self.assertTrue(is_edit_object)

    def test_views_correct_context_post_create(self):
        """Проверяем соответствие контекста post_create."""
        response = self.authorized_client.get(self.post_create)
        form_object = response.context['form']
        is_edit_object = response.context.get('is_edit', None)
        self.assertIsInstance(form_object, PostForm)
        self.assertIsNone(is_edit_object)

    def test_views_correct_post_creation(self):
        """Проверяем что пост не попадает на страницу другой группы."""
        response = self.authorized_client.get(self.post_other_group)
        page_object = len(response.context['page_obj'])
        self.assertEqual(page_object, 0)

    def test_views_correct_context_image(self):
        """Проверяем что картинка передается с контекстом."""
        path_dict = {
            self.post_index,
            self.post_profile,
            self.post_group,
        }
        for path in path_dict:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                obj = response.context['page_obj'][0].image
                self.assertIsInstance(obj, ImageFieldFile)
        response = self.authorized_client.get(self.post_posts)
        obj = response.context['post'].image
        self.assertIsInstance(obj, ImageFieldFile)

    def test_views_correct_context_comment(self):
        """Проверяем что комменты попадают в контекст."""
        response = self.guest_client.get(self.post_posts)
        obj = response.context['comments']
        self.assertIn(self.comment, obj)

    def test_views_no_auth_comment_creation(self):
        """
        Проверяем что неавторизованный пользователь не может комментировать.
        """
        comments_count = Comment.objects.count()
        data = {
            'text': 'Комментарий',
        }
        response = self.guest_client.post(
            self.post_comment,
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comments_count, Comment.objects.count())

    def test_views_index_cache(self):
        """Проверяем что главная страница кешируется на 20 секунд."""
        response = self.guest_client.get(self.post_index)
        page_context = response.content
        new_post = Post.objects.create(
            text='Кешированный текст',
            author=self.user,
        )
        cache.set('index_page', page_context)
        self.assertEqual(response.content, cache.get('index_page'))
        new_post.delete()
        self.assertEqual(response.content, cache.get('index_page'))
        cache.clear()
        self.assertNotEqual(response.content, cache.get('index_page'))


class PostViewsFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.follower = User.objects.create_user(username='follower')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый заголовок',
            pub_date='12.02.2022',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.post_follow = reverse(
            'posts:profile_follow',
            kwargs={'username': self.post.author}
        )
        self.post_unfollow = reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.post.author}
        )
        self.post_follow_index = reverse('posts:follow_index')
        self.redirect = f'/auth/login/?next={self.post_follow}'

    def test_views_auth_user_follow(self):
        """
        Проверяем что авторизованный пользователь
        может подписаться на автора.
        """
        response = self.follower_client.get(self.post_follow)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower,
                author=self.post.author
            ).exists()
        )

    def test_views_no_auth_user_follow(self):
        """
        Проверяем что не авторизованный пользователь
        не может подписаться на автора.
        """
        response = self.guest_client.get(self.post_follow, follow=True)
        self.assertRedirects(response, self.redirect)
        self.assertFalse(
            Follow.objects.filter(
                author=self.post.author
            ).exists()
        )

    def test_views_auth_user_unfollow(self):
        """
        Проверяем что авторизованный пользователь
        может отписаться от автора.
        """
        self.follower_client.get(self.post_follow)
        response = self.follower_client.get(self.post_unfollow)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower,
                author=self.post.author
            ).exists()
        )

    def test_views_follow_self(self):
        """Проверяем что нельзя подписаться на себя."""
        response = self.authorized_client.get(self.post_follow)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower,
                author=self.post.author
            ).exists()
        )


class PostViewsFollowIndexTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.follower = User.objects.create_user(username='follower')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый заголовок',
            pub_date='12.02.2022',
        )
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.follower,
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.post_follow = reverse(
            'posts:profile_follow',
            kwargs={'username': self.post.author}
        )
        self.post_unfollow = reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.post.author}
        )
        self.post_follow_index = reverse('posts:follow_index')

    def test_views_follow_index_page_obj(self):
        """
        Проверяем наличие поста в подписках
        подписанных пользователей.
        """
        obj = self.post
        response = self.follower_client.get(self.post_follow_index)
        page_obj = response.context['page_obj']
        context = page_obj.object_list
        self.assertIn(obj, context)

    def test_views_unfollow_index_page_obj(self):
        """
        Проверяем отсутствие поста в подписках
        не подписанных пользователей.
        """
        obj = self.post
        self.follower_client.get(self.post_unfollow)
        response = self.follower_client.get(self.post_follow_index)
        page_obj = response.context['page_obj']
        context = page_obj.object_list
        self.assertNotIn(obj, context)


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.other_user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.other_group = Group.objects.create(
            title='Тестовый заголовок 2',
            description='Тестовый текст 2',
            slug='test_2-slug'
        )
        objs = [
            Post(
                author=cls.user,
                group=cls.group,
                text=f'Тестовый заголовок {i}',
                pub_date=f'{i}.02.2022',
            )
            for i in range(10)
        ]
        cls.posts = Post.objects.bulk_create(objs=objs)
        cls.post_11 = Post.objects.create(
            author=cls.user,
            group=cls.other_group,
            text='Тестовый заголовок 10',
            pub_date='21.02.2022',
        )
        cls.post_12 = Post.objects.create(
            author=cls.other_user,
            group=cls.group,
            text='Тестовый заголовок 11',
            pub_date='22.02.2022',
        )
        cls.post_13 = Post.objects.create(
            author=cls.user,
            group=cls.other_group,
            text='Тестовый заголовок 13',
            pub_date='24.02.2022',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.other_client = Client()
        self.other_client.force_login(self.other_user)
        self.post_index = reverse('posts:index')
        self.post_group = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )
        self.post_profile = reverse(
            'posts:profile',
            kwargs={'username': self.user}
        )

    def test_views_paginator_first_page(self):
        """Проверяем работу пажинатора, первая страница."""
        paths = {
            self.post_index,
            self.post_group,
            self.post_profile,
        }
        for path in paths:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_views_paginator_second_page(self):
        """Проверяем работу пажинатора, вторая страница."""
        paths = {
            self.post_index: 3,
            self.post_group: 1,
            self.post_profile: 2,
        }
        for path, value in paths.items():
            with self.subTest(path=path):
                response = self.authorized_client.get(path, {'page': 2})
                self.assertEqual(len(response.context['page_obj']), value)
