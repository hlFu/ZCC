#constant value put here

UNDEFINED = -100

class NodeKind:
    STMT = 1
    EXP = 2
    
class StmtKind:
    IF     = 1
    REPEAT = 2
    ASSIGN = 3

class ExpKind:
    OP    = 1
    CONST = 2
    ID    = 3

class ExpType:
    VOID    = 1
    INTEGER = 2
    FLOAT   = 3
    BOOLEAN = 4