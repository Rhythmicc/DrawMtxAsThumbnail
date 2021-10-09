from . import *

class Drawer:
    def __init__(self, filepath: str, has_aver: bool, force_update: bool = False, set_log_times: int = 2, set_mat_size: int = 200):
        self.filepath = filepath
        self.force_update = force_update
        self.has_aver = has_aver
        self.img_path = filepath.split('.')
        self.img_path = '.'.join(self.img_path[:-1]) + '_{}' + '.svg'
        self.log_times = set_log_times
        console.print(info_string, f'路径模板: "{self.img_path}"')

        self.matSize = set_mat_size

        self.ticks, self.mtx, self.coo_shape, \
            self.coo_data, self.coo_rows, self.coo_cols, \
            self.raw_mat, self.mat, self.div, \
            self.row_size, self.col_size, \
            self.row_block_sz, self.col_block_sz \
            = None, None, None, None, None, None, None, None, None, None, None, None, None
        self.absVal = 1

    def loadMtx(self, st=None):
        if st:
            st.update(status='正在加载矩阵并生成画布')
        self.mtx = coo_matrix(mmread(self.filepath))
        self.matSize = min(max(self.mtx.shape), self.matSize)
        # self.ticks = np.linspace(0, self.matSize, 4)

        self.coo_shape = self.mtx.shape
        if self.coo_shape[0] > self.coo_shape[1]:
            self.row_size = self.matSize
            self.row_block_sz = int(math.ceil(self.coo_shape[0] / self.row_size))
            self.col_size = int(math.ceil(self.matSize * (self.coo_shape[1] / self.coo_shape[0])))
            self.col_block_sz = int(math.ceil(self.coo_shape[1] / self.col_size))
        else:
            self.col_size = self.matSize
            self.col_block_sz = int(math.ceil(self.coo_shape[1] / self.col_size))
            self.row_size =  int(math.ceil(self.matSize * (self.coo_shape[0] / self.coo_shape[1])))
            self.row_block_sz = int(math.ceil(self.coo_shape[0] / self.col_size))

        self.xticks = np.linspace(0, self.col_size, 4)
        self.yticks = np.linspace(0, self.row_size, 4)
        self.coo_data = self.mtx.data
        self.coo_rows = self.mtx.row // self.row_block_sz
        self.coo_cols = self.mtx.col // self.col_block_sz
        self.raw_mat = np.zeros((self.row_size, self.col_size), dtype=float)

        if self.has_aver:
            self.div = np.ones((self.row_size, self.col_size), dtype=float)
            for i in zip(self.coo_data, self.coo_rows, self.coo_cols):
                self.raw_mat[i[1:]] += i[0]
                self.div[i[1:]] += 1
            self.div[self.div > 1] -= 1
        else:
            for i in zip(self.coo_data, self.coo_rows, self.coo_cols):
                self.raw_mat[i[1:]] += i[0]

    def aver(self):
        if os.path.exists(self.img_path.format('aver')) and not self.force_update:
            return

        with console.status('正在执行: aver') as st:
            if self.raw_mat is None:
                self.loadMtx(st)
            self.mat = self.raw_mat.copy()
            self.mat /= self.div
            self.absVal = max(abs(max([max(i) for i in self.mat])), abs(min([min(i) for i in self.mat])))
            self.draw('aver')

    def abs(self):
        if os.path.exists(self.img_path.format('abs')) and not self.force_update:
            return

        with console.status('正在执行: abs') as st:
            if self.raw_mat is None:
                self.loadMtx(st)
            self.mat = self.raw_mat.copy()
            self.mat[self.mat > 0] = 1
            self.mat[self.mat < 0] = -1
            self.absVal = 1
            self.draw('abs')

    def real(self):
        if os.path.exists(self.img_path.format('real')) and not self.force_update:
            return

        with console.status('正在执行: real') as st:
            if self.raw_mat is None:
                self.loadMtx(st)
            self.mat = self.raw_mat.copy()
            self.absVal = max(abs(max(self.coo_data)), abs(min(self.coo_data)))
            self.draw('real')

    def log(self):
        if os.path.exists(self.img_path.format('log')) and not self.force_update:
            return

        with console.status('正在执行: log') as st:
            if self.raw_mat is None:
                self.loadMtx(st)
            self.mat = self.raw_mat.copy()
            for _ in range(self.log_times):
                self.mat[self.mat > 0] = np.log(self.mat[self.mat > 0])
                self.mat[self.mat < 0] = -np.log(-self.mat[self.mat < 0])
            self.absVal = max(abs(max([max(i) for i in self.mat])), abs(min([min(i) for i in self.mat])))
            self.draw('log')

    def draw(self, suffix: str):
        if self.mat is None:
            return
        console.print(info_string, 'absVal =', self.absVal)

        fig = plt.figure()
        plt.imshow(
            self.mat,
            cmap='bwr',
            norm=cm.colors.Normalize(vmin=-self.absVal, vmax=self.absVal)
        )
        plt.xticks(
            ticks=self.xticks,
            labels=[int(i * self.row_block_sz) for i in self.xticks[:-1]] + [self.coo_shape[0]],
        )
        plt.yticks(
            ticks=self.yticks,
            labels=[int(i * self.col_block_sz) for i in self.yticks[:-1]] + [self.coo_shape[1]]
        )
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.colorbar()
        fig.savefig(self.img_path.format(suffix), format='svg', transparent=True)
        plt.close(fig)
