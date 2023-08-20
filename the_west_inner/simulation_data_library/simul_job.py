from dataclasses import dataclass
import typing
import js2py
import math
import random
from functools import partial
from collections import defaultdict


from simul_work_relevant_bonuses import Work_bonuses
from ..items import Items



@dataclass
class Job_reward_data:
    '''
    This class reprezents the effective job reward result of a job.
    '''
    wage : int
    exp_reward : int
    luck_drop : dict[int,int]
    product_dropped : dict[int,int]
    damage_taken : int
    oup : int
    @staticmethod
    def sum_reward_dict(dict1:dict[int,int] , dict2:dict[int,int]):
        union = set(dict1).union(set(dict2))
        return {x:dict1.get(x,0) + dict2.get(x,0) for x in union}
    
    def __add__(self,other:typing.Self) -> typing.Self:
        return Job_reward_data(
                                wage = self.wage + other.wage,
                                exp_reward = self.exp_reward + other.exp_reward,
                                luck_drop = self.sum_reward_dict(dict1 =self.luck_drop,dict2=other.luck_drop),
                                product_dropped = self.sum_reward_dict(dict1 = self.product_dropped,dict2= other.product_dropped),
                                damage_taken = self.damage_taken + other.damage_taken,
                                oup = self.oup + other.oup
                            )
class Item_drop_calculator():
    @staticmethod
    def calculate_number_of_items_dropped(player_luck_coeficient:int) -> int:
        number_of_item_dropped = player_luck_coeficient // 100
        chance = random.randint(0, 100)
    
        if chance < player_luck_coeficient % 100 :
            number_of_item_dropped += 1
        
        return number_of_item_dropped
    @staticmethod
    def get_item_drop_dict(player_luck_coeficient:int,drop_range:tuple[int,int],items:Items) -> dict[int, int]:
        number_of_items = Item_drop_calculator.calculate_number_of_items_dropped(player_luck_coeficient = player_luck_coeficient)
        droppable_items = [x for x in items.get_droppable_items() if drop_range[0] <= x['price'] <= drop_range[1]]
        return_dict = defaultdict(int)
    
        for _ in range(number_of_items):
            item = random.choice(droppable_items)
            item_id_selected = item['item_id']
            return_dict[item_id_selected] += 1
    
        return dict(return_dict)
    @staticmethod
    def calculate_item_drop_coeficient(job_duration:typing.Literal[15,600,3600],player_drop:int,job_is_silver:bool) ->int:
        base_chance = {1:0.03,600:0.09,3600:0.27}[job_duration]
        if job_is_silver:
                base_chance = base_chance * 1.5
        return base_chance * player_drop * 100

@dataclass
class Job_reward_stats():
    '''
    This class reprezents the general reward stats adjusted for workpoints,character class , premium and job_time.
    '''
    wage: int
    exp : int
    inferior_luck : int
    superior_luck : int
    danger : int
    product_rate : dict[int,int]
    job_id : int
    is_silver : bool
    def _normalize_by_time(self,time:int) -> typing.Self :
        TIME_CONSTANT_DICT = {3600:1,600:2.15,15:10}
        return Job_reward_stats(
                                wage = math.ceil(self.wage / TIME_CONSTANT_DICT[time]),
                                exp = math.ceil(self.exp / TIME_CONSTANT_DICT[time]),
                                inferior_luck = self.inferior_luck ,
                                superior_luck = self.superior_luck ,
                                danger = self.danger ,
                                product_rate = {
                                                product_id: math.ceil( indiv_prod_rate / TIME_CONSTANT_DICT[time]) 
                                                                    for product_id,indiv_prod_rate in self.product_rate} ,
                                job_id = self.job_id,
                                is_silver = self.is_silver
                                )
    def simulate_job(self,time:typing.Literal[15,600,3600],items:Items,player_data: Work_bonuses) ->Job_reward_data:
        self = self._normalize_by_time(time=time)
        player_luck_coeficient = Item_drop_calculator.calculate_item_drop_coeficient(
                                                                                    job_duration = time,
                                                                                    player_drop = player_data.item_drop ,
                                                                                    job_is_silver = self.is_silver
                                                                                    )
        player_product_drop_coeficient_funct = partial(Item_drop_calculator.calculate_item_drop_coeficient,
                                                job_duration= 15,
                                                job_is_silver = self.is_silver
                                                )

        return Job_reward_data(
                                wage = self.wage,
                                exp_reward = self.exp,
                                luck_drop = Item_drop_calculator.get_item_drop_dict(
                                                                player_luck_coeficient = player_luck_coeficient,
                                                                drop_range = (self.inferior_luck,self.superior_luck),
                                                                items = items
                                                            ),
                                product_dropped = {
                                                product_id:player_product_drop_coeficient_funct(player_drop = base_rate)
                                                                for product_id,base_rate in self.product_rate} ,
                                damage_taken = 0 ,
                                oup = 0
                                )
