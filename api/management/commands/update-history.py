from django.core.management.base import BaseCommand, CommandError
from api.utils import parse_history
from login.models import User

class Command(BaseCommand):
    help = 'Update history for users who requested it'

    def handle(self, *args, **options):
        user_id = "polarbier"
        parse_history(User.objects.get(id=user_id).secret)
