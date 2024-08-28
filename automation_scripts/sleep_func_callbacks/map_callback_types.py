import typing

T = typing.TypeVar('T')
M = typing.TypeVar('M')

class TypeMapping:
    """
    A class to map an original type to a dictionary of types with corresponding conversion functions.

    This class allows the user to specify an origin type and a dictionary where keys are target types
    and values are functions that convert an instance of the origin type to an instance of the target type.

    Usage:
    1. Create an instance of TypeMapping with the origin type and a dictionary of conversion functions.
    2. Use the provided methods to interact with the type mappings.

    Example:
    ```python
    def int_to_str(value: int) -> str:
        return str(value)

    def int_to_float(value: int) -> float:
        return float(value)

    type_mapping = TypeMapping(int, {str: int_to_str, float: int_to_float})
    print(type_mapping.convert(42, str))  # Outputs: "42"
    print(type_mapping.convert(42, float))  # Outputs: 42.0
    ```

    Args:
    - origin_type: The original type from which conversions will be made.
    - type_dict: A dictionary where keys are target types and values are functions that convert the origin type to the target type.

    Attributes:
    - origin_type (T): The original type.
    - type_dict (dict[typing.Type[M], typing.Callable[[T], M]]): The dictionary of target types and conversion functions.
    """
    def __init__(self, origin_type: typing.Type[T], type_dict: typing.Dict[typing.Type[M], typing.Callable[[T], M]]):
        """
        Initializes an instance of TypeMapping with the given origin type and type dictionary.

        Args:
        - origin_type: The original type from which conversions will be made.
        - type_dict: A dictionary where keys are target types and values are functions that convert the origin type to the target type.

        Returns:
        None
        """
        self.origin_type = origin_type
        self.type_dict = type_dict

    def convert(self, value: T, target_type: typing.Type[M]) -> M:
        """
        Converts a value of the origin type to the specified target type using the conversion function.

        Args:
        - value: The value to convert.
        - target_type: The target type to which the value will be converted.

        Returns:
        The converted value of the target type.

        Raises:
        - KeyError: If the target type is not found in the type dictionary.
        """
        if target_type not in self.type_dict:
            raise KeyError(f"No conversion function for target type {target_type}")
        
        conversion_function = self.type_dict[target_type]
        return conversion_function(value)


class TypeMappingList:
    """
    A class to manage a list of TypeMapping instances and provide unified type conversion functionality.

    This class allows the user to manage multiple TypeMapping instances and provides methods to check
    if a conversion is possible and to perform the conversion if possible.

    Usage:
    1. Create an instance of TypeMappingList with a list of TypeMapping instances.
    2. Use the `can_convert` method to check if a conversion is possible.
    3. Use the `convert` method to perform the conversion if possible.

    Example:
    ```python
    def int_to_str(value: int) -> str:
        return str(value)

    def int_to_float(value: int) -> float:
        return float(value)

    type_mapping_int = TypeMapping(int, {str: int_to_str, float: int_to_float})
    
    type_mapping_list = TypeMappingList([type_mapping_int])

    print(type_mapping_list.can_convert(int, str))  # Outputs: True
    print(type_mapping_list.convert(42, str))  # Outputs: "42"
    print(type_mapping_list.convert(42, float))  # Outputs: 42.0
    ```

    Args:
    - type_map_list: A list of TypeMapping instances.

    Attributes:
    - type_map_dict (dict[typing.Type[T], TypeMapping]): A dictionary of TypeMapping instances keyed by origin type.
    """
    def __init__(self, type_map_list: typing.List[TypeMapping]):
        """
        Initializes an instance of TypeMappingList with the given list of TypeMapping instances.

        Args:
        - type_map_list: A list of TypeMapping instances.

        Returns:
        None
        """
        self.type_map_dict = {type_map.origin_type: type_map for type_map in type_map_list}

    def can_convert(self, original_type: typing.Type[T], target_type: typing.Type[M]) -> bool:
        """
        Checks if a conversion from the original type to the target type is possible.

        Args:
        - original_type: The original type from which conversion is to be checked.
        - target_type: The target type to which conversion is to be checked.

        Returns:
        bool: True if the conversion is possible, False otherwise.
        """
        return original_type in self.type_map_dict and target_type in self.type_map_dict[original_type].type_dict

    def convert(self, obj: T, target_type: typing.Type[M]) -> typing.Optional[M]:
        """
        Converts an object to the specified target type if possible.

        Args:
        - obj: The object to convert.
        - target_type: The target type to which the object is to be converted.

        Returns:
        The converted object of the target type, or None if conversion is not possible.
        """
        obj_type = type(obj)

        if not self.can_convert(obj_type, target_type):
            return None

        return self.type_map_dict[obj_type].convert(obj, target_type)
    
    def extend(self, other_mapping_list: typing.Self) -> None:
        """
        Extends the current TypeMappingList with another TypeMappingList.

        Args:
        - other_mapping_list: Another TypeMappingList whose mappings will be added to the current instance.

        Returns:
        None
        """
        for origin_type, other_mapping in other_mapping_list.type_map_dict.items():
            if origin_type in self.type_map_dict:
                # Update the existing type dictionary with new mappings from other_mapping
                self.type_map_dict[origin_type].type_dict.update(other_mapping.type_dict)
            else:
                # Add the new TypeMapping to the current dictionary
                self.type_map_dict[origin_type] = other_mapping
    def __add__(self, other: typing.Self | None) -> typing.Self:
        """
        Combines the current TypeMappingList with another TypeMappingList.
    
        Args:
        - other: Another TypeMappingList to combine with the current instance.
    
        Returns:
        A new TypeMappingList instance containing the combined type mappings.
        """
        
        if other is None:
            return self.type_map_dict
        
        # Create a new list of TypeMappings starting with a copy of the current mappings
        new_mapping_list = TypeMappingList(list(self.type_map_dict.values()))
    
        # Extend the new list with the other TypeMappingList
        new_mapping_list.extend(other)
        
        return new_mapping_list