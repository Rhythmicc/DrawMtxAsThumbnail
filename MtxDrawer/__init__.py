from QuickProject import QproDefaultConsole as console
from QuickProject import QproInfoString as info_string
from QuickProject import QproWarnString as warn_string
from QuickProject import QproErrorString as erro_string
from QuickProject import QproDefaultStatus as status
from QuickProject import _ask, user_lang, external_exec, user_pip
from decimal import getcontext, Decimal, ROUND_HALF_EVEN
import sys

name = 'MtxDrawer'
getcontext().rounding = ROUND_HALF_EVEN


def my_round(x: float) -> int:
    return int(Decimal(x).quantize(Decimal('1')))


def requirePackage(
    pname: str,
    module: str = "",
    real_name: str = "",
    not_exit: bool = True,
    not_ask: bool = False,
    set_pip: str = user_pip,
):
    """
    获取本机上的python第三方库

    :param pname: 库名
    :param module: 待引入的模块名，可缺省
    :param real_name: 用于 pip3 install 的名字
    :param not_exit: 安装后不退出
    :param not_ask: 不询问
    :param set_pip: pip3的路径
    :return: 库或模块的地址
    """
    try:
        exec(f"from {pname} import {module}" if module else f"import {pname}")
    except (ModuleNotFoundError, ImportError):
        if not_ask:
            return None
        if _ask(
            {
                "type": "confirm",
                "message": f"""{name} require {pname + (' -> ' + module if module else '')}, confirm to install?"""
                if user_lang != "zh"
                else f"""{name} 依赖 {pname + (' -> ' + module if module else '')}，确认安装吗？""",
                "default": True,
            }
        ):
            package_name = pname.split('.')[0] if not real_name else real_name
            if not package_name: # 引用为自身
                package_name = name
            with status(
                f"Installing {package_name}"
                if user_lang != "zh"
                else f"正在安装 {package_name}"
            ):
                st, _ = external_exec(
                    f"{set_pip} install {package_name} -U",
                    True,
                )
            if st:
                console.print(
                    erro_string,
                    f"Install {pname + (' -> ' + module if module else '')} failed, please install it manually: "
                    if user_lang != "zh"
                    else f"安装 {pname + (' -> ' + module if module else '')} 失败，请手动安装: ",
                    f"'{set_pip} install {package_name} -U'",
                )
                exit(-1)
            if not_exit:
                exec(f"from {pname} import {module}" if module else f"import {pname}")
            else:
                console.print(
                    info_string,
                    "Install complete! Run again:"
                    if user_lang != "zh"
                    else f"安装完成！再次运行:",
                    " ".join(sys.argv),
                )
                exit(0)
        else:
            exit(-1)
    return eval(f"{module if module else pname}")
