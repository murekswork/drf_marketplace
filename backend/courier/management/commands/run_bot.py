from courier.telegram_backend.tg import (
    main,  # Import the async main function from your bot file
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run the bot asynchronously'

    def handle(self, *args, **options):
        main()
