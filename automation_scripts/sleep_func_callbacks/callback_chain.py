import typing
from automation_scripts.sleep_func_callbacks.callback_frequency import FrequencyRule,AlwaysRunRule


class CallbackChainer:
    """
    A class for chaining multiple callback functions along with their arguments and keyword arguments.

    This class allows you to build a chain of callback functions, and later create a combined function
    that executes each callback in the specified order with combined arguments.

    Usage:
    1. Create an instance of CallbackChainer.
    2. Add callback functions using the `add_callback` method.
    3. Use the `chain_function` method to obtain a combined function that executes the callback chain.

    Example:
    ```python
    chainer = CallbackChainer()
    chainer.add_callback(callback_function1, arg1, kwarg1=value1)
    chainer.add_callback(callback_function2, arg2, kwarg2=value2)

    combined_function = chainer.chain_function(additional_arg, additional_kwarg=value3)
    combined_function()
    ```

    Args:
    None

    Attributes:
    - callback_chain (list): A list to store the callbacks along with their arguments and keyword arguments.

    Methods:
    - add_callback(callback_function: Callable, *args, **kwargs): Adds a callback function to the chain.
    - chain_function(*args, **kwargs) -> Callable: Returns a combined function for executing the callback chain.
    """
    def __init__(self):
        """
        Initializes an instance of CallbackChainer with an empty callback chain.

        Returns:
        None
        """
        self.callback_chain: list[tuple[typing.Callable, tuple, dict]] = []
        self.frequency_chain : list[FrequencyRule] = []

    def add_callback(self, callback_function: typing.Callable, *args, **kwargs):
        """
        Adds a callback function along with its arguments and keyword arguments to the callback chain.

        Args:
        - callback_function: The callback function to add.
        - args: Arguments for the callback function.
        - kwargs: Keyword arguments for the callback function.

        Returns:
        None
        """
        self.callback_chain.append((callback_function, args, kwargs))
        self.frequency_chain.append(AlwaysRunRule())
    
    def set_frequency(self,rule:FrequencyRule):
        
        self.frequency_chain[-1] = rule

    def chain_function(self, *args, **kwargs) -> typing.Callable:
        """
        Returns a chained function that executes each callback in the chain with combined arguments.

        Args:
        - args: Additional arguments to be combined with the stored arguments.
        - kwargs: Additional keyword arguments to be combined with the stored keyword arguments.

        Returns:
        Callable: A function that executes the callback chain.
        """
        def chained_function():
            """
            Executes the callback chain with combined arguments.

            Returns:
            None
            """
            for callback_data , frequency_rule in zip(self.callback_chain,self.frequency_chain):
                if frequency_rule.should_run():
                    callback_function, stored_args, stored_kwargs = callback_data
                    # Filter kwargs based on expected arguments of the callback function
                    valid_kwargs = {
                        key: value for key, value in kwargs.items() if key in callback_function.__code__.co_varnames
                    }
    
                    # Combine stored args/kwargs with provided args/filtered kwargs
                    combined_args = args + stored_args
                    combined_kwargs = {**valid_kwargs, **stored_kwargs}
    
                    # Call the callback function with combined args/kwargs
                    callback_function(*combined_args, **combined_kwargs)

        return chained_function
    
    def __add__(self , other_chain : typing.Self) -> typing.Self:
        
        new_chainer = CallbackChainer()
        
        new_chainer.callback_chain = self.callback_chain + other_chain.callback_chain
        new_chainer.frequency_chain = self.frequency_chain + other_chain.frequency_chain
        
        return new_chainer