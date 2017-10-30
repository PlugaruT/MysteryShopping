from django.test import TestCase

from mystery_shopping.common.models import Tag


class TagCase(TestCase):
    def test_get_or_create_all_returns_tags(self):
        names = {'tag1', 'tag2'}
        type = 'return1'

        tags = Tag.objects.get_or_create_all(type, names)
        self.assertEqual(len(tags), 2)
        self.assertIsInstance(tags[0], Tag, "the returned object is not a Tag type")

        tag_names = {t.name for t in tags}
        self.assertSetEqual(names, tag_names)

    def test_create_multiple(self):
        names = {'tag1', 'tag2', 'tag3'}
        type = 'multiple1'

        Tag.objects.get_or_create_all(type, names)

        tags = Tag.objects.all_of_type(type).all()
        self.assertEqual(len(tags), 3)

        tag_names = {t.name for t in tags}
        self.assertSetEqual(names, tag_names)

    def test_create_existing_multiple(self):
        names1 = {'tag1', 'tag2', 'tag3'}
        names2 = {'tag2', 'tag3', 'tag4'}
        type = 'multiple2'

        Tag.objects.get_or_create_all(type, names1)
        Tag.objects.get_or_create_all(type, names2)

        tags = Tag.objects.all_of_type(type)
        self.assertEqual(len(tags), 4)

        tag_names = {t.name for t in tags}
        self.assertSetEqual(names1 | names2, tag_names)

