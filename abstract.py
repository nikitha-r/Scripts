class ArchInfoApi(MethodResource):

    class ArchetypeFormatter(AbstractItemFormatter):

        def format_item(self, item):
            formatted_dict = dict(item.__dict__)
            formatted_dict.update(item.lifestyle.__dict__)
            formatted_dict.update(item.lifestyle.physiology.__dict__)
            return formatted_dict

    arg_map = {
        "subject_id": fields.Str(required=True),
        "page_no": fields.Int(required=True),
        "per_page": fields.Int(required=True,
                               validate=validate.Range(min=1, max=100))
    }

    @doc(description='Retrieve archetyped results for subject_id.',
         tags=['Archetype'])
    @marshal_with(ArchetypePaginationSchema(),
                  description='Archetype results for the request.',
                  code=200)
    @marshal_with(ErrorSchema(),
                  description='Invalid input is provided',
                  code=404)
    @use_kwargs(arg_map, locations=("querystring",))
    def get(self, subject_id, page_no, per_page):
        query = db.session.query(Arche) \
            .join(ArcMap)\
            .join(SubjMatching) \
            .filter(SubjMatching.subject_id == subject_id)\
            .filter(SubjMatching.best_fit == 1)\
            .order_by(ArcMap.rmse)
        return paginate(query, page_no, per_page, self.ArchetypeFormatter())


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

