from QuickProject import QproDefaultConsole as console
from QuickProject import QproInfoString as info_string
from QuickProject import QproWarnString as warn_string
from QuickProject import QproErrorString as erro_string
from decimal import getcontext, Decimal, ROUND_HALF_EVEN

name = 'MtxDrawer'
getcontext().rounding = ROUND_HALF_EVEN


def my_round(x: float) -> int:
    return int(Decimal(x).quantize(Decimal('1')))
