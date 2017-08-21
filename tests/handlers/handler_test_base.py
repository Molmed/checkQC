
import unittest


class HandlerTestBase(unittest.TestCase):

    @staticmethod
    def map_errors_and_warnings_to_class_names(errors_and_warnings):
        class_names = list(map(lambda x: type(x).__name__, errors_and_warnings))
        return class_names
