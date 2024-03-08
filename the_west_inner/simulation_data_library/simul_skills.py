import math
import typing
from enum import Enum, auto

class CharacterSkillsEnum(Enum):
    # Attributes
    STRENGTH = auto()
    MOBILITY = auto()
    DEXTERITY = auto()
    CHARISMA = auto()

    # Strength-based skills
    BUILD = auto()
    PUNCH = auto()
    TOUGH = auto()
    ENDURANCE = auto()
    HEALTH = auto()

    # Mobility-based skills
    RIDE = auto()
    REFLEX = auto()
    DODGE = auto()
    HIDE = auto()
    SWIM = auto()

    # Dexterity-based skills
    AIM = auto()
    SHOT = auto()
    PITFALL = auto()
    FINGER_DEXTERITY = auto()
    REPAIR = auto()

    # Charisma-based skills
    LEADERSHIP = auto()
    TACTIC = auto()
    TRADE = auto()
    ANIMAL = auto()
    APPEARANCE = auto()

    def __str__(self):
        return self.name.lower()
    @classmethod
    def get_all_skills(cls):
        attributes = {'STRENGTH', 'MOBILITY', 'DEXTERITY', 'CHARISMA'}
        return [skill.name.lower() for skill in cls if skill.name not in attributes]
    @classmethod
    def get_all_attributes(cls):
        attributes = {'STRENGTH', 'MOBILITY', 'DEXTERITY', 'CHARISMA'}
        return [attribute.name.lower() for attribute in cls if attribute.name in attributes]
class Attributes():
    def __init__(self,strength:int,mobility:int,dexterity:int,charisma:int):
        self.strength = strength
        self.mobility = mobility
        self.dexterity = dexterity
        self.charisma = charisma
    def __getitem__(self,number:int) -> int:
        if number == 1 or number == "strength":
            return self.strength
        elif number == 2    or number == "mobility" or number == "flexibility":
            return self.mobility
        elif number == 3   or number == "dexterity":
            return self.dexterity
        elif number == 4 or number == "charisma":
            return self.charisma
        else:
            return "Error"
    def __setitem__(self,number:typing.Union[str,int],value:int):
        if number == 1 or number == "strength":
            self.strength = value
        elif number == 2    or number == "mobility" or number == "flexibility":
            self.mobility = value
        elif number == 3   or number == "dexterity":
            self.dexterity = value
        elif number == 4 or number == "charisma":
            self.charisma = value
        else:
            return "Error"
    def __str__(self) -> str:
        return (
            f'strength: {self.strength} '
            f'mobility: {self.mobility} '
            f'dexterity: {self.dexterity} '
            f'charisma: {self.charisma} '
        )
    def __add__(self,other:typing.Self) -> typing.Self:
        return Attributes(
                    self.strength + other.strength,
                    self.mobility + other.mobility,
                    self.dexterity + other.dexterity,
                    self.charisma + other.charisma
                    )
    def __mul__(self,other:int) -> typing.Self:
        return Attributes(
                    self.strength * other,
                    self.mobility * other,
                    self.dexterity * other,
                    self.charisma * other
                    )
    def __rmul__(self,other:int) -> typing.Self:
        return Attributes(
                    self.strength * other,
                    self.mobility * other,
                    self.dexterity * other,
                    self.charisma * other
                    )
    def __iter__(self):
        self.numarator = 1
        return self
    def __next__(self):
        if self.numarator <= 4:
            returnabil = self[self.numarator]
            self.numarator += 1
            return returnabil
        else:
            raise StopIteration
    def __round__(self,n:str) -> typing.Self:
        if n == "ceil":
            return Attributes(
                    math.ceil(self.strength),
                    math.ceil(self.mobility),
                    math.ceil(self.dexterity),
                    math.ceil(self.charisma)
                    )
        elif n == "floor":
            return Attributes(
                    math.floor(self.strength),
                    math.floor(self.mobility),
                    math.floor(self.dexterity),
                    math.floor(self.charisma)
                    )
        else:
            return Attributes(
                    round(self.strength),
                    round(self.mobility),
                    round(self.dexterity),
                    round(self.charisma)
                    )
    @staticmethod
    def null_attributes() -> typing.Self:
        return Attributes(0,0,0,0)
