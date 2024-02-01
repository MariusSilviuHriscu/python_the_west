import typing

class CallbackChainer:
    def __init__(self):
        self.callback_chain = []

    def add_callback(self, callback_function: typing.Callable, *args, **kwargs):
        self.callback_chain.append((callback_function, args, kwargs))

    def chain_function(self) -> typing.Callable:
        def chained_function():
            for callback_function, args, kwargs in self.callback_chain:
                callback_function(*args, **kwargs)

        return chained_function