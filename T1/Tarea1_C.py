# Ese codigo sigue siendo el original, hay que cambiarle el proposito....

import pyomo.environ as pyo
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
gamma = [0.8 if t >= 120 else 1.0 for t in range(T)]

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

factor_emision = { # tCO2/MWh
    "Gas_Base_1": 0.35,"Gas_Base_2": 0.38, "Diesel_Med_1": 0.65, "Diesel_Med_2": 0.68, "Peaker": 0.75    
}

umbral_diario = 1500 # tCO2/diarias
monto_multa = 100000000  # supongo que todo lo monetario está en clp....

dias = range(7)

BIG_M_Umbral = sum(
    24 * Pmax[g] * factor_emision[g]
    for g in generadores
) # para no poner un numero Arbitrariamente alto, se pone el valor que produciria 
  # encender todos los generadores al maximo, siendo el techo absoluto de lo lograble

#   Solver de programacion lineal
#   De acá en más se usan los nombres de la guia

modelo = pyo.ConcreteModel()

##  Los conjuntos [ pyo.Set() ]
modelo.G = pyo.Set(initialize=generadores)
modelo.T = pyo.Set(initialize=horas)
modelo.D = pyo.Set(initialize=dias)

##  Parametros
modelo.Pmin = pyo.Param(
    modelo.G,
    initialize=Pmin
)
modelo.Pmax = pyo.Param(
    modelo.G,
    initialize=Pmax
)
modelo.cvar = pyo.Param(
    modelo.G,
    initialize=coste_mw
)
modelo.cstart = pyo.Param(
    modelo.G,
    initialize=coste_partida
)
modelo.cnl = pyo.Param(
    modelo.G,
    initialize=coste_nl
)
modelo.R = pyo.Param(
    modelo.G,
    initialize=rampa
)

modelo.demanda = pyo.Param(
    modelo.T,
    initialize=lambda modelo, t: demanda_neta[t] # Uhhhh????
)
modelo.reserva = pyo.Param(
    modelo.T,
    initialize=lambda modelo, t: reserva[t]
)
modelo.precio_imp = pyo.Param(
    modelo.T,
    initialize=lambda modelo, t: precio_importe[t]
)
modelo.X0 = pyo.Param( # el estado inicial como parametor
    modelo.G,
    initialize=X0
)
modelo.U0 = pyo.Param( # el estado inicial como parametro
    modelo.G,
    initialize=U0
)

modelo.E_day = pyo.Param( # limite diario
    initialize=umbral_diario
)
modelo.F = pyo.Param( # coste fijo por exceso de Emisiones
    initialize=monto_multa
)
modelo.e_g = pyo.Param( # produccion de tCO2 por cada MWh generados por g
    modelo.G,
    initialize=factor_emision
)



##  Las Variables
modelo.X = pyo.Var( # Potencia generada por g en t
    modelo.G,
    modelo.T,
    domain=pyo.NonNegativeReals
)
modelo.U = pyo.Var( # Encendido (o no): g en t
    modelo.G,
    modelo.T,
    domain=pyo.Binary
)
modelo.Y = pyo.Var( # Partida
    modelo.G,
    modelo.T,
    domain=pyo.Binary
)
modelo.Z = pyo.Var( # Potencia Comprada
    modelo.T,
    domain=pyo.NonNegativeReals
)
# modificacion es 
modelo.E = pyo.Var( # Emisiones del complejo por cada dia
    modelo.D,
    domain=pyo.NonNegativeReals
)
modelo.M = pyo.Var( # 1 si el complejo es Multado; 0 en caso contrario; por cada DIA
    modelo.D,
    domain=pyo.Binary
)

##  Funcion Objetivo

def objetivo(modelo):
    return sum(
        (modelo.cvar[g] * modelo.X[g, t] + modelo.cstart[g] * modelo.Y[g, t] + modelo.cnl[g] * modelo.U[g,t])
        for g in modelo.G
        for t in modelo.T
    )+sum(
        modelo.precio_imp[t] * modelo.Z[t]
        for t in modelo.T
    )+sum(
        modelo.M[d]* modelo.F
        for d in modelo.D
    )

