import unittest
from app.models import User, Permission


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salt_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertNotEqual(u.password_hash, u2.password_hash)

    def test_roles_and_permission(self):
        u = User(email='zens53@163.com', password='www')
        self.assertTrue(u.can(Permission.ADMINISTER))