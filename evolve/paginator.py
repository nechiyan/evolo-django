from django.core.paginator import Paginator as DjangoPaginator, EmptyPage, PageNotAnInteger

class Paginator(DjangoPaginator):
    def __init__(self, instances=[], count=10, items_per_page=10, default_page_number=1, page_number=None):
        super().__init__(instances, items_per_page)

        if page_number is None:
            page_number = default_page_number
        else:
            try:
                page_number = int(page_number)
            except (TypeError, ValueError):
                page_number = default_page_number

        try:
            instances = self.page(page_number)
        except PageNotAnInteger:
            instances = self.page(1)
        except EmptyPage:
            instances = self.page(self.num_pages)

        self.objects = instances.object_list
        self.current_page = instances.number
        self.total_pages = self.num_pages
        self.total_items = self.count
        self.first_item = instances.start_index()
        self.last_item = instances.end_index()
        self.has_next_page = instances.has_next()
        self.has_previous_page = instances.has_previous()
        self.next_page_number = instances.next_page_number() if self.has_next_page else None
        self.previous_page_number = instances.previous_page_number() if self.has_previous_page else None

    @property
    def pagination_data(self):
        return {
            "current_page": self.current_page,
            "has_next_page": self.has_next_page,
            "next_page_number": self.next_page_number,
            "has_previous_page": self.has_previous_page,
            "previous_page_number": self.previous_page_number,
            "total_pages": self.total_pages,
            "total_items": self.total_items,
            "first_item": self.first_item,
            "last_item": self.last_item,
        }
