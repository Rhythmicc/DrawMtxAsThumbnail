import numpy as cnp
cimport numpy as cnp
from libc.stdlib cimport free

cdef extern from "numpy/arrayobject.h":
    ctypedef cnp.npy_intp npy_intp
    cnp.ndarray PyArray_SimpleNew(int nd, npy_intp* dims, int typenum)
    cnp.ndarray PyArray_SimpleNewFromData(int nd, npy_intp* dims, int typenum, void* data)

cdef int _numpy_initialized = cnp.import_array()

cdef extern from "_MatGen.c":
    ctypedef struct ThumbnailMatrix:
        unsigned long long rows
        unsigned long long cols  # original size (rows, cols)
        unsigned long long trows
        unsigned long long tcols # thumbnail size (trows, tcols)
        double* raw_mat # data of the matrix (trows, tcols)
        double real_max_value
        double real_min_value
        double* div_mat    # division matrix (trows, tcols)
    ThumbnailMatrix mat_gen_impl(const char* file_path, int block_sz, unsigned long long mat_sz, int using_div)

def mat_gen(str file_path, int block_sz, int mat_sz, int using_div):
    """
    Read matrix from file_path and return a dense matrix.
    """
    cdef ThumbnailMatrix mat = mat_gen_impl(file_path.encode('utf-8'), block_sz, mat_sz, using_div)
    cdef cnp.ndarray[cnp.double_t, ndim=2] raw_mat
    cdef cnp.ndarray[cnp.double_t, ndim=2] div_mat
    if mat.raw_mat == NULL:
        raise ValueError("Cannot read matrix from file: {}".format(file_path))
    cdef npy_intp dims[2]
    dims[0] = mat.trows
    dims[1] = mat.tcols
    raw_mat = cnp.PyArray_SimpleNewFromData(2, dims, cnp.NPY_DOUBLE, <void*>mat.raw_mat).copy()
    free(mat.raw_mat)
    if using_div:
        div_mat = cnp.PyArray_SimpleNewFromData(2, dims, cnp.NPY_DOUBLE, <void*>mat.div_mat).copy()
        free(mat.div_mat)
    else:
        div_mat = None
    
    return {
        "rows": mat.rows,
        "cols": mat.cols,
        "trows": mat.trows,
        "tcols": mat.tcols,
        "raw_mat": raw_mat,
        "div_mat": div_mat,
        "real_max_value": mat.real_max_value,
        "real_min_value": mat.real_min_value
    }
