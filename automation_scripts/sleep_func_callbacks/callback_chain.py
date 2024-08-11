import typing
import inspect

from automation_scripts.sleep_func_callbacks.callback_frequency import FrequencyRule,AlwaysRunRule
from automation_scripts.sleep_func_callbacks.map_callback_types import TypeMappingList

T = typing.TypeVar('T')

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
    def __init__(self , type_map_list : None | TypeMappingList = None):
        """
        Initializes an instance of CallbackChainer with an empty callback chain.

        Returns:
        None
        """
        self.type_map_list = type_map_list
        self.callback_chain: list[tuple[typing.Callable, tuple, dict]] = []
        self.frequency_chain : list[FrequencyRule] = []
        self.default_chainer_kwargs : dict = {}
    
    def add_default_kwargs(self , **kwargs) :
        
        self.default_chainer_kwargs = {**self.default_chainer_kwargs , **kwargs}
    
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
    
    def add_args(self , *args , **kwargs):
        
        last_callback , last_args , last_kwarg = self.callback_chain[-1]
        
        new_args = (*args , *last_args)
        new_kwargs = {**kwargs ,**last_kwarg}
        
        self.callback_chain[-1] = (last_callback, new_args ,new_kwargs)

    def get_missing_kwargs(self , func : typing.Callable , kwargs) -> dict[str , typing.Type]:
        
        sig = inspect.signature(func)
        
        missing_kword_args = {name : param.annotation for name,param in sig.parameters.items() if name not in kwargs}
        return missing_kword_args
    def create_missing_kwargs(self, missing_kwargs : dict[str , typing.Type[T]] , all_kwargs_available : dict) -> dict[str,T]:
        
        if self.type_map_list is None:
            return {}
        
        if missing_kwargs == {}:
            return {}
        
        
        
        new_dict = {}
        for arg_name, arg_value_type in missing_kwargs.items():
            
            for _ , arg_value_all in all_kwargs_available.items():
                
                if self.type_map_list.can_convert(original_type = type(arg_value_all) , 
                                                  target_type = arg_value_type
                                                  ):
                    
                    new_dict[arg_name] = self.type_map_list.convert(
                        arg_value_all ,
                        target_type = arg_value_type
                    )
        
        if len(missing_kwargs.keys()) != len(new_dict.keys()):
            missing_kwargs_keys = [x for x in missing_kwargs if x not in new_dict]
            raise ValueError(f'Could not complete all missing args ! {missing_kwargs_keys}')
        
        return new_dict
        
        
        
        
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
                    
                    all_combined_kwargs = {**kwargs , **stored_kwargs , **self.default_chainer_kwargs}
                    
                    missing_kwargs = self.get_missing_kwargs(func=callback_function , kwargs= all_combined_kwargs)
                    
                    result_kwargs = self.create_missing_kwargs(
                        missing_kwargs = missing_kwargs,
                        all_kwargs_available= all_combined_kwargs
                    )
                    
                    final_kwargs = {**combined_kwargs , **result_kwargs}
                    final_filtered_kwargs = {
                        key: value for key, value in final_kwargs.items() if key in callback_function.__code__.co_varnames
                    }
                    
                    # Call the callback function with combined args/kwargs
                    callback_function(*combined_args, **final_filtered_kwargs)

        return chained_function
    
    def __add__(self , other_chain : typing.Self) -> typing.Self:
        
        new_type_map = self.type_map_list + other_chain.type_map_list
        
        new_chainer = CallbackChainer(type_map_list = new_type_map)
        
        new_chainer.callback_chain = self.callback_chain + other_chain.callback_chain
        new_chainer.frequency_chain = self.frequency_chain + other_chain.frequency_chain
        new_chainer.default_chainer_kwargs = {**self.default_chainer_kwargs,
                                              **other_chain.default_chainer_kwargs                                     
        }
        
        return new_chainer