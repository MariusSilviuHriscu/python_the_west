
from the_west_inner.current_events.current_event_handler import EventHandler
from the_west_inner.current_events.current_event_data import (CurrentEventData,
                                                              EventCurrency,
                                                              CurrencyData,
                                                              CostData,
                                                              EventStageData
)



def load_current_event(event_handler : EventHandler , wof_id : int) -> dict[str , str|dict]:
    return event_handler.init_event(wof_id = wof_id)


def build_cost_data(response:dict[str,str|dict]) -> CostData:
    cost_data = response.get('mode').get('cost')
    return CostData(
        bribe_cost = cost_data.get('bribe'),
        main_cost=cost_data.get('main'),
        reset_cost=cost_data.get('reset')
    )

def build_currency_data(response :dict[str , str|dict]) -> CurrencyData:
    currencies_data = response.get('mode').get('currencies')
    return CurrencyData(
        cost_data= build_cost_data(response = response),
        bribe_list = currencies_data.get('bribe',[]),
        reset_list = currencies_data.get('reset',[]),
        main_list = currencies_data.get('main',[])
    )

def build_event_stage_data(response : dict[str,str|dict]) -> EventStageData:
    return EventStageData(
        gamble_prizes = response.get('prizes').get('gamblePrizes')
    )

def build_current_event_data(
                            response : dict[str, str|dict] ,
                            event_currency_ammount : EventCurrency,
                            wof_id : int) -> CurrentEventData:
    
    
    return CurrentEventData(
        event_name = response.get('name'),
        event_currency_ammount = event_currency_ammount,
        event_wof= wof_id,
        enhancements = response.get('prizes').get('enhancements'),
        can_halve_time = response.get('mode').get('canHalveTime'),
        currency_data = build_currency_data(response = response),
        event_stage_data = build_event_stage_data(response=response)
    )