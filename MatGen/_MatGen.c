#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <ctype.h>

#define MM_MAX_LINE_LENGTH 1025
#define MatrixMarketBanner "%%MatrixMarket"
#define MM_MAX_TOKEN_LENGTH 64

#define max(a,b) ((a)>(b)?(a):(b))
#define min(a,b) ((a)<(b)?(a):(b))

typedef char MM_typecode[4];

/********************* MM_typecode query fucntions ***************************/

#define mm_is_matrix(typecode) ((typecode)[0] == 'M')

#define mm_is_sparse(typecode) ((typecode)[1] == 'C')
#define mm_is_coordinate(typecode) ((typecode)[1] == 'C')
#define mm_is_dense(typecode) ((typecode)[1] == 'A')
#define mm_is_array(typecode) ((typecode)[1] == 'A')

#define mm_is_complex(typecode) ((typecode)[2] == 'C')
#define mm_is_real(typecode) ((typecode)[2] == 'R')
#define mm_is_pattern(typecode) ((typecode)[2] == 'P')
#define mm_is_integer(typecode) ((typecode)[2] == 'I')

#define mm_is_symmetric(typecode) ((typecode)[3] == 'S')
#define mm_is_general(typecode) ((typecode)[3] == 'G')
#define mm_is_skew(typecode) ((typecode)[3] == 'K')
#define mm_is_hermitian(typecode) ((typecode)[3] == 'H')

/********************* MM_typecode modify fucntions ***************************/

#define mm_set_matrix(typecode) ((*typecode)[0] = 'M')
#define mm_set_coordinate(typecode) ((*typecode)[1] = 'C')
#define mm_set_array(typecode) ((*typecode)[1] = 'A')
#define mm_set_dense(typecode) mm_set_array(typecode)
#define mm_set_sparse(typecode) mm_set_coordinate(typecode)

#define mm_set_complex(typecode) ((*typecode)[2] = 'C')
#define mm_set_real(typecode) ((*typecode)[2] = 'R')
#define mm_set_pattern(typecode) ((*typecode)[2] = 'P')
#define mm_set_integer(typecode) ((*typecode)[2] = 'I')

#define mm_set_symmetric(typecode) ((*typecode)[3] = 'S')
#define mm_set_general(typecode) ((*typecode)[3] = 'G')
#define mm_set_skew(typecode) ((*typecode)[3] = 'K')
#define mm_set_hermitian(typecode) ((*typecode)[3] = 'H')

#define mm_clear_typecode(typecode) ((*typecode)[0] = (*typecode)[1] = \
                                         (*typecode)[2] = ' ',         \
                                     (*typecode)[3] = 'G')

#define mm_initialize_typecode(typecode) mm_clear_typecode(typecode)

/********************* Matrix Market error codes ***************************/

#define MM_COULD_NOT_READ_FILE 11
#define MM_PREMATURE_EOF 12
#define MM_NOT_MTX 13
#define MM_NO_HEADER 14
#define MM_UNSUPPORTED_TYPE 15
#define MM_LINE_TOO_LONG 16
#define MM_COULD_NOT_WRITE_FILE 17

/******************** Matrix Market internal definitions ********************

   MM_matrix_typecode: 4-character sequence

                    ojbect 		sparse/   	data        storage
                                dense     	type        scheme

   string position:	 [0]        [1]			[2]         [3]

   Matrix typecode:  M(atrix)  C(oord)		R(eal)   	G(eneral)
                                A(array)	C(omplex)   H(ermitian)
                                            P(attern)   S(ymmetric)
                                            I(nteger)	K(kew)

 ***********************************************************************/

#define MM_MTX_STR "matrix"
#define MM_ARRAY_STR "array"
#define MM_DENSE_STR "array"
#define MM_COORDINATE_STR "coordinate"
#define MM_SPARSE_STR "coordinate"
#define MM_COMPLEX_STR "complex"
#define MM_REAL_STR "real"
#define MM_INT_STR "integer"
#define MM_GENERAL_STR "general"
#define MM_SYMM_STR "symmetric"
#define MM_HERM_STR "hermitian"
#define MM_SKEW_STR "skew-symmetric"
#define MM_PATTERN_STR "pattern"

