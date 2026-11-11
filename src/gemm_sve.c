/*
 * gemm_sve.c — GEMM C = A x B en float con intrínsecos SVE (ACLE).
 * El código es agnóstico a la longitud vectorial (VLA): el mismo binario
 * Uso: ./gemm_sve N        (por defecto N = 64)
 *
 * Compilar sin gem5 (pruebas con QEMU):
 *   aarch64-linux-gnu-gcc -O2 -march=armv8-a+sve -fno-tree-vectorize -static gemm_sve.c -o gemm_sve -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <arm_sve.h>

#ifdef USE_M5
#include <gem5/m5ops.h>
#define ROI_BEGIN() m5_reset_stats(0, 0)
#define ROI_END()   m5_dump_stats(0, 0)
#else
#define ROI_BEGIN() ((void)0)
#define ROI_END()   ((void)0)
#endif

/* Misma inicialización que gemm_scalar.c: el checksum debe coincidir. */
static void init(float *A, float *B, float *C, int N) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            A[i * N + j] = (float)((i + 2 * j) % 7 - 3);
            B[i * N + j] = (float)((3 * i + j) % 5 - 2);
            C[i * N + j] = 0.0f;
        }
}

/* Núcleo medido. Mismo orden i-k-j que la versión escalar, pero el bucle
 * interno procesa svcntw() floats por iteración (4 con VL=128, 32 con 1024).
 * svwhilelt crea un predicado que apaga los carriles que pasan de N,
 * así no hace falta un bucle de "residuo" aunque N no sea múltiplo de VL. */
static void gemm(const float *A, const float *B, float *C, int N) {
    for (int i = 0; i < N; i++)
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

/* Referencia escalar ingenua i-j-k. Fuera de la ROI. */
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
    printf("gemm_sve N=%d  VL=%d bits  checksum=%.1f  %s\n", N,
           (int)svcntb() * 8, suma, err ? "FALLO" : "OK");

    free(A); free(B); free(C);
    return err ? 1 : 0;
}
