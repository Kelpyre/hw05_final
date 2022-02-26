from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
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
        self.post_posts = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        )
        self.post_create = reverse('posts:post_create')
        self.post_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        )

    def test_urls_auth_exists(self):
        """Проверяем существование страниц для авторизованного пользователя"""
        paths = {
            self.post_index,
            self.post_group,
            self.post_profile,
            self.post_posts,
            self.post_create,
            self.post_edit,
        }
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(
                    self.authorized_client.get(path).status_code,
                    200
                )

    def test_urls_non_auth_exists(self):
        """
        Проверяем существование страниц для неавторизованного пользователя
        """
        paths = {
            self.post_index,
            self.post_group,
            self.post_profile,
            self.post_posts,
        }
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(
                    self.guest_client.get(path).status_code,
                    200
                )

    def test_urls_non_auth_redirect(self):
        """Проверяем редиректы неавторизованного пользователя"""
        path_edit = self.post_edit
        path_create = '/create/'
        responce_edit = f'/auth/login/?next={self.post_edit}'
        responce_create = f'/auth/login/?next={self.post_create}'
        paths = {
            path_create: responce_create,
            path_edit: responce_edit,
        }
        for path, responce in paths.items():
            with self.subTest(path=path):
                self.assertRedirects(
                    self.guest_client.get(path, follow=True),
                    responce
                )

    def test_urls_other_user_redirect(self):
        """Проверяем редирект изменения поста для не автора"""
        path = self.post_edit
        request = self.other_client.get(path, follow=True)
        response = self.post_posts
        self.assertRedirects(
            request,
            response,
        )

    def test_urls_no_page(self):
        """Проверяем недоступность несуществующей страницы."""
        clients = {
            self.guest_client,
            self.authorized_client,
            self.other_client,
        }
        for client in clients:
            with self.subTest(client=client):
                response = client.get('/unexisting_page/')
                self.assertEqual(
                    response.status_code,
                    404,
                )
                self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_correct_template(self):
        """Проверяем соответствие темплейтов адресам."""
        templates_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
