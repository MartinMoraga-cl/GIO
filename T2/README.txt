- TAREA 2:

El código implementa una solución por fuerza bruta basada en NumPy para la resolución y análisis estadístico de problemas de optimización cuadrática con variables binarias (x_i in {-1, 1}).

Estrategias del codigo:

1. Vectorización total del espacio de soluciones: Se evito todo lo posible el uso de los ciclos `for` anidados para recorrer el espacio de soluciones factibles. Mediante operaciones a nivel de bits (desplazamientos y máscaras bitwise) y el uso de broadcasting de NumPy, se genera la matriz completa de combinaciones (X_comb) en un solo bloque contiguo en memoria, aprobechando la cache de las CPUs.

2. Evaluación masiva con np.einsum: La función objetivo se evalúa de forma paralelizada utilizando contracción de tensores con np.einsum("ij,ij->i", X_comb @ Q_base, X_comb), aprovechando las rutinas optimizadas de bajo nivel de NumPy en lugar de bucles lentos en el intérprete de Python.

3. Desacople de la matriz base (Q_base) y la diagonal: Dado que los casos evaluados solo difieren en los parámetros de ladiagonal (Q_base + m*I), se explotan dos propiedades analíticas para evitar duplicar cómputos caros:
   - Evaluación única de la función objetivo: Como las variables cumplen x_i^2 = 1, el aporte de la diagonal es un escalar constante (n*m). Por lo tanto, el óptimo se calcula directamente a partir de la base como p* = p_base + n * m, sin reevaluar las combinaciones para cada m.
   - Relacion de los autovalores: Los autovalores de la matriz completa cumplen que el autovalor mínimo es igual a lambda_min(Q_base) + m, evitando recalcular la diagonalización completa y buscar mínimos repetidas veces, lo cual para dimensiones altas es caro computacionalmente.


Contenido del Zip:
- Tarea2OR_Moraga_Taito.pdf: Informe detallado con el desarrollo analítico.
- Tarea2.py: Script principal. Ejecuta la generación de instancias, busca los óptimos por fuerza bruta, obtiene los GAPs y exporta los resultados a CSV.
- graficar.py: Script complementario. Lee los datos CSV consolidados y genera las gráficas de comportamiento del GAP relativo promedio con su respectiva desviación estándar.
- T2_resultados.csv: Archivo con las estadísticas resumidas por dimensión n (medias, desviaciones, mejores y peores casos para ambos escenarios de m).
- T2_instancias.csv: Registro detallado con los resultados individuales por cada ejecución e instancia.
- GAP_m1.png: Gráfico de la evolución del GAP relativo para el caso m = 1.
- GAP_mn2.png: Gráfico de la evolución del GAP relativo para el caso m = n^2.
- bruta_fuerza.m: iteracion temprana de la estrategia para entender mejor el problema, hecho en Octave (similar a Matlab).
