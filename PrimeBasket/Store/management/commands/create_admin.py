"""Bootstrap a PrimeBasket admin panel account.

Usage:
    python manage.py create_admin --username admin --password "SomeStrongPassword123"

There is no default/hardcoded admin account anywhere in the code -- this command is the only way to
create one, and the password is always stored hashed (django.contrib.auth.hashers.make_password),
never in plain text.
"""

import getpass

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from pymongo.errors import PyMongoError

from PrimeBasket.database.mongodb import admins_collection


class Command(BaseCommand):
    help = "Create or update a PrimeBasket admin panel account."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True, help="Admin username")
        parser.add_argument(
            "--password",
            required=False,
            help="Admin password (omit to be prompted securely instead)",
        )

    def handle(self, *args, **options):
        username = options["username"].strip()
        if not username:
            raise CommandError("Username cannot be empty.")

        password = options.get("password")
        if not password:
            password = getpass.getpass("Admin password: ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                raise CommandError("Passwords did not match.")

        if len(password) < 8:
            raise CommandError("Password must be at least 8 characters.")

        try:
            admins_collection.update_one(
                {"username": username},
                {"$set": {"username": username, "password": make_password(password)}},
                upsert=True,
            )
        except PyMongoError as exc:
            raise CommandError(f"Could not reach MongoDB: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(f"Admin account '{username}' is ready."))
