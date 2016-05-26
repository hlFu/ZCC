#common structure put here
from const import *

class TreeNode:
    child    = []
    sibling  = None
    lineno   = UNDEFINED  # line number
    nodeKind = UNDEFINED  # enum in NodeKind
    kind     = UNDEFINED  # enum in StmtKind, ExpKind
    attr     = UNDEFINED  # enum in ExpKind
    type     = UNDEFINED  # enum in ExpType