/*  high level routines */
static char *mm_strdup(const char *s);
static char *mm_typecode_to_str(MM_typecode matcode);
static int mm_read_mtx_crd(char *fname, int *M, int *N, int *nz, int **II, int **JJ, double **val, MM_typecode *matcode);
static int mm_read_banner(FILE *f, MM_typecode *matcode);
static int mm_read_mtx_crd_size(FILE *f, unsigned long long *M, unsigned long long *N, unsigned long long *nz);
static int mm_read_mtx_array_size(FILE *f, int *M, int *N);
static int mm_write_banner(FILE *f, MM_typecode matcode);
static int mm_write_mtx_crd_size(FILE *f, int M, int N, int nz);
static int mm_write_mtx_array_size(FILE *f, int M, int N);
static int mm_is_valid(MM_typecode matcode);
static int mm_write_mtx_crd(char fname[], int M, int N, int nz, int II[], int JJ[], double val[], MM_typecode matcode);
static int mm_read_mtx_crd_data(FILE *f, int M, int N, int nz, int II[], int JJ[], double val[], MM_typecode matcode);
static int mm_read_mtx_crd_entry(FILE *f, int *II, int *JJ, double *real, double *imag, MM_typecode matcode);
static int mm_read_unsymmetric_sparse(const char *fname, int *M_, int *N_, int *nz_, double **val_, int **II_, int **JJ_);

static char *mm_strdup(const char *s)
{
    int len = strlen(s);
    char *s2 = (char *)malloc((len + 1) * sizeof(char));
    return strcpy(s2, s);
}

static char *mm_typecode_to_str(MM_typecode matcode)
{
    char buffer[MM_MAX_LINE_LENGTH];
    char *types[4];
    char *mm_strdup(const char *);
    // int error =0;

    /* check for MTX type */
    if (mm_is_matrix(matcode))
        types[0] = (char *)MM_MTX_STR;
    // else
    //     error=1;

    /* check for CRD or ARR matrix */
    if (mm_is_sparse(matcode))
        types[1] = (char *)MM_SPARSE_STR;
    else if (mm_is_dense(matcode))
        types[1] = (char *)MM_DENSE_STR;
    else
        return NULL;

    /* check for element data type */
    if (mm_is_real(matcode))
        types[2] = (char *)MM_REAL_STR;
    else if (mm_is_complex(matcode))
        types[2] = (char *)MM_COMPLEX_STR;
    else if (mm_is_pattern(matcode))
        types[2] = (char *)MM_PATTERN_STR;
    else if (mm_is_integer(matcode))
        types[2] = (char *)MM_INT_STR;
    else
        return NULL;

    /* check for symmetry type */
    if (mm_is_general(matcode))
        types[3] = (char *)MM_GENERAL_STR;
    else if (mm_is_symmetric(matcode))
        types[3] = (char *)MM_SYMM_STR;
    else if (mm_is_hermitian(matcode))
        types[3] = (char *)MM_HERM_STR;
    else if (mm_is_skew(matcode))
        types[3] = (char *)MM_SKEW_STR;
    else
        return NULL;

    sprintf(buffer, "%s %s %s %s", types[0], types[1], types[2], types[3]);
    return mm_strdup(buffer);
}

static int mm_read_mtx_crd(char *fname, int *M, int *N, int *nz, int **II, int **JJ,
                           double **val, MM_typecode *matcode)
{
    int ret_code;
    FILE *f;

    if (strcmp(fname, "stdin") == 0)
        f = stdin;
    else if ((f = fopen(fname, "r")) == NULL)
        return MM_COULD_NOT_READ_FILE;

    if ((ret_code = mm_read_banner(f, matcode)) != 0)
        return ret_code;

    if (!(mm_is_valid(*matcode) && mm_is_sparse(*matcode) &&
          mm_is_matrix(*matcode)))
        return MM_UNSUPPORTED_TYPE;

    if ((ret_code = mm_read_mtx_crd_size(f, M, N, nz)) != 0)
        return ret_code;

    *II = (int *)malloc(*nz * sizeof(int));
    *JJ = (int *)malloc(*nz * sizeof(int));
    *val = NULL;

    if (mm_is_complex(*matcode))
    {
        *val = (double *)malloc(*nz * 2 * sizeof(double));
        ret_code = mm_read_mtx_crd_data(f, *M, *N, *nz, *II, *JJ, *val,
                                        *matcode);
        if (ret_code != 0)
            return ret_code;
    }
    else if (mm_is_real(*matcode))
    {
        *val = (double *)malloc(*nz * sizeof(double));
        ret_code = mm_read_mtx_crd_data(f, *M, *N, *nz, *II, *JJ, *val,
                                        *matcode);
        if (ret_code != 0)
            return ret_code;
    }

    else if (mm_is_pattern(*matcode))
    {
        ret_code = mm_read_mtx_crd_data(f, *M, *N, *nz, *II, *JJ, *val,
                                        *matcode);
        if (ret_code != 0)
            return ret_code;
    }

    if (f != stdin)
        fclose(f);
    return 0;
}

