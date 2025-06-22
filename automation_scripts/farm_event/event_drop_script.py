
from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.universal_callback_map import UNIVERSAL_MAPPING
from the_west_inner.game_classes import Game_classes
from the_west_inner.login import Game_login

from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.universal_callback_map import UNIVERSAL_MAPPING
from automation_scripts.sleep_func_callbacks.misc_func_callback import check_and_update_skills

from the_west_inner.misc_scripts import collect_daily_reward

from automation_scripts.exp_gain_script.example_exp_scripts.cycle_script_v1 import CycleScriptManager
from automation_scripts.stop_events.script_exception_handler import handle_exceptions
from automation_scripts.stop_events.script_events import CompleteStopEvent
from the_west_inner.linear_quest_manager import LinearQuestManager
from automation_scripts.quest_solver_scripts.linear_quests_solver import LinearQuestSolver
from the_west_inner.player_data import ClassTypeEnum

from automation_scripts.sleep_func_callbacks.lambda_frequency_create import make_check_if_can_change_class


def select_class(game : Game_classes):
    
    can_change = make_check_if_can_change_class(game)
    
    if not can_change():
        return
    
    payload  = {
    'head': 'male_white/avatar_male_blank',
    'eyes': 'male_white/eyes/male_white_eyes_1',
    'nose': 'male_white/nose/male_white_nose_1',
    'mouth': 'male_white/mouth/male_white_mouth_1',
    'hatsb': 'male_white/hatsb/hat_1_b',
    'hair': 'male_white/hair/male_hair_bald',
    'clothing': 'male_white/clothing/male_clothing_coat',
    'beards1': 'male_white/beards1/beard_full_blonde',
    'hatsa': 'male_white/hatsa/hat_1_a',
    'pose': 'male_white/pose/transparent',
    'background': 'bg0',
    'sex': 'male',
    'color': 'white'
    }
    game.handler.post(
        window='character',
        action= 'change_avatar',
        payload= payload,
        use_h= True
    )
    
    game.player_data.select_class(
    handler = game.handler,
    class_type_enum= ClassTypeEnum.ADVENTURER
    )
    
    print("Class selected: Adventurer")




class EventDropScript() :
    
    def __init__(self  , achievement_id : int ):
        
        self.achievement_id = achievement_id
    
    def received_achievement(self, game : Game_classes) -> bool:
        
        result = game.handler.post(
            window='achievement',
            action='get_list',
            payload= {'folder' : 'seasonlines' , 'playerid' : game.player_data.id},
            use_h= True
            )
        
        return self.achievement_id in [x.get('id') for x in result.get('achievements').get('finished')]
    
    def make_checkable_achievement_func(self) -> callable:
        
        def check_achievement(game : Game_classes):
            if self.received_achievement(game):
                print(f"Achievement {self.achievement_id} received.")
                CompleteStopEvent().raise_exception()
            else:
                print(f"Achievement {self.achievement_id} not received yet.")
        
        return check_achievement
    
    @handle_exceptions
    def _work_no_usable(self , login : Game_login , setup_chainer : CallbackChainer):
        
        manager = CycleScriptManager(
            game_login = login,
            equipment_changer= None,
            setup_executable= setup_chainer
        )
        
        work_chainer = CallbackChainer(type_map_list = UNIVERSAL_MAPPING)

        work_chainer.add_callback(
            callback_function= check_and_update_skills,
            target_attribute_key='strength',
            target_skill_key='build')
        
        work_chainer.add_callback(
            callback_function= self.make_checkable_achievement_func()
        )
        
        work_chainer.add_callback(
            callback_function=select_class
        )
                

        for _ in manager.cycle(250,work_chainer):
            pass
        
    def finish_initial_missions(self, game : Game_classes):
        linear_manager = LinearQuestManager(
            handler= game.handler
        )

        linear_solver = LinearQuestSolver(
            game_classes= game,
            linear_quest_manager=linear_manager
        )

        linear_solver.solve()
        
    
    def work_no_usable(self ,game_classes : Game_classes , login : Game_login):
        
        self.finish_initial_missions(game_classes)
        
        setup_chainer = CallbackChainer(type_map_list=UNIVERSAL_MAPPING)

        setup_chainer.add_callback(
            callback_function= collect_daily_reward
        )
        setup_chainer.add_callback(
            callback_function= self.make_checkable_achievement_func()
        )
        
        self._work_no_usable(
            login= login,
            setup_chainer= setup_chainer
        )
        