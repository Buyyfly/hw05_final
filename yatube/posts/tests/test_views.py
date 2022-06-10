import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание',
        )
        for i in range(settings.POSTS_PAGE + 1):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )

        cls.templates_paginator_test = {
            'posts/index.html': reverse('posts:post_list'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': f'{cls.group.slug}'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': f'{cls.user.username}'}
            ),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:post_list'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_paginator(self):
        for template, reverse_name in self.templates_paginator_test.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.POSTS_PAGE)
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 1)

    def test_templates_pages_names_paginator_context(self):
        for template, reverse_name in self.templates_paginator_test.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn('page_obj', response.context)
                first_object = response.context['page_obj'][0]
                TaskURLTests.cs(self,
                                text=first_object.text,
                                author=first_object.author,
                                group=first_object.group)

    def test_post_detail_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertIn('post', response.context)
        first_object = response.context['post']
        self.assertNotEqual(first_object.group, 'NoGroup')
        TaskURLTests.cs(self,
                        text=first_object.text,
                        author=first_object.author,
                        group=first_object.group)

    def test_create_edit_post_context(self):
        templates_create_edit = {
            1: reverse('posts:post_create'),
            2: reverse('posts:post_edit',
                       kwargs={'post_id': f'{self.post.id}'})
        }
        for template, reverse_name in templates_create_edit.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)

                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form'
                        ).fields.get(value)
                        self.assertIsInstance(form_field, expected)

    def test_post_image_context(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_image = Post.objects.create(
            author=self.user,
            text='text2',
            group=self.group,
            image=uploaded
        )

        for template, reverse_name in self.templates_paginator_test.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn('page_obj', response.context)
                first_object = response.context['page_obj'][0]
                TaskURLTests.cs(self,
                                text=first_object.text,
                                author=first_object.author,
                                group=first_object.group,
                                image='posts/small.gif')

        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{post_image.id}'})
        )
        self.assertIn('post', response.context)
        first_object = response.context['post']
        self.assertNotEqual(first_object.group, 'NoGroup')
        TaskURLTests.cs(self,
                        text=first_object.text,
                        author=first_object.author,
                        group=first_object.group,
                        image='posts/small.gif')
    # Не могу найти инф., когда переименовываю, функцию не может найти
    # точнее когда у нее имя больше 3х символов. Прошу подсказать

    def cs(self, text, author, group, image=None):
        self.assertEqual(group, self.group)
        self.assertEqual(author, self.user)
        if image is not None:
            self.assertEqual(text, 'text2')
            self.assertEqual(image, 'posts/small.gif')
        else:
            self.assertEqual(text, 'Тестовый пост')


class TestSubs(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='Author')
        cls.user = User.objects.create_user(username='TestUser_sub')
        cls.user_not_sub = User.objects.create_user(
            username='TestUser_not_sub'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.follow_count = Post.objects.count()
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    def test_subs_auth_user(self):
        """Проверим что работает подписка проверкой кол-ва
        записей при переходе на страницу подписок
        """
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_author.username})
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            self.follow_count + 1,
            len(response.context['page_obj'])
        )

    def test_unfollow_aunt_user(self):
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_author.username})
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(self.follow_count, len(response.context['page_obj']))

    def test_not_subs_user(self):
        """Проверка что у пользователя не
        отображатся посты на которые он не подписан
        """
        authorized_client = Client()
        authorized_client.force_login(self.user_not_sub)
        response = authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(self.follow_count, len(response.context['page_obj']))