class Strength_based_skills():
    def __init__(self,build:int ,punch:int ,tough:int ,endurance:int ,health:int ):
        self.build = build
        self.punch = punch
        self.tough = tough
        self.endurance = endurance
        self.health = health
    def __getitem__(self,number) -> int:
        if number == 1 or number == "build":
            return self.build
        elif number == 2 or number == "punch":
            return self.punch
        elif number == 3 or number == "tough":
            return self.tough
        elif number == 4 or number == "endurance":
            return self.endurance
        elif number == 5 or number == "health":
            return self.health
        else:
            return "Error"
    def __setitem__(self,number:typing.Union[str,int],value:int):
        if number == 1 or number == "build":
            self.build = value
        elif number == 2 or number == "punch":
            self.punch = value
        elif number == 3 or number == "tough":
            self.tough = value
        elif number == 4 or number == "endurance":
            self.endurance = value
        elif number == 5 or number == "health":
            self.health = value
        else:
            return "Error"
    def __str__(self):
        return (
            f'build: {self.build} ' 
            f'punch: {self.punch} ' 
            f'tough: {self.tough} ' 
            f'endurance: {self.endurance} ' 
            f'health: {self.health} '
        )
    def __add__(self,other: typing.Self) -> typing.Self:
        return Strength_based_skills(
                        self.build + other.build,
                        self.punch + other.punch,
                        self.tough + other.tough,
                        self.endurance + other.endurance,
                        self.health + other.health
                        )
    def __mul__(self,other:int) -> typing.Self:
        return Strength_based_skills(
                        self.build * other,
                        self.punch * other,
                        self.tough * other,
                        self.endurance * other,
                        self.health * other
                        )
    def __rmul__(self,other:int) -> typing.Self:
        return Strength_based_skills(
                        self.build * other,
                        self.punch * other,
                        self.tough * other,
                        self.endurance * other,
                        self.health * other
                        )
    def __iter__(self):
        self.numarator = 1
        return self
    def __next__(self):
        if self.numarator <= 5:
            returnabil = self[self.numarator]
            self.numarator += 1
            return returnabil
        else:
            raise StopIteration
    def __round__(self,n:str) -> typing.Self:
        if n == "ceil":
            return Strength_based_skills(
                        math.ceil(self.build),
                        math.ceil(self.punch),
                        math.ceil(self.tough),
                        math.ceil(self.endurance),
                        math.ceil(self.health)
                        )
        elif n == "floor":
            return Strength_based_skills(
                        math.floor(self.build),
                        math.floor(self.punch),
                        math.floor(self.tough),
                        math.floor(self.endurance),
                        math.floor(self.health)
                        )
        else:
            return Strength_based_skills(
                        round(self.build),
                        round(self.punch),
                        round(self.tough),
                        round(self.endurance),
                        round(self.health)
                        )
    @staticmethod
    def null_skills() -> typing.Self:
        return Strength_based_skills(0,0,0,0,0)
class Mobility_based_skills():
    def __init__(self,ride:int ,reflex:int ,dodge:int ,hide:int ,swim:int ):
        self.ride = ride
        self.reflex = reflex
        self.dodge = dodge
        self.hide = hide
        self.swim = swim
    def __getitem__(self,number:int) -> int:
        if number == 1 or number == "ride":
            return self.ride
        elif number == 2 or number == "reflex":
            return self.reflex
        elif number == 3 or number == "dodge":
            return self.dodge
        elif number == 4 or number == "hide":
            return self.hide
        elif number == 5 or number == "swim":
            return self.swim
        else:
            return "Error"
    def __setitem__(self,number:typing.Union[str,int],value:int):
        if number == 1 or number == "ride":
            self.ride = value
        elif number == 2 or number == "reflex":
            self.reflex = value
        elif number == 3 or number == "dodge":
            self.dodge = value
        elif number == 4 or number == "hide":
            self.hide = value
        elif number == 5 or number == "swim":
            self.swim = value
        else:
            return "Error"
    def __str__(self):
        return (
            f'ride: {self.ride},  ' 
            f'reflex: {self.reflex},  ' 
            f'dodge: {self.dodge},  ' 
            f'hide: {self.hide},  ' 
            f'swim: {self.swim} ' 
            )
    def __add__(self,other:typing.Self) -> typing.Self:
        return Mobility_based_skills(
                    self.ride + other.ride,
                    self.reflex + other.reflex,
                    self.dodge + other.dodge,
                    self.hide + other.hide,
                    self.swim + other.swim
                    )
    def __mul__(self,other:int) -> typing.Self:
        return Mobility_based_skills(
                    self.ride * other,
                    self.reflex * other,
                    self.dodge * other,
                    self.hide * other,
                    self.swim * other
                    )
    def __rmul__(self,other:int) -> typing.Self:
        return Mobility_based_skills(
                    self.ride * other,
                    self.reflex * other,
                    self.dodge * other,
                    self.hide * other,
                    self.swim * other
                    )
    def __iter__(self):
        self.numarator = 1
        return self
    def __next__(self):
        if self.numarator <= 5:
            returnabil = self[self.numarator]
            self.numarator += 1
            return returnabil
        else:
            raise StopIteration
    def __round__(self,n:str) -> typing.Self:
        if n == "ceil":
            return Mobility_based_skills(
                        math.ceil(self.ride),
                        math.ceil(self.reflex),
                        math.ceil(self.dodge),
                        math.ceil(self.hide),
                        math.ceil(self.swim)
                        )
        elif n == "floor":
            return Mobility_based_skills(
                        math.floor(self.ride),
                        math.floor(self.reflex),
                        math.floor(self.dodge),
                        math.floor(self.hide),
                        math.floor(self.swim)
                        )
        else:
            return Mobility_based_skills(
                        round(self.ride),
                        round(self.reflex),
                        round(self.dodge),
                        round(self.hide),
                        round(self.swim)
                        )
    @staticmethod
    def null_skills() -> typing.Self:
        return Mobility_based_skills(0,0,0,0,0)
