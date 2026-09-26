#   Este es la variacion con la bateria
#   incluye variaciones en el: balance de energia,
#   capacidad, tasas y eficiencias de carga y descarga

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

#   Planteamiento de programacion lineal
#   De acá en más se usan los nombres de la guia [dentro de lo que se puede, hay palabras reservadas]

modelo = pyo.ConcreteModel()

##  Los conjuntos [ pyo.Set() ]
modelo.G = pyo.Set(initialize=generadores)
modelo.T = pyo.Set(initialize=horas)
modelo.B = pyo.Set(initialize=baterias)     # Añadido de la variacion: es ell grupo de baterias, en este caso es solo una...

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
    initialize=lambda modelo, t: demanda_neta[t]
)
modelo.reserva = pyo.Param(
    modelo.T,
    initialize=lambda modelo, t: reserva[t]
)
modelo.precio_imp = pyo.Param(
    modelo.T,
    initialize=lambda modelo, t: precio_importe[t]
)

modelo.Smax = pyo.Param(
    modelo.B,
    initialize=Smax
)
modelo.Bch = pyo.Param(
    modelo.B,
    initialize=Bch
)
modelo.Bdis = pyo.Param(
    modelo.B,
    initialize=Bdis
) 
modelo.eta_ch = pyo.Param(
    modelo.B,
    initialize=eta_ch
)
modelo.eta_dis = pyo.Param(
    modelo.B,
    initialize=eta_dis
)

