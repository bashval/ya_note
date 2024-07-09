import pytest
from django.urls import reverse

from notes.forms import NoteForm


def test_note_in_list_for_author(note, author_client):
    url = reverse('notes:list')
    response = author_client.get(url)
    object_list = response.context['object_list']
    assert note in object_list


def test_note_not_in_list_for_another_user(note, not_author_client):
    url = reverse('notes:list')
    response = not_author_client.get(url)
    object_list = response.context['object_list']
    assert note not in object_list


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:add', None)
    )
)
def test_authorized_user_has_form(name, args, author_client):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], NoteForm)
