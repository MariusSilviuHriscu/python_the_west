from .quest_group_data import QuestGroupData

from the_west_inner.quest_requirements import (Quest_requirement_item_to_hand_work_product_seconds,
                                               Quest_requirement_work_n_times,
                                               Quest_requirement_duel_quest_npc
)


GROUP_4 = QuestGroupData(
    group_id = 4,
    required_group_id = 17,
    quest_requirements = {
        23 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=743000,
                                                                  number = 1,
                                                                  quest_id = 23,
                                                                  solved = False
                                                                  )
              ],
        24 : [Quest_requirement_duel_quest_npc(quest_id=24,
                                              solved=True)
             ],
        25 : [Quest_requirement_work_n_times(work_id=11,
                                            required_work_times=4,
                                            solved = False
                                            )
             ],
        26 : [Quest_requirement_duel_quest_npc(quest_id=26,
                                              solved=True)
             ]
    },
    accept_quest_requirement = {}
)