modelo.X0 = pyo.Param( # el estado inicial como parametor
    modelo.G,
    initialize=X0
)
modelo.U0 = pyo.Param( # el estado inicial como parametro
    modelo.G,
    initialize=U0
)
modelo.S0 = pyo.Param( # energia inicial del banco de baterias
    modelo.B,
    initialize=S0
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
modelo.S = pyo.Var( # Energia en MWh almacenada en la bateria b en el periodo t
    modelo.B,
    modelo.T,
    domain=pyo.NonNegativeReals
)
modelo.F = pyo.Var( # El flujo de energia que vé la red, >0 es que suministra, <0 es que solicita a la red
    modelo.T,
    domain=pyo.Reals    # ?
)
modelo.C = pyo.Var( # Tasa de carga en MW vistos por la red
    modelo.B,
    modelo.T,
    domain=pyo.NonNegativeReals
)
modelo.D = pyo.Var( # Tasa de descarga en MW vistos por la red
    modelo.B,
    modelo.T,
    domain=pyo.NonNegativeReals
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

def balance(modelo, t):     # Balance de energia - Oferta demanda - más el aporte de las baterias
    return sum(
        modelo.X[g, t]
        for g in modelo.G
    ) + modelo.F[t] + modelo.Z[t] == modelo.demanda[t]
def partida(modelo, g, t):  # Relacion entre el estado (U) y el que tenga que encenderse (Y)
    if t == 0:
        return modelo.Y[g, t] >= modelo.U[g, t] - modelo.U0[g]  # Condicion inicial
    return modelo.Y[g, t] >= modelo.U[g, t] - modelo.U[g, t-1]
def margen(modelo, t):      # La capacidad ociosa debe ser de almenos el 10% extra
    return sum(
        modelo.U[g, t]*modelo.Pmax[g] - modelo.X[g,t]
        for g in modelo.G
    ) + (max_importe - modelo.Z[t]) >= modelo.reserva[t]    ################## <---------------- Falta modificar, creo....
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


def flujo(modelo, t):   # F condensa el flujo neto de las baterias a la red
    return sum(
        modelo.D[b,t] - modelo.C[b,t]
        for b in modelo.B
    ) == modelo.F[t]
def almacenamiento(modelo, b, t):   # La carga depende del estado anterior, y de los flujos de carga y descarga, cada uno contando la eficiencia
    if t==0:
        return modelo.S[b,t] == modelo.S0[b] + modelo.eta_ch[b]*modelo.C[b,t] - modelo.D[b,t]/modelo.eta_dis[b]
    return modelo.S[b,t] == modelo.S[b, t-1] + modelo.eta_ch[b]*modelo.C[b,t] - modelo.D[b,t]/modelo.eta_dis[b]
def limite_carga(modelo, b, t):     # Bue dudo que esto necesite comentario...
    return modelo.C[b,t] <= modelo.Bch[b]
def limite_descarga(modelo, b, t):  # lo dicho arriba...
    return modelo.D[b,t] <= modelo.Bdis[b]
def limite_guardado(modelo, b, t):
    return modelo.S[b, t] <= modelo.Smax[b]
def estado_final(modelo, b):
    return modelo.S[b, T-1] >= modelo.S0[b]


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

modelo.flujo = pyo.Constraint(
    modelo.T,
    rule=flujo
)
modelo.almacenamiento = pyo.Constraint(
    modelo.B,
    modelo.T,
    rule=almacenamiento
)
modelo.limite_carga = pyo.Constraint(
    modelo.B,
    modelo.T,
    rule=limite_carga
)
modelo.limite_descarga = pyo.Constraint(
    modelo.B,
    modelo.T,
    rule=limite_descarga
)
modelo.limite_guardado = pyo.Constraint(
    modelo.B,
    modelo.T,
    rule=limite_guardado
)
modelo.estado_final = pyo.Constraint(
    modelo.B,
    rule=estado_final
)


##  Pedirle porfavor al PC que lo resuelva :)

solver = pyo.SolverFactory("appsi_highs")
resultado = solver.solve(modelo)

print("Estado:", resultado.solver.termination_condition)
print("Objetivo =", pyo.value(modelo.obj))


# Guardar resultados, gracias chati!

import csv
import os

CARPETA_RESULTADOS = "resultados_variacion_a"
os.makedirs(CARPETA_RESULTADOS, exist_ok=True)

# Despacho + batería

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
        "flujo_bateria_mw",
        "reserva_efectiva_mw",
        "reserva_requerida_mw",

        "Gas_Base_1_u",
        "Gas_Base_2_u",
        "Diesel_Med_1_u",
        "Diesel_Med_2_u",
        "Peaker_u",

        "Banco_Baterias_1_carga_mw",
        "Banco_Baterias_1_descarga_mw",
        "Banco_Baterias_1_energia_mwh",

        "Gas_Base_1_y",
        "Gas_Base_2_y",
        "Diesel_Med_1_y",
        "Diesel_Med_2_y",
        "Peaker_y"
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
            pyo.value(modelo.F[t]),
            reserva_efectiva,
            pyo.value(modelo.reserva[t]),

            pyo.value(modelo.U["Gas_Base_1", t]),
            pyo.value(modelo.U["Gas_Base_2", t]),
            pyo.value(modelo.U["Diesel_Med_1", t]),
            pyo.value(modelo.U["Diesel_Med_2", t]),
            pyo.value(modelo.U["Peaker", t]),

            pyo.value(modelo.C["Banco_Baterias_1", t]),
            pyo.value(modelo.D["Banco_Baterias_1", t]),
            pyo.value(modelo.S["Banco_Baterias_1", t]),

            pyo.value(modelo.Y["Gas_Base_1", t]),
            pyo.value(modelo.Y["Gas_Base_2", t]),
            pyo.value(modelo.Y["Diesel_Med_1", t]),
            pyo.value(modelo.Y["Diesel_Med_2", t]),
            pyo.value(modelo.Y["Peaker", t])
        ])

# Resumen

archivo_resumen = os.path.join(CARPETA_RESULTADOS, "resumen.txt")

with open(archivo_resumen, "w", encoding="utf-8") as f:
    f.write(f"Estado: {resultado.solver.termination_condition}\n")
    f.write(f"Objetivo: {pyo.value(modelo.obj)}\n")
    f.write(
        f"SOC inicial (MWh): "
        f"{pyo.value(modelo.S0['Banco_Baterias_1'])}\n"
    )
    f.write(
        f"SOC final (MWh): "
        f"{pyo.value(modelo.S['Banco_Baterias_1', T-1])}\n"
    )

print(f"Resultados guardados en: {CARPETA_RESULTADOS}/")
