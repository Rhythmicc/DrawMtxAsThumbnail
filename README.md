# Draw Mtx As Thumbnail - 将Mtx画为缩略图

## 安装

```shell
python3 setup.py sdist
pip3 install dist/MtxDrawer-0.0.1.tar.gz

# 或者

pip3 install MtxDrawer
```

自动安装依赖并注册一个命令`mtx-drawer`

## 运行

```shell
mtx-drawer draw-one [--force] [--log_times <n: int>] <filepath> <-ops <aver | abs | real | log>... >
mtx-drawer draw [--force] [--log_times <n: int>] <-ops <aver | abs | real | log>... >
```
### 解释

1. 第一条命令是为文件`<filepath>`画缩略图，其中`<ops>`是<font color="red">必填的多选参数</font>只能在命令末尾赋值，用于指定缩略图的类型，其中`<aver>`表示平均值，`<abs>`表示绝对值，`<real>`表示实际值，`<log>`表示对数值进行对数变换; `force`表示强制重新画缩略图默认为否，`log_times`表示画缩略图对像素值取log的次数默认为2。
2. 第二条命令会递归搜索当前路径下的所有mtx文件并绘制缩略图，参数含义与上一条描述一致。

注意: ops作为必填多选参数，必须在命令的末尾为其赋值，否则会报错。

### 获取帮助

```shell
mtx-drawer --help
```

![](https://cos.rhythmlian.cn/ImgBed/376449cfb835db2d7a3eb49aa760d80b.png)

### 例子

```shell
mtx-drawer draw-one 2.mtx --force --log_times 0 -ops aver abs log real # 一次性绘制2.mtx的四种图，log取0次，强制替换
mtx-drawer draw-one 2.mtx  -ops aver abs log real # 一次性绘制2.mtx的四种图，log取2次，不强制替换
mtx-drawer draw --force -ops aver abs log # 绘制当前目录及子目录下的全部mtx文件的三种图，强制替换
mtx-drawer draw -ops aver abs log real # 绘制当前目录及子目录下的全部mtx文件的三种图，不强制替换且log取2次
```

### 特殊说明

子矩阵划分方式：当行列不相等时，较大的属性被分为`matSize`块，较小的属性为`rate * matSize`块；其中`rate`为$ min(m,n)/max(m,n) $

## 基于Drawer类的自定义开发

```python
from MtxDrawer.Drawer import Drawer

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

|     ![](./img/ash85_aver.png)<br />平均值     |    ![](./img/ash85_real.png)<br />不处理    |
| :-------------------------------------------: | :-----------------------------------------: |
| ![](./img/ash85_log.png)<br /><b>取0次log</b> | ![](./img/ash85_abs.png)<br /><b>绝对值</b> |

### 现代IDE下的提示

![](./img/1.png)

