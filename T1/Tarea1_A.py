#   Este es la variacion con la bateria
#   incluye variaciones en el: balance de energia,
#   capacidad, tasas y eficiencias de carga y descarga

import pyomo.environ as pyo
import numpy as np
import math

T = 168 # Periodos, en hrs, asique solo una semanda
horas = range(T) # genera el listados de 0 a 167
SEMILLA = 69
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
    demanda_neta[t]   = int(ppeak*gamma[t]*perfil_diario[hora]*(1+epsilon[t]))
    precio_importe[t] = int((100000+90000*perfil_diario[hora])*(1+eta[t]))
    reserva[t] = demanda_neta[t]*0.1
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
        return modelo.R[g] >= modelo.X[g, t] - modelo.X0[g] 
    return modelo.R[g] >= modelo.X[g, t] - modelo.X[g, t-1] 
def incremento_inf(modelo, g, t):
    if t == 0:
        return -modelo.R[g] <= modelo.X[g, t] - modelo.X0[g]
    return -modelo.R[g] <= modelo.X[g, t] - modelo.X[g, t-1]


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
#print("X =", pyo.value(modelo.X))
#print("Y =", pyo.value(modelo.Y))
#print("Z =", pyo.value(modelo.Z))
print("Objetivo =", pyo.value(modelo.obj))


print("Hora | Demanda | Gas_B1(X,U) | Gas_B2(X,U) | Diesel_Med_1 | Diesel_Med_2 | Peaker(X,U) | Importe | F_bat | S_bat")
print("-" * 115)

for t in modelo.T:
    print(
        f"{t:4} | "
        f"{pyo.value(modelo.demanda[t]):7.1f} | "
        f"{pyo.value(modelo.X['Gas_Base_1',t]):6.0f},{pyo.value(modelo.U['Gas_Base_1',t]):3.0f} | "
        f"{pyo.value(modelo.X['Gas_Base_2',t]):6.0f},{pyo.value(modelo.U['Gas_Base_2',t]):3.0f} | "
        f"{pyo.value(modelo.X['Diesel_Med_1',t]):6.0f},{pyo.value(modelo.U['Diesel_Med_1',t]):3.0f} | "
        f"{pyo.value(modelo.X['Diesel_Med_2',t]):6.0f},{pyo.value(modelo.U['Diesel_Med_2',t]):3.0f} | "
        f"{pyo.value(modelo.X['Peaker',t]):6.0f},{pyo.value(modelo.U['Peaker',t]):3.0f} | "
        f"{pyo.value(modelo.Z[t]):7.1f} | "
        f"{pyo.value(modelo.F[t]):6.1f} | "
        f"{pyo.value(modelo.S['Banco_Baterias_1',t]):6.1f}"
    )


print(
    "Estado inicial:",
    [pyo.value(modelo.S0[b]) for b in modelo.B]
)

print(
    "Estado final:",
    [pyo.value(modelo.S[b,T-1]) for b in modelo.B]
)


## Graficos, Chati es una bestia para graficar, es super tedioso lo que biene acá abojo.....

import matplotlib.pyplot as plt

# ============================================================
# Grafico 1: Despacho y balance de potencia
# ============================================================

plt.figure(figsize=(14, 7))

# Generadores
for g in modelo.G:
    plt.plot(
        horas,
        [pyo.value(modelo.X[g, t]) for t in modelo.T],
        label=g
    )

# Importación
plt.plot(
    horas,
    [pyo.value(modelo.Z[t]) for t in modelo.T],
    label="Importación"
)

# Flujo neto de batería
plt.plot(
    horas,
    [pyo.value(modelo.F[t]) for t in modelo.T],
    label="Batería (F)"
)

# Demanda
plt.plot(
    horas,
    [pyo.value(modelo.demanda[t]) for t in modelo.T],
    label="Demanda"
)

# Capacidad instalada operativa
capacidad_operativa = [
    sum(
        pyo.value(modelo.Pmax[g]) * pyo.value(modelo.U[g, t])
        for g in modelo.G
    )
    for t in modelo.T
]

plt.plot(
    horas,
    capacidad_operativa,
    label="Capacidad operativa"
)

# Reserva operativa efectiva
reserva_efectiva = [
    sum(
        pyo.value(modelo.Pmax[g]) * pyo.value(modelo.U[g, t])
        - pyo.value(modelo.X[g, t])
        for g in modelo.G
    )
    + (max_importe - pyo.value(modelo.Z[t]))
    for t in modelo.T
]

plt.plot(
    horas,
    reserva_efectiva,
    label="Reserva efectiva"
)

# Reserva requerida
plt.plot(
    horas,
    [pyo.value(modelo.reserva[t]) for t in modelo.T],
    label="Reserva requerida"
)

plt.axhline(
    0,
    linewidth=0.8
)

plt.xlabel("Hora")
plt.ylabel("Potencia [MW]")
plt.title("Despacho de generación y operación de la batería")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()


# ============================================================
# Grafico 2: Estado de carga de la batería
# ============================================================

plt.figure(figsize=(14, 5))

SOC = [
    pyo.value(modelo.S["Banco_Baterias_1", t])
    for t in modelo.T
]

plt.plot(
    horas,
    SOC,
    label="Energía almacenada"
)

# Capacidad máxima
plt.axhline(
    pyo.value(modelo.Smax["Banco_Baterias_1"]),
    linestyle="--",
    label="Capacidad máxima"
)

# Estado inicial
plt.axhline(
    pyo.value(modelo.S0["Banco_Baterias_1"]),
    linestyle=":",
    label="Estado inicial"
)

plt.xlabel("Hora")
plt.ylabel("Energía almacenada [MWh]")
plt.title("Estado de carga de la batería")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()
