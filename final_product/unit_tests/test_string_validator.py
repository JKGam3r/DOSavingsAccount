import unittest

from SavingsDatabaseApplication.program_code.string_validator import *

class MyTestCase(unittest.TestCase):
    def test_is_minimum_length(self):
        ''' Test 0, 1, and MANY for password length '''
        # Test 0
        self.assertEqual(is_minimum_length("", 0), True)
        # Test 1
        self.assertEqual(is_minimum_length("A", 0), True)
        # Test MANY
        self.assertEqual(is_minimum_length("5t", 0), True)
        self.assertEqual(is_minimum_length("Ag5%-", 0), True)
        self.assertEqual(is_minimum_length(";\tp", 0), True)

        ''' Test 0, 1, and MANY for minimum number of characters '''
        # Test 0
        self.assertEqual(is_minimum_length("MyPassword", 0), True)
        # Test 1
        self.assertEqual(is_minimum_length("MyPassword", 1), True)
        # Test MANY
        self.assertEqual(is_minimum_length("MyPassword", 5), True)
        self.assertEqual(is_minimum_length("MyPassword", 10), True)
        self.assertEqual(is_minimum_length("MyPassword", 15), False)

        ''' Test MANY for various combinations of lengths and number of characters '''
        self.assertEqual(is_minimum_length("my\nline", 3), True)
        self.assertEqual(is_minimum_length("my\nline", 20), False)
        self.assertEqual(is_minimum_length("", 5), False)
        self.assertEqual(is_minimum_length("p@s$w0rd", 3), True)
        self.assertEqual(is_minimum_length("\t", 1), True) # \ + t is just one character

    def test_is_min_num_special_chars(self):
        ''' Test 0, 1, and MANY for password length '''
        # Test 0
        self.assertEqual(is_min_num_special_chars("", 0), True)
        # Test 1
        self.assertEqual(is_min_num_special_chars("%", 0), True)
        # Test MANY
        self.assertEqual(is_min_num_special_chars("5t", 0), True)
        self.assertEqual(is_min_num_special_chars("Ag5%-", 0), True)
        self.assertEqual(is_min_num_special_chars(";\tp", 0), True)

        ''' Test 0, 1, and MANY for minimum number of special characters '''
        # Test 0
        self.assertEqual(is_min_num_special_chars("MyP@ssword", 0), True)
        # Test 1
        self.assertEqual(is_min_num_special_chars("MyP@ssword", 1), True)
        # Test MANY
        self.assertEqual(is_min_num_special_chars("MyP@ssword", 2), False)
        self.assertEqual(is_min_num_special_chars("MyP@s$word", 2), True)
        self.assertEqual(is_min_num_special_chars("MyP@s$w0rd", 15), False)

        ''' Test MANY for various combinations of lengths and number of characters '''
        self.assertEqual(is_min_num_special_chars("$p3ci@1", 2), True)
        self.assertEqual(is_min_num_special_chars("$p3ci@1", 3), False)
        self.assertEqual(is_min_num_special_chars("OnlyTimeWillTell", 1), False)
        self.assertEqual(is_min_num_special_chars("###", 3), True)

    def test_is_min_num_lower_case(self):
        ''' Test 0, 1, and MANY for password length '''
        # Test 0
        self.assertEqual(is_min_num_lower_case("", 0), True)
        # Test 1
        self.assertEqual(is_min_num_lower_case("m", 0), True)
        # Test MANY
        self.assertEqual(is_min_num_lower_case("Mm", 0), True)
        self.assertEqual(is_min_num_lower_case("Ag5%-", 0), True)
        self.assertEqual(is_min_num_lower_case(";\tp", 0), True)

        ''' Test 0, 1, and MANY for minimum number of lower case letters '''
        # Test 0
        self.assertEqual(is_min_num_lower_case("LOWERCASe", 0), True)
        # Test 1
        self.assertEqual(is_min_num_lower_case("LOWERCASe", 1), True)
        # Test MANY
        self.assertEqual(is_min_num_lower_case("LOWERCASe", 2), False)
        self.assertEqual(is_min_num_lower_case("LoWERCASe", 2), True)
        self.assertEqual(is_min_num_lower_case("LoWERCASe", 15), False)

        ''' Test MANY for various combinations of lengths and number of characters '''
        self.assertEqual(is_min_num_lower_case("wILLYwONKA", 2), True)
        self.assertEqual(is_min_num_lower_case("wILLYwONKA", 3), False)
        self.assertEqual(is_min_num_lower_case("\n", 1), False)
        self.assertEqual(is_min_num_lower_case("tHE cAT iN tHE hAT", 3), True)

    def test_is_min_num_upper_case(self):
        ''' Test 0, 1, and MANY for password length '''
        # Test 0
        self.assertEqual(is_min_num_upper_case("", 0), True)
        # Test 1
        self.assertEqual(is_min_num_upper_case("m", 0), True)
        # Test MANY
        self.assertEqual(is_min_num_upper_case("Mm", 0), True)
        self.assertEqual(is_min_num_upper_case("Ag5%-", 0), True)
        self.assertEqual(is_min_num_upper_case(";\tP", 0), True)

        ''' Test 0, 1, and MANY for minimum number of upper case letters '''
        # Test 0
        self.assertEqual(is_min_num_upper_case("uppercaseE", 0), True)
        # Test 1
        self.assertEqual(is_min_num_upper_case("uppercaseE", 1), True)
        # Test MANY
        self.assertEqual(is_min_num_upper_case("uppercaseE", 2), False)
        self.assertEqual(is_min_num_upper_case("UppercaseE", 2), True)
        self.assertEqual(is_min_num_upper_case("UppercaseE", 15), False)

        ''' Test MANY for various combinations of lengths and number of characters '''
        self.assertEqual(is_min_num_upper_case("WillyWonka", 2), True)
        self.assertEqual(is_min_num_upper_case("WillyWonka", 3), False)
        self.assertEqual(is_min_num_upper_case("\nt", 1), False)
        self.assertEqual(is_min_num_upper_case("The Cat In The Hat", 3), True)

    def test_is_min_num_digits(self):
        ''' Test 0, 1, and MANY for password length '''
        # Test 0
        self.assertEqual(is_min_num_digits("", 0), True)
        # Test 1
        self.assertEqual(is_min_num_digits("5", 0), True)
        # Test MANY
        self.assertEqual(is_min_num_digits("M5", 0), True)
        self.assertEqual(is_min_num_digits("Ag5%-", 0), True)
        self.assertEqual(is_min_num_digits(";\t8", 0), True)

        ''' Test 0, 1, and MANY for minimum number of upper case letters '''
        # Test 0
        self.assertEqual(is_min_num_digits("3", 0), True)
        # Test 1
        self.assertEqual(is_min_num_digits("3", 1), True)
        # Test MANY
        self.assertEqual(is_min_num_digits("3", 2), False)
        self.assertEqual(is_min_num_digits("3m4", 2), True)
        self.assertEqual(is_min_num_digits("3m4", 15), False)

        ''' Test MANY for various combinations of lengths and number of characters '''
        self.assertEqual(is_min_num_digits("42", 2), True)
        self.assertEqual(is_min_num_digits("42", 3), False)
        self.assertEqual(is_min_num_digits("the number one", 1), False)
        self.assertEqual(is_min_num_digits("Password12345", 3), True)

    def test_has_forbidden_chars(self):
        ''' Test 0, 1, and MANY for password length '''
        # Test 0
        self.assertEqual(has_forbidden_chars(""), False)
        self.assertEqual(has_forbidden_chars("m#5U*8sI"), False)
        # Test 1
        self.assertEqual(has_forbidden_chars("try SPACE"), True)
        # Test MANY
        self.assertEqual(has_forbidden_chars("try SPACEand/"), True)
        self.assertEqual(has_forbidden_chars("/\\"), True)
        self.assertEqual(has_forbidden_chars("   "), True)

    def test_contains_email_symbols(self):
        ''' Test 0, 1, and MANY for number of '@' and '.' symbols '''
        self.assertEqual(contains_email_symbols("email_address"), False)
        # Test 0 @'s
        self.assertEqual(contains_email_symbols(".email_address"), False)
        # Test 0 .'s
        self.assertEqual(contains_email_symbols("@email_address"), False)
        # Test 1
        self.assertEqual(contains_email_symbols("email_address@domain_name.domain"), True)
        # Test MANY
        self.assertEqual(contains_email_symbols("@_@"), False)
        self.assertEqual(contains_email_symbols("johnsmith@@@email.com"), False)
        self.assertEqual(contains_email_symbols("@tsymbol"), False)
        self.assertEqual(contains_email_symbols("@."), True)

        # Special case: switched order
        self.assertEqual(contains_email_symbols(".@"), False)

    def test_is_valid_email(self):
        ''' Email format: username@domain_name.domain '''
        # Test valid format:
        self.assertEqual(is_valid_email("username@domain_name.domain"), True)
        # Test missing username
        self.assertEqual(is_valid_email("@domain_name.domain"), False)
        # Test missing domain_name
        self.assertEqual(is_valid_email("username@.domain"), False)
        # Test missing domain
        self.assertEqual(is_valid_email("username@domain_name."), False)
        # Test other cases
        self.assertEqual(is_valid_email(""), False)
        self.assertEqual(is_valid_email("@."), False)

    def test_is_all_numbers(self):
        ''' Test 0, 1, and MANY, referring to the number of non-numeral characters '''
        # Test 0
        self.assertEqual(is_all_numbers(""), True)
        # Test 1
        self.assertEqual(is_all_numbers("r"), False)
        self.assertEqual(is_all_numbers("5r"), False)
        # Test MANY
        self.assertEqual(is_all_numbers("name"), False)
        self.assertEqual(is_all_numbers("n@m3"), False)
        self.assertEqual(is_all_numbers("12345g"), False)
        self.assertEqual(is_all_numbers("345"), True)

        ''' Test first, middle, and last, referring to the placement of a non-digit character in the string '''
        # Test first
        self.assertEqual(is_all_numbers("a123"), False)
        # Test last
        self.assertEqual(is_all_numbers("123z"), False)
        # Test middle
        self.assertEqual(is_all_numbers("1a23"), False)
        self.assertEqual(is_all_numbers("12rtu3"), False)
        self.assertEqual(is_all_numbers("1a2b4c5d3e"), False)
        self.assertEqual(is_all_numbers("74031"), True)

        ''' Test 0, 1, and MANY for the number of decimal places '''
        # Test 0
        self.assertEqual(is_all_numbers("105"), True)
        # Test 1
        self.assertEqual(is_all_numbers("10.5"), True)
        # Test MANY
        self.assertEqual(is_all_numbers("1.0.5"), False)
        self.assertEqual(is_all_numbers(".1.0.5"), False)
        self.assertEqual(is_all_numbers(".1.0.5."), False)

        # Additional Case
        self.assertEqual(is_all_numbers("."), False)

    def test_hidden_email_address(self):
        ''' Test 0, 1, 2, 3, and MANY referring to the number of characters in the email address's name '''
        # Test 0
        self.assertEqual(hidden_email_address("@email.com"), "@email.com")
        # Test 1
        self.assertEqual(hidden_email_address("a@email.com"), "*@email.com")
        # Test 2
        self.assertEqual(hidden_email_address("az@email.com"), "**@email.com")
        # Test 3
        self.assertEqual(hidden_email_address("ajz@email.com"), "a*z@email.com")
        # Test MANY
        self.assertEqual(hidden_email_address("abcd@email.com"), "a**d@email.com")
        self.assertEqual(hidden_email_address("abcdefgh@email.com"), "a******h@email.com")
        self.assertEqual(hidden_email_address("python@email.com"), "p****n@email.com")

if __name__ == '__main__':
    unittest.main()
