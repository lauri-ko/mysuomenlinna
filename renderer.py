import django
import os
from django.template import Template
from django.conf import settings
from django.template.loader import get_template

currentDir = os.path.dirname(os.path.realpath(__file__))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(currentDir, 'templates')]
    }
]
settings.configure(TEMPLATES=TEMPLATES)
django.setup()

def renderTimetable(context):
    timetable_template = get_template("mysuomenlinna.html")
    return timetable_template.render(context)