modelo.obj = pyo.Objective(
    rule=objetivo,
    sense=pyo.minimize
)

##  Restricciones, constrains... S.T. .... cual nombre mejor?

### Osea, primero se construyen las definiciones que lluego se usan de reglas
def pot_min(modelo, g, t):  # Potencia Minima
    return modelo.X[g, t] >= modelo.Pmin[g] * modelo.U[g, t]
def pot_max(modelo, g, t):  # Potencia Maxima
    return modelo.X[g, t] <= modelo.Pmax[g] * modelo.U[g, t]

def balance(modelo, t):     # Balance de energia - Oferta demanda
    return sum(
        modelo.X[g, t]
        for g in modelo.G
    ) + modelo.Z[t] == modelo.demanda[t]
def partida(modelo, g, t):  # Relacion entre el estado (U) y el que tenga que encenderse (Y)
    if t == 0:
        return modelo.Y[g, t] >= modelo.U[g, t] - modelo.U0[g]  # Condicion inicial
    return modelo.Y[g, t] >= modelo.U[g, t] - modelo.U[g, t-1]
def margen(modelo, t):      # La capacidad ociosa debe ser de almenos el 10% extra
    return sum(
        modelo.U[g, t]*modelo.Pmax[g] - modelo.X[g,t]
        for g in modelo.G
    ) + (max_importe - modelo.Z[t]) >= modelo.reserva[t]
def limite_compra(modelo, t):
    return modelo.Z[t] <= max_importe


def incremento_sup(modelo, g, t):
    if t == 0:
        return modelo.X[g, t] - modelo.X0[g] <= modelo.R[g] * modelo.U0[g] + modelo.Pmin[g] * (modelo.U[g, t] - modelo.U0[g])
    return modelo.X[g, t] - modelo.X[g, t-1] <= modelo.R[g] * modelo.U[g, t-1] + modelo.Pmin[g] * (modelo.U[g, t] - modelo.U[g, t-1])

def incremento_inf(modelo, g, t):
    if t == 0:
        return modelo.X0[g] - modelo.X[g, t] <= modelo.R[g] * modelo.U[g, t] + modelo.Pmin[g] * (modelo.U0[g] - modelo.U[g, t])
    return modelo.X[g, t-1] - modelo.X[g, t] <= modelo.R[g] * modelo.U[g, t] + modelo.Pmin[g] * (modelo.U[g, t-1] - modelo.U[g, t])


def emision_dia(modelo, d):
    return modelo.E[d] == sum(
        modelo.X[g, d*24 + h] * modelo.e_g[g]
        for g in modelo.G
        for h in range(24)
    )

def limite_co2(modelo, d):
    return modelo.E[d] <= modelo.E_day + BIG_M_Umbral * modelo.M[d]


### Ahora si pasan a ser restricciones aplicadas
modelo.pmin = pyo.Constraint(
    modelo.G,
    modelo.T,
    rule = pot_min
)
modelo.pmax = pyo.Constraint(
    modelo.G,
    modelo.T,
    rule = pot_max
)
modelo.balance = pyo.Constraint(
    modelo.T,
    rule=balance
)
modelo.partida = pyo.Constraint(
    modelo.G,
    modelo.T,
    rule=partida
)
modelo.margen = pyo.Constraint(
    modelo.T,
    rule=margen
)
modelo.limite_compra = pyo.Constraint(
    modelo.T,
    rule=limite_compra
)
modelo.incremento_sup = pyo.Constraint(
    modelo.G,
    modelo.T,
    rule=incremento_sup
)
modelo.incremento_inf = pyo.Constraint(
    modelo.G,
    modelo.T,
    rule=incremento_inf
)


modelo.emision_dia = pyo.Constraint(
    modelo.D,
    rule=emision_dia
)

