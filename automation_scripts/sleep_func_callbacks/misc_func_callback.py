from the_west_inner.requests_handler import requests_handler
from the_west_inner.reports import Reports_manager
from the_west_inner.player_data import Player_data
from the_west_inner.consumable import Consumable_handler
from the_west_inner.work_manager import Work_manager

from automation_scripts.marketplace_scripts.marketplace_observer import MarketplaceProductObserver


def read_report_rewards(report_manager: Reports_manager) -> None:
    """
    Reads the reports using the provided Reports_manager and prints the rewards.

    Args:
    - report_manager (Reports_manager): An instance of Reports_manager.

    Returns:
    None
    """
    report_manager._read_reports(retry_times=3)
    print(f'I have read this: {report_manager.rewards}')


def recharge_health(handler: requests_handler,
                    player_data: Player_data,
                    work_manager: Work_manager,
                    consumable_handler: Consumable_handler,
                    recharge_hp_consumable_id: int) -> None:
    """
    Recharges the player's health if it is below a certain threshold.

    Args:
    - handler (requests_handler): An instance of the requests_handler.
    - player_data (Player_data): An instance of Player_data containing player's information.
    - work_manager (Work_manager): An instance of Work_manager for managing work tasks.
    - consumable_handler (Consumable_handler): An instance of Consumable_handler for using consumables.
    - recharge_hp_consumable_id (int): The ID of the consumable used for health recharge.

    Returns:
    None
    """
    player_data.update_character_variables(handler=handler)
    
    print('Checked HP')
    if player_data.hp / player_data.hp_max < 0.25:
        work_manager.cancel_all_tasks()
        consumable_handler.use_consumable(consumable_id=recharge_hp_consumable_id)
        player_data.update_character_variables(handler=handler)


def check_marketplace_items(marketplace_observer: MarketplaceProductObserver) -> None:
    """
    Searches for items in the marketplace using the provided MarketplaceProductObserver.

    Args:
    - marketplace_observer (MarketplaceProductObserver): An instance of MarketplaceProductObserver.

    Returns:
    None
    """
    marketplace_observer.search_all()
