from django.db.models import QuerySet


class TagQuerySet(QuerySet):
    def all_of_type(self, type):
        return self.filter(type=type)

    def get_or_create_all(self, type, tag_names):
        result = list()
        if tag_names:
            if not isinstance(tag_names, (list, tuple, set)):
                tag_names = (tag_names,)

            for tag_name in tag_names:
                tag, created = self.get_or_create(type=type, name=tag_name)
                result.append(tag)

        return result