class Dexterity_based_skills():
    def __init__(self,aim:int ,shot:int ,pitfall:int ,finger_dexterity:int ,repair:int ):
        self.aim = aim
        self.shot = shot
        self.pitfall = pitfall
        self.finger_dexterity = finger_dexterity
        self.repair = repair
    def __getitem__(self,number:int) -> int:
        if number == 1 or number == "aim":
            return self.aim
        elif number == 2    or number == "shot":
            return self.shot
        elif number == 3   or number == "pitfall":
            return self.pitfall
        elif number == 4 or number == "finger_dexterity":
            return self.finger_dexterity
        elif number == 5 or number == "repair":
            return self.repair
        else:
            return "Error"
    def __setitem__(self,number:int,value:int):
        if number == 1 or number == "aim":
            self.aim = value
        elif number == 2 or number == "shot":
            self.shot = value
        elif number == 3 or number == "pitfall":
            self.pitfall = value
        elif number == 4 or number == "finger_dexterity":
            self.finger_dexterity = value
        elif number == 5 or number == "repair":
            self.repair = value
        else:
            return "Error"
    def __str__(self):
        return (
                f'aim: {self.aim},  '
                f'shot: {self.shot},  '
                f'pitfall: {self.pitfall},  '
                f'finger_dexterity: {self.finger_dexterity},  '
                f'repair: {self.repair} '
                )
    def __add__(self,other:typing.Self) -> typing.Self:
        return Dexterity_based_skills(
                    self.aim + other.aim,
                    self.shot + other.shot,
                    self.pitfall + other.pitfall,
                    self.finger_dexterity + other.finger_dexterity,
                    self.repair + other.repair
                    )
    def __mul__(self,other:int) -> typing.Self:
        return Dexterity_based_skills(
                    self.aim * other,
                    self.shot * other,
                    self.pitfall * other,
                    self.finger_dexterity * other,
                    self.repair * other
                    )
    def __rmul__(self,other:int) -> typing.Self:
        return Dexterity_based_skills(
                    self.aim * other,
                    self.shot * other,
                    self.pitfall * other,
                    self.finger_dexterity * other,
                    self.repair * other
                    )
    def __iter__(self):
        self.numarator = 1
        return self
    def __next__(self):
        if self.numarator <= 5:
            returnabil = self[self.numarator]
            self.numarator += 1
            return returnabil
        else:
            raise StopIteration
    def __round__(self,n:str) -> typing.Self:
        if n == "ceil":
            return Dexterity_based_skills(
                    math.ceil(self.aim),
                    math.ceil(self.shot),
                    math.ceil(self.pitfall),
                    math.ceil(self.finger_dexterity),
                    math.ceil(self.repair)
                    )
        elif n == "floor":
            return Dexterity_based_skills(
                    math.floor(self.aim),
                    math.floor(self.shot),
                    math.floor(self.pitfall),
                    math.floor(self.finger_dexterity),
                    math.floor(self.repair)
                    )
        else:
            return Dexterity_based_skills(
                    round(self.aim),
                    round(self.shot),
                    round(self.pitfall),
                    round(self.finger_dexterity),
                    round(self.repair)
                    )
    @staticmethod
    def null_skills() -> typing.Self:
        return Dexterity_based_skills(0,0,0,0,0)
