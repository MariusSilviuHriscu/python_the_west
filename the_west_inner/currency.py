from dataclasses import dataclass

@dataclass
class Currency:
    
    cash : int
    deposit : int
    oup : int
    nuggets : int
    veteran_points : int
    max_oup : int = 3000
    @property
    def total_money(self) -> int :
        return self.cash + self.deposit
    
    def add_cash(self , ammount : int) :
        self.cash  += ammount
    
    def consume_money(self, ammount : int) :
        if ammount > self.total_money :
            raise ValueError(f"Can't spend {ammount} when you only have {self.total_money} ! ")
        if ammount > self.cash :
            self.deposit = self.deposit - ammount + self.cash
            self.cash = 0
        else:
            self.cash = self.cash - ammount 
    
    def modify_money(self , new_cash : int, new_deposit : int):
        self.cash = new_cash
        self.deposit = new_deposit
    
    def modify_oup(self, oup_delta : int) :
        
        if self.oup + oup_delta < 0 :
            raise ValueError('Tried subtracting more oup than possible !')
        if self.oup + oup_delta > self.max_oup:
            raise ValueError('Tried to add too many oup')
        
        self.oup = self.oup + oup_delta

def build_currency(input_dict:dict) -> Currency:
    return Currency(cash = input_dict['cash'],
                    deposit = input_dict['deposit'],
                    oup = input_dict['upb'],
                    nuggets = input_dict['nuggets'],
                    veteran_points = input_dict['veteranPoints'],
                    max_oup = 3000
                    )
