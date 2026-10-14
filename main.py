from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
# 1. Importamos AulaController junto a los demas controladores
from views import EstudianteController, AulaController, MateriaController, MatriculaController

# Se crea UN solo controlador de cada tipo.
# Inyeccion de dependencias:
# - Aulas se pasa a Materias para asignar y validar el espacio fisico.
# - Estudiantes y Materias se pasan a Matriculas (flujo 1 a 1 intacto).
estudiantes = EstudianteController()
aulas = AulaController()                # <--- NUEVO CONTROLADOR
materias = MateriaController(aulas)     # <--- RECIBE A AULAS
matriculas = MatriculaController(estudiantes, materias)


# =====================================================================
# AYUDAS DE PANTALLA
# =====================================================================

def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    """Devuelve un entero o None si el usuario escribio otra cosa."""
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    # Los controladores devuelven la TUPLA (exito, mensaje)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavia."):
    """Sirve para estudiantes, aulas, materias y matriculas: cada modelo sabe mostrarse."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    # Recorre el DICCIONARIO del objeto: clave y valor a la vez
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# =====================================================================
# MENU DE AULAS (NUEVO)
# =====================================================================

def crear_aula():
    imprimir_titulo("CREAR AULA / LABORATORIO")
    datos = {
        "codigo": input("Codigo (ej. LAB-101, AULA-204): "),
        "edificio": input("Edificio o Bloque: "),
        "capacidad": input("Capacidad maxima [Enter = 40]: "),
        "tipo": input("Tipo (Teórica / Laboratorio / Taller) [Enter = Teórica]: "),
    }
    if not datos["tipo"].strip():
        datos["tipo"] = "Teórica"

    mostrar_resultado(*aulas.crear(datos))
    pausa()


def listar_aulas():
    imprimir_titulo("AULAS Y LABORATORIOS")
    mostrar_lista(aulas.leer(), "Todavia no hay aulas registradas.")
    pausa()


def buscar_aula():
    imprimir_titulo("BUSCAR AULA")
    termino = input("Codigo, edificio o tipo: ")
    encontradas = aulas.buscar(termino)
    mostrar_lista(encontradas, f"Ninguna aula coincide con '{termino}'.")
    pausa()


def ver_aula():
    imprimir_titulo("VER AULA POR ID")
    aula = aulas.obtener(pedir_entero("Id: "))
    if aula is None:
        imprimir_error("No encontrada")
    else:
        mostrar_detalle(aula)
        asignadas = materias.por_aula(aula.id)
        print(f"\n  Materias dictadas en esta aula ({len(asignadas)}):")
        for m in asignadas:
            print(f"    - [{m.codigo}] {m.nombre} (Cupos: {m.cupos})")
    pausa()


def actualizar_aula():
    imprimir_titulo("ACTUALIZAR AULA")
    id_aula = pedir_entero("Id: ")
    aula = aulas.obtener(id_aula)
    if aula is None:
        imprimir_error("No encontrada")
        return pausa()

    imprimir_info(f"Editando: {aula.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("codigo", "edificio", "capacidad", "tipo"):
        actual = getattr(aula, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*aulas.actualizar(id_aula, cambios))
    pausa()


def eliminar_aula():
    imprimir_titulo("ELIMINAR AULA")
    id_aula = pedir_entero("Id: ")
    aula = aulas.obtener(id_aula)
    if aula is None:
        imprimir_error("No encontrada")
        return pausa()

    asignadas = materias.por_aula(id_aula)
    if asignadas:
        imprimir_info(f"Aviso: Hay {len(asignadas)} materia(s) asignada(s) a esta aula.")

    imprimir_info(f"Se eliminara: {aula.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*aulas.eliminar(id_aula))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# =====================================================================
# MENU DE ESTUDIANTES
# =====================================================================

def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet: "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(estudiantes.leer(), "Todavia no hay estudiantes registrados.")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    encontrados = estudiantes.buscar(termino)
    mostrar_lista(encontrados, f"Ningun estudiante coincide con '{termino}'.")
    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    estudiante = estudiantes.obtener(pedir_entero("Id: "))
    if estudiante is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(estudiante)
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*estudiantes.actualizar(id_estudiante, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {estudiante.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*estudiantes.eliminar(id_estudiante))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# =====================================================================
# MENU DE MATERIAS
# =====================================================================

def crear_materia():
    imprimir_titulo("CREAR MATERIA")

    # Mostramos aulas disponibles para que el usuario conozca los IDs
    imprimir_info("Aulas disponibles:")
    mostrar_lista(aulas.leer(), "No hay aulas registradas (se creara sin aula asignada).")

    datos = {
        "nombre": input("\nNombre: "),
        "codigo": input("Codigo: "),
        "creditos": input("Creditos: "),
        "cupos": input("Cupos iniciales [Enter = 30]: "),
        "aula_id": pedir_entero("Id del aula (0 o vacio si no tiene): ") or 0,
    }
    mostrar_resultado(*materias.crear(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(materias.leer(), "Todavia no hay materias creadas.")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o codigo: ")
    mostrar_lista(materias.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = materias.obtener(pedir_entero("Id: "))
    if materia is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(materia)
        aula_obj = aulas.obtener(materia.aula_id) if materia.aula_id else None
        info_aula = f"{aula_obj.codigo} - {aula_obj.edificio} ({aula_obj.tipo})" if aula_obj else "Sin aula asignada"
        print(f"  Espacio Asignado: {info_aula}")
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = materias.obtener(id_materia)
    if materia is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    # Opcion para cambiar el aula asociada
    cambio_aula_id = input(f"Aula ID [{materia.aula_id}]: ").strip()
    if cambio_aula_id:
        try:
            cambios["aula_id"] = int(cambio_aula_id)
        except ValueError:
            imprimir_error("El ID de aula debe ser un numero")
            return pausa()

    mostrar_resultado(*materias.actualizar(id_materia, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = materias.obtener(id_materia)
    if materia is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {materia.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*materias.eliminar(id_materia))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# =====================================================================
# MENU DE MATRICULAS (TRANSACCIONAL 1 A 1 INTACTO)
# =====================================================================

def registrar_matricula():
    imprimir_titulo("REGISTRAR MATRICULA")
    imprimir_info("Estudiantes:")
    mostrar_lista(estudiantes.leer())
    imprimir_info("Materias:")
    mostrar_lista(materias.leer())

    datos = {
        "estudiante_id": pedir_entero("\nId del estudiante: "),
        "materia_id": pedir_entero("Id de la materia: "),
        "periodo": input("Periodo (ej. 2026-1): "),
    }
    
    if None in (datos["estudiante_id"], datos["materia_id"]):
        imprimir_error("Los IDs deben ser numeros enteros")
        return pausa()

    mostrar_resultado(*matriculas.crear(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRICULAS ACTIVAS")
    mostrar_lista(matriculas.leer(), "Todavia no hay inscripciones.")
    pausa()


def asentar_calificacion():
    imprimir_titulo("ASENTAR CALIFICACION")
    id_matricula = pedir_entero("Id de la matricula: ")
    if not id_matricula:
        return pausa()
        
    nota = input("Ingrese la nota (0 a 20): ")
    mostrar_resultado(*matriculas.actualizar(id_matricula, {"nota": nota}))
    pausa()


def ver_reporte():
    imprimir_titulo("REPORTE ACADEMICO")
    texto = matriculas.reporte_academico(pedir_entero("Id del estudiante: "))
    if texto is None:
        imprimir_error("El estudiante no existe.")
    else:
        print(texto)
    pausa()


def anular_matricula():
    imprimir_titulo("ANULAR MATRICULA")
    id_matricula = pedir_entero("Id de la matricula: ")
    if id_matricula and confirmar("Se liberara el cupo. ¿Confirma?"):
        mostrar_resultado(*matriculas.eliminar(id_matricula))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


def resumen():
    imprimir_titulo("RESUMEN GENERAL")
    print(f"  Aulas/Labs  : {len(aulas.leer())}")
    print(f"  Edificios   : {', '.join(aulas.edificios()) or '-'}")
    print(f"  Estudiantes : {len(estudiantes.leer())}")
    print(f"  Carreras    : {', '.join(estudiantes.carreras_registradas()) or '-'}")
    print(f"  Materias    : {len(materias.leer())}")
    
    llenas = [m for m in materias.leer() if not m.hay_cupo()]
    print(f"  Sin cupos   : {', '.join(m.codigo for m in llenas) or 'ninguna'}")
    print(f"  Matriculas  : {len(matriculas.leer())}")
    pausa()


# =====================================================================
# MENUS: DICCIONARIOS tecla -> (texto, funcion)
# =====================================================================

MENU_AULAS = {
    "1": ("Crear aula/laboratorio", crear_aula),
    "2": ("Ver todas", listar_aulas),
    "3": ("Buscar", buscar_aula),
    "4": ("Ver por id", ver_aula),
    "5": ("Actualizar", actualizar_aula),
    "6": ("Eliminar", eliminar_aula),
    "0": ("Volver", None),
}

MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por id", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por id", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Inscribir estudiante", registrar_matricula),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Asentar calificacion", asentar_calificacion),
    "4": ("Ver reporte academico", ver_reporte),
    "5": ("Anular matricula", anular_matricula),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    """Un solo bucle para los submenus."""
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opcion: ").strip()
        if tecla not in opciones:
            imprimir_error("Opcion no valida")
            pausa()
            continue

        _texto, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA ACADEMICO")
        print("  1. Estudiantes")
        print("  2. Aulas / Laboratorios")   # <--- NUEVA OPCION EN EL MENU
        print("  3. Materias")
        print("  4. Matriculas")
        print("  5. Resumen")
        print("  0. Salir\n")

        tecla = input("Opcion: ").strip()
        if tecla == "1":
            ejecutar_menu("GESTION DE ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("GESTION DE AULAS", MENU_AULAS)
        elif tecla == "3":
            ejecutar_menu("GESTION DE MATERIAS", MENU_MATERIAS)
        elif tecla == "4":
            ejecutar_menu("GESTION DE MATRICULAS", MENU_MATRICULAS)
        elif tecla == "5":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opcion no valida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")