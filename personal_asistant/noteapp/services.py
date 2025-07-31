from .models import Note
from django.db import transaction
from django.forms.models import model_to_dict


def create_note_for_user(user, data):
    """
    Створює Note для заданого користувача, обробляє також ManyToMany поля.
    """
    m2m_data = {}
    normal_data = {}

    # Розділяємо звичайні поля і M2M
    for key, value in data.items():
        field = Note._meta.get_field(key)
        if field.many_to_many:
            m2m_data[key] = value
        else:
            normal_data[key] = value

    # Створюємо Note без M2M
    note = Note(**normal_data)
    note.user = user

    # Зберігаємо Note перед прив’язкою M2M
    with transaction.atomic():
        note.save()
        for key, value in m2m_data.items():
            getattr(note, key).set(value)

    return note

