import csv
import matplotlib.pyplot as plt

# Leer resultados del experimento
n_valores = []
mean_gap1 = []
std_gap1 = []
mean_gap2 = []
std_gap2 = []

with open("T2_resultados.csv", "r", newline="") as archivo:
    reader = csv.DictReader(archivo)
    for fila in reader:
        n_valores.append(int(fila["n"]))
        mean_gap1.append(float(fila["mean_gap_m1"]))
        std_gap1.append(float(fila["std_gap_m1"]))
        mean_gap2.append(float(fila["mean_gap_mn2"]))
        std_gap2.append(float(fila["std_gap_mn2"]))

# Mostrar resultados en pantalla
print("\nRESULTADOS DEL EXPERIMENTO")
print("n     GAP m=1 (%)     GAP m=n^2 (%)")
for i in range(len(n_valores)):
    print(
        f"{n_valores[i]:2d}    "
        f"{mean_gap1[i]*100:12.4f}    "
        f"{mean_gap2[i]*100:12.4f}"
    )

# Funcion para generar los graficos
def graficar_gap(n, promedio, desviacion, titulo, archivo):
    promedio_pct = [x * 100 for x in promedio]
    desviacion_pct = [x * 100 for x in desviacion]
    plt.figure(figsize=(9, 5))

    # Curva del GAP promedio
    plt.plot(
        n,
        promedio_pct,
        marker="o",
        markersize=4,
        linewidth=1.8,
        label="GAP promedio"
    )

    # Region sombreada de desviacion estandar
    inferior = [
        p - d for p, d in zip(promedio_pct, desviacion_pct)
    ]
    superior = [
        p + d for p, d in zip(promedio_pct, desviacion_pct)
    ]

    plt.fill_between(
        n,
        inferior,
        superior,
        alpha=0.2,
        label="Promedio ± desviación estándar"
    )

    plt.xlabel("Dimensión n")
    plt.ylabel("GAP relativo (%)")
    plt.title(titulo)
    plt.xticks(n)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(archivo, dpi=300, bbox_inches="tight")
    y_max = max(superior)
    plt.ylim(-0.1 * y_max, None)
    plt.show()
    plt.close()


# Grafico 1: m = 1
graficar_gap(
    n_valores,
    mean_gap1,
    std_gap1,
    "GAP relativo promedio - Caso m = 1",
    "GAP_m1.png"
)

# Grafico 2: m = n^2
graficar_gap(
    n_valores,
    mean_gap2,
    std_gap2,
    "GAP relativo promedio - Caso m = n^2",
    "GAP_mn2.png"
)


print("\nGraficos generados:")
print("  GAP_m1.png")
print("  GAP_mn2.png")
