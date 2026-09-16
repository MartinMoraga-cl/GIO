import pyomo.environ as pyo
import numpy as np

### TESTEOOO, modelo inventado 

T = 24 # Periodos, en hrs, asique solo un dia...
horas = range(T) # genera el listados de 1 a 24
SEMILLA = 69
RNG = np.random.default_rng(SEMILLA) # raro el python es.... esto es como intanciar un generador de rng....

demanda_neta = RNG.integers(
        low  = 10,
        high = 300,
        size = T
)

#   Diccionarios, la forma "bonita"
##  Generadores
gens = ["G1","G2", "G3"] # debo controlarme y contar desde el 1.... ufff
Pmin = {
        "G1": 10,
        "G2": 25,
        "G3": 30
}
Pmax = {
        "G1": 100,
        "G2": 120,
        "G3": 90
}
coste = {
        "G1": 5,
        "G2": 6,
        "G3": 2
}
coste_partida = {
        "G1": 10,
        "G2": 30,
        "G3": 20
}
X0 = {
        "G1": 1,
        "G2": 0,
        "G3": 1
}

#   Solver de programacion lineal

modelo = pyo.ConcreteModel()

##  Los conjuntos [ pyo.Set() ]
modelo.G = pyo.Set(initialize=gens)
modelo.T = pyo.Set(initialize=horas)

##  Parametros
modelo.Pmin = pyo.Param(
        modelo.G,
        initialize=Pmin
)
modelo.Pmax = pyo.Param(
        modelo.G,
        initialize=Pmax
)
modelo.coste = pyo.Param(
        modelo.G,
        initialize=coste
)
modelo.coste_partida = pyo.Param(
        modelo.G,
        initialize=coste_partida
)
modelo.demanda = pyo.Param(
        modelo.T,
        initialize=lambda modelo, t: demanda_neta[t] # Uhhhh????
)
modelo.X0 = pyo.Param(
        modelo.G,
        initialize=X0
)

##  Las Variables
modelo.X = pyo.Var( # Encendido o no
        modelo.G,
        modelo.T,
        domain=pyo.Binary
)
modelo.Y = pyo.Var( # Potencia
        modelo.G,
        modelo.T,
        domain=pyo.NonNegativeReals
)
modelo.Z = pyo.Var( # Partida
        modelo.G,
        modelo.T,
        domain=pyo.Binary
)

##  Funcion Objetivo

def objetivo(modelo):
    return sum(
        modelo.coste[g] * modelo.Y[g, t] + modelo.coste_partida[g] * modelo.Z[g, t]
        for g in modelo.G
        for t in modelo.T
    )

modelo.obj = pyo.Objective(
    rule=objetivo,
    sense=pyo.minimize
)

##  Restricciones, constrains... S.T. .... cual nombre mejor?

def pot_min(modelo, g, t):
    return modelo.Y[g, t] >= modelo.Pmin[g] * modelo.X[g, t]
def pot_max(modelo, g, t):
    return modelo.Y[g, t] <= modelo.Pmax[g] * modelo.X[g, t]
def balance(modelo, t):
    return sum(
        modelo.Y[g, t]
        for g in modelo.G
    ) == modelo.demanda[t]
def partida(modelo, g, t):
    if t == 0:
        return modelo.Z[g, t] >= modelo.X[g, t] - modelo.X0[g]
    return modelo.Z[g, t] >= modelo.X[g, t] - modelo.X[g, t-1]

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

##  Pedirle porfavor al PC que lo resuelva :)

solver = pyo.SolverFactory("appsi_highs")
resultado = solver.solve(modelo)

print("Estado:", resultado.solver.termination_condition)
#print("X =", pyo.value(modelo.X))
#print("Y =", pyo.value(modelo.Y))
#print("Z =", pyo.value(modelo.Z))
print("Objetivo =", pyo.value(modelo.obj))



print("\nResultados:")
print("Hora | Demanda | G1(X,Y) | G2(X,Y) | G3(X,Y) | Partidas")
print("-" * 65)

for t in modelo.T:
    print(
        f"{t:4} | "
        f"{pyo.value(modelo.demanda[t]):7.1f} | "
        f"{pyo.value(modelo.X['G1',t]):4.0f},{pyo.value(modelo.Y['G1',t]):5.1f} | "
        f"{pyo.value(modelo.X['G2',t]):4.0f},{pyo.value(modelo.Y['G2',t]):5.1f} | "
        f"{pyo.value(modelo.X['G3',t]):4.0f},{pyo.value(modelo.Y['G3',t]):5.1f} | "
        f"{sum(pyo.value(modelo.Z[g,t]) for g in modelo.G):8.0f}"
    )
