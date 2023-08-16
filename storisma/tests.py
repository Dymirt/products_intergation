from django.test import TestCase
from wordpress.models import group_variations_attributes_by_id


class GroupWordPressAttributesTest(TestCase):
    def test_group_wordpress_attributes(self):
        variations = [
            {
                "attributes": [
                    {"id": 1, "option": "Option A"},
                    {"id": 2, "option": "Option X"},
                ]
            },
            {
                "attributes": [
                    {"id": 1, "option": "Option B"},
                    {"id": 3, "option": "Option Y"},
                ]
            },
            {
                "attributes": [
                    {"id": 1, "option": "Option B"},
                    {"id": 3, "option": "Option Y"},
                ]
            },
        ]

        result = group_variations_attributes_by_id(variations)

        expected_result = [
            {"attribute_id": 1, "options": {"Option A", "Option B"}},
            {"attribute_id": 2, "options": {"Option X"}},
            {"attribute_id": 3, "options": {"Option Y"}},
        ]

        self.assertEqual(result, expected_result)