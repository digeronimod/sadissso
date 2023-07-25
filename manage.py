#!/usr/bin/python3
import os, sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sadis.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as error:
        raise ImportError(
            "Couldn't import Django!"
        ) from error

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
