from .quest_group_data import QuestGroupData

from the_west_inner.quest_requirements import (Quest_requirement_duel_quest_npc,
                                               Quest_requirement_item_to_hand_work_product_seconds,
                                               Quest_requirement_work_n_times,
                                               Quest_requirement_get_n_skill_points
)


GROUP_5 = QuestGroupData(
    group_id = 5,
    required_group_id = 4,
    quest_requirements = {
        27 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=702000,
                                                                 number = 1,
                                                                 quest_id= 27,
                                                                 solved= False
                                                                 )
             ],
        28 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=757000,
                                                                 number = 1,
                                                                 quest_id= 28,
                                                                 solved= False
                                                                 )
             ],
        29 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=746000,
                                                                 number = 1,
                                                                 quest_id= 29,
                                                                 solved= False
                                                                 )
             ],
        30 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=703000,
                                                                 number = 1,
                                                                 quest_id= 30,
                                                                 solved= False
                                                                 )
             ],
        31 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=709000,
                                                                 number = 1,
                                                                 quest_id= 31,
                                                                 solved= False
                                                                 )
             ],
        32 : [],
        180 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=706000,
                                                                 number = 1,
                                                                 quest_id= 180,
                                                                 solved= False
                                                                 )
             ]
    },
    accept_quest_requirement = {}
)