static int mm_read_banner(FILE *f, MM_typecode *matcode)
{
    char line[MM_MAX_LINE_LENGTH];
    char banner[MM_MAX_TOKEN_LENGTH];
    char mtx[MM_MAX_TOKEN_LENGTH];
    char crd[MM_MAX_TOKEN_LENGTH];
    char data_type[MM_MAX_TOKEN_LENGTH];
    char storage_scheme[MM_MAX_TOKEN_LENGTH];
    char *p;

    mm_clear_typecode(matcode);

    if (fgets(line, MM_MAX_LINE_LENGTH, f) == NULL)
        return MM_PREMATURE_EOF;

    if (sscanf(line, "%s %s %s %s %s", banner, mtx, crd, data_type,
               storage_scheme) != 5)
        return MM_PREMATURE_EOF;

    for (p = mtx; *p != '\0'; *p = tolower(*p), p++)
        ; /* convert to lower case */
    for (p = crd; *p != '\0'; *p = tolower(*p), p++)
        ;
    for (p = data_type; *p != '\0'; *p = tolower(*p), p++)
        ;
    for (p = storage_scheme; *p != '\0'; *p = tolower(*p), p++)
        ;

    /* check for banner */
    if (strncmp(banner, MatrixMarketBanner, strlen(MatrixMarketBanner)) != 0)
        return MM_NO_HEADER;

    /* first field should be "mtx" */
    if (strcmp(mtx, MM_MTX_STR) != 0)
        return MM_UNSUPPORTED_TYPE;
    mm_set_matrix(matcode);

    /* second field describes whether this is a sparse matrix (in coordinate
            storgae) or a dense array */

    if (strcmp(crd, MM_SPARSE_STR) == 0)
        mm_set_sparse(matcode);
    else if (strcmp(crd, MM_DENSE_STR) == 0)
        mm_set_dense(matcode);
    else
        return MM_UNSUPPORTED_TYPE;

    /* third field */

    if (strcmp(data_type, MM_REAL_STR) == 0)
        mm_set_real(matcode);
    else if (strcmp(data_type, MM_COMPLEX_STR) == 0)
        mm_set_complex(matcode);
    else if (strcmp(data_type, MM_PATTERN_STR) == 0)
        mm_set_pattern(matcode);
    else if (strcmp(data_type, MM_INT_STR) == 0)
        mm_set_integer(matcode);
    else
        return MM_UNSUPPORTED_TYPE;

    /* fourth field */

    if (strcmp(storage_scheme, MM_GENERAL_STR) == 0)
        mm_set_general(matcode);
    else if (strcmp(storage_scheme, MM_SYMM_STR) == 0)
        mm_set_symmetric(matcode);
    else if (strcmp(storage_scheme, MM_HERM_STR) == 0)
        mm_set_hermitian(matcode);
    else if (strcmp(storage_scheme, MM_SKEW_STR) == 0)
        mm_set_skew(matcode);
    else
        return MM_UNSUPPORTED_TYPE;

    return 0;
}

static int mm_read_mtx_crd_size(FILE *f, unsigned long long *M, unsigned long long *N, unsigned long long *nz)
{
    char line[MM_MAX_LINE_LENGTH];
    int num_items_read;

    /* set return null parameter values, in case we exit with errors */
    *M = *N = *nz = 0;

    /* now continue scanning until you reach the end-of-comments */
    do
    {
        if (fgets(line, MM_MAX_LINE_LENGTH, f) == NULL)
            return MM_PREMATURE_EOF;
    } while (line[0] == '%');

    /* line[] is either blank or has M,N, nz */
    if (sscanf(line, "%lli %lli %lli", M, N, nz) == 3)
        return 0;

    else
        do
        {
            num_items_read = fscanf(f, "%lli %lli %lli", M, N, nz);
            if (num_items_read == EOF)
                return MM_PREMATURE_EOF;
        } while (num_items_read != 3);

    return 0;
}

