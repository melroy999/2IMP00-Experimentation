import unittest

from main import event_list_invert, merge_event_lists_union


# noinspection DuplicatedCode
class TestInversionOperations(unittest.TestCase):
    def test_inversion_simple_range_1(self):
        result = event_list_invert([('x', float('-inf'), 0, 1, 't1'), ('x', 0, 1, 1, 't1')])
        self.assertEqual([('x', 0, 0, 0, 't1'), ('x', float('inf'), 1, 1, 't1')], result)

    def test_inversion_simple_range_2(self):
        result = event_list_invert([('x', float('-inf'), 0, 1, 't1'), ('x', 0, 1, 0, 't1')])
        self.assertEqual([('x', 0, 0, 1, 't1'), ('x', float('inf'), 1, 1, 't1')], result)

    def test_inversion_simple_range_3(self):
        result = event_list_invert([('x', 0, 0, 0, 't1'), ('x', float('inf'), 1, 1, 't1')])
        self.assertEqual([('x', float('-inf'), 0, 1, 't1'), ('x', 0, 1, 1, 't1')], result)

    def test_inversion_simple_range_4(self):
        result = event_list_invert([('x', 0, 0, 1, 't1'), ('x', float('inf'), 1, 1, 't1')])
        self.assertEqual([('x', float('-inf'), 0, 1, 't1'), ('x', 0, 1, 0, 't1')], result)

    def test_inversion_closed_range_1(self):
        result = event_list_invert([
            ('x', float('-inf'), 0, 1, 't1'),
            ('x', 0, 1, 1, 't1'),
            ('x', 1, 0, 1, 't1'),
            ('x', float('inf'), 1, 1, 't1')
        ])
        self.assertEqual([('x', 0, 0, 0, 't1'), ('x', 1, 1, 0, 't1')], result)

    def test_inversion_closed_range_2(self):
        result = event_list_invert([
            ('x', float('-inf'), 0, 1, 't1'),
            ('x', 0, 1, 0, 't1'),
            ('x', 1, 0, 0, 't1'),
            ('x', float('inf'), 1, 1, 't1')
        ])
        self.assertEqual([('x', 0, 0, 1, 't1'), ('x', 1, 1, 1, 't1')], result)

    def test_inversion_closed_range_3(self):
        result = event_list_invert([
            ('x', float('-inf'), 0, 1, 't1'),
            ('x', 0, 1, 0, 't1'),
            ('x', 0, 0, 0, 't1'),
            ('x', float('inf'), 1, 1, 't1')
        ])
        self.assertEqual([('x', 0, 0, 1, 't1'), ('x', 0, 1, 1, 't1')], result)

    def test_inversion_point_1(self):
        result = event_list_invert([
            ('x', 0, 0, 1, 't1'),
            ('x', 0, 1, 1, 't1'),
        ])
        self.assertEqual([
            ('x', float('-inf'), 0, 1, 't1'),
            ('x', 0, 1, 0, 't1'),
            ('x', 0, 0, 0, 't1'),
            ('x', float('inf'), 1, 1, 't1')
        ], result)

    def test_inversion_infinite_range(self):
        result = event_list_invert([('x', float('-inf'), 0, 1, 't1'), ('x', float('inf'), 1, 1, 't1')])
        self.assertEqual([], result)


# noinspection DuplicatedCode
class TestUnionOperations(unittest.TestCase):
    def test_union_simple_ranges_1(self):
        lhs = [('x', float('-inf'), 0, 1, 't1'), ('x', 0, 1, 0, 't1')]
        rhs = [('x', 0, 0, 0, 't1'), ('x', float('inf'), 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual(lhs + rhs, result)

    def test_union_simple_ranges_2(self):
        lhs = [('x', float('-inf'), 0, 1, 't1'), ('x', 0, 1, 1, 't1')]
        rhs = [('x', 0, 0, 1, 't1'), ('x', float('inf'), 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual([('x', float('-inf'), 0, 1, 't1'), ('x', float('inf'), 1, 1, 't1')], result)

    def test_union_closed_ranges_1(self):
        lhs = [('x', 0, 0, 1, 't1'), ('x', 7, 1, 0, 't1')]
        rhs = [('x', 5, 0, 0, 't1'), ('x', 10, 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual([('x', 0, 0, 1, 't1'), ('x', 10, 1, 1, 't1')], result)

    def test_union_closed_ranges_2_o_o(self):
        lhs = [('x', 0, 0, 1, 't1'), ('x', 5, 1, 0, 't1')]
        rhs = [('x', 5, 0, 0, 't1'), ('x', 10, 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual(lhs + rhs, result)

    def test_union_closed_ranges_2_i_o(self):
        lhs = [('x', 0, 0, 1, 't1'), ('x', 5, 1, 1, 't1')]
        rhs = [('x', 5, 0, 0, 't1'), ('x', 10, 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual([('x', 0, 0, 1, 't1'), ('x', 10, 1, 1, 't1')], result)

    def test_union_closed_ranges_2_o_i(self):
        lhs = [('x', 0, 0, 1, 't1'), ('x', 5, 1, 0, 't1')]
        rhs = [('x', 5, 0, 1, 't1'), ('x', 10, 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual([('x', 0, 0, 1, 't1'), ('x', 10, 1, 1, 't1')], result)

    def test_union_closed_ranges_2_i_i(self):
        lhs = [('x', 0, 0, 1, 't1'), ('x', 5, 1, 1, 't1')]
        rhs = [('x', 5, 0, 1, 't1'), ('x', 10, 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual([('x', 0, 0, 1, 't1'), ('x', 10, 1, 1, 't1')], result)

    def test_union_contained_closed_ranges_1(self):
        lhs = [('x', 0, 0, 1, 't1'), ('x', 5, 1, 1, 't1')]
        rhs = [('x', 0, 0, 1, 't1'), ('x', 2, 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual(lhs, result)

    def test_union_contained_closed_ranges_2(self):
        lhs = [('x', 0, 0, 0, 't1'), ('x', 5, 1, 1, 't1')]
        rhs = [('x', 0, 0, 1, 't1'), ('x', 2, 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual([('x', 0, 0, 1, 't1'), ('x', 5, 1, 1, 't1')], result)

    def test_union_contained_closed_ranges_3(self):
        lhs = [('x', 0, 0, 1, 't1'), ('x', 5, 1, 0, 't1')]
        rhs = [('x', 3, 0, 1, 't1'), ('x', 5, 1, 1, 't1')]
        result = merge_event_lists_union(lhs, rhs)
        self.assertEqual([('x', 0, 0, 1, 't1'), ('x', 5, 1, 1, 't1')], result)


if __name__ == '__main__':
    unittest.main()
