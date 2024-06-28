import functools
from typing import Dict

from the_west_inner.game_classes import Game_classes
from the_west_inner.bag import Bag
from the_west_inner.consumable import Consumable_handler
from the_west_inner.items import Items

from automation_scripts.stop_events.script_events import StopEvent


def open_event_boxes(target_id: int,
                     consumable_handler: Consumable_handler,
                     items: Items,
                     bag: Bag) -> None:
    """
    Opens event boxes and prints the items obtained.

    Args:
        target_id (int): The ID of the target event box.
        consumable_handler (Consumable_handler): Handler to manage consumable items.
        items (Items): Items object to fetch item details.
        bag (Bag): Bag object containing the items.
    """
    results: Dict[int, int] = consumable_handler.open_box(
        box_id=target_id,
        number=bag[target_id],
        time_sleep=0.5
    )
    
    print({
        items.find_item(item_id=x).get('name'): y for x, y in results.items()
    })


def check_event_drop_number(target_item_id: int, target_item_number: int, game_classes: Game_classes) -> None:
    """
    Checks if the number of a target item matches the specified number and stops the event if true.

    Args:
        target_item_id (int): The ID of the target item to check.
        target_item_number (int): The number of the target item to trigger the stop event.
        game_classes (Game_classes): The game classes object containing handlers and items.
    """
    stop_event = StopEvent(
        callback_func=functools.partial(open_event_boxes,
                                        target_id=target_item_id,
                                        consumable_handler=game_classes.consumable_handler,
                                        items=game_classes.items,
                                        bag=game_classes.bag)
    )
    
    if target_item_number == game_classes.bag[target_item_id]:
        stop_event.raise_exception()
