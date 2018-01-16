
class Parser(object):
    """
    Parser is the base class for all parser implementations.

    A Parser will parse data and send it to its subscribers. Exactly what an item of data is depends on the particular
    implementation. The subscribers are then responsible for deciding if they are interested in that particular datum
    or not.

    Parsers should be connected to their subscribing handlers by a third class, an example of how this can
    be accomplished can be found in the QCEngine.

    Classes inheriting the Parser class must implement their `run` method. For details on what is required
    by the method implementation see the `run` method documentation.

    Furthermore in order for Parsers to be identifiable it is necessary to implement a custom version
    of `__eq__` and `__hash__`, which provides a custom definition of equivalence, this can e.g. be based on
    which runfolder the parser is setup to get its data from.
    """

    def __init__(self):
        self.subscribers = []

    def add_subscribers(self, new_subscribers):
        """
        Add the following subscriber(s) to this parser.

        :param new_subscribers: a instance of a Subscriber or a list of Subscriber instances
        :returns: None
        """
        if isinstance(new_subscribers, list):
            self.subscribers = self.subscribers + new_subscribers
        else:
            self.subscribers.append(new_subscribers)

    def _send_to_subscribers(self, value):
        """
        Calling this method will send `value` to all subscribers

        :param value: The value to send to the subscribers
        :returns: None
        """
        for subscriber in self.subscribers:
            subscriber.send(value)

    def run(self):
        """
        All Parsers must implement this method. Calling it should parse the data, what ever that means in the
        particular context, and send this data to its subscribers.

        The run method should send data to the parsers subscribers using the `_send_to_subscribers` method.

        :returns: None
        """
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError
