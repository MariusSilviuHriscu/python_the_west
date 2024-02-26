from .quest_group_data import QuestGroupData

from the_west_inner.quest_requirements import (Quest_requirement_item_to_hand_work_product_seconds,
                                               Quest_requirement_work_n_times
)


GROUP_17 = QuestGroupData(
    group_id = 17,
    required_group_id = 1,
    quest_requirements = {
        120 : [Quest_requirement_work_n_times(work_id = 1,
                                              required_work_times = 4,
                                              solved = False
                                              )
               
               ],
        121 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=704000,
                                                                   number = 1,
                                                                   quest_id = 121,
                                                                   solved = False
                                                                   )
               ],
        122 : [Quest_requirement_work_n_times(work_id = 8,
                                              required_work_times = 4,
                                              solved = False
                                              )
               
               ],
        123 : [Quest_requirement_work_n_times(work_id = 3,
                                              required_work_times = 4,
                                              solved = False
                                              )
               
               ]
    },
    accept_quest_requirement = {}
)