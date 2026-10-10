from app.log_utils import get_daily_logger
from app.mysql_utils import mysql_execute, mysql_query, mysql_next_id

logger = get_daily_logger()

def get_sys_config():
    query_result = mysql_query("SELECT * FROM TB_DOM_CONFIG ORDER BY Id DESC LIMIT 1;")
    return {"error": 0, "message": "Ok", "response": query_result[0] if query_result else {}}

def add_sys_config(data):
    """
    Inserta la configuración del sistema.
    data es un diccionario con los campos de TB_DOM_CONFIG.
    Si no se envía Id, se genera con mysql_next_id para evitar depender de AUTO_INCREMENT.
    """
    from datetime import datetime

    try:
        data = dict(data or {})

        next_id = mysql_next_id('TB_DOM_CONFIG')
        if next_id in (None, ''):
            next_id = 1
        data['Id'] = next_id

        campos = ['Id']
        valores = [str(next_id)]

        if 'Creacion' not in data:
            campos.append('Creacion')
            valores.append(f"'{datetime.now().astimezone().strftime('%Y/%m/%d %H:%M:%S')}'")

        for key, value in data.items():
            if key == 'Id':
                continue
            campos.append(key)
            if isinstance(value, str):
                escaped_value = value.replace("'", "''")
                valores.append(f"'{escaped_value}'")
            else:
                valores.append(str(value))
        
        campos_str = ', '.join(campos)
        valores_str = ', '.join(valores)
        query = f"INSERT INTO TB_DOM_CONFIG ({campos_str}) VALUES ({valores_str})"
        
        #logger.info(f"[add_sys_config] Insertando: {query}")
        mysql_execute(query)
        return {"error": 0, "message": "Ok"}
    except Exception as e:
        logger.error(f"[add_sys_config] Error: {str(e)}")
        return {"error": 1, "message": f"Error: {str(e)}"}
