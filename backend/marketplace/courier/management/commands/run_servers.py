from django.core.management.base import BaseCommand
from subprocess import Popen

class Command(BaseCommand):
    help = 'Starts Gunicorn and Daphne servers'

    def handle(self, *args, **options):
        gunicorn_process = Popen(['gunicorn', '-b', '0.0.0.0:8000', 'cfehome.wsgi:application'])
        daphne_process = Popen(['daphne', '-b', '0.0.0.0', '-p', '8001', 'cfehome.asgi:application'])

        try:
            gunicorn_process.wait()
            daphne_process.wait()
        except KeyboardInterrupt:
            gunicorn_process.terminate()
            daphne_process.terminate()