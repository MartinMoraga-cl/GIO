import numpy as np
import math

T = 168 # Periodos, en hrs, asique solo una semanda
horas = range(T) # genera el listados de 0 a 167
SEMILLA = 480
RNG = np.random.default_rng(SEMILLA) # raro el python es.... esto es como intanciar un generador de rng....

perfil_diario = [   # estos corchetes son una lista... los otros son Diccionarios
    0.55, 0.50, 0.47, 0.45, 0.46, 0.52, 0.62, 0.75, 0.85, 0.88, 0.90, 0.89,
    0.86, 0.85, 0.86, 0.88, 0.92, 0.97, 1.00, 0.98, 0.90, 0.80, 0.70, 0.60
]

ppeak = RNG.normal(loc=300, scale=0.05*300)
epsilon = RNG.normal(loc=0, scale=0.03, size=T) 
gamma = [0.8 if t > 120 else 1.0 for t in range(T)]

demanda_neta = [0] * T # notacion WEONA que tiene el python..., se inicializa una lista de T 0s

# importe
eta = RNG.normal(loc=0, scale=0.05, size=T)
precio_importe = [0] * T # bueee, ya di mi opinion de esto..., en C es solo precio_importe[T] = {0}, muyo mejor para los ojos
max_importe = 80 #MW

# reserva 
reserva = [0] * T

# demanda, importe y reserva salieron a iterar...
for t in range(T):
    hora = t%24
    demanda_neta[t]   = round(ppeak*gamma[t]*perfil_diario[hora]*(1+epsilon[t]))
    precio_importe[t] = round((100000+90000*perfil_diario[hora])*(1+eta[t]))
    reserva[t] = round(demanda_neta[t]*0.1)
# ...Y volvieron evaluados :)

#   Diccionarios, la forma "bonita"
##  Generadores
generadores = ["Gas_Base_1","Gas_Base_2", "Diesel_Med_1", "Diesel_Med_2", "Peaker"] # debo controlarme y contar desde el 1.... ufff
Pmin = {
    "Gas_Base_1": 40,"Gas_Base_2": 35, "Diesel_Med_1": 15, "Diesel_Med_2": 12, "Peaker": 8
}
Pmax = {
    "Gas_Base_1": 120,"Gas_Base_2": 100, "Diesel_Med_1": 60, "Diesel_Med_2": 50, "Peaker": 40
}
coste_mw = {
    "Gas_Base_1": 45000,"Gas_Base_2": 48000, "Diesel_Med_1": 85000, "Diesel_Med_2": 90000, "Peaker": 120000
}
coste_partida = {
    "Gas_Base_1": 2000000,"Gas_Base_2": 1800000, "Diesel_Med_1": 600000, "Diesel_Med_2": 500000, "Peaker": 200000
}
coste_nl = {
    "Gas_Base_1": 300000,"Gas_Base_2": 260000, "Diesel_Med_1": 120000, "Diesel_Med_2": 100000, "Peaker": 50000
}
rampa = {
    "Gas_Base_1": 30,"Gas_Base_2": 30, "Diesel_Med_1": 40, "Diesel_Med_2": 40, "Peaker": 40
}
X0 = {
    "Gas_Base_1": 40,"Gas_Base_2": 35, "Diesel_Med_1": 0, "Diesel_Med_2": 0, "Peaker": 0
}
U0 = {
    "Gas_Base_1": 1,"Gas_Base_2": 1, "Diesel_Med_1": 0, "Diesel_Med_2": 0, "Peaker": 0    
}

##  Parte de la variacion de este ejercicio
### Algo entrete de que sean periodos de 1 hora implica que si se pide del banco 5MW entonces se usan 5MWh... sin conversiones de unidades!
baterias = ["Banco_Baterias_1"] # Solo se pide una unica bateria.... pero para dejarlo expansible....
Smax = {       # maxima Energia almacenada: MWh  
    "Banco_Baterias_1": 200
}
Bch = {     # Tasa de descarga, potencia: MW
    "Banco_Baterias_1": 60
}
Bdis = {    # Tasa de carga, potencia: MW 
    "Banco_Baterias_1": 60 
}
eta_ch = {  # Eficiencia carga, adimensional
    "Banco_Baterias_1": 0.95
}
eta_dis = { # Eficiencia descarga, adimensional
    "Banco_Baterias_1": 0.95
}
S0 = {      # Estado inicial de energia almacenada: MWh
    "Banco_Baterias_1": 100
}





# ============================================================
# Guardar parámetros
# ============================================================
import csv
import os

CARPETA_RESULTADOS = "datos"
os.makedirs(CARPETA_RESULTADOS, exist_ok=True)


# ============================================================
# Datos por periodo
# ============================================================

archivo = os.path.join(
    CARPETA_RESULTADOS,
    "demanda.csv"
)

with open(
    archivo,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "periodo",
        "dia",
        "hora_dia",
        "demanda_neta_mw",
        "precio_importe_mwh",
        "reserva_mw",
        "epsilon",
        "eta",
        "gamma"
    ])

    for t in range(T):

        writer.writerow([
            t,
            t // 24 + 1,
            t % 24,
            demanda_neta[t],
            precio_importe[t],
            reserva[t],
            epsilon[t],
            eta[t],
            gamma[t]
        ])


# ============================================================
# Parámetros generales
# ============================================================

archivo = os.path.join(
    CARPETA_RESULTADOS,
    "parametros.csv"
)

with open(
    archivo,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "parametro",
        "tipo",
        "elemento",
        "valor",
        "unidad"
    ])

    writer.writerow([
        "T",
        "general",
        "",
        T,
        "h"
    ])

    writer.writerow([
        "SEMILLA",
        "general",
        "",
        SEMILLA,
        "-"
    ])

    writer.writerow([
        "ppeak",
        "general",
        "",
        ppeak,
        "MW"
    ])

    writer.writerow([
        "max_importe",
        "general",
        "",
        max_importe,
        "MW"
    ])

    # --------------------------------------------------------
    # Perfil diario
    # --------------------------------------------------------

    for h in range(24):

        writer.writerow([
            "perfil_diario",
            "perfil",
            h,
            perfil_diario[h],
            "-"
        ])


    # --------------------------------------------------------
    # Generadores
    # --------------------------------------------------------

    for g in generadores:

        writer.writerow([
            "Pmin",
            "generador",
            g,
            Pmin[g],
            "MW"
        ])

        writer.writerow([
            "Pmax",
            "generador",
            g,
            Pmax[g],
            "MW"
        ])

        writer.writerow([
            "coste_mw",
            "generador",
            g,
            coste_mw[g],
            "$/MWh"
        ])

        writer.writerow([
            "coste_partida",
            "generador",
            g,
            coste_partida[g],
            "$"
        ])

        writer.writerow([
            "coste_nl",
            "generador",
            g,
            coste_nl[g],
            "$/h"
        ])

        writer.writerow([
            "rampa",
            "generador",
            g,
            rampa[g],
            "MW/h"
        ])

        writer.writerow([
            "X0",
            "generador",
            g,
            X0[g],
            "MW"
        ])

        writer.writerow([
            "U0",
            "generador",
            g,
            U0[g],
            "-"
        ])


print(f"Datos generados correctamente.")
print(f"Demanda: {CARPETA_RESULTADOS}/demanda.csv")
print(f"Parámetros: {CARPETA_RESULTADOS}/parametros.csv")
