from abc import ABC, abstractmethod

from models import Estudiante, Aula, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
# Solo dice QUE metodos debe tener todo controlador.
# COMO se hace cada uno lo escribe cada controlador, de la forma mas simple.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE AULAS (NUEVO)
# =====================================================================
class AulaController(CrudBase):

    def __init__(self, archivo="datos/aulas.json"):
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Aula.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for aula in self.lista:
            datos.append(aula.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Valida que el codigo sea obligatorio/unico y la capacidad numerica."""
        if id_actual is None:
            if str(datos.get("codigo", "")).strip() == "":
                return "El campo codigo es obligatorio"

        capacidad = str(datos.get("capacidad", "")).strip()
        if capacidad != "" and not capacidad.isdigit():
            return "La capacidad debe ser un numero entero positivo"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            for otra in self.lista:
                if otra.codigo == codigo and otra.id != id_actual:
                    return f"Ya existe un aula o laboratorio con el codigo '{codigo}'"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_aula):
        for aula in self.lista:
            if aula.id == id_aula:
                return aula
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas

        for aula in self.lista:
            if (texto in aula.codigo.lower()
                    or texto in aula.edificio.lower()
                    or texto in aula.tipo.lower()):
                encontradas.append(aula)
        return encontradas

    def siguiente(self):
        mayor = 0
        for aula in self.lista:
            if aula.id > mayor:
                mayor = aula.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        capacidad = str(datos.get("capacidad", "")).strip()

        aula = Aula(
            self.siguiente(),
            str(datos["codigo"]).strip().upper(),
            str(datos.get("edificio", "")).strip().title(),
            int(capacidad) if capacidad != "" else 40,
            str(datos.get("tipo", "Teórica")).strip().capitalize()
        )
        self.lista.append(aula)
        self.guardar()
        return True, f"Aula creada: {aula.etiqueta()}"

    def actualizar(self, id_aula, datos):
        aula = self.obtener(id_aula)
        if aula is None:
            return False, f"No existe un aula con id {id_aula}"
        if not datos:
            return False, "No se indico ningun cambio"

        permitidos = {"codigo", "edificio", "capacidad", "tipo"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_aula)
        if error:
            return False, error

        if "codigo" in datos:
            aula.codigo = str(datos["codigo"]).strip().upper()
        if "edificio" in datos:
            aula.edificio = str(datos["edificio"]).strip().title()
        if "capacidad" in datos:
            aula.capacidad = int(datos["capacidad"])
        if "tipo" in datos:
            aula.tipo = str(datos["tipo"]).strip().capitalize()

        self.guardar()
        return True, f"Aula {id_aula} actualizada"

    def eliminar(self, id_aula):
        aula = self.obtener(id_aula)
        if aula is None:
            return False, f"No existe un aula con id {id_aula}"

        self.lista.remove(aula)
        self.guardar()
        return True, f"Aula {id_aula} eliminada"

    def edificios(self):
        """CONJUNTO de edificios o bloques registrados sin repetidos."""
        return sorted({a.edificio for a in self.lista if a.edificio != ""})


# =====================================================================
# CONTROLADOR DE ESTUDIANTES (ORIGINAL INTACTO)
# =====================================================================
class EstudianteController(CrudBase):

    def __init__(self, archivo="datos/estudiantes.json"):
        self.gestor = GestorJSON(archivo)

        # Leemos el JSON y convertimos cada diccionario en un objeto Estudiante
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for estudiante in self.lista:
            datos.append(estudiante.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Devuelve un mensaje de error, o None si todo esta bien."""
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email invalido: '{email}'"
            # CONJUNTO con los emails de los OTROS estudiantes para evitar duplicados
            usados = {e.email for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya esta registrado en otro estudiante"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for estudiante in self.lista:
            if (texto in estudiante.nombre.lower()
                    or texto in estudiante.apellido.lower()
                    or texto in estudiante.email
                    or texto in estudiante.carnet.lower()
                    or texto in estudiante.carrera.lower()):
                encontrados.append(estudiante)
        return encontrados

    def siguiente(self):
        mayor = 0
        for estudiante in self.lista:
            if estudiante.id > mayor:
                mayor = estudiante.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos.get("carnet", "")).strip().upper(),
            str(datos.get("carrera", "")).strip().title()
        )
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indico ningun cambio"

        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    def carreras_registradas(self):
        """CONJUNTO de carreras: sin repetidos. sorted() lo devuelve como lista."""
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


