import os
import sys
from DrawMtxAsThumbnail import console, info_string, erro_string
from DrawMtxAsThumbnail.Drawer import Drawer

rt_path = './'

arg_check = []
valid_args = ['--force', '--set-log-times', '-one']
for item in sys.argv:
    if item.startswith('-') and item not in valid_args:
        arg_check.append(item)
if arg_check:
    console.print(erro_string, f'存在非法参数: {arg_check}')
    exit(1)


def main():
    force_update = '--force' in sys.argv
    if force_update:
        sys.argv.remove('--force')

    if '--set-log-times' in sys.argv:
        times = sys.argv[sys.argv.index('--set-log-times') + 1]
        sys.argv.remove('--set-log-times')
        sys.argv.remove(times)
        times = int(times)
    else:
        times = 2

    if '-one' in sys.argv:
        filepath = sys.argv[sys.argv.index('-one') + 1]
        sys.argv.remove('-one')
        sys.argv.remove(filepath)
        drawer = Drawer(filepath, 'aver' in sys.argv[1:], force_update, times)
        for func in sys.argv[1:]:
            drawer.call(func)
        exit(0)

    for rt, sonDirs, sonFiles in os.walk(rt_path, followlinks=True):
        if not rt.endswith('/'):
            rt += '/'
        for file in sonFiles:
            if file.endswith('.mtx'):
                try:
                    console.print(info_string, f'正在处理: "{rt + file}"')
                    drawer = Drawer(rt + file, 'aver' in sys.argv[1:], force_update, times)
                    for func in sys.argv[1:]:
                        drawer.call(func)
                except Exception:
                    console.print_exception()
                else:
                    console.print(info_string, '处理完成')
                finally:
                    console.print('-' * console.width)
