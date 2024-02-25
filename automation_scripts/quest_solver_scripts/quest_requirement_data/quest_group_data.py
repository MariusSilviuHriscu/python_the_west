import typing

from dataclasses import dataclass

from the_west_inner.quest_requirements import Quest_requirement


QuestDataType = dict[int:list[Quest_requirement]]


@dataclass
class QuestInfo:
    
    quest_group : int
    quest_id : int
    quest_requirements : list[Quest_requirement]  

class QuestGroupData:
    def __init__(self,
                 group_id: int,
                 required_group_id: int,
                 quest_requirements: dict[int, list[Quest_requirement]],
                 accept_quest_requirement: dict[int, list[Quest_requirement]],
                 previous_quest_group: typing.Optional['QuestGroupData'] = None
                 ):
        self.group_id = group_id
        self.required_group_id = required_group_id
        self.quest_requirements = quest_requirements
        self.accept_quest_requirement = accept_quest_requirement
        self.previous_quest_group = previous_quest_group
        self._last_quest_id = None

    def add_previous_node(self, previous_node: 'QuestGroupData'):
        self.previous_quest_group = previous_node

    def get_requirements_by_quest_id(self, quest_id) -> list[Quest_requirement]:
        if quest_id not in self.quest_requirements:
            raise Exception('This quest id is not found in your saved quest data!')
        return self.quest_requirements.get(quest_id)

    def iter_requirements(self, reverse: bool = False) -> typing.Iterator[tuple[int, list[Quest_requirement]]]:
        items = reversed(self.quest_requirements.items()) if reverse else self.quest_requirements.items()
        return iter(items)
    
    def unorder(self):
        self.previous_quest_group = None
    
    
    def list_quest_info(self) -> list[QuestInfo]:
        
        list = []
        
        start = self
        
        while start is not None:
           list.extend(
               ( QuestInfo(quest_group = start.group_id,quest_id=quest_id,quest_requirements = quest_requirements ) 
                for quest_id,quest_requirements in start.iter_requirements(reverse=True) )
           )
           start = start.previous_quest_group
        list.reverse()
        return list

    @property
    def last_quest_id(self) -> int:
        if self._last_quest_id:
            return self._last_quest_id
        self._last_quest_id = list(self.quest_requirements.keys())[-1]
        return self._last_quest_id

def organize_quest_groups(
                        unordered_quest_group_data_collection : typing.Iterable[QuestGroupData],
                        target_quest_group : int
                        ) -> typing.Iterable[QuestGroupData]:
    
    unordered_dict = {x.group_id:x for x in unordered_quest_group_data_collection}
    
    
    if target_quest_group not in unordered_dict:
        
        raise ValueError('Could not find the required target quest group!')
    
    
    node = unordered_dict.get(target_quest_group)
    required_node = node.required_group_id
    
    reversed_ordered_list = [node]
    while required_node is not None:
        node = unordered_dict.get(required_node)
        reversed_ordered_list.append(node)
        
        required_node = node.required_group_id
    #twice reversed
    return reversed(reversed_ordered_list)
    
    
def assemble_quest_group_linked_list(quest_group_data_collection : typing.Iterable[QuestGroupData],target_quest_group:int = None):
    for quest_data in quest_group_data_collection:
        quest_data.unorder()
    
    if target_quest_group is not None:
        quest_group_data_collection = organize_quest_groups(unordered_quest_group_data_collection = quest_group_data_collection,
                                                            target_quest_group= target_quest_group
                                                            )
    
    previous_node = None
    for quest_group_data in quest_group_data_collection:
        
        quest_group_data.add_previous_node(previous_node = previous_node)
        
        previous_node = quest_group_data
    
    return previous_node
