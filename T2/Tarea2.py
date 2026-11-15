import numpy as np
import csv

# Parametros del experimento
n_max = 18 #18
num_instancias = 100

# Almacenamiento de GAPs, prealocacion de memoria
gaps_caso1 = np.zeros((n_max, num_instancias))
gaps_caso2 = np.zeros((n_max, num_instancias))
optimos_caso1 = np.zeros((n_max, num_instancias))
optimos_caso2 = np.zeros((n_max, num_instancias))

# Generador aleatorio
rng = np.random.default_rng(69) # Semilla fija para tener resultados reproducibles

for n in range(1, n_max + 1):   # Recorrido de las dimensiones
    print(f"Procesando dimension n = {n}...")

    # Generar todas las combinaciones posibles de x en {-1, 1}
    # logrado mediante la conversion del numero de iteracion al binario
    combinaciones = np.arange(2**n, dtype=np.uint32) # se genera un arreglo de numeros enteros: 0, 1, 2, ...., n^2-1
    bits = np.arange(n, dtype=np.uint32)    # tambien es un arreglo de enteros: 0, 1, 2, ...., n-1; pero es para indicar la posicion del bit

    # pero el binario es de 0 a 1, asique hay que pasarlo a -1 y 1
    X_comb = 1.0 - 2.0 * ((combinaciones[:, None] >> bits) & 1)
    # cada numero se desplaza por "bits" y luego un and bitwise para solo tener el valor de la posicion indicada (se aplica una "mascara")
    # ademas, numpy permite un comportamiento similar a matlab en donde combinaciones es un vector columna y bits es un vector fila, el resultado es una matriz
    # en la que cada columna es una combinacion (n^2), y cada fila el valor que deberia tomar x_i

    for inst in range(num_instancias):
        # Generar matriz simetrica con elementos U[0,1]
        R = rng.random((n, n))  # R es una matriz totalmente aleatoria, y por ende, no simetrica
        Q_base = np.triu(R, 1)  # se toma solo la parte superior a la diagonal
        Q_base = Q_base + Q_base.T  # y se copia por debajo de la diagonal, el .T lo proporciona la libreria numpy y es para trasponer la matriz
        # Q_base es solo, como su nombre lo induica, una base, dado que su diagonal es 0
        # pero para el caso m=1 y m=n^2 se beneficial al solo tener que modificar la diagonal, asi se pueden correr en el mismo loop sin regenerar la matriz aleatoria

        # Evaluar la funcion objetivo para todas las combinaciones para Q_base, pero expresado como tensor, de esta manera se usa la potencia de numpy en lugar
        # de ciclos for anidados que no estan optimizados, esto es importante dado que la cantidad de combinaciones crece exponencialmente
        # ademas, numpy implementa paralelismo en este tipo de operaciones
        valores = np.einsum(
            "ij,ij->i",
            X_comb @ Q_base,
            X_comb
        )

        p_base = np.min(valores) # se busca el minimo global de la matriz base (sin la diagonal)
        # y acá la sutileza, dado que la diagonal siempre vale lo mismo para cada caso, se agrega luego, asique p_base es el minimo global para cada combinacion
        # de la Q_base de esta instancia; por lo que p_m=1 se agrega n y para p_m=n^2 se agrega n^3

        # Menor autovalor de Q_base, gracias numpy por dar los autovalores en orden
        lambda_min = np.linalg.eigvalsh(Q_base)[0]
        # Dado que la diferencia entre las matrices es la diagonal: Q_base + m1*I o +m2*I... la diferencia entre autovalores es m1 o m2

        # --- Caso 1: m = 1 ---
        m1 = 1
        # lamentablemente * es un simbolo reservado, asique p* para el caso 1 quedó como p_star1...
        p_star1 = p_base + n * m1   # El optimo es la base más el aporte de la diagonal
        optimos_caso1[n - 1, inst] = p_star1 # Lo guardamos
        cota_dual1 = n * (lambda_min + m1) # el autovalor minimo de la base está m1 por debajo, dado que posee la diagonal en cero

        gaps_caso1[n - 1, inst] = ((p_star1 - cota_dual1) / abs(p_star1))   # formula indicada en la tarea

        # --- Caso 2: m = n^2 ---
        m2 = n**2

        p_star2 = p_base + n * m2   # El optimo es la base más el aporte de la diagonal
        optimos_caso2[n - 1, inst] = p_star2 # lo guardamos
        cota_dual2 = n * (lambda_min + m2) # el autovalor minimo de la base está m2 por debajo, dado que posee la diagonal en cero

        gaps_caso2[n - 1, inst] = ((p_star2 - cota_dual2) / abs(p_star2))   # formula indicada en la tarea

    print(f"  Completado n = {n}")


# --- Guardado de datos y exportacion a .csv ---

# Estadisticas de GAP
mean_gap1 = np.mean(gaps_caso1, axis=1)
std_gap1 = np.std(gaps_caso1, axis=1, ddof=1)

mean_gap2 = np.mean(gaps_caso2, axis=1)
std_gap2 = np.std(gaps_caso2, axis=1, ddof=1)

# Estadisticas de optimos
mean_p1 = np.mean(optimos_caso1, axis=1)
mean_p2 = np.mean(optimos_caso2, axis=1)

# Peor caso medio (promedio de los peores valores de cada dimension)
worst_mean_p1 = np.max(optimos_caso1, axis=1)
worst_mean_p2 = np.max(optimos_caso2, axis=1)

# Mejor y peor instancia de todas las dimensiones
best_p1 = np.min(optimos_caso1, axis=1)
worst_p1 = np.max(optimos_caso1, axis=1)

best_p2 = np.min(optimos_caso2, axis=1)
worst_p2 = np.max(optimos_caso2, axis=1)


# Exportar resultados resumidos

with open("T2_resultados.csv", "w", newline="") as archivo:
    writer = csv.writer(archivo)

    writer.writerow([
        "n",
        "mean_gap_m1",
        "std_gap_m1",
        "mean_p_m1",
        "worst_p_m1",
        "best_p_m1",
        "worst_instance_p_m1",
        "mean_gap_mn2",
        "std_gap_mn2",
        "mean_p_mn2",
        "worst_p_mn2",
        "best_p_mn2",
        "worst_instance_p_mn2"
    ])

    for i in range(n_max):
        writer.writerow([
            i + 1,
            mean_gap1[i],
            std_gap1[i],
            mean_p1[i],
            worst_mean_p1[i],
            best_p1[i],
            worst_p1[i],
            mean_gap2[i],
            std_gap2[i],
            mean_p2[i],
            worst_mean_p2[i],
            best_p2[i],
            worst_p2[i]
        ])


print("\nExperimento finalizado.")
print("Archivos generados:")
print("  T2_resultados.csv")
print("  T2_instancias.csv")