static int mm_read_mtx_array_size(FILE *f, int *M, int *N)
{
    char line[MM_MAX_LINE_LENGTH];
    int num_items_read;
    /* set return null parameter values, in case we exit with errors */
    *M = *N = 0;

    /* now continue scanning until you reach the end-of-comments */
    do
    {
        if (fgets(line, MM_MAX_LINE_LENGTH, f) == NULL)
            return MM_PREMATURE_EOF;
    } while (line[0] == '%');

    /* line[] is either blank or has M,N, nz */
    if (sscanf(line, "%d %d", M, N) == 2)
        return 0;

    else /* we have a blank line */
        do
        {
            num_items_read = fscanf(f, "%d %d", M, N);
            if (num_items_read == EOF)
                return MM_PREMATURE_EOF;
        } while (num_items_read != 2);

    return 0;
}

static int mm_write_banner(FILE *f, MM_typecode matcode)
{
    char *str = mm_typecode_to_str(matcode);
    int ret_code;

    ret_code = fprintf(f, "%s %s\n", MatrixMarketBanner, str);
    free(str);
    if (ret_code != 2)
        return MM_COULD_NOT_WRITE_FILE;
    else
        return 0;
}

static int mm_write_mtx_crd_size(FILE *f, int M, int N, int nz)
{
    if (fprintf(f, "%d %d %d\n", M, N, nz) != 3)
        return MM_COULD_NOT_WRITE_FILE;
    else
        return 0;
}

static int mm_write_mtx_array_size(FILE *f, int M, int N)
{
    if (fprintf(f, "%d %d\n", M, N) != 2)
        return MM_COULD_NOT_WRITE_FILE;
    else
        return 0;
}

static int mm_is_valid(MM_typecode matcode) /* too complex for a macro */
{
    if (!mm_is_matrix(matcode))
        return 0;
    if (mm_is_dense(matcode) && mm_is_pattern(matcode))
        return 0;
    if (mm_is_real(matcode) && mm_is_hermitian(matcode))
        return 0;
    if (mm_is_pattern(matcode) && (mm_is_hermitian(matcode) ||
                                   mm_is_skew(matcode)))
        return 0;
    return 1;
}

/*  high level routines */

static int mm_write_mtx_crd(char fname[], int M, int N, int nz, int II[], int JJ[],
                            double val[], MM_typecode matcode)
{
    FILE *f;
    int i;

    if (strcmp(fname, "stdout") == 0)
        f = stdout;
    else if ((f = fopen(fname, "w")) == NULL)
        return MM_COULD_NOT_WRITE_FILE;

    /* print banner followed by typecode */
    fprintf(f, "%s ", MatrixMarketBanner);
    fprintf(f, "%s\n", mm_typecode_to_str(matcode));

    /* print matrix sizes and nonzeros */
    fprintf(f, "%d %d %d\n", M, N, nz);

    /* print values */
    if (mm_is_pattern(matcode))
        for (i = 0; i < nz; i++)
            fprintf(f, "%d %d\n", II[i], JJ[i]);
    else if (mm_is_real(matcode))
        for (i = 0; i < nz; i++)
            fprintf(f, "%d %d %20.16g\n", II[i], JJ[i], val[i]);
    else if (mm_is_complex(matcode))
        for (i = 0; i < nz; i++)
            fprintf(f, "%d %d %20.16g %20.16g\n", II[i], JJ[i], val[2 * i],
                    val[2 * i + 1]);
    else
    {
        if (f != stdout)
            fclose(f);
        return MM_UNSUPPORTED_TYPE;
    }

    if (f != stdout)
        fclose(f);

    return 0;
}

static int mm_read_mtx_crd_data(FILE *f, int M, int N, int nz, int II[], int JJ[],
                                double val[], MM_typecode matcode)
{
    int i;
    if (mm_is_complex(matcode))
    {
        for (i = 0; i < nz; i++)
            if (fscanf(f, "%d %d %lg %lg", &II[i], &JJ[i], &val[2 * i], &val[2 * i + 1]) != 4)
                return MM_PREMATURE_EOF;
    }
    else if (mm_is_real(matcode))
    {
        for (i = 0; i < nz; i++)
        {
            if (fscanf(f, "%d %d %lg\n", &II[i], &JJ[i], &val[i]) != 3)
                return MM_PREMATURE_EOF;
        }
    }

    else if (mm_is_pattern(matcode))
    {
        for (i = 0; i < nz; i++)
            if (fscanf(f, "%d %d", &II[i], &JJ[i]) != 2)
                return MM_PREMATURE_EOF;
    }
    else
        return MM_UNSUPPORTED_TYPE;

    return 0;
}

