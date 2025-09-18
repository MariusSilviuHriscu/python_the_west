import typing
from the_west_inner.duels import NpcDuelList,DuelNpcData, DuelWeaponEnum , NpcFilterFuncType



from typing import Protocol,runtime_checkable

from the_west_inner.items import Items



class IncorrectRuleOrderException(Exception):
    pass

@runtime_checkable
class DuelNpcSelectionRule(Protocol):
    items : Items
    accepts_list : bool
    key : NpcFilterFuncType
    
    def apply_func(self, npc_list : NpcDuelList | list[DuelNpcData] ) -> list[DuelNpcData] :
        if npc_list == []:
            return []
        
        if isinstance(npc_list, NpcDuelList ):
            
            if not self.accepts_list:
                raise IncorrectRuleOrderException('This exception should be first in the rule queue !')
            
            return npc_list.get_npc_by_func(key = self.key)
        
        return [x for x in npc_list if self.key(x)]
    
    def select_npc(self, npc_list : NpcDuelList | list[DuelNpcData]) -> list[DuelNpcData] :
        
        pass

class DuelNpcSelectionComposer:
    
    def __init__(self ,
                 selection_rule_list : list[DuelNpcSelectionRule]):
        
        self.selection_rule_list = selection_rule_list
        
    def select_npc(self,
                   npc_list : NpcDuelList | list[DuelNpcData]
                   ) ->list[DuelNpcData] :
        
        for rule in self.selection_rule_list:
            
            npc_list = rule.select_npc(
                npc_list = npc_list
            )
        
        return npc_list
        

class FireWeaponRule(DuelNpcSelectionRule):
    
    def __init__(self , items : Items):
        
        self.items = items
        self.accepts_list = False
        self.key = lambda x : self.items.weapon_type(item_id= x.weapon_id ) == DuelWeaponEnum.FIRE
    
    def select_npc(self , npc_list : NpcDuelList | list[DuelNpcData]) -> list[DuelNpcData] :
        
        return self.apply_func(npc_list = npc_list
                               )


class LooseShootingIntervalRule(DuelNpcSelectionRule):
    
    def __init__(self , items : Items):
        
        self.items = items
        self.accepts_list = True
        self.key = lambda x : 0 < x.shot < 600
    
    def select_npc(self , npc_list : NpcDuelList | list[DuelNpcData]) -> list[DuelNpcData] :
        
        return self.apply_func(npc_list=npc_list)

class LooseAimIntervalRule(DuelNpcSelectionRule):
    
    def __init__(self , items : Items):
        
        self.items = items
        self.accepts_list = True
        self.key = lambda x : 0 < x.aim < 600
    
    def select_npc(self , npc_list : NpcDuelList | list[DuelNpcData]) -> list[DuelNpcData] :
        
        return self.apply_func(npc_list=npc_list)


def build_npc_duel_rule_composer(
        rule_classes: typing.List[typing.Type[DuelNpcSelectionRule]],
        items: Items
    ) -> DuelNpcSelectionComposer:
    """
    Build a DuelNpcSelectionComposer from a list of rule classes and an Items instance.
    
    :param rule_classes: List of DuelNpcSelectionRule subclasses (not instances)
    :param items: Items instance to pass to each rule
    :return: DuelNpcSelectionComposer instance with all rules instantiated
    """
    instantiated_rules = [rule_class(items) for rule_class in rule_classes]
    return DuelNpcSelectionComposer(instantiated_rules)