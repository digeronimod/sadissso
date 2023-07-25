# Django
from django.core.management.base import BaseCommand
# SADIS
from users.models import StudentModel

class Command(BaseCommand):
    help = 'Add all calendly events from Calendly.'

    def handle(self, *args, **options):
        students = StudentModel.objects.all()

        for student in students:
            word_count = len(student.name.split())
            print(f'[{student.id}] {student.name}: {word_count}')

            if word_count < 2:
                break;

        print('Done!')
