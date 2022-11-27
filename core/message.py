class Message:
    """
    A simple message object taking keyword arguments and saving them as message attributes.
    """
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def __str__(self):
        element_list = [': '.join([str(k), str(v)]) for k, v in self.__dict__.items()]
        return str(element_list)
