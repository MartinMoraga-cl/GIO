import numpy as np
import csv

# Parametros del experimento
n_max = 18
num_instancias = 100

# Almacenamiento de GAPs
gaps_caso1 = np.zeros((n_max, num_instancias))
gaps_caso2 = np.zeros((n_max, num_instancias))

# Generador aleatorio
rng = np.random.default_rng()

for n in range(1, n_max + 1):
    print(f"Procesando dimension n = {n}...")

    # Generar todas las combinaciones posibles de x en {-1, 1}
    combinaciones = np.arange(2**n, dtype=np.uint32)
    bits = np.arange(n, dtype=np.uint32)

    X_comb = 1.0 - 2.0 * ((combinaciones[:, None] >> bits) & 1)

    for inst in range(num_instancias):

        # Generar matriz simetrica con elementos U[0,1]
        R = rng.random((n, n))
        Q_base = np.triu(R, 1)
        Q_base = Q_base + Q_base.T

        # Evaluar todas las combinaciones para Q_base
        valores = np.einsum(
            "ij,ij->i",
            X_comb @ Q_base,
            X_comb
        )

        p_base = np.min(valores)

        # Menor autovalor de Q_base
        lambda_min = np.linalg.eigvalsh(Q_base)[0]

        # --------------------------------
        # Caso 1: m = 1
        # --------------------------------
        m1 = 1

        p_star1 = p_base + n * m1
        cota_dual1 = n * (lambda_min + m1)

        gaps_caso1[n - 1, inst] = (
            (p_star1 - cota_dual1) / abs(p_star1)
        )

        # --------------------------------
        # Caso 2: m = n^2
        # --------------------------------
        m2 = n**2

        p_star2 = p_base + n * m2
        cota_dual2 = n * (lambda_min + m2)

        gaps_caso2[n - 1, inst] = (
            (p_star2 - cota_dual2) / abs(p_star2)
        )

    print(f"  Completado n = {n}")


# ==========================================
# Calcular promedios y desviaciones estandar
# ==========================================

mean_gap1 = np.mean(gaps_caso1, axis=1)
std_gap1 = np.std(gaps_caso1, axis=1, ddof=1)

mean_gap2 = np.mean(gaps_caso2, axis=1)
std_gap2 = np.std(gaps_caso2, axis=1, ddof=1)


# ==========================================
# Exportar resultados resumidos
# ==========================================

with open("T2_resultados.csv", "w", newline="") as archivo:
    writer = csv.writer(archivo)

    writer.writerow([
        "n",
        "mean_gap_m1",
        "std_gap_m1",
        "mean_gap_mn2",
        "std_gap_mn2"
    ])

    for i in range(n_max):
        writer.writerow([
            i + 1,
            mean_gap1[i],
            std_gap1[i],
            mean_gap2[i],
            std_gap2[i]
        ])


# ==========================================
# Exportar GAPs individuales
# ==========================================

with open("T2_instancias.csv", "w", newline="") as archivo:
    writer = csv.writer(archivo)

    writer.writerow([
        "n",
        "instancia",
        "caso",
        "m",
        "GAP"
    ])

    for i in range(n_max):
        for inst in range(num_instancias):

            writer.writerow([
                i + 1,
                inst + 1,
                "m=1",
                1,
                gaps_caso1[i, inst]
            ])

            writer.writerow([
                i + 1,
                inst + 1,
                "m=n^2",
                (i + 1)**2,
                gaps_caso2[i, inst]
            ])


print("\nExperimento finalizado.")
print("Archivos generados:")
print("  T2_resultados.csv")
print("  T2_instancias.csv")

