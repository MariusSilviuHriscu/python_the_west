import typing

from dataclasses import dataclass

from the_west_inner.quest_requirements import Quest_requirement


QuestDataType = dict[int:list[Quest_requirement]]

@dataclass
class QuestGroupData:
    
    group_id : int
    required_group_id : int
    quest_requirements : QuestDataType
    accept_quest_requirement : QuestDataType
    
    def get_requirements_by_quest_id(self,quest_id) -> list[Quest_requirement]:
        
        if quest_id not in self.quest_requirements:
            raise Exception('This quest id is not found in your saved quest data!')
        
        return self.quest_requirements.get(quest_id)
    
    def iter_requirments(self) -> typing.Iterator[tuple[int,Quest_requirement]]:
        
        return self.quest_requirements.items()