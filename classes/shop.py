

class Shop:
    def __init__(self):
        self.tiersToCost={
            1:800,
            2:1600,
            3:3200,
            4:6400,
            5:-1
        }
    
    def getCost(self,tier:int):
        return self.tiersToCost[tier]