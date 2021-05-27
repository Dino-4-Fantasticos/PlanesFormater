import glob
import json

planes_nombres = []
claves_materias = []

materias = []
planes = []

materias_samp = []
planes_samp = []


def unregistered_course(materia):
    global claves_materias
    return materia["clave"] not in claves_materias


def read_file():
    global materias, claves_materias, planes_nombres, planes

    file_names = glob.glob("./json_formats/*.json")

    for file_name in file_names:
        file = open(file_name, "r")
        yeison = json.loads(file.readline())
        materias_plan = []

        for semestre in yeison["materias"]:
            materias_semestre = []

            for materia in semestre:
                if materia["clave"]:
                    if unregistered_course(materia):
                        claves_materias.append(materia["clave"])
                        materias.append(materia)

                    materias_semestre.append({"clave": materia["clave"]})

            materias_plan.append(materias_semestre)

        yeison["materias"] = materias_plan

        if yeison["siglas"] not in planes_nombres:
            planes.append(yeison)
            planes_nombres.append(yeison["siglas"])

        file.close()


def write_file():
    with open("formated/materias.json", "w") as outfile:
        json.dump(materias, outfile, indent=2, ensure_ascii=False)

    with open("formated/planes.json", "w") as outfile:
        json.dump(planes, outfile, indent=2, ensure_ascii=False)


def isTec21(nombre_plan):
    return int(nombre_plan[-2:]) >= 19


def generate_json(line, materias_semestre):
    global materias_samp
    attributes = line.replace("\n", "").split("\t")
    clave = attributes[0]

    if len(attributes) != 7:
        json_var = {
            "clave": clave,
            "nombre": attributes[1],
            "horasClase": int(attributes[2]),
            "horasLaboratorio": int(attributes[3]),
            "unidades": int(attributes[4]),
            "creditosAcademicos": float(attributes[5]),
        }

    else:
        json_var = {
            "clave": clave,
            "nombre": attributes[1],
            "horasClase": int(attributes[2]),
            "horasLaboratorio": int(attributes[3]),
            "unidades": float(attributes[4]),
            "creditosAcademicos": float(attributes[5]),
            "unidadesDeCarga": float(attributes[6]),
        }

    if clave not in claves_materias:
        materias_samp.append(json_var)
        claves_materias.append(clave)

    materias_semestre.append({"clave": clave})


def readTec20(file, nombre_plan):
    global planes_samp
    materias_semestre = []

    plan = {
        "siglas": nombre_plan,
        "nombre": file.readline().replace("\n", ""),
        "esVigente": True,
        "esTec21": False,
        "materias": [],
    }

    line = file.readline()
    while line:
        if "Semestre" in line:
            if len(materias_semestre):
                plan["materias"].append(materias_semestre)
            materias_semestre = []

        elif "Clave\tNombre" not in line and line[0].isalpha() and "Code\tName" not in line:
            generate_json(line, materias_semestre)

        line = file.readline()

    plan["materias"].append(materias_semestre)
    materias_semestre = []
    planes_samp.append(plan)
    planes_nombres.append(nombre_plan)


def readTec21(file, nombre_plan):
    global planes_samp
    materias_semestre = []

    plan = {
        "siglas": nombre_plan,
        "nombre": file.readline().replace("\n", ""),
        "esVigente": True,
        "esTec21": True,
        "materias": [],
    }

    banned_lines = [
        "Unidad de formación\n",
        "CL\n",
        "A\n",
        "U\n",
        "CA\n",
        "UDC\n",
        "Clave\tDescripción\n",
    ]

    line = file.readline()
    while line:
        if "Semestre" in line:
            if len(materias_semestre):
                plan["materias"].append(materias_semestre)
            materias_semestre = []

        elif "Semana" not in line and line not in banned_lines:
            complete_line = line.replace("\n", "\t") + file.readline()
            generate_json(complete_line, materias_semestre)

        line = file.readline()

    plan["materias"].append(materias_semestre)
    materias_semestre = []
    planes_samp.append(plan)
    planes_nombres.append(nombre_plan)


def read_samp_file():
    global materias, claves_materias, planes_nombres, planes, materias_samp

    file_names = glob.glob("./txt_formats/*.txt")

    for file_name in file_names:
        file = open(file_name, "r")

        nombre_plan = file_name.replace(".txt", "").replace("./samp/", "").upper()

        if nombre_plan in planes_nombres:
            continue

        if isTec21(nombre_plan):
            readTec21(file, nombre_plan)
        else:
            readTec20(file, nombre_plan)


def write_samp_file():
    with open("formated/materias_samp.json", "w") as outfile:
        json.dump(materias_samp, outfile, indent=2, ensure_ascii=False)

    with open("formated/planes_samp.json", "w") as outfile:
        json.dump(planes_samp, outfile, indent=2, ensure_ascii=False)


read_samp_file()
read_file()

write_samp_file()
write_file()

print("Ganamos")
