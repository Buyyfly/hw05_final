from http import HTTPStatus
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            id='111',
            group=cls.group,

        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_create_post_guest(self):
        """Тестирование создания поста
        для не авторизированного пользователя
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'text_guest',
            'group': self.group.pk,
        }
        response = self.guest_client.post(reverse('posts:post_create'),
                                          data=form_data, follow=True)

        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post(self):
        """Тестирование создания поста
        для авторизированного пользователя"""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'text2',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data, follow=True)

        self.assertRedirects(response,
                             reverse(
                                 'posts:profile',
                                 kwargs={'username': self.user})
                             )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                author=self.user,
                text='text2',
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Тестирование редактирования поста"""
        uploaded = SimpleUploadedFile(
            name='small_edit.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'text1',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data, follow=True)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id})
                             )
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                author=self.user,
                text='text1',
                image='posts/small_edit.gif'
            ).exists()
        )

    def test_comment_post(self):
        """Тестролвания добавления комменатриев к постам"""
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': 'test com',
        }
        comments_count = self.post.comments.count()
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}
        ), data=form_data, follow=True)
        self.assertEqual(self.post.comments.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=self.post.id,
                text='test com',
                author=self.user
            ).exists()
        )
