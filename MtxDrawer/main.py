from QuickProject.Commander import Commander
from . import console, info_string, status
from .Drawer import Drawer
import os

app = Commander("mtx-drawer")
rt_path = os.path.abspath(os.getcwd())


@app.custom_complete("font_color")
def draw_one():
    return ["black", "white", "red", "green", "blue", "yellow", "cyan", "magenta"]

@app.custom_complete("img_format")
def draw_one():
    return ["svg", "png", "jpg", "jpeg", "bmp", "eps"]

@app.custom_complete("ops")
def draw_one():
    return ['abs', 'log', 'aver', 'real']

@app.custom_complete('font_color')
def draw():
    return ["black", "white", "red", "green", "blue", "yellow", "cyan", "magenta"]

@app.custom_complete('img_format')
def draw():
    return ["svg", "png", "jpg", "jpeg", "bmp", "eps"]

@app.custom_complete('ops')
def draw():
    return ['abs', 'log', 'aver', 'real']

@app.command()
def draw_one(
    filepath: str,
    ops: list,
    force: bool = False,
    log_times: int = 2,
    mat_size: int = 200,
    block_size: int = -1,
    img_format: str = "svg",
    font_color: str = "black",
    show_in_console: bool = False,
):
    """
    单个文件处理
    :param filepath: 文件路径
    :param ops: 操作列表
    :param force: 是否强制更新
    :param log_times: 取log次数
    :param mat_size: 缩略图尺寸
    :param block_size: 设置块大小（此参数设置后将覆盖mat_size）
    :param img_format: 图片格式
    :param font_color: 字体颜色
    :param show_in_console: 是否在控制台显示图像, 如果为True则不会保存图像
    :return:
    """
    status("处理").start()
    try:
        drawer = Drawer(
            filepath,
            "aver" in ops,
            force,
            log_times,
            set_mat_size=mat_size,
            set_block_size=block_size,
            img_format=img_format,
            font_color=font_color,
            show_in_console=show_in_console,
        )
    except ValueError:
        return
    for func in ops:
        drawer.call(func)
    status.stop()


@app.command()
def draw(
    ops: list,
    force: bool = False,
    log_times: int = 2,
    mat_size: int = 200,
    block_size: int = -1,
    img_format: str = "svg",
    font_color: str = "black",
):
    """
    多个文件处理
    :param ops: 操作列表
    :param force: 是否强制更新
    :param log_times: 取log次数
    :param mat_size: 缩略图尺寸
    :param block_size: 设置块大小（此参数设置后将覆盖mat_size）
    :return:
    """
    has_aver = "aver" in ops
    status("遍历并处理").start()
    for rt, _, sonFiles in os.walk(rt_path, followlinks=True):
        for file in sonFiles:
            if file.endswith(".mtx"):
                try:
                    console.print(f'{os.path.join(rt, file)}', justify="center")
                    drawer = Drawer(
                        os.path.join(rt, file),
                        has_aver,
                        force,
                        log_times,
                        set_mat_size=mat_size,
                        set_block_size=block_size,
                        img_format=img_format,
                        font_color=font_color,
                    )
                    for func in ops:
                        drawer.call(func)
                except ValueError:
                    continue
                except Exception:
                    console.print_exception()
                finally:
                    console.print("-" * console.width)
    status.stop()
    console.print(info_string, "处理完成")
    console.print("-" * console.width)


@app.command()
def update():
    """
    更新
    """
    from QuickProject import user_pip, external_exec

    with status("正在更新..."):
        external_exec(f"{user_pip} install -U MtxDrawer")
    console.print(info_string, "更新完成")


def main():
    app()


if __name__ == "__main__":
    main()
