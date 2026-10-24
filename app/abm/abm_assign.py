from app.log_utils import get_daily_logger
from app.mysql_utils import mysql_execute, mysql_query, mysql_next_id

logger = get_daily_logger()

def get_assign_list():
    query = """SELECT ASS.Id, ASS.Objeto, HW.Dispositivo, ASS.Port, ASS.Tipo 
                FROM TB_DOM_ASSIGN AS ASS, TB_DOM_PERIF AS HW 
                WHERE ASS.Dispositivo = HW.Id 
                ORDER BY ASS.Objeto ASC;"""
    query_result = mysql_query(query);
    return {"error": 0, "message": "Ok", "response": query_result}

def get_assign_list_all():
    query_result = mysql_query("SELECT * FROM TB_DOM_ASSIGN")
    return {"error": 0, "message": "Ok", "response": query_result}

def get_assign(id):
    query_result = mysql_query(f"SELECT * FROM TB_DOM_ASSIGN WHERE Id = {id}")
    return {"error": 0, "message": "Ok", "response": query_result}

def add_assign(data):
    next_id = mysql_next_id('TB_DOM_ASSIGN')
    if next_id in (None, ''):
        next_id = 1
    data['Id'] = next_id
    data['Actualizar'] = 1  # Marcar para actualizar el HW

    campos = []
    valores = []
    for key, value in data.items():
        campos.append(key)
        if isinstance(value, str):
            escaped_value = value.replace("'", "''")
            valores.append(f"'{escaped_value}'")
        else:
            valores.append(str(value))

    campos_str = ', '.join(campos)
    valores_str = ', '.join(valores)
    query = f"INSERT INTO TB_DOM_ASSIGN ({campos_str}) VALUES ({valores_str})"

    #logger.info(f"[add_assign] Insertando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok", "Id": next_id}

def update_assign(data):
    Id = data.get('Id')
    if not Id:
        return {"error": 1, "message": "Id es requerido"}

    data['Actualizar'] = 1  # Marcar para actualizar el HW
    campos_valores = []
    for key, value in data.items():
        if key == 'Id':
            continue
        if isinstance(value, str):
            escaped_value = value.replace("'", "''")
            campos_valores.append(f"{key} = '{escaped_value}'")
        else:
            campos_valores.append(f"{key} = {value}")

    campos_valores_str = ', '.join(campos_valores)
    query = f"UPDATE TB_DOM_ASSIGN SET {campos_valores_str} WHERE Id = {Id}"

    #logger.info(f"[update_assign] Actualizando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}

def delete_assign(Id):
    if not Id:
        return {"error": 1, "message": "Id es requerido"}

    query = f"DELETE FROM TB_DOM_ASSIGN WHERE Id = {Id}"
    #logger.info(f"[delete_assign] Eliminando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}

def change_assign_by_id(id, accion, parametro=0):
    if accion == 1:
        logger.info(f"[change_assign_by_id] Encender: {id}")
        mysql_execute(f"UPDATE TB_DOM_ASSIGN SET Estado = 1, Actualizar = 1 WHERE Id = {id}")
    elif accion == 2:
        logger.info(f"[change_assign_by_id] Apagar: {id}")
        mysql_execute(f"UPDATE TB_DOM_ASSIGN SET Estado = 0, Actualizar = 1 WHERE Id = {id}")
    elif accion == 3:
        logger.info(f"[change_assign_by_id] Alternar: {id}")
        mysql_execute(f"UPDATE TB_DOM_ASSIGN SET Estado = (1 - Estado), Actualizar = 1 WHERE Id = {id}")
    elif accion == 4:
        if parametro == 0:
            parametro = 1  # Valor por defecto para la duración del pulso
        logger.info(f"[change_assign_by_id] Pulso de: {parametro}s a: {id}")
        mysql_execute(f"UPDATE TB_DOM_ASSIGN SET Estado = (1 + {parametro}), Actualizar = 1 WHERE Id = {id}")
    else:
        logger.warning(f"change_assign_by_id: acción desconocida {accion} para Id={id}")

def change_assign_by_name(name, accion, parametro=0):
    if accion == 1:
        logger.info(f"[change_assign_by_name] Encender: {name}")
        mysql_execute(f"UPDATE TB_DOM_ASSIGN SET Estado = 1, Actualizar = 1 WHERE Objeto = '{name}'")
    elif accion == 2:
        logger.info(f"[change_assign_by_name] Apagar: {name}")
        mysql_execute(f"UPDATE TB_DOM_ASSIGN SET Estado = 0, Actualizar = 1 WHERE Objeto = '{name}'")
    elif accion == 3:
        logger.info(f"[change_assign_by_name] Alternar: {name}")
        mysql_execute(f"UPDATE TB_DOM_ASSIGN SET Estado = (1 - Estado), Actualizar = 1 WHERE Objeto = '{name}'")
    elif accion == 4:
        if parametro == 0:
            parametro = 1  # Valor por defecto para la duración del pulso
        logger.info(f"[change_assign_by_name] Pulso de: {parametro}s a: {name}")
        mysql_execute(f"UPDATE TB_DOM_ASSIGN SET Estado = (1 + {parametro}), Actualizar = 1 WHERE Objeto = '{name}'")
    else:
        logger.warning(f"change_assign_by_name: acción desconocida {accion} para Objeto={name}")

def add_assign_to_planta(id, planta):
    if not id or not planta:
        return {"error": 1, "message": "Id y Planta son requeridos"}
    query = f"UPDATE TB_DOM_ASSIGN SET Icono_Apagado = 'lamp0.png',Icono_Encendido = 'lamp1.png', Cord_x = 200, Cord_y = 50, Planta = {planta}, Actualizar = 1 WHERE Id = {id}"
    #logger.info(f"[add_assign_to_planta] Actualizando: {query}")
    mysql_execute(query)
    return {"error": 0, "message": "Ok"}

def update_assign_state(mac, port, estado):
    if mac != None and port != None and estado != None:
        #logger.info(f"[update_assign_state] MAC: {mac}, Port: {port}, Estado: {estado}")
        query = f"UPDATE TB_DOM_ASSIGN SET Estado = {estado} WHERE Dispositivo = (SELECT Id FROM TB_DOM_PERIF WHERE MAC = '{mac}') AND Port = '{port}' AND (Tipo = 1 OR Tipo = 2 OR Tipo = 4 OR Tipo = 6) AND Estado != {estado}"
        mysql_execute(query)

def get_mobile_assign_list(grupo):
    if grupo:
        query_result = mysql_query(f"SELECT Id, Objeto, Tipo, Icono_Apagado, Icono_Encendido, Estado, Grupo_Visual, Planta, Cord_x, Cord_y FROM TB_DOM_ASSIGN WHERE Grupo_Visual = '{grupo}';")
    else:
        query_result = mysql_query("SELECT Id, Objeto, Tipo, Icono_Apagado, Icono_Encendido, Estado, Grupo_Visual, Planta, Cord_x, Cord_y FROM TB_DOM_ASSIGN;")
    return {"error": 0, "message": "Ok", "response": query_result if query_result else []}

def switch_mobile_assign(objeto):
    if objeto:
        mysql_execute(f"UPDATE TB_DOM_ASSIGN SET Estado = (1 - Estado), Actualizar = 1 WHERE Objeto = '{objeto}'")
        return {"error": 0, "message": "Ok"}
    else:
        return {"error": 1, "message": "Objeto es requerido"}