from QuickProject.Commander import Commander
from DrawMtxAsThumbnail import console, info_string
from DrawMtxAsThumbnail.Drawer import Drawer

app = Commander(True)
rt_path = './'


@app.command()
def draw_one(filepath: str, ops: list, force: bool = False, log_times: int = 2):
    """
    单个文件处理
    """
    drawer = Drawer(filepath, 'aver' in ops, force, log_times)
    for func in ops:
        drawer.call(func)


@app.command()
def draw(ops: list, force: bool = False, log_times: int = 2):
    """
    多个文件处理
    :param ops: 操作列表
    :param force: 是否强制更新
    :param log_times: 取log次数
    :return:
    """
    import os

    has_aver = 'aver' in ops
    for rt, sonDirs, sonFiles in os.walk(rt_path, followlinks=True):
        if not rt.endswith('/'):
            rt += '/'
        for file in sonFiles:
            if file.endswith('.mtx'):
                try:
                    console.print(info_string, f'正在处理: "{rt + file}"')
                    drawer = Drawer(rt + file, has_aver, force, log_times)
                    for func in ops:
                        drawer.call(func)
                except Exception:
                    console.print_exception()
                else:
                    console.print(info_string, '处理完成')
                finally:
                    console.print('-' * console.width)
    console.print(info_string, '处理完成')
    console.print('-' * console.width)


def main():
    app()
