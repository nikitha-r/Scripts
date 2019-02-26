"""
ABSTRACT METHOD USAGE.

INFO: Here format_item method refers to abstract method. 
An abstract method is a method that is declared, but contains no implementation. 
Abstract classes may not be instantiated, and require subclasses to provide implementations for the abstract methods. 

APPLICATION BELOW: format_item(method implies format of the data) can be changed from api to api.
Hence, what we do is we just declare format_item as abstract method in pagination.py and use across all the api's 
with different data formatting.
Therfore we can use one method for different purposes accross diffent api's. In below api have update only two dict 
and in someother api we will update ten dict.
"""

#api.py
class GetInfoApi(MethodResource):

    class GetInfoFormatter(AbstractItemFormatter):

        def format_item(self, item):
            formatted_dict = dict(item.__dict__)
            formatted_dict.update(item.Customer.__dict__)
            formatted_dict.update(item.Customer.Purchase.__dict__)
            return formatted_dict

    
    def get(self, subject_id, page_no, per_page):
        query = db.session.query(Customer, Purchase).outerjoin(Purchase, Customer.id == Purchase.customer_id).all()
        return paginate(query, page_no, per_page, self.GetInfoFormatter())



#pagination.py
class AbstractItemFormatter(object):

    @abstractmethod
    def format_item(self, item):
        raise NotImplementedError()


class Page(object):

    def __init__(self, items, page, page_size, total):
        self.items = items
        self.previous_page = None
        self.next_page = None
        self.has_previous = page > 1
        if self.has_previous:
            self.previous_page = page - 1
        previous_items = (page - 1) * page_size
        self.has_next = previous_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(math.ceil(total / float(page_size)))


def paginate(query, page, page_size, formatter=None):
    if page <= 0:
        raise AttributeError('page needs to be >= 1')
    if page_size <= 0:
        raise AttributeError('page_size needs to be >= 1')
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    total = query.order_by(None).count()
    if formatter:
        formatted_items = []
        for item in items:
            formatted_items.append(formatter.format_item(item))
            try:
                print ArchOutSchema().load(formatter.format_item(item))
            except Exception, e:
                print "**********"+e
        return Page(formatted_items, page, page_size, total)
    else:
        return Page(items, page, page_size, total)



