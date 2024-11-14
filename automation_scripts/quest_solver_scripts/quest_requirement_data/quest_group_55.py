from .quest_group_data import QuestGroupData

from the_west_inner.quest_requirements import (Quest_requirement_duel_quest_npc,
                                               Quest_requirement_item_to_hand_work_product_seconds,
                                               Quest_requirement_work_n_times,
                                               Quest_requirement_get_n_skill_points,
                                               Quest_requirement_work_quest_item,
                                               Quest_requirement_sell_item,
                                               Quest_requirement_execute_script,
                                               Quest_requirement_item_to_hand_work_product_hourly
)

from automation_scripts.quest_solver_scripts.quest_requirement_data.quest_group_55_annex import GROUP_55_ANNEX
from automation_scripts.quest_solver_scripts.quest_requirement_data.solve_quest_script_builder import build_solver_executable




GROUP_55 = QuestGroupData(
    group_id = 55,
    required_group_id = 5,
    quest_requirements = {
        530 : [Quest_requirement_duel_quest_npc(quest_id=530,
                                                solved=True)
               ],
        531 : [Quest_requirement_work_n_times(work_id = 94,
                                            required_work_times=4,
                                            solved = False
                                            ),
               Quest_requirement_work_quest_item(item_id = 1805000,
                                                 work_id = 94 ,
                                                 solved= False 
                                                 )
             ],
        532 : [Quest_requirement_work_n_times(work_id = 5,
                                            required_work_times=1,
                                            solved = False
                                            ),
               Quest_requirement_work_quest_item(item_id = 1806000,
                                                 work_id = 5 ,
                                                 solved= False 
                                                 )
             ],
        533 : [],
        534 : [],
        535 : [Quest_requirement_sell_item(item_id=569000,
                                            solved=False)
               ],
        536 : [],
        537 : [Quest_requirement_item_to_hand_work_product_seconds],
        538 : [Quest_requirement_execute_script(script=build_solver_executable(quest_group_data = GROUP_55_ANNEX) )
               ],
        540 : [Quest_requirement_work_n_times(work_id = 17,
                                            required_work_times = 4,
                                            solved = False
                                            )],
        541 : [Quest_requirement_work_n_times(work_id = 20,
                                            required_work_times = 4,
                                            solved = False
                                            )],
        542 : [Quest_requirement_work_n_times(work_id = 22,
                                            required_work_times = 4,
                                            solved = False
                                            )],
    },
    accept_quest_requirement = {}
)