"""
Constants for the FDS project.

This module is intended to store all the global or application-wide constants
to avoid hardcoding values ("magic strings" or "magic numbers") directly in the code.
Using constants improves readability, maintainability, and reduces the risk of errors
caused by typos in literal values.

Convention:
- All constants must be in UPPER_SNAKE_CASE.
- Group related constants together with a descriptive comment if necessary.
"""

# User Roles
# These roles define the access levels and capabilities of users within the system.
# The roles are hierarchical in terms of permissions, from the least privileged (Subscriber)
# to the most privileged (Manager).


class UserRoles:
    """
    Defines the roles for users in the system.
    """
    SUBSCRIBER = 'subscriber'
    MEMBER = 'member'
    STUDENT = 'student'
    ASSISTANT = 'assistant'
    MANAGER = 'manager'

    CHOICES = (
        (SUBSCRIBER, 'Subscriber'),
        (MEMBER, 'Member'),
        (STUDENT, 'Student'),
        (ASSISTANT, 'Assistant'),
        (MANAGER, 'Manager'),
    )

    @classmethod
    def get_choices(cls):
        """
        Returns the choices tuple for model fields.
        """
        return cls.CHOICES

    @classmethod
    def get_default(cls):
        """
        Returns the default role for a new user.
        """
        return cls.SUBSCRIBER