static int mm_read_mtx_crd_entry(FILE *f, int *II, int *JJ, double *real, double *imag,
                                 MM_typecode matcode)
{
    if (mm_is_complex(matcode))
    {
        if (fscanf(f, "%d %d %lg %lg", II, JJ, real, imag) != 4)
            return MM_PREMATURE_EOF;
    }
    else if (mm_is_real(matcode))
    {
        if (fscanf(f, "%d %d %lg\n", II, JJ, real) != 3)
            return MM_PREMATURE_EOF;
    }

    else if (mm_is_pattern(matcode))
    {
        if (fscanf(f, "%d %d", II, JJ) != 2)
            return MM_PREMATURE_EOF;
    }
    else
        return MM_UNSUPPORTED_TYPE;

    return 0;
}

static int mm_read_unsymmetric_sparse(const char *fname, int *M_, int *N_, int *nz_,
                                      double **val_, int **II_, int **JJ_)
{
    FILE *f;
    MM_typecode matcode;
    int M, N, nz;
    int i;
    double *val;
    int *II, *JJ;

    if ((f = fopen(fname, "r")) == NULL)
        return -1;

    if (mm_read_banner(f, &matcode) != 0)
    {
        printf("mm_read_unsymetric: Could not process Matrix Market banner ");
        printf(" in file [%s]\n", fname);
        return -1;
    }

    if (!(mm_is_real(matcode) && mm_is_matrix(matcode) && mm_is_sparse(matcode)))
    {
        fprintf(stderr, "Sorry, this application does not support ");
        fprintf(stderr, "Market Market type: [%s]\n",
                mm_typecode_to_str(matcode));
        return -1;
    }

    /* find out size of sparse matrix: M, N, nz .... */

    if (mm_read_mtx_crd_size(f, &M, &N, &nz) != 0)
    {
        fprintf(stderr, "read_unsymmetric_sparse(): could not parse matrix size.\n");
        return -1;
    }

    *M_ = M;
    *N_ = N;
    *nz_ = nz;

    /* reseve memory for matrices */

    II = (int *)malloc(nz * sizeof(int));
    JJ = (int *)malloc(nz * sizeof(int));
    val = (double *)malloc(nz * sizeof(double));

    *val_ = val;
    *II_ = II;
    *JJ_ = JJ;

    /* NOTE: when reading in doubles, ANSI C requires the use of the "l"  */
    /*   specifier as in "%lg", "%lf", "%le", otherwise errors will occur */
    /*  (ANSI C X3.159-1989, Sec. 4.9.6.2, p. 136 lines 13-15)            */

    for (i = 0; i < nz; i++)
    {
        fscanf(f, "%d %d %lg\n", &II[i], &JJ[i], &val[i]);
        II[i]--; /* adjust from 1-based to 0-based */
        JJ[i]--;
    }
    fclose(f);

    return 0;
}

#define max(a,b) ((a)>(b)?(a):(b))
#define min(a,b) ((a)<(b)?(a):(b))

typedef struct
{
    unsigned long long rows;
    unsigned long long cols;
    unsigned long long trows;
    unsigned long long tcols;
    double *raw_mat;
    double real_max_value;
    double real_min_value;
    double *div_mat;
} ThumbnailMatrix;

