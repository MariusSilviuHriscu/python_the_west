from enum import IntEnum

from automation_scripts.product_work_cycle import CycleJobsProducts
from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.universal_callback_map import UNIVERSAL_MAPPING
from the_west_inner.game_classes import Game_classes
from the_west_inner.items import get_corresponding_work_id
from the_west_inner.work import Work, get_closest_workplace_data
from the_west_inner.work_manager import Work_manager
from automation_scripts.sleep_func_callbacks.recharge_health import recharge_health_script

from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.universal_callback_map import UNIVERSAL_MAPPING



class PremiumMedalies(IntEnum):
    CHARACTER_MEDAL = 21340000
    ENERGY_MEDAL = 21341000
    SALARY_MEDAL = 21343000


def stop_works(work_manager : Work_manager):
    
    work_manager.cancel_all_tasks()


class FarmEventProductScript():
    
    def __init__(self, drop_item : int , achievement_id : int , usable_list : list[int] , desired_product : int):
        
        self.drop_item = drop_item
        self.achievement_id = achievement_id
        self.usable_list = usable_list
        self.desired_product = desired_product
    
    def received_achievement(self, game : Game_classes) -> bool:
        
        result = game.handler.post(
            window='achievement',
            action='get_list',
            payload= {'folder' : 'seasonlines' , 'playerid' : game.player_data.id},
            use_h= True
            )
        
        return self.achievement_id in [x.get('id') for x in result.get('achievements').get('finished')]
    
    def callback_chain(self, game : Game_classes) -> CallbackChainer:
        
        
        stop_work_chain = CallbackChainer()
        stop_work_chain.add_callback(
            callback_function=stop_works,
            work_manager = game.work_manager
        )
        
        chainer = CallbackChainer(type_map_list= UNIVERSAL_MAPPING)
        
        chainer.add_callback(
            callback_function= recharge_health_script,
            #player_data = game.player_data,
            usable_list = [2116000 , 1974000 , 2117000 ],
            min_percent_hp = 20,
            #bag = game.bag,
            #handler = game.handler,
            #consumable_handler = game.consumable_handler,
            stop_event_callable= stop_work_chain.chain_function(),
        )
        
        chainer.add_default_kwargs(game_classes = game)
        
        return chainer
    
    def get_work_data(self, game : Game_classes) -> Work:
        
        job_id , x ,y = get_closest_workplace_data(
        handler= game.handler,
        job_id= get_corresponding_work_id(id_item=self.desired_product,
                                        work_list= game.work_list
                                        ),
        job_list = game.work_list,
        player_data= game.player_data)
        
        return Work(job_id= job_id,x= x, y= y, duration=15)
    
    def _work(self , game : Game_classes, usable_id : int , work : Work):
        
        cycle = CycleJobsProducts(
            handler=game.handler,
            work_manager= game.work_manager,
            consumable_handler= game.consumable_handler,
            job_data= work,
            player_data= game.player_data,
            product_id=self.drop_item ,
            game_classes= game
        )
        
        cycle.set_consumable_limit(limit_number= game.bag[usable_id])
        
        cycle.update_work_callback_chainer(
            callback_chain= self.callback_chain(game= game),
        )
        
        cycle.cycle(
            energy_consumable= usable_id,
            target_number= 100  - game.bag[self.drop_item],
            number_of_task_groups=4)
    
    def work(self , game : Game_classes):
        
        if self.received_achievement(game):
            return
        
        if game.bag[PremiumMedalies.CHARACTER_MEDAL] and not game.premium.character :

            game.consumable_handler._use_consumable(
                consumable_id= PremiumMedalies.CHARACTER_MEDAL
            )
            print('caracter')
        if game.bag[PremiumMedalies.ENERGY_MEDAL] and not game.premium.regen:

            game.consumable_handler._use_consumable(
                consumable_id= PremiumMedalies.ENERGY_MEDAL
            )
            print('energie')
            
        if game.bag[PremiumMedalies.SALARY_MEDAL] and not game.premium.money:

            game.consumable_handler._use_consumable(
                consumable_id= PremiumMedalies.SALARY_MEDAL
            )
            print('salariu')
        
        game.bag.update_inventory(handler=game.handler)
        game.player_data.update_all(handler=game.handler)
        work = self.get_work_data(game= game)
        
        for usable in self.usable_list:
            if not game.bag[usable] and usable != self.usable_list[-1]:
                continue
            self._work(
                game= game,
                usable_id= usable,
                work= work
            )
            
            if self.received_achievement(game):
                return
            
            game.bag.update_inventory(handler=game.handler)
            game.player_data.update_all(handler=game.handler)

        
        
        