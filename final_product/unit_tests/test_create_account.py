import unittest

from SavingsDatabaseApplication.program_code.create_account import *

class MyTestCase(unittest.TestCase):
    def test_generate_account_number(self):
        account_creator = AccountCreator(None, None, None, None, None)
        self.assertEqual(account_creator.generate_account_number(), "10000000")
        self.assertEqual(account_creator.generate_account_number(), "10000001")
        self.assertEqual(account_creator.generate_account_number(), "10000002")
        self.assertEqual(account_creator.generate_account_number(), "10000003")
        self.assertEqual(account_creator.generate_account_number(), "10000004")
        self.assertEqual(account_creator.generate_account_number(), "10000005")


if __name__ == '__main__':
    unittest.main()
