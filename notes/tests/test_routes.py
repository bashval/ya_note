from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Dummy User')
        cls.non_author = User.objects.create(username='The other User')
        cls.note = Note.objects.create(
            title='Note title',
            text='Note text',
            slug='note_1',
            author=cls.author
        )

    def test_page_avialability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_avialability_for_existing_note(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.non_author, HTTPStatus.NOT_FOUND)
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_page_availability_for_authorised_user(self):
        self.client.force_login(self.author)
        for name in ('notes:list', 'notes:add'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymus_user(self):
        login_url = reverse('users:login')
        slug = (self.note.slug,)
        urls = (
            ('notes:add', None),
            ('notes:detail', slug),
            ('notes:edit', slug),
            ('notes:delete', slug),
            ('notes:list', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
