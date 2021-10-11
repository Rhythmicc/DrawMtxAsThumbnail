from DrawMtxAsThumbnail.Drawer import Drawer


@Drawer.algorithmWrapper()
def myOwnAlgorithm(mat, extern_arg):
    print(extern_arg)
    return max(abs(max([max(i) for i in mat])), abs(min([min(i) for i in mat])))


drawer = Drawer('dist/2.mtx', False, set_log_times=0, force_update=True)
drawer.call('myOwnAlgorithm', extern_arg=1)
