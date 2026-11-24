/*
 * gemm_omp.c — GEMM paralelo C = A x B (float), repartido por filas entre hilos.
 * Uso: ./gemm_omp N T        (por defecto N = 64, T = 1)
 *
 * Implementado con pthreads, no con OpenMP: en el modo SE de gem5 OpenMP suele
 * fallar (su runtime consulta /proc y /sys, que gem5 no emula bien), mientras que
 * pthreads solo necesita clone y futex, que gem5 sí emula. El nombre se mantiene
 * por consistencia con el plan del grupo.
 *
 * Reglas para E4:
 *   - En gem5 se necesitan al menos T núcleos (se.py -n T): en modo SE cada hilo
 *     ocupa un contexto de hardware y no hay planificador que los multiplexe.
 *   - La ROI cubre solo el cálculo en paralelo: los hilos se crean ANTES de la ROI
 *     y se sincronizan con barreras, así la creación de hilos (llamadas al sistema
 *     emuladas por gem5, con costo poco realista) no contamina la medición.
 *
 * Reparto: el hilo t calcula las filas [t*N/T, (t+1)*N/T). Bloques contiguos de
 * filas: cada hilo escribe en su propia zona de C (sin falso compartido salvo, a
 * lo sumo, una línea de caché en cada frontera).
 *
 * Versión vectorial (para E6): con -DUSE_SVE -march=armv8-a+sve el bucle interno
 * usa el mismo kernel SVE que gemm_sve.c, agnóstico a la longitud vectorial.
 * Así E6 combina las dos formas de paralelismo: filas repartidas entre núcleos
 * (como E4) y varios elementos de C por instrucción dentro de cada núcleo (como
 * E3). Todo lo demás (reparto, barreras, ROI, verificación) es idéntico, de modo
 * que la diferencia entre gemm_omp y gemm_omp_sve es solo el kernel.
 *
 * Compilar para QEMU:
 *   aarch64-linux-gnu-gcc -O2 -fno-tree-vectorize -static -pthread gemm_omp.c -o gemm_omp -lm
 *   ... -march=armv8-a+sve -DUSE_SVE gemm_omp.c -o gemm_omp_sve -lm     (versión SVE)
 * Compilar para gem5 (ROI activa): agregar -DUSE_M5 -I<gem5>/include ... libm5.a
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <pthread.h>

#ifdef USE_SVE
#include <arm_sve.h>
#define NOMBRE "gemm_omp_sve"
#else
#define NOMBRE "gemm_omp"
#endif

#ifdef USE_M5
#include <gem5/m5ops.h>
#define ROI_BEGIN() m5_reset_stats(0, 0)
#define ROI_END()   m5_dump_stats(0, 0)
#else
#define ROI_BEGIN() ((void)0)
#define ROI_END()   ((void)0)
#endif

#define MAX_THREADS 64

/* Misma inicialización que gemm_scalar.c: enteros pequeños, sumas exactas en float. */
static void init(float *A, float *B, float *C, int N) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            A[i * N + j] = (float)((i + 2 * j) % 7 - 3);
            B[i * N + j] = (float)((3 * i + j) % 5 - 2);
            C[i * N + j] = 0.0f;
        }
}

#ifdef USE_SVE
/* Núcleo medido, versión SVE: el mismo kernel que gemm_sve.c restringido a las
 * filas [i0, i1). El bucle interno procesa svcntw() floats por iteración (4 con
 * VL = 128 bits, 32 con 1024) y svwhilelt apaga los carriles que pasan de N. */
static void gemm_rows(const float *A, const float *B, float *C, int N, int i0, int i1) {
    for (int i = i0; i < i1; i++)
        for (int k = 0; k < N; k++) {
            svfloat32_t a = svdup_n_f32(A[i * N + k]);   /* a en todos los carriles */
            for (int j = 0; j < N; j += svcntw()) {
                svbool_t pg = svwhilelt_b32_s32(j, N);
                svfloat32_t b = svld1_f32(pg, &B[k * N + j]);
                svfloat32_t c = svld1_f32(pg, &C[i * N + j]);
                c = svmla_f32_x(pg, c, a, b);              /* c += a * b */
                svst1_f32(pg, &C[i * N + j], c);
            }
        }
}
#else
/* Núcleo medido: mismo orden i-k-j que gemm_scalar.c, restringido a [i0, i1). */
static void gemm_rows(const float *A, const float *B, float *C, int N, int i0, int i1) {
    for (int i = i0; i < i1; i++)
        for (int k = 0; k < N; k++) {
            float a = A[i * N + k];
            for (int j = 0; j < N; j++)
                C[i * N + j] += a * B[k * N + j];
        }
}
#endif

