import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# Crear o conectar a la base de datos
conn = sqlite3.connect('citas.db')
c = conn.cursor()

# Crear la tabla de pacientes y citas si no existen
c.execute('''
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS citas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER,
    fecha TEXT,
    hora_inicio TEXT,
    hora_fin TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
)
''')
conn.commit()

def agregar_paciente():
    st.title("Agregar Paciente")
    nombre = st.text_input("Nombre del Paciente")
    if st.button("Agregar Paciente"):
        try:
            c.execute("INSERT INTO pacientes (nombre) VALUES (?)", (nombre,))
            conn.commit()
            st.success(f"Paciente {nombre} agregado exitosamente")
        except sqlite3.IntegrityError:
            st.error("El paciente ya existe")

def borrar_paciente():
    st.title("Borrar Paciente")
    nombre = st.text_input("Nombre del Paciente")
    if st.button("Borrar Paciente"):
        c.execute("DELETE FROM pacientes WHERE nombre = ?", (nombre,))
        conn.commit()
        st.success(f"Paciente {nombre} borrado exitosamente")

def consultar_pacientes():
    st.title("Consultar Pacientes")
    c.execute("SELECT * FROM pacientes")
    pacientes = c.fetchall()
    for paciente in pacientes:
        st.write(f"ID: {paciente[0]}, Nombre: {paciente[1]}")

def registrar_cita():
    st.title("Registrar Cita")
    c.execute("SELECT * FROM pacientes")
    pacientes = c.fetchall()
    if not pacientes:
        st.warning("No hay pacientes registrados. Registra un paciente primero.")
        return
    paciente_dict = {paciente[1]: paciente[0] for paciente in pacientes}
    paciente_nombre = st.selectbox("Selecciona el Paciente", list(paciente_dict.keys()))
    paciente_id = paciente_dict[paciente_nombre]

    fecha = st.date_input("Selecciona la Fecha")
    hora_inicio = st.selectbox("Selecciona la Hora de Inicio", [f"{h}:00" for h in range(8, 16)])
    hora_inicio_dt = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M")
    hora_fin_dt = hora_inicio_dt + timedelta(hours=1)
    hora_inicio_str = hora_inicio_dt.strftime("%H:%M")
    hora_fin_str = hora_fin_dt.strftime("%H:%M")

    if st.button("Registrar Cita"):
        c.execute('''
        SELECT * FROM citas WHERE paciente_id = ? AND fecha = ? AND hora_inicio = ?
        ''', (paciente_id, fecha, hora_inicio_str))
        cita_existente = c.fetchone()
        if cita_existente:
            st.error("El paciente ya tiene una cita en ese horario")
        else:
            c.execute('''
            INSERT INTO citas (paciente_id, fecha, hora_inicio, hora_fin)
            VALUES (?, ?, ?, ?)
            ''', (paciente_id, fecha, hora_inicio_str, hora_fin_str))
            conn.commit()
            st.success(f"Cita registrada para {paciente_nombre} el {fecha} de {hora_inicio_str} a {hora_fin_str}")

def borrar_cita():
    st.title("Borrar Cita")
    c.execute("SELECT * FROM pacientes")
    pacientes = c.fetchall()
    if not pacientes:
        st.warning("No hay pacientes registrados. Registra un paciente primero.")
        return
    paciente_dict = {paciente[1]: paciente[0] for paciente in pacientes}
    paciente_nombre = st.selectbox("Selecciona el Paciente", list(paciente_dict.keys()))
    paciente_id = paciente_dict[paciente_nombre]

    fecha = st.date_input("Selecciona la Fecha")
    hora_inicio = st.selectbox("Selecciona la Hora de Inicio", [f"{h}:00" for h in range(8, 16)])
    hora_inicio_str = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M").strftime("%H:%M")

    if st.button("Borrar Cita"):
        c.execute('''
        DELETE FROM citas WHERE paciente_id = ? AND fecha = ? AND hora_inicio = ?
        ''', (paciente_id, fecha, hora_inicio_str))
        conn.commit()
        st.success(f"Cita para {paciente_nombre} el {fecha} a las {hora_inicio_str} borrada exitosamente")

def consultar_citas():
    st.title("Consultar Citas")
    c.execute('''
    SELECT pacientes.nombre, citas.fecha, citas.hora_inicio, citas.hora_fin
    FROM citas
    JOIN pacientes ON citas.paciente_id = pacientes.id
    ''')
    citas = c.fetchall()
    for cita in citas:
        st.write(f"Paciente: {cita[0]}, Fecha: {cita[1]}, Hora: {cita[2]} - {cita[3]}")

st.sidebar.title("Menú Principal")

menu_principal = st.sidebar.radio("Selecciona una opción", ["Ninguna", "Pacientes", "Citas"], index=0)

if menu_principal == "Pacientes":
    password = st.sidebar.text_input("Introduce la contraseña", type="password")
    if password:
        if password == "Tt3plco4$":
            st.sidebar.title("Opciones de Pacientes")
            opcion = st.sidebar.radio("Selecciona una opción", ["Agregar Paciente", "Borrar Paciente", "Consultar Pacientes"], index=0)
            if opcion == "Agregar Paciente":
                agregar_paciente()
            elif opcion == "Borrar Paciente":
                borrar_paciente()
            elif opcion == "Consultar Pacientes":
                consultar_pacientes()
        else:
            st.sidebar.error("Contraseña incorrecta")
elif menu_principal == "Citas":
    st.sidebar.title("Opciones de Citas")
    opcion = st.sidebar.radio("Selecciona una opción", ["Registrar Cita", "Borrar Cita", "Consultar Citas"], index=0)
    if opcion == "Registrar Cita":
        registrar_cita()
    elif opcion == "Borrar Cita":
        borrar_cita()
    elif opcion == "Consultar Citas":
        consultar_citas()

