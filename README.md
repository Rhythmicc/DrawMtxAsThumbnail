# Draw Mtx As Thumbnail - 将Mtx画为缩略图

## 安装

```shell
python3 setup.py install
```

自动安装依赖并注册一个命令`mtx-drawer`

## 运行

```shell
mtx-drawer <aver | abs | real | log...> [-one <*.mtx>] [--set-log-times <n: int>] [--force]
```

| 参数                         | 说明                                                         |
| ---------------------------- | ------------------------------------------------------------ |
| `<aver, abs, real, log>`  | 选择绘图算法, 目前支持针对子矩阵元素和取均值、取绝对值（正值为1，负值为-1）、不做处理、取若干次log |
| `[-one <*.mtx>]`             | 放弃自动搜索，指定一个mtx文件开始画                          |
| `[--set-log-times <n: int>]` | 设置log算法的取log次数，默认两次                             |
| `[--force]`                  | 强制覆盖已有的画图结果                                       |

### 例子

```shell
mtx-drawer aver abs log real -one 2.mtx --set-log-times 0 --force # 一次性绘制2.mtx的四种图，log取0次，强制替换
mtx-drawer aver abs log --force # 绘制当前目录及子目录下的全部mtx文件的三种图，强制替换
```

### 特殊说明

子矩阵划分方式：当行列不相等时，较大的属性被分为`matSize`块，较小的属性为`rate * matSize`块；其中`rate`为$ min(m,n)/max(m,n) $

## 基于Drawer类的自定义开发

```python
from DrawMtxAsThumbnail.Drawer import Drawer

"""
您可以通过如下方式自定义算法并通过Drawer对象的call方法来调用；
自定义算法可接受的参数将在下表中说明，此外，自定义算法必须返回一个数值用于表示color_bar的显示范围（返回1则表示-1~1）
"""

@Drawer.algorithmWrapper()
def myOwnAlgorithm(mat, extern_arg):
    print(extern_arg)
    return max(abs(max([max(i) for i in mat])), abs(min([min(i) for i in mat])))


drawer = Drawer('dist/2.mtx', False, set_log_times=0, force_update=True)
drawer.call('myOwnAlgorithm', extern_arg=1)

"""
---结果---

[信息] 路径模板: "dist/2_{}.svg"
1
[信息] absVal = 1
"""
```

| 合法参数  | 说明 |
| --------- | ---- |
| `has_aver` | 是否有取平均值选项 => div是否可用 |
| `log_times` | 外部设定的取log的次数 |
| `mat_size` | 矩阵行列值较大的属性被分的块数 |
| `mtx` | 文件的scipy.sparse.coo_matrix对象，未做任何更改 |
| `coo_shape` | mtx的尺寸 |
| `coo_data` | 矩阵的非零元值 |
| `coo_rows` | 矩阵的非零元素行索引映射到mat的行值 |
| `coo_cols` | 矩阵的非零元素列索引映射到mat的列值 |
| `mat` | 被初始化好的二维画布对象，类型为numpy.array |
| `div` | 子矩阵非零元数，只有当has_aver为True时才会有效 |
| `row_size` | mat的行数 |
| `col_size` | mat的列数 |
| `row_block_sz` | 划分的子矩阵的行数 |
| `col_block_sz` | 划分的子矩阵的列数 |
| `extern_*` | 额外的参数命名方式，需以"extern_xx=bala"的方式调用 |

## 样例

|     ![](./dist/ash85_aver.svg)<br />平均值     |    ![](./dist/ash85_real.svg)<br />不处理    |
| :--------------------------------------------: | :------------------------------------------: |
| ![](./dist/ash85_log.svg)<br /><b>取0次log</b> | ![](./dist/ash85_abs.svg)<br /><b>绝对值</b> |

### 现代IDE下的提示

![](./img/1.png)

