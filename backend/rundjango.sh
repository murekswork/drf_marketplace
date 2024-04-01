#!/bin/bash

# Run Django development server in one terminal
gnome-terminal -- python manage.py runserver

# Run custom management command in another terminal
gnome-terminal -- python manage.py your_custom_command_name