# =====================================================================
# CONTROLADOR DE MATERIAS (ADAPTADO CON AULAS)
# =====================================================================
class MateriaController(CrudBase):

    def __init__(self, aulas=None, archivo="datos/materias.json"):
        # Se recibe opcionalmente AulaController para validar pertenencia fisica
        self.aulas = aulas
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for materia in self.lista:
            datos.append(materia.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        creditos = str(datos.get("creditos", "")).strip()
        if creditos != "" and not creditos.isdigit():
            return "Los creditos deben ser un numero entero"

        cupos = str(datos.get("cupos", "")).strip()
        if cupos != "" and not cupos.isdigit():
            return "Los cupos deben ser un numero entero positivo"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            for otra in self.lista:
                if otra.codigo == codigo and otra.id != id_actual:
                    return f"Ya existe una materia con el codigo {codigo}"

        # Validacion opcional de existencia de aula
        if "aula_id" in datos:
            try:
                aula_id = int(datos["aula_id"])
                if aula_id < 0:
                    return "El id de aula no puede ser negativo"
                if self.aulas and aula_id > 0:
                    if self.aulas.obtener(aula_id) is None:
                        return f"No existe un aula con id {aula_id}"
            except (TypeError, ValueError):
                return "El id de aula debe ser un numero entero"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for materia in self.lista:
            if texto in materia.nombre.lower() or texto in materia.codigo.lower():
                encontrados.append(materia)
        return encontrados

    def siguiente(self):
        mayor = 0
        for materia in self.lista:
            if materia.id > mayor:
                mayor = materia.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        creditos = str(datos.get("creditos", "")).strip()
        cupos = str(datos.get("cupos", "")).strip()
        aula_id = int(datos.get("aula_id", 0))

        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            int(creditos) if creditos != "" else 0,
            int(cupos) if cupos != "" else Materia.CUPOS_MAXIMOS,
            aula_id
        )

        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indico ningun cambio"

        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos", "aula_id"}
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])
        if "aula_id" in datos:
            materia.aula_id = int(datos["aula_id"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"

        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    def por_aula(self, id_aula):
        """Filtra y devuelve todas las asignaturas dictadas en un aula especifica."""
        return [m for m in self.lista if m.aula_id == int(id_aula)]


# =====================================================================
# CONTROLADOR DE MATRICULAS (TRANSACCIONAL 1 A 1 INTACTO)
# =====================================================================
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="datos/matriculas.json"):
        # INYECCION DE DEPENDENCIAS: Usa a los otros dos controladores
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for matricula in self.lista:
            datos.append(matricula.a_diccionario())
        self.gestor.guardar(datos)

    def validar_creacion(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser numeros enteros"

        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe un estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe una materia con id {materia_id}"

        if not materia.hay_cupo():
            return f"La materia {materia.codigo} ya no tiene cupos disponibles"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for matricula in self.lista:
            if matricula.id == id_matricula:
                return matricula
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas

        for matricula in self.lista:
            if texto in matricula.periodo.lower() or texto in matricula.fecha:
                encontradas.append(matricula)
        return encontradas

    def siguiente(self):
        mayor = 0
        for matricula in self.lista:
            if matricula.id > mayor:
                mayor = matricula.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar_creacion(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))

        matricula = Matricula(
            self.siguiente(),
            int(datos["estudiante_id"]),
            materia.id,
            str(datos.get("periodo", "Actual")).strip().upper()
        )

        materia.ocupar_cupo()
        self.materias.guardar()

        self.lista.append(matricula)
        self.guardar()

        return True, f"Inscripcion registrada exitosamente. Cupos restantes: {materia.cupos}"

    def actualizar(self, id_matricula, datos):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matricula {id_matricula}"

        if "nota" not in datos:
            return False, "Solo se puede actualizar la nota de una matricula"

        if not Materia.es_nota_valida(datos["nota"]):
            return False, "La nota no es valida. Debe ser un numero entre 0 y 20"

        matricula.nota = float(datos["nota"])
        self.guardar()

        estado_final = matricula.estado()
        return True, f"Calificacion guardada. Estado academico: {estado_final}"

    def eliminar(self, id_matricula):
        """Retirar matricula: se borra y el cupo se devuelve a la materia."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matricula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matricula {id_matricula} anulada y cupo liberado"

    def reporte_academico(self, id_estudiante):
        """Genera un boletin en texto del estudiante y sus materias."""
        estudiante = self.estudiantes.obtener(id_estudiante)
        if estudiante is None:
            return None

        texto = f"BOLETIN ACADEMICO - {estudiante.nombre_completo()}\n"
        texto += f"Carrera: {estudiante.carrera}\n"
        texto += "-" * 50 + "\n"

        inscripciones = [m for m in self.lista if m.estudiante_id == id_estudiante]
        if not inscripciones:
            texto += "El estudiante no tiene materias registradas.\n"
            return texto

        for mat in inscripciones:
            materia = self.materias.obtener(mat.materia_id)
            nombre_mat = materia.nombre if materia else "Materia eliminada"
            texto += f"{mat.periodo} | {nombre_mat} -> Nota: {mat.nota} [{mat.estado()}]\n"

        texto += "-" * 50
        return texto