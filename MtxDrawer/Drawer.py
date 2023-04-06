import os
import math
from pylab import cm
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import mmread
from scipy.sparse import coo_matrix
from . import *
import inspect
from inspect import isfunction
from typing import Callable, Any


class Drawer:
    algorithm_func_table = {}
    valid_parameters = {
        "has_aver",
        "log_times",
        "mat_size",
        "mtx",
        "coo_shape",
        "coo_data",
        "coo_rows",
        "coo_cols",
        "mat",
        "div",
        "row_size",
        "col_size",
        "row_block_sz",
        "col_block_sz",
    }

    @classmethod
    def algorithmWrapper(cls):
        """
        Drawer 的算法装饰器, 已内置 aver, log, real, abs四种算法,
        您通过此装饰器可以轻松自定义算法, 支持直接获取Drawer对象支持的参数, 主要包含如下内容,
        (如自定义算法需要其他参数输入, 参数名需要以extern_开头, 并需要以extern_xxx=bala的形式赋值)
        has_aver: 是否有取平均值选项 => div是否可用

        log_times: 外部设定的取log的次数

        mat_size: 矩阵行列值较大的属性被分的块数

        mtx: 文件的scipy.sparse.coo_matrix对象, 未做任何更改

        coo_shape: mtx的尺寸

        coo_data: 矩阵的非零元值

        coo_rows: 矩阵的非零元素行索引映射到mat的行值

        coo_cols: 矩阵的非零元素列索引映射到mat的列值

        mat: 被初始化好的二维画布对象, 类型为numpy.array

        div: 子矩阵非零元数, 只有当has_aver为True时才会有效

        row_size: mat的行数

        col_size: mat的列数

        row_block_sz: 划分的子矩阵的行数

        col_block_sz: 划分的子矩阵的列数
        """

        def wrapper(func: Callable[[Any], float]):
            if not isfunction(func):
                raise TypeError("Algorithm Wrapper should wrap a function!")
            func_analyser = inspect.signature(func)
            func_name = func.__name__.strip("_")
            if func_name in Drawer.algorithm_func_table:
                raise Exception(f"Algorithm '{func_name}' already exists!")
            for arg in func_analyser.parameters.values():
                if arg.name not in Drawer.valid_parameters and not arg.name.startswith(
                    "extern_"
                ):
                    raise Exception(
                        "Arg must in supported args or startswith 'extern_'"
                    )
            Drawer.algorithm_func_table[func_name] = {
                "func": func,
                "analyser": func_analyser,
            }

        return wrapper

    def __init__(
        self,
        filepath: str,
        has_aver: bool,
        force_update: bool = False,
        set_log_times: int = 2,
        set_mat_size: int = 200,
        set_block_size: int = -1,
        img_format: str = "svg",
        font_color: str = "black",
        show_in_console: bool = False,
    ):
        """
        初始化Drawer对象
        :param filepath: 矩阵文件路径
        :param has_aver: 是否有取平均值选项
        :param force_update: 是否强制更新图像
        :param set_log_times: 取log的次数
        :param set_mat_size: 缩略图尺寸
        :param set_block_size: 设置块大小（此参数设置后将覆盖set_mat_size）
        :param img_format: 图像格式
        :param font_color: 字体颜色
        :param show_in_console: 是否在控制台显示图像, 如果为True则不会保存图像
        """
        self.img_format = img_format
        self.font_color = font_color
        self.filepath = filepath
        self.force_update = force_update
        self.has_aver = has_aver
        self.img_path = filepath.split(".")
        self.img_path = ".".join(self.img_path[:-1]) + "_{}" + f".{img_format}"
        self.log_times = set_log_times
        self.show_in_console = show_in_console
        if self.show_in_console:
            console.print(info_string, "已开启控制台显示图像")
        else:
            console.print(info_string, f'路径模板: "{self.img_path}"')

        self.mat_size = set_mat_size
        self.block_sz = set_block_size

        (
            self.mtx,
            self.coo_shape,
            self.coo_data,
            self.coo_rows,
            self.coo_cols,
            self.raw_mat,
            self.mat,
            self.div,
            self.row_size,
            self.col_size,
            self.row_block_sz,
            self.col_block_sz,
            self.x_ticks,
            self.y_ticks,
        ) = (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        self.absVal = 1

    def loadMtx(self):
        status.update("加载矩阵")
        try:
            self.mtx = coo_matrix(mmread(self.filepath))
        except ValueError:
            console.print(
                erro_string, "读取矩阵失败: 可能此文件格式不符合标准Matrix Market格式, 或位置值不以1作为第一个元素"
            )
            raise ValueError("读取矩阵失败: 可能此文件格式不符合标准Matrix Market格式, 或位置值不以1作为第一个元素")
        self.coo_shape = self.mtx.shape
        if self.block_sz > 0:
            self.row_size = int(math.ceil(self.coo_shape[0] / self.block_sz))
            self.col_size = int(math.ceil(self.coo_shape[1] / self.block_sz))
            self.row_block_sz = self.col_block_sz = self.block_sz
            self.y_ticks = np.linspace(0, self.row_size, 4)
            self.x_ticks = np.linspace(0, self.col_size, 4)
        else:
            self.mat_size = min(max(self.mtx.shape), self.mat_size)
            if self.coo_shape[0] >= self.coo_shape[1]:
                rate = self.coo_shape[1] / self.coo_shape[0]
                self.row_size = self.mat_size
                self.row_block_sz = self.coo_shape[0] / self.row_size
                self.col_size = int(math.ceil(self.mat_size * rate))
                self.col_block_sz = self.coo_shape[1] / self.col_size
                self.y_ticks = np.linspace(0, self.row_size, 4)
                self.x_ticks = np.linspace(0, self.col_size, max(my_round(4 * rate), 2))
            else:
                rate = self.coo_shape[0] / self.coo_shape[1]
                self.col_size = self.mat_size
                self.col_block_sz = self.coo_shape[1] / self.col_size
                self.row_size = int(math.ceil(self.mat_size * rate))
                self.row_block_sz = self.coo_shape[0] / self.row_size
                self.x_ticks = np.linspace(0, self.col_size, 4)
                self.y_ticks = np.linspace(0, self.row_size, max(my_round(4 * rate), 2))

        self.coo_data = self.mtx.data
        self.coo_rows = np.floor(self.mtx.row / self.row_block_sz).astype(np.int32)
        self.coo_cols = np.floor(self.mtx.col / self.col_block_sz).astype(np.int32)
        self.raw_mat = np.zeros((self.row_size, self.col_size), dtype=float)

        status.update("生成画布")
        if self.has_aver:
            self.div = np.ones((self.row_size, self.col_size), dtype=float)
            for i in zip(self.coo_data, self.coo_rows, self.coo_cols):
                self.raw_mat[i[1:]] += i[0]
                self.div[i[1:]] += 1
            self.div[self.div > 1] -= 1
        else:
            for i in zip(self.coo_data, self.coo_rows, self.coo_cols):
                self.raw_mat[i[1:]] += i[0]

    def call(self, func_name: str, **kw_extern_args):
        status(f"正在执行: {func_name}").start()
        func_name = func_name.strip("_")
        if func_name not in Drawer.algorithm_func_table:
            raise KeyError(f"Algorithm '{func_name}' not registered!")
        analyser = Drawer.algorithm_func_table[func_name]["analyser"]
        algorithm = Drawer.algorithm_func_table[func_name]["func"]
        args_body = {}
        if self.raw_mat is None:
            self.loadMtx()
            status(f"正在执行: {func_name}")
        self.mat = self.raw_mat.copy()
        for arg in analyser.parameters.values():
            if arg.name in Drawer.valid_parameters:
                args_body[arg.name] = getattr(self, arg.name)
        args_body.update(kw_extern_args)
        if os.path.exists(self.img_path.format(func_name)) and not self.force_update:
            return
        self.absVal = algorithm(**args_body)
        self.draw(func_name)

    def draw(self, suffix: str):
        if self.mat is None:
            return
        console.print(info_string, "absVal =", self.absVal)

        fig = plt.figure()
        plt.imshow(
            self.mat,
            cmap="bwr",
            norm=cm.colors.Normalize(vmin=-self.absVal, vmax=self.absVal),
        )
        plt.xticks(
            ticks=self.x_ticks,
            labels=[int(i * self.row_block_sz) for i in self.x_ticks[:-1]]
            + [self.coo_shape[1]],
        )
        plt.yticks(
            ticks=self.y_ticks,
            labels=[int(i * self.col_block_sz) for i in self.y_ticks[:-1]]
            + [self.coo_shape[0]],
        )
        plt.tick_params(axis="x", colors=self.font_color)
        plt.tick_params(axis="y", colors=self.font_color)
        bar = plt.colorbar()
        bar.ax.tick_params(labelcolor=self.font_color)
        # 设置背景透明
        fig.patch.set_alpha(0)
        if not self.show_in_console:
            fig.savefig(
                self.img_path.format(suffix),
                format=self.img_format,
                dpi=300,
            )
        else:
            requirePackage('QuickStart_Rhy.ImageTools.ImagePreview', 'image_preview', 'QuickStart_Rhy')(fig)
        plt.close(fig)


@Drawer.algorithmWrapper()
def aver(mat, div):
    mat /= div
    return max(abs(max([max(i) for i in mat])), abs(min([min(i) for i in mat])))


@Drawer.algorithmWrapper()
def _abs(mat):
    mat[mat > 0] = 1
    mat[mat < 0] = -1
    return 1


@Drawer.algorithmWrapper()
def real(coo_data) -> float:
    return max(abs(max(coo_data)), abs(min(coo_data)))


@Drawer.algorithmWrapper()
def log(mat: np.ndarray, log_times: int) -> float:
    for _ in range(log_times):
        mat[mat > 0] = np.log(mat[mat > 0])
        mat[mat < 0] = -np.log(-mat[mat < 0])
    return max(abs(max([max(i) for i in mat])), abs(min([min(i) for i in mat])))
