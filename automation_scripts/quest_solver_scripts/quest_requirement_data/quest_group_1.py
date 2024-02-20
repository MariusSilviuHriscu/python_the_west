from .quest_group_data import QuestGroupData

from the_west_inner.quest_requirements import (Quest_requirement_duel_quest_npc,
                                               Quest_requirement_item_to_hand_work_product_seconds,
                                               Quest_requirement_work_n_times,
                                               Quest_requirement_get_n_skill_points
)


GROUP_1 = QuestGroupData(
    group_id = 1,
    required_group_id = None,
    quest_requirements = {
        0 : [Quest_requirement_duel_quest_npc(quest_id=0,
                                              solved=True)
             ],
        1 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=702000,
                                                                 number = 1,
                                                                 quest_id= 1,
                                                                 solved= False
                                                                 )
             ],
        2 : [Quest_requirement_work_n_times(work_id=2,
                                            required_work_times=1,
                                            solved = False
                                            )
             ],
        3 : [Quest_requirement_work_n_times(work_id=7,
                                            required_work_times=1,
                                            solved = False
                                            )
             ],
        4 : [Quest_requirement_get_n_skill_points(target_number=3,
                                                  skill_key = 'health',
                                                  solved=False
                                                  )
             ],
        5 : [],
        6 : [Quest_requirement_work_n_times(work_id=6,
                                            required_work_times=2,
                                            solved = False
                                            )
             ],
        7 : [Quest_requirement_work_n_times(work_id=93,
                                            required_work_times=1,
                                            solved = False
                                            )
             ],
        8 : [Quest_requirement_duel_quest_npc(quest_id=0,
                                              solved=True)
             ]
    },
    accept_quest_requirement = {}
)