@dataclass
class Job_raw_data():
    '''
    This class reprezents the stats of a player regarding a certain job
    '''
    motivation : int
    dollar : int
    experience : int
    luck : int
    danger : int
    job_id : int
    work_points : int
    product_rate : int
    requirements : int
    is_silver : bool
    
    def get_hourly_rate(self) -> Job_reward_stats:
        functext = f"""
        function calc(r1, r2, formula, points, malus, magic, mot, factor, freezeBronze) {{
		var step = Math.ceil((malus+1)/5), stars = Math.min(Math.floor(points/step), 15), dmot = Math.ceil(mot/25)*0.25;
		return points < 5*step || points <= malus
				? Math[r1](({{0:1,1:2,2:3,3:4,4:5,5:6.25}})[freezeBronze ? 0 : stars] * magic * dmot * factor)
				: Math[r2](formula(points - malus, stars) * magic * dmot * factor)
	    }};
        function calcWage(pts, mal, magic, mot, fac){{
		return calc('ceil', 'round', function(lp){{ return 6.25*Math.pow(lp, 0.05) }}, pts, mal, magic, mot, fac);
	    }};
	    function calcExp(pts, mal, magic, mot, fac){{
		return calc('ceil', 'ceil', function(lp){{ return 6.25 }}, pts, mal, magic, mot, fac);
	    }};
	    function calcLuck(pts, mal, magic, mot, fac){{
		return calc('floor', 'floor', function(lp){{ return 6.25*Math.pow(lp, 0.2) }}, pts, mal, (0.9*magic + 5)/1.25, 100, fac);
	    }};
	    function calcProductRate(pts, mal, magic, mot, fac){{
		return calc('round', 'round', function(lp, stars){{ return stars < 15 ? 6.25 : 9.375 }}, pts, mal, magic, 100, fac);
	    }};
	    function calcDanger(pts, mal, magic, mot, fac){{
		return calc('round', 'round', function(lp){{ return Math.pow(lp, -0.2) }}, pts, mal, magic, 100, fac, true);
	    }};
        mot = Math.min(Math.max({self.motivation} || 0, 0), 100);
		var sp = {self.work_points};
        function() {{ 
            wage = calcWage(sp, {self.requirements}, {self.dollar}, mot, 1)
            exp = calcExp(sp, {self.requirements}, {self.experience}, mot, 1)
            luck_inferior  = calcLuck(sp, {self.requirements}, {self.luck}, mot, 1)
            luck_superior  = calcLuck(sp, {self.requirements}, {self.luck}, mot, 3)
            danger = calcDanger(sp, {self.requirements}, {self.danger}, mot, 1)
            product_rate = {{}};
            var temp = {self.product_rate};
            for (var elem in temp) {{
                product_rate[elem] = calcProductRate(sp, {self.requirements}, temp[elem], mot, 1)
            }}
        return {{"wage":wage,"exp":exp,"luck_inferior":luck_inferior,"luck_superior":luck_superior,"danger":danger,"product_rate":product_rate}}
        }} """
        res1 = js2py.eval_js(functext)
        job_data_dict  = res1()
        return Job_reward_stats(
                                wage = job_data_dict['wage'],
                                exp = job_data_dict['exp'] ,
                                inferior_luck = job_data_dict['luck_inferior'],
                                superior_luck = job_data_dict['luck_superior'],
                                danger = job_data_dict['danger'],
                                product_rate = job_data_dict['product_rate'],
                                job_id = self.job_id,
                                is_silver = self.is_silver
                                )

class Job_rewards_simulator():
    def __init__(self,job_raw_data:Job_raw_data,items:Items,player_data:Work_bonuses):
        self.job_raw_data = job_raw_data
        self.items = items
        self.player_data = player_data
    def simulate_job(self,time:typing.Literal[15,600,3600]):
        return self.job_raw_data.get_hourly_rate().simulate_job(time = time,items=self.items,player_data=self.player_data)
