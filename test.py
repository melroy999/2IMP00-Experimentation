import unittest

from main import event_list_invert


class TestMergeOperations(unittest.TestCase):
    def test_inversion_simple_range(self):
        result = event_list_invert([('x', float('-inf'), 0, 1, 't1'), ('x', 0, 1, 1, 't1')])
        self.assertEqual([('x', 0, 0, 0, 't1'), ('x', float('inf'), 1, 1, 't1')], result)

    def test_inversion_infinite_range(self):
        result = event_list_invert([('x', float('-inf'), 0, 1, 't1'), ('x', float('inf'), 1, 1, 't1')])
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
