from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст записки.'
    NOTE_TITLE = 'Заголовок'
    NOTE_SLUG = 'note_1'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Note author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.note_form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymus_user_cant_create_note(self):
        self.client.post(self.url, data=self.note_form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        response = self.author_client.post(
            self.url, data=self.note_form_data
        )
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_user_can_create_note_without_slug(self):
        note_without_slug_form_data = {
            key: self.note_form_data[key]
            for key in self.note_form_data
            if key != 'slug'
        }
        response = self.author_client.post(
            self.url, data=note_without_slug_form_data
        )
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_user_cant_create_note_with_existing_slug(self):
        response = self.author_client.post(
            self.url, data=self.note_form_data
        )
        self.assertRedirects(response, self.success_url)
        another_note_same_slug_form_data = {
            'title': 'Some title',
            'text': 'Some text',
            'slug': self.NOTE_SLUG
        }
        response = self.author_client.post(
            self.url, data=another_note_same_slug_form_data
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.NOTE_SLUG + WARNING
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст записки.'
    NEW_NOTE_TEXT = 'Обновленный текст записки'
    NOTE_TITLE = 'Заголовок'
    NEW_NOTE_TITLE = 'Новый заголовок'
    NOTE_SLUG = 'note'
    NEW_NOTE_SLUG = 'new_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Note author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_user = User.objects.create(username='Not an author')
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.another_user_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.another_user_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
