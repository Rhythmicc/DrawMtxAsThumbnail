from QuickProject.Commander import Commander
from . import console, info_string, status
from .Drawer import Drawer
import os

app = Commander("mtx-drawer")
rt_path = os.path.abspath(os.getcwd())


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
    :return:
    """
    try:
        status("处理").start()
        drawer = Drawer(
            filepath,
            "aver" in ops,
            force,
            log_times,
            set_mat_size=mat_size,
            set_block_size=block_size,
            img_format=img_format,
            font_color=font_color,
        )
        status.stop()
    except ValueError:
        return
    for func in ops:
        drawer.call(func)


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