modelo.limite_co2 = pyo.Constraint(
    modelo.D,
    rule=limite_co2
)

##  Pedirle porfavor al PC que lo resuelva :)

solver = pyo.SolverFactory("appsi_highs")
resultado = solver.solve(modelo)

print("Estado:", resultado.solver.termination_condition)
print("Objetivo =", pyo.value(modelo.obj))

# Guardar resultados, gracias Chati!

import csv
import os

CARPETA_RESULTADOS = "resultados_variacion_c"
os.makedirs(CARPETA_RESULTADOS, exist_ok=True)

# Despacho horario

archivo_despacho = os.path.join(CARPETA_RESULTADOS, "despacho.csv")

with open(archivo_despacho, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "hora",
        "dia",
        "hora_dia",
        "demanda_mw",

        "Gas_Base_1_mw",
        "Gas_Base_2_mw",
        "Diesel_Med_1_mw",
        "Diesel_Med_2_mw",
        "Peaker_mw",

        "importacion_mw",
        "capacidad_operativa_mw",
        "reserva_efectiva_mw",
        "reserva_requerida_mw",

        "Gas_Base_1_u",
        "Gas_Base_2_u",
        "Diesel_Med_1_u",
        "Diesel_Med_2_u",
        "Peaker_u"
    ])

    for t in modelo.T:
        capacidad_operativa = sum(
            pyo.value(modelo.U[g, t]) * Pmax[g]
            for g in generadores
        )

        reserva_efectiva = (
            capacidad_operativa
            - sum(pyo.value(modelo.X[g, t]) for g in generadores)
            + (max_importe - pyo.value(modelo.Z[t]))
        )

        writer.writerow([
            t,
            t // 24 + 1,
            t % 24,

            pyo.value(modelo.demanda[t]),

            pyo.value(modelo.X["Gas_Base_1", t]),
            pyo.value(modelo.X["Gas_Base_2", t]),
            pyo.value(modelo.X["Diesel_Med_1", t]),
            pyo.value(modelo.X["Diesel_Med_2", t]),
            pyo.value(modelo.X["Peaker", t]),

            pyo.value(modelo.Z[t]),
            capacidad_operativa,
            reserva_efectiva,
            pyo.value(modelo.reserva[t]),

            pyo.value(modelo.U["Gas_Base_1", t]),
            pyo.value(modelo.U["Gas_Base_2", t]),
            pyo.value(modelo.U["Diesel_Med_1", t]),
            pyo.value(modelo.U["Diesel_Med_2", t]),
            pyo.value(modelo.U["Peaker", t])
        ])


# Emisiones diarias

archivo_emisiones = os.path.join(
    CARPETA_RESULTADOS,
    "emisiones_diarias.csv"
)

with open(archivo_emisiones, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "dia",
        "emisiones_tco2",
        "umbral_tco2",
        "exceso_tco2",
        "multa"
    ])

    for d in modelo.D:
        emisiones = pyo.value(modelo.E[d])
        exceso = max(0, emisiones - umbral_diario)
        multa = pyo.value(modelo.M[d]) * monto_multa

        writer.writerow([
            d + 1,
            emisiones,
            umbral_diario,
            exceso,
            multa
        ])

# Resumen

archivo_resumen = os.path.join(CARPETA_RESULTADOS, "resumen.txt")

dias_sobre_umbral = sum(
    1
    for d in modelo.D
    if pyo.value(modelo.E[d]) > umbral_diario
)

multas_totales = sum(
    pyo.value(modelo.M[d]) * monto_multa
    for d in modelo.D
)

with open(archivo_resumen, "w", encoding="utf-8") as f:
    f.write(f"Estado: {resultado.solver.termination_condition}\n")
    f.write(f"Objetivo: {pyo.value(modelo.obj)}\n")
    f.write(f"Días sobre el umbral: {dias_sobre_umbral}\n")
    f.write(f"Multas totales: {multas_totales}\n")

print(f"Resultados guardados en: {CARPETA_RESULTADOS}/")