class Charisma_based_skills():
    def __init__(self,leadership:int,tactic:int,trade:int,animal:int,appearance:int):
        self.leadership = leadership
        self.tactic = tactic
        self.trade = trade
        self.animal = animal
        self.appearance = appearance
    def __getitem__(self,number:int) -> int:
        if number == 1 or number == "leadership":
            return self.leadership
        elif number == 2 or number == "tactic":
            return self.tactic
        elif number == 3 or number == "trade":
            return self.trade
        elif number == 4 or number == "animal":
            return self.animal
        elif number == 5 or number == "appearance":
            return self.appearance
        else:
            return "Error"
    def __setitem__(self,number:int,value:int):
        if number == 1 or number == "leadership":
            self.leadership = value
        elif number == 2 or number == "tactic":
            self.tactic = value
        elif number == 3 or number == "trade":
            self.trade = value
        elif number == 4 or number == "animal":
            self.animal = value
        elif number == 5 or number == "appearance":
            self.appearance = value
        else:
            return "Error"
    def __str__(self):
        return (
                f'leadership: {self.leadership},'
                f' tactic: {self.tactic}, '
                f' trade: {self.trade},  '
                f' animal: {self.animal}, '
                f' appearance: {self.appearance}'
                )
    def __add__(self,other:typing.Self) -> typing.Self:
        return Charisma_based_skills(
                    self.leadership + other.leadership,
                    self.tactic + other.tactic,
                    self.trade + other.trade,
                    self.animal + other.animal,
                    self.appearance + other.appearance
                    )
    def __mul__(self,other:int) -> typing.Self:
        return Charisma_based_skills(
                    self.leadership * other,
                    self.tactic * other,
                    self.trade * other,
                    self.animal * other,
                    self.appearance * other
                    )
    def __rmul__(self,other:int) -> typing.Self:
        return Charisma_based_skills(
                    self.leadership * other,
                    self.tactic * other,
                    self.trade * other,
                    self.animal * other,
                    self.appearance * other
                    )
    def __iter__(self):
        self.numarator = 1
        return self
    def __next__(self):
        if self.numarator <= 5:
            returnabil = self[self.numarator]
            self.numarator += 1
            return returnabil
        else:
            raise StopIteration
    def __round__(self,n:str) -> typing.Self:
        if n == "ceil":
            return Charisma_based_skills(
                    math.ceil(self.leadership),
                    math.ceil(self.tactic),
                    math.ceil(self.trade),
                    math.ceil(self.animal),
                    math.ceil(self.appearance)
                    )
        elif n == "floor":
            return Charisma_based_skills(
                    math.floor(self.leadership),
                    math.floor(self.tactic),
                    math.floor(self.trade),
                    math.floor(self.animal),
                    math.floor(self.appearance)
                    )
        else:
            return Charisma_based_skills(
                    round(self.leadership),
                    round(self.tactic),
                    round(self.trade),
                    round(self.animal),
                    round(self.appearance)
                    )
    @staticmethod
    def null_skills() -> typing.Self:
        return Charisma_based_skills(0,0,0,0,0)
