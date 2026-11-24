/*
 * gemm_scalar.c — GEMM escalar C = A x B en precisión simple (float).
 * Uso: ./gemm_scalar N        (por defecto N = 64)
 *
 * Compilar sin gem5 (pruebas con QEMU):
 *   aarch64-linux-gnu-gcc -O2 -fno-tree-vectorize -static gemm_scalar.c -o gemm_scalar -lm
 * Compilar para gem5 (con la ROI activa):
 *   ... -DUSE_M5 -I<gem5>/include ... -L<gem5>/util/m5/build/arm64/out -lm5
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifdef USE_M5
#include <gem5/m5ops.h>
#define ROI_BEGIN() m5_reset_stats(0, 0)
#define ROI_END()   m5_dump_stats(0, 0)
#else
#define ROI_BEGIN() ((void)0)
#define ROI_END()   ((void)0)
#endif

/* Valores enteros pequeños: los productos y sumas son exactos en float,
 * así la verificación no depende del orden de las operaciones. */
static void init(float *A, float *B, float *C, int N) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            A[i * N + j] = (float)((i + 2 * j) % 7 - 3);
            B[i * N + j] = (float)((3 * i + j) % 5 - 2);
            C[i * N + j] = 0.0f;
        }
}

/* Núcleo medido. Orden i-k-j: el bucle interno recorre B y C por filas
 * (acceso contiguo), mejor para la caché que el orden i-j-k. */
static void gemm(const float *A, const float *B, float *C, int N) {
    for (int i = 0; i < N; i++)
        for (int k = 0; k < N; k++) {
            float a = A[i * N + k];
            for (int j = 0; j < N; j++)
                C[i * N + j] += a * B[k * N + j];
        }
}

/* Referencia ingenua i-j-k, independiente de gemm(). Fuera de la ROI. */
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

int main(int argc, char **argv) {
    int N = (argc > 1) ? atoi(argv[1]) : 64;
    if (N <= 0) { fprintf(stderr, "N inválido\n"); return 2; }

    float *A = malloc(sizeof(float) * N * N);
    float *B = malloc(sizeof(float) * N * N);
    float *C = malloc(sizeof(float) * N * N);
    if (!A || !B || !C) { fprintf(stderr, "Sin memoria\n"); return 2; }

    init(A, B, C, N);

    ROI_BEGIN();
    gemm(A, B, C, N);
    ROI_END();

    int err = check(A, B, C, N);
    double suma = 0.0;
    for (int i = 0; i < N * N; i++) suma += C[i];
    printf("gemm_scalar N=%d  checksum=%.1f  %s\n", N, suma,
           err ? "FALLO" : "OK");

    free(A); free(B); free(C);
    return err ? 1 : 0;
}
