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

class CallbackChainer:
    def __init__(self):
        self.callback_chain = []

    def add_callback(self, callback_function: typing.Callable, *args, **kwargs):
        self.callback_chain.append((callback_function, args, kwargs))

    def chain_function(self, *args, **kwargs) -> typing.Callable:
        def chained_function():
            for callback_function, stored_args, stored_kwargs in self.callback_chain:
                # Filter kwargs based on expected arguments of the callback function
                valid_kwargs = {key: value for key, value in kwargs.items() if key in callback_function.__code__.co_varnames}

                # Combine stored args/kwargs with provided args/filtered kwargs
                combined_args = args + stored_args
                combined_kwargs = {**valid_kwargs, **stored_kwargs}

                # Call the callback function with combined args/kwargs
                callback_function(*combined_args, **combined_kwargs)

        return chained_function