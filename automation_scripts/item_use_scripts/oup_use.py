from dataclasses import dataclass

from the_west_inner.bag import Bag
from the_west_inner.currency import Currency
from the_west_inner.consumable import Consumable_handler
from the_west_inner.game_classes import Game_classes


OUP_LETTER_VALUES : dict[int,int] = {
    
    2136000 : 25,
    2393000 : 40,
    2137000 : 50,
    2394000 : 90,
    2138000 : 100,
    2395000 : 200,
    2139000 : 250,
    2624000 : 500,
    2396000 : 550,
    2172000 : 1000,
    2397000 : 1000
}

def _get_reduced_count(letter_count : dict[int,int]) -> dict[int,int]:
    
    for letter in OUP_LETTER_VALUES.keys():
        
        if letter in letter_count:
            
            return {
                ** letter_count,
                letter : letter_count[letter] - 1
            }
    return {}
            
            
def get_letters(currency : Currency ,
                bag : Bag,
                letter_count : None | dict[int,int] = None
                )->dict[int,int]:
    
    
    oup_capacity = currency.max_oup - currency.oup
    
    if oup_capacity <= min(OUP_LETTER_VALUES.values()):
        return {}
    
    if letter_count is None:
        letter_count = {item_id : bag[item_id] for item_id in OUP_LETTER_VALUES.keys()}
    
    letter_count = {item_id : num for item_id,num in letter_count.items() if num != 0}
    
    if letter_count == {}:
        return {}
    
    total_value = sum([OUP_LETTER_VALUES[item_id] * num for item_id,num in letter_count.items()])
        
    if total_value > oup_capacity:
        
        
        
        return get_letters(currency=currency,
                            bag= bag,
                            letter_count = _get_reduced_count(letter_count=letter_count)
                            )
    
    return letter_count


def use_oup_letters(game_classes : Game_classes):
    
    currency = game_classes.currency
    bag = game_classes.bag
    consumable_handler = game_classes.consumable_handler
    
    currency.update_raw_oup(
            game_classes.handler
        )
    
    
    use_letter_dict = get_letters(
        currency= currency,
        bag= bag
    )
    start_oup = currency.oup
    
    
    for letter,num in use_letter_dict.items():
        
        current_oup = currency.oup
        
        consumable_handler._use_consumable(
            consumable_id = letter,
            number= num
        )
        
        currency.update_raw_oup(
            game_classes.handler
        )
        
        if current_oup + OUP_LETTER_VALUES.get(letter)  * num != currency.oup:
            
            raise ValueError('You have more oup than expected!')
    
    print(f'We used oup letters for a total of {currency.oup - start_oup}')