/* Referencia ingenua i-j-k, independiente del núcleo paralelo. Fuera de la ROI. */
static int check(const float *A, const float *B, const float *C, int N) {
    int errores = 0;
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            float ref = 0.0f;
            for (int k = 0; k < N; k++)
                ref += A[i * N + k] * B[k * N + j];
            if (fabsf(ref - C[i * N + j]) > 1e-3f) {
                if (errores < 5)
                    printf("Error en C[%d][%d]: %f (esperado %f)\n",
                           i, j, C[i * N + j], ref);
                errores++;
            }
        }
    return errores;
}

typedef struct {
    int id, T, N;
    const float *A, *B;
    float *C;
} args_t;

static pthread_barrier_t barrier;

/* Todos los hilos (incluido el principal, id = 0) ejecutan esto. */
static void *worker(void *p) {
    args_t *a = (args_t *)p;
    int i0 = (int)((long)a->id * a->N / a->T);
    int i1 = (int)((long)(a->id + 1) * a->N / a->T);

    pthread_barrier_wait(&barrier);          /* todos los hilos creados y listos */
    if (a->id == 0) ROI_BEGIN();
    pthread_barrier_wait(&barrier);          /* nadie empieza antes del reset */

    gemm_rows(a->A, a->B, a->C, a->N, i0, i1);

    pthread_barrier_wait(&barrier);          /* esperar al hilo más lento */
    if (a->id == 0) ROI_END();
    return NULL;
}

int main(int argc, char **argv) {
    int N = (argc > 1) ? atoi(argv[1]) : 64;
    int T = (argc > 2) ? atoi(argv[2]) : 1;
    if (N <= 0) { fprintf(stderr, "N inválido\n"); return 2; }
    if (T <= 0 || T > MAX_THREADS || T > N) {
        fprintf(stderr, "T inválido (1..%d y T <= N)\n", MAX_THREADS);
        return 2;
    }

    float *A = malloc(sizeof(float) * N * N);
    float *B = malloc(sizeof(float) * N * N);
    float *C = malloc(sizeof(float) * N * N);
    if (!A || !B || !C) { fprintf(stderr, "Sin memoria\n"); return 2; }

    init(A, B, C, N);

    pthread_t th[MAX_THREADS];
    args_t args[MAX_THREADS];
    pthread_barrier_init(&barrier, NULL, (unsigned)T);

    for (int t = 0; t < T; t++)
        args[t] = (args_t){ .id = t, .T = T, .N = N, .A = A, .B = B, .C = C };
    for (int t = 1; t < T; t++)
        if (pthread_create(&th[t], NULL, worker, &args[t]) != 0) {
            fprintf(stderr, "No se pudo crear el hilo %d (¿hay %d núcleos en gem5?)\n", t, T);
            return 2;
        }
    worker(&args[0]);                         /* el hilo principal es el hilo 0 */
    for (int t = 1; t < T; t++)
        pthread_join(th[t], NULL);
    pthread_barrier_destroy(&barrier);

    int err = check(A, B, C, N);
    double suma = 0.0;
    for (int i = 0; i < N * N; i++) suma += C[i];
#ifdef USE_SVE
    printf(NOMBRE " N=%d T=%d VL=%d  checksum=%.1f  %s\n", N, T,
           (int)svcntw() * 32, suma, err ? "FALLO" : "OK");
#else
    printf(NOMBRE " N=%d T=%d  checksum=%.1f  %s\n", N, T, suma,
           err ? "FALLO" : "OK");
#endif

    free(A); free(B); free(C);
    return err ? 1 : 0;
}