class Skills():
    def __init__(self,
                 strength_skills:Strength_based_skills,
                 mobility_skills:Mobility_based_skills,
                 dexterity_skills:Dexterity_based_skills,
                 charisma_skills:Charisma_based_skills,
                 attributes:Attributes ):
        self.attributes = attributes
        self.strength = attributes.strength
        self.mobility = attributes.mobility
        self.dexterity = attributes.dexterity
        self.charisma =  attributes.charisma
        self.strength_based_skills = strength_skills
        self.mobility_based_skills = mobility_skills
        self.dexterity_based_skills = dexterity_skills
        self.charisma_based_skills = charisma_skills
    @property
    def effective_skills(self) -> typing.Self:
        effective_strenght_skills = self.strength_based_skills + Strength_based_skills(*[self.strength for _ in range(5)])
        effective_mobility_skills = self.mobility_based_skills + Mobility_based_skills(*[self.mobility for _ in range(5)])
        effective_dexterity_skills = self.dexterity_based_skills + Dexterity_based_skills(*[self.dexterity for _ in range(5)])
        effective_charisma_skills = self.charisma_based_skills + Charisma_based_skills(*[self.charisma for _ in range(5)])
        effective_attributes = Attributes(*[0 for _ in range(4)])
        return Skills(
                strength_skills = effective_strenght_skills,
                mobility_skills = effective_mobility_skills,
                dexterity_skills = effective_dexterity_skills,
                charisma_skills = effective_charisma_skills,
                attributes = effective_attributes
                )
    def __str__(self):
        return (
            f'attributes:{{ {self.attributes} }},'
            f'strength based skills:{{ {self.strength_based_skills}}},'
            f'mobility based skills: {{{self.mobility_based_skills}}},'
            f'dexterity based skills: {{{self.dexterity_based_skills}}},'
            f'charisma based skills: {{{self.charisma_based_skills}}}'
        )
    def __add__(self,other:typing.Self) -> typing.Self:
        new_attributes = self.attributes + other.attributes
        return Skills(
                strength_skills = self.strength_based_skills + other.strength_based_skills,
                mobility_skills = self.mobility_based_skills + other.mobility_based_skills,
                dexterity_skills = self.dexterity_based_skills + other.dexterity_based_skills,
                charisma_skills = self.charisma_based_skills + other.charisma_based_skills,
                attributes = new_attributes
                )
    def __radd__(self,other:typing.Self) -> typing.Self:
        if other == 0:
            return self
        new_attributes = self.attributes + other.attributes
        return Skills(
                strength_skills = self.strength_based_skills + other.strength_based_skills,
                mobility_skills = self.mobility_based_skills + other.mobility_based_skills,
                dexterity_skills = self.dexterity_based_skills + other.dexterity_based_skills,
                charisma_skills = self.charisma_based_skills + other.charisma_based_skills,
                attributes = new_attributes
                )
    def __mul__(self,other:int) -> typing.Self:
        new_attributes = self.attributes * other
        return Skills(
                strength_skills = self.strength_based_skills * other,
                mobility_skills = self.mobility_based_skills * other,
                dexterity_skills = self.dexterity_based_skills * other,
                charisma_skills = self.charisma_based_skills * other,
                attributes = new_attributes
                )
    def __rmul__(self,other:int) -> typing.Self:
        new_attributes = self.attributes * other
        return Skills(
                strength_skills = self.strength_based_skills * other,
                mobility_skills = self.mobility_based_skills * other,
                dexterity_skills = self.dexterity_based_skills * other,
                charisma_skills = self.charisma_based_skills * other,
                attributes = new_attributes
                )
    def __getitem__(self,numar:int) -> int:
        if self.attributes[numar] != "Error":
            return self.attributes[numar]
        elif self.strength_based_skills[numar] != "Error":
            return self.strength_based_skills[numar]
        elif self.mobility_based_skills[numar] != "Error":
            return self.mobility_based_skills[numar]
        elif self.dexterity_based_skills[numar] != "Error":
            return self.dexterity_based_skills[numar]
        elif self.charisma_based_skills[numar] != "Error":
            return self.charisma_based_skills[numar]
        else:
            return "Error"
    def __setitem__(self,numar:int,value:int):
        if self.attributes[numar] != "Error":
            self.attributes[numar] = value
        elif self.strength_based_skills[numar] != "Error":
            self.strength_based_skills[numar] = value
        elif self.mobility_based_skills[numar] != "Error":
            self.mobility_based_skills[numar] = value
        elif self.dexterity_based_skills[numar] != "Error":
            self.dexterity_based_skills[numar] = value
        elif self.charisma_based_skills[numar] != "Error":
            self.charisma_based_skills[numar] = value
        else:
            return "Error"
    def __iter__(self):
        self.item_dict = {1:self.attributes,
                          2:self.strength_based_skills,
                          3:self.mobility_based_skills,
                          4:self.dexterity_based_skills,
                          5:self.charisma_based_skills}
        self.class_iterator = 1
        self.additional_iterator = 1
        return self
    def __next__(self):
        if self.class_iterator <= 5:
            returnabil =  self.item_dict[self.class_iterator][self.additional_iterator]
            if self.additional_iterator == 5:
                self.class_iterator += 1
                self.additional_iterator = 1
            else:
                self.additional_iterator += 1
            return returnabil
        else:
            raise StopIteration
    def __round__(self,n:str) -> typing.Self:
        new_attributes = self.attributes.__round__(n)
        return Skills(
            strength_skills = self.strength_based_skills.__round__(n),
            mobility_skills = self.mobility_based_skills.__round__(n),
            dexterity_skills = self.dexterity_based_skills.__round__(n),
            charisma_skills = self.charisma_based_skills.__round__(n),
            attributes = new_attributes)
    @staticmethod
    def null_skill() -> typing.Self:
        return Skills(
                    strength_skills= Strength_based_skills.null_skills(),
                    mobility_skills= Mobility_based_skills.null_skills(),
                    dexterity_skills= Dexterity_based_skills.null_skills(),
                    charisma_skills= Charisma_based_skills.null_skills(),
                    attributes= Attributes.null_attributes()
                    )