class Message:
    """
    A simple, generic message object
    """
    def __init__(self, **kwargs):
        """
        Initialize object.
        :param kwargs: Any passed keyword arguments are stored as object attributes
        """
        self.__dict__ = kwargs

    def __str__(self):
        """
        String representation.
        :return: str
        """
        element_list = [': '.join([str(k), str(v)]) for k, v in self.__dict__.items()]
        return str(element_list)