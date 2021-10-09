import os
import sys
import math
from pylab import cm
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import mmread
from scipy.sparse import coo_matrix
from rich.console import Console

name = 'DrawMtxAsThumbnail'
console = Console()
info_string = '[[bold cyan]信息[/bold cyan]]'
warn_string = '[[bold yellow]警告[/bold yellow]]'
erro_string = '[[bold red]错误[/bold red]]'
