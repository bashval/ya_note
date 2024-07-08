from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestNotesPage(TestCase):

    NOTES_NUMBER = 500

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Test author')
        Note.objects.bulk_create(
            Note(
                title=f'Note {index}',
                text='Note text.',
                slug=f'note_{index}',
                author=cls.author
            )
            for index in range(cls.NOTES_NUMBER)
        )

    def test_notes_count(self):
        """Check that the user has all his notes available on list page."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, self.NOTES_NUMBER)


class TestAddNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Notes Author')

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
