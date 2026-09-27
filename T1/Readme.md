# Tarea 1 — ILN250 2s26

## Integrantes

- Martín Moraga González - 202321062-5
- Renzo Taito Rojas - 202321057-9

## Estructura del proyecto

```text
T1/
├── datos/
│   ├── demanda.csv
│   └── parametros.csv
├── resultados_base/
│   ├── despacho.csv
│   └── resumen.txt
├── resultados_variacion_a/
│   ├── despacho.csv
│   └── resumen.txt
├── resultados_variacion_B/
│   ├── despacho_variacion_B.csv
│   └── resumen_variacion_B.txt
├── resultados_variacion_c/
│   ├── barrido_multa.csv
│   ├── barrido_multa.txt
│   ├── despacho.csv
│   ├── emisiones_diarias.csv
│   └── resumen.txt
├── generadorDatos.py
├── Tarea1.py
├── Tarea1_A.py
├── Tarea1_B.py
├── Tarea1_C.py
├── Tarea1_C_barrido.py
├── Graficos.xlsx
├── Readme.md
└── Tarea_1_ILN250_2s26_ENUNCIADO.pdf
```

## Descripción de los archivos

### Modelos

- `Tarea1.py`: implementación y resolución del modelo base.
- `Tarea1_A.py`: modelo base incorporando un sistema de almacenamiento mediante batería.
- `Tarea1_B.py`: modelo base incorporando demanda interrumpible/respuesta de demanda.
- `Tarea1_C.py`: modelo base incorporando una penalización fija por cada día que supera el umbral de emisiones.
- `Tarea1_C_barrido.py`: código auxiliar utilizado para estudiar la sensibilidad de la solución frente a distintos valores de la penalización `F`. No es necesario para resolver la instancia principal de la variación C.
- `generadorDatos.py`: genera la instancia de datos utilizada por los distintos modelos.

Los cuatro modelos principales corresponden a la misma instancia del problema. La generación de datos utiliza una semilla fija, por lo que los resultados son reproducibles.

### Datos

La carpeta `datos/` contiene la instancia utilizada por los modelos:

- `demanda.csv`: datos de los 168 períodos, incluyendo demanda neta, precio de importación, reserva y variables utilizadas en la generación de la demanda.
- `parametros.csv`: parámetros estáticos del problema, incluyendo características de las unidades generadoras, costos, límites y parámetros generales.

Los datos fueron generados mediante `generadorDatos.py`.

### Resultados

Cada modelo genera sus resultados en una carpeta independiente:

- `resultados_base/`: resultados del modelo base.
- `resultados_variacion_a/`: resultados de la variación A.
- `resultados_variacion_B/`: resultados de la variación B.
- `resultados_variacion_c/`: resultados de la variación C.

Los archivos `despacho.csv` contienen el despacho obtenido para cada período. Los archivos `resumen.txt` contienen los principales resultados de cada ejecución.

La variación C incluye adicionalmente:

- `emisiones_diarias.csv`: emisiones calculadas para cada día.
- `barrido_multa.csv`: resultados del análisis de sensibilidad de la penalización.
- `barrido_multa.txt`: resumen del barrido realizado.

### Visualización

`Graficos.xlsx` contiene una recopilación manual de los resultados generados por los modelos. El archivo está organizado mediante distintas hojas y contiene las tablas y gráficos utilizados en el informe.

Este archivo no constituye una fuente independiente de resultados: sus datos provienen de los archivos `CSV` generados por los modelos.

## Librerías utilizadas

Los códigos utilizan:

- `pyomo.environ`
- `numpy`
- `math`

El solver utilizado para resolver los modelos es **HiGHS**, mediante la interfaz `appsi_highs` de Pyomo.

## Entorno de ejecución

Se recomienda utilizar un entorno virtual de Python para instalar las dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pyomo numpy
```

El solver HiGHS debe estar disponible para Pyomo. Con `highspy` puede instalarse mediante:

```bash
pip install highspy
```

## Ejecución

Desde el directorio que contiene los archivos de la tarea:

```bash
python generadorDatos.py
python Tarea1.py
python Tarea1_A.py
python Tarea1_B.py
python Tarea1_C.py
```

Los resultados se generan en las carpetas correspondientes.

El archivo `Tarea1_C_barrido.py` es independiente de la ejecución normal de la variación C y se utilizó únicamente para estudiar la sensibilidad del modelo frente a diferentes valores de `F`:

```bash
python Tarea1_C_barrido.py
```

Este análisis puede requerir un tiempo de ejecución considerablemente mayor que las resoluciones individuales, debido a que resuelve repetidamente el modelo para distintos valores de la penalización.

## Convención de índices

Los modelos están implementados en Python utilizando índices desde `0` hasta `167`, correspondientes a los 168 períodos de la instancia.

En la formulación matemática del informe se utiliza la convención habitual:

```text
t = 1, ..., 168
```

Por lo tanto, el período `t=0` del código corresponde al período `t=1` de la formulación, y así sucesivamente. Esta diferencia corresponde únicamente a la indexación utilizada por Python y no representa una diferencia entre las instancias.

## Reproducibilidad

La instancia utiliza una semilla fija para la generación de números aleatorios. De esta forma, la demanda, precios y demás variables generadas pueden reproducirse manteniendo el mismo procedimiento de generación.

Las distintas variaciones utilizan la misma instancia base, de modo que las diferencias observadas entre escenarios corresponden a las modificaciones realizadas al modelo y no a cambios en los datos de entrada.

## Observaciones

El análisis de sensibilidad de la variación C se realizó mediante `Tarea1_C_barrido.py`. Este archivo tiene carácter auxiliar y no es necesario para reproducir el resultado principal presentado para `F = 100000000` CLP.

Los resultados principales del informe corresponden a las ejecuciones individuales de `Tarea1.py`, `Tarea1_A.py`, `Tarea1_B.py` y `Tarea1_C.py`.
