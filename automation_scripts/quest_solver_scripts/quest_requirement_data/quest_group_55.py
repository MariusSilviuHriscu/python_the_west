from .quest_group_data import QuestGroupData

from the_west_inner.quest_requirements import (Quest_requirement_duel_quest_npc,
                                               Quest_requirement_item_to_hand_work_product_seconds,
                                               Quest_requirement_work_n_times,
                                               Quest_requirement_get_n_skill_points,
                                               Quest_requirement_work_quest_item,
                                               Quest_requirement_sell_item
)


GROUP_55 = QuestGroupData(
    group_id = 1,
    required_group_id = None,
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
                                            solved=True)
               ]
    },
    accept_quest_requirement = {}
)