import streamlit as st
import pandas as pd
from sympy import symbols, Rational, simplify

st.title("Calculadora de sistemas lineales ")

# Número de filas (ecuaciones) y columnas (variables)
n = st.number_input("Número de ecuaciones (filas):", min_value=2, max_value=10, value=3)
m = st.number_input("Número de incógnitas (columnas):", min_value=2, max_value=10, value=3)

st.write(f"Introduce los coeficientes y términos que desee en su sistema {n}x{m}:")

# Crear DataFrame dinámico: n filas, m+1 columnas
cols = [f"a{i+1}" for i in range(m)] + ["b"]
df = pd.DataFrame([["0"]*(m+1) for _ in range(n)], columns=cols)

# Mostrar tabla editable
edited_df = st.data_editor(df, num_rows=n, use_container_width=True)

# ================= Función para mostrar matriz alineada =================
def matriz_str(M):
    filas = []
    for i in range(len(M)):
        fila = [f"{str(M[i][j]):>8}" for j in range(len(M[0])-1)]
        fila.append(f"| {str(M[i][-1]):>8}")
        filas.append(" ".join(fila))
    return "\n".join(filas)

# ================= Función Gauss-Jordan =================
def gauss_jordan_simb(M):
    pasos = []
    n_rows, n_cols = len(M), len(M[0])
    
    # Convertir a fracciones o expresiones simbólicas
    for i in range(n_rows):
        for j in range(n_cols):
            try:
                M[i][j] = Rational(M[i][j])
            except:
                M[i][j] = simplify(M[i][j])
    
    pasos.append(("Matriz inicial", matriz_str(M)))
    
    # Eliminación hacia abajo
    for k in range(min(n_rows, n_cols-1)):
        # Pivoteo parcial
        pivot_row = k
        for i in range(k, n_rows):
            if M[i][k] != 0:
                pivot_row = i
                break
        if pivot_row != k:
            M[k], M[pivot_row] = M[pivot_row], M[k]
            pasos.append((f"Intercambio fila {k+1} y fila {pivot_row+1}", matriz_str(M)))
        
        pivot = M[k][k]
        if pivot != 0:
            M[k] = [simplify(el/pivot) for el in M[k]]
            pasos.append((f"Normalizar fila {k+1} (dividir por {pivot})", matriz_str(M)))
        
        for i in range(k+1, n_rows):
            factor = M[i][k]
            if factor != 0:
                M[i] = [simplify(M[i][j] - factor*M[k][j]) for j in range(n_cols)]
                pasos.append((f"Fila {i+1} = Fila {i+1} - ({factor})*Fila {k+1}", matriz_str(M)))
    
    # Eliminación hacia arriba
    for k in range(min(n_rows, n_cols-1)-1, -1, -1):
        for i in range(k-1, -1, -1):
            factor = M[i][k]
            if factor != 0:
                M[i] = [simplify(M[i][j] - factor*M[k][j]) for j in range(n_cols)]
                pasos.append((f"Fila {i+1} = Fila {i+1} - ({factor})*Fila {k+1}", matriz_str(M)))
    
    # Detectar tipo de sistema
    tipo = "Determinada (solución única)"
    for i in range(n_rows):
        if all(M[i][j] == 0 for j in range(n_cols-1)):
            if M[i][-1] != 0:
                tipo = "Incompatible (sin solución)"
            else:
                tipo = "Infinitas soluciones"
    
    # Extraer soluciones
    sol = {}
    if tipo == "Determinada (solución única)":
        for i in range(min(n_rows, n_cols-1)):
            sol[f"x{i+1}"] = M[i][-1]
    
    return pasos, sol, tipo

# ================= Resolver =================
if st.button("Resolver Sistema"):
    M_list = []
    for row in edited_df.values:
        M_list.append([str(x) for x in row])
    
    pasos, sol, tipo = gauss_jordan_simb(M_list)
    
    st.markdown(f"### Tipo de sistema: {tipo}")
    
    st.markdown("### Proceso paso a paso:")
    for desc, paso in pasos:
        st.markdown(f"**{desc}:**")
        st.code(paso, language="text")
        st.text("")
    
    if tipo == "Determinada (solución única)":
        st.markdown("### Solución final:")
        for var, val in sol.items():
            st.text(f"{var} = {val}")
    elif tipo == "Incompatible (sin solución)":
        st.markdown("### No hay solución posible.")
    else:
        st.markdown("### El sistema tiene infinitas soluciones (variables libres)")
