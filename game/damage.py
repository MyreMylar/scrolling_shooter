
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

DamageType = enum('BULLET', 'FIRE', 'MISSILE')

class Damage():
    def __init__(self, amount, damageType):
        self.amount = amount
        self.type = damageType
        