static ThumbnailMatrix mat_gen_impl(const char *filepath, int block_sz, unsigned long long mat_sz, int using_div)
{
    ThumbnailMatrix res;
    memset(&res, 0, sizeof(ThumbnailMatrix));
    res.raw_mat = NULL;
    res.div_mat = NULL;
    res.real_max_value = 0;
    res.real_min_value = 0;

    int isInteger = 0, isReal = 0, isPattern = 0, isSymmetric_tmp = 0, isComplex = 0;
    unsigned long long m, n, nnz;
    MM_typecode matcode;

    int fd = open(filepath, O_RDONLY);
    if (fd == -1)
        return res;

    struct stat sb;
    if (fstat(fd, &sb) == -1)
    {
        perror("fstat");
        close(fd);
        return res;
    }

    char *file_data = (char *)mmap(NULL, sb.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (file_data == MAP_FAILED)
    {
        perror("mmap");
        close(fd);
        return res;
    }

    if (madvise(file_data, sb.st_size, MADV_SEQUENTIAL) == -1)
    {
        perror("madvise");
        munmap(file_data, sb.st_size);
        close(fd);
        return res;
    }

    if (madvise(file_data, sb.st_size, MADV_WILLNEED) == -1)
    {
        perror("madvise");
        munmap(file_data, sb.st_size);
        close(fd);
        return res;
    }

    FILE *fp = fopen(filepath, "r");
    if (fp == NULL)
    {
        perror("fopen");
        munmap(file_data, sb.st_size);
        close(fd);
        return res;
    }

    if (mm_read_banner(fp, &matcode) != 0)
    {
        printf("Could not process Matrix Market banner.\n");
        fclose(fp);
        return res;
    }

    if (mm_is_pattern(matcode))
        isPattern = 1;
    if (mm_is_real(matcode))
        isReal = 1;
    if (mm_is_complex(matcode))
        isComplex = 1;
    if (mm_is_integer(matcode))
        isInteger = 1;
    if (mm_is_symmetric(matcode) || mm_is_hermitian(matcode))
        isSymmetric_tmp = 1;

    // Read matrix dimensions and number of non-zeros
    if (mm_read_mtx_crd_size(fp, &m, &n, &nnz) != 0)
    {
        printf("Could not read matrix dimensions.\n");
        fclose(fp);
        return res;
    }

    double row_block_sz, col_block_sz;
    res.rows = m;
    res.cols = n;

    if (block_sz > 0)
    {
        res.trows = (m + block_sz - 1) / block_sz;
        res.tcols = (n + block_sz - 1) / block_sz;
        row_block_sz = col_block_sz = block_sz;
    }
    else
    {
        unsigned long long mat_size = min(mat_sz, max(m, n));
        if (m >= n)
        {
            double rate = (double)n / (double)m;
            res.trows = mat_size;
            res.tcols = ceil(mat_size * rate);
            row_block_sz = m * 1.0 / res.trows;
            col_block_sz = n * 1.0 / res.tcols;
        }
        else
        {
            double rate = (double)m / (double)n;
            res.tcols = mat_size;
            res.trows = ceil(mat_size * rate);
            row_block_sz = m * 1.0 / res.trows;
            col_block_sz = n * 1.0 / res.tcols;
        }
    }

    unsigned long long ia, ja;
    double val, val_im;
    int is_one_based = 1;

    double *raw_mat = (double *)calloc(res.trows * res.tcols, sizeof(double));
    if (raw_mat == NULL)
    {
        printf("\nFailed to allocate memory for canvas: Matrix size = %llu x %llu, Non-zeros = %llu, Canvas size = %llu x %llu\n", m, n, nnz, res.trows, res.tcols);
        fclose(fp);
        munmap(file_data, sb.st_size);
        close(fd);
        return res;
    }

    double *div_mat = NULL;
    if (using_div)
    {
        div_mat = (double *)calloc(res.trows * res.tcols, sizeof(double));
        if (div_mat == NULL)
        {
            perror("Failed to allocate memory for counters");
            fclose(fp);
            munmap(file_data, sb.st_size);
            close(fd);
            return res;
        }
    }

    char line[MM_MAX_LINE_LENGTH];
    for (unsigned long long index = 0; index < nnz; ++index)
    {
        if (fgets(line, sizeof(line), fp) != NULL)
        {   
            if (isPattern) {
                sscanf(line, "%lli%lli", &ia, &ja);
                val = 1;
            }
            else if (isReal || isInteger)
                sscanf(line, "%lli%lli%lg", &ia, &ja, &val);
            else if (isComplex)
                sscanf(line, "%lli%lli%lg%lg", &ia, &ja, &val, &val_im);
            
            if (is_one_based && (ia == 0 || ja == 0))
                is_one_based = 0;
            if (is_one_based)
            {
                --ia;
                --ja;
            }

            unsigned long long row = min(floor(ia / row_block_sz), res.trows - 1);
            unsigned long long col = min(floor(ja / col_block_sz), res.tcols - 1);

            raw_mat[row * res.tcols + col] += val;
            if (index) {
                res.real_max_value = max(res.real_max_value, val);
                res.real_min_value = min(res.real_min_value, val);
            } else res.real_max_value = res.real_min_value = val;

            if (using_div)
            {
                div_mat[row * res.tcols + col] += 1;
            }

            if (isSymmetric_tmp && ia != ja)
            {
                raw_mat[col * res.tcols + row] += val;
                if (using_div)
                {
                    div_mat[col * res.tcols + row] += 1;
                }
            }
        }
    }

    if (using_div) {
        for (int i = 0; i < res.trows * res.tcols; ++i)
        {
            if (div_mat[i] == 0)
                div_mat[i] = 1;
        }
    }

    fclose(fp);
    munmap(file_data, sb.st_size);
    close(fd);

    res.raw_mat = raw_mat;
    res.div_mat = div_mat;

    return res;
}
