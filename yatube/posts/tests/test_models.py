from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, Comment, Follow

User = get_user_model()

WORD_COUNT = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.other_user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки 15 символов',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.other_user,
            text='Тестовый комментарий для проверки 15 символов',
        )
        cls.follow = Follow.objects.create(
            user=cls.other_user,
            author=cls.user,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post_str = self.post.__str__()
        group_str = self.group.__str__()
        comment_str = self.comment.__str__()
        follow_str = self.follow.__str__()
        post_dict = {
            post_str: self.post.text[:WORD_COUNT],
            group_str: self.group.title,
            comment_str: self.comment.text[:WORD_COUNT],
            follow_str: self.follow.user.username
        }
        for key, value in post_dict.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_models_post_fields_meta(self):
        """
        Проверяем, что у модели поста
        корректно работают verbose_name и help_text.
        """
        text_verbose = self.post._meta.get_field('text').verbose_name
        text_help = self.post._meta.get_field('text').help_text
        pub_date_verbose = self.post._meta.get_field('pub_date').verbose_name
        pub_date_help = self.post._meta.get_field('pub_date').help_text
        author_verbose = self.post._meta.get_field('author').verbose_name
        author_help = self.post._meta.get_field('author').help_text
        group_verbose = self.post._meta.get_field('group').verbose_name
        group_help = self.post._meta.get_field('group').help_text
        post_dict = {
            group_verbose: 'Group',
            group_help: 'Группа, к которой будет относиться пост',
            text_verbose: 'Текст поста',
            text_help: 'Текст нового поста',
            pub_date_verbose: 'Дата публикации',
            pub_date_help: 'Дата публикации поста',
            author_verbose: 'Автор',
            author_help: 'Автор поста',
        }
        for key, value in post_dict.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_models_group_fields_meta(self):
        """
        Проверяем, что у модели группы
        корректно работают verbose_name и help_text.
        """
        title_verbose = self.group._meta.get_field('title').verbose_name
        title_help = self.group._meta.get_field('title').help_text
        slug_verbose = self.group._meta.get_field('slug').verbose_name
        slug_help = self.group._meta.get_field('slug').help_text
        description_verbose = self.group._meta.get_field(
            'description'
        ).verbose_name
        description_help = self.group._meta.get_field(
            'description'
        ).help_text
        group_dict = {
            title_verbose: 'Название',
            title_help: 'Название группы',
            slug_verbose: 'Идентификатор',
            slug_help: 'Идентификатор группы',
            description_verbose: 'Описание',
            description_help: 'Описание группы',
        }
        for key, value in group_dict.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_models_comment_fields_meta(self):
        """
        Проверяем, что у модели комментариев
        корректно работают verbose_name и help_text.
        """
        post_verbose = self.comment._meta.get_field('post').verbose_name
        post_help = self.comment._meta.get_field('post').help_text
        author_verbose = self.comment._meta.get_field('author').verbose_name
        author_help = self.comment._meta.get_field('author').help_text
        text_verbose = self.comment._meta.get_field('text').verbose_name
        text_help = self.comment._meta.get_field('text').help_text
        pub_date_verbose = self.comment._meta.get_field(
            'pub_date').verbose_name
        pub_date_help = self.comment._meta.get_field('pub_date').help_text
        post_dict = {
            post_verbose: 'Пост',
            post_help: 'Пост, к которому будет относиться комментарий',
            text_verbose: 'Текст комментария',
            text_help: 'Текст нового комментария',
            pub_date_verbose: 'Дата публикации',
            pub_date_help: 'Дата публикации комментария',
            author_verbose: 'Автор',
            author_help: 'Автор комментария',
        }
        for key, value in post_dict.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_models_follow_fields_meta(self):
        """
        Проверяем, что у модели подписок
        корректно работают verbose_name и help_text.
        """
        user_verbose = self.follow._meta.get_field('user').verbose_name
        user_help = self.follow._meta.get_field('user').help_text
        author_verbose = self.follow._meta.get_field('author').verbose_name
        author_help = self.follow._meta.get_field('author').help_text
        post_dict = {
            user_verbose: 'Пользователь',
            user_help: 'Пользователь, который подписался',
            author_verbose: 'Автор',
            author_help: 'Автор, на которого подписались',
        }
        for key, value in post_dict.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)
