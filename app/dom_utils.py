from app.log_utils import get_daily_logger
from app.mysql_utils import mysql_execute, mysql_query, mysql_next_id
from app.abm.abm_user import check_card_auth
from app.abm.abm_assign import change_assign_by_id
from app.abm.abm_group import change_group_by_id

logger = get_daily_logger()

def check_io_event(mac, io, status):
    logger.info(f"[check_io_event] EVENTO: HW: {mac} Port: {io} Status: {status}")
    if io == "CARD":
        cambio = "OFF_a_ON"
    else:
        cambio = "OFF_a_ON" if str(status) == "1" else "ON_a_OFF"
    query = (
        "SELECT EV.Enviar, EV.Objeto_Destino, EV.Grupo_Destino, EV.Particion_Destino, "
        "EV.Variable_Destino, EV.Parametro_Evento "
        "FROM TB_DOM_PERIF AS HW "
        "JOIN TB_DOM_ASSIGN AS ASS ON HW.Id = ASS.Dispositivo "
        "JOIN TB_DOM_EVENT AS EV ON ASS.Id = EV.Objeto_Origen "
        f"WHERE EV.{cambio} = 1 AND ASS.Port = %s AND HW.MAC = %s;"
    )
    query_result = mysql_query(query, (io, mac))

    if not query_result:
        return None

    for i in range(0, len(query_result)):
        if io == "CARD":
            # Tengo que validar la tarjeta para cada evento
            if not check_card_auth(status):
                return None
        if query_result[i]['Objeto_Destino']:
            logger.info(f"[check_io_event] ACCION: Enviar: {query_result[i]['Enviar']} a Objeto: {query_result[i]['Objeto_Destino']}")
            change_assign_by_id(query_result[i]['Objeto_Destino'], query_result[i]['Enviar'], query_result[i]['Parametro_Evento'])
            pass
        if query_result[i]['Grupo_Destino']:
            logger.info(f"[check_io_event] ACCION: Enviar: {query_result[i]['Enviar']} a Grupo: {query_result[i]['Grupo_Destino']}")
            change_group_by_id(query_result[i]['Grupo_Destino'], query_result[i]['Enviar'], query_result[i]['Parametro_Evento'])
            pass
        if query_result[i]['Particion_Destino']:
            logger.info(f"[check_io_event] ACCION: Enviar: {query_result[i]['Enviar']} a Particion: {query_result[i]['Particion_Destino']}")
            # TODO: Procesar evento para partición
            pass
        if query_result[i]['Variable_Destino']:
            logger.info(f"[check_io_event] ACCION: Enviar: {query_result[i]['Enviar']} a Variable: {query_result[i]['Variable_Destino']}")
            # TODO: Procesar evento para variable
            pass


    return query_result

def analyze_event(mac, changes, 
                  io1, io2, io3, io4, io5, io6, io7, io8, 
                  out1, out2, out3, out4, out5, out6, out7, out8, card):
    if changes != None:
        #logger.info(f"[analyze_event] MAC: {mac} Cambios: {changes}")
        for i in range(1, 9):
            if f"IO{i}" in changes:
                check_io_event(mac, f"IO{i}", eval(f"io{i}"))
            if f"OUT{i}" in changes:
                check_io_event(mac, f"OUT{i}", eval(f"out{i}"))
    if card != None:
        check_io_event(mac, "CARD", card)

def get_hw_io_status(hw_mac_addr):
    resp = "error=0&message=Ok"

    query_result = mysql_query(f"SELECT Port, Estado, Tipo FROM TB_DOM_ASSIGN WHERE (Tipo = 0 OR Tipo = 3 OR Tipo = 5) AND Dispositivo = (SELECT Id FROM TB_DOM_PERIF WHERE MAC = '{hw_mac_addr}')")
    if query_result:
        resp += "&" + "&".join([f"{item['Port']}={item['Estado']}" for item in query_result])
        return resp
    else:
        return "error=0&message=Ok"

def get_hw_update_data(hw_mac_addr, update_io=None):
    firmware = ""
    wifi_config = ""
    io_config = ""
    wiegand = ""
    io1 = "i"
    io2 = "i"
    io3 = "i"
    io4 = "i"
    io5 = "i"
    io6 = "i"

    query_result = mysql_query(f"SELECT Dispositivo, Tipo, Update_Firmware, Update_WiFi, Update_Config FROM TB_DOM_PERIF WHERE MAC = '{hw_mac_addr}'")
    if query_result:
        tipo_hw = query_result[0]['Tipo']
        #
        #   El dispositivo tiene que solicitar download de fiermware y reiniciar
        #
        if query_result[0]['Update_Firmware'] == 1:
            logger.info(f"Solicitando a {query_result[0]['Dispositivo']} que actualize firmware")
            firmware = "&update=firmware"
            mysql_execute(f"UPDATE TB_DOM_PERIF SET Update_Firmware = 0 WHERE MAC = '{hw_mac_addr}'")
        #
        #   Actualizazo configuración de wifi del dispositivo
        #
        if query_result[0]['Update_WiFi'] == 1:
            logger.info(f"Enviando datos de WiFi a: {query_result[0]['Dispositivo']}")
            config_result = mysql_query("SELECT * FROM TB_DOM_CONFIG ORDER BY Id DESC LIMIT 1;")
            if config_result:
                config = config_result[0]
                wifi_config += f"&ap1={config.get('Wifi_AP1', '')}"
                wifi_config += f"&ap1p={config.get('Wifi_AP1_Pass', '')}"
                wifi_config += f"&ap2={config.get('Wifi_AP2', '')}"
                wifi_config += f"&ap2p={config.get('Wifi_AP2_Pass', '')}"
                wifi_config += f"&ce1={config.get('Home_Host_1_Address', '')}"
                wifi_config += f"&ce2={config.get('Home_Host_2_Address', '')}"
                #
                if query_result[0]['Tipo'] == 1:
                    wifi_config += f"&rep=1"
                elif query_result[0]['Tipo'] == 5:
                    wifi_config += f"&rep={config.get('Wifi_Report', '')}"
                #
                wifi_config += f"&path={config.get('Rqst_Path', '')}"
            mysql_execute(f"UPDATE TB_DOM_PERIF SET Update_WiFi = 0 WHERE MAC = '{hw_mac_addr}'")
        #
        #   ACtualizo la configuración de I/O del dispositivo
        #
        if query_result[0]['Update_Config'] == 1 or update_io:
            if tipo_hw == 1:    # IO-WiFi
                logger.info(f"Enviando configuracion de I/O a: {query_result[0]['Dispositivo']}")
                config_result = mysql_query(f"SELECT A.Port, A.Tipo FROM TB_DOM_ASSIGN AS A, TB_DOM_PERIF AS P WHERE A.Dispositivo = P.Id AND P.MAC = '{hw_mac_addr}';")
                wiegand = "&wiegand=0"
                if config_result:
                    for item in config_result:
                        tipo = "x"
                        # Tipo
                        if item['Tipo'] == 0 or item['Tipo'] == 3 or item['Tipo'] == 5:
                            tipo = "o"
                        elif item['Tipo'] == 1 or item['Tipo'] == 4:
                            tipo = "i"
                        elif item['Tipo'] == 2:
                            tipo = "a"
                        # Port
                        if item['Port'] == "IO1":
                            io1 = tipo
                        elif item['Port'] == "IO2":
                            io2 = tipo
                        elif item['Port'] == "IO3":
                            io3 = tipo
                        elif item['Port'] == "IO4":
                            io4 = tipo
                        elif item['Port'] == "IO5":
                            io5 = tipo
                        elif item['Port'] == "IO6":
                            io6 = tipo
                        elif item['Port'] == "CARD":
                            wiegand = "&wiegand=1"
                # Armo la configuraciòn de I/O
                io_config = f"{wiegand}&cfgIO1={io1}&cfgIO2={io2}&cfgIO3={io3}&cfgIO4={io4}&cfgIO5={io5}&cfgIO6={io6}"
            elif tipo_hw == 5:      # Touch
                logger.info(f"Solicitando a {query_result[0]['Dispositivo']} que actualize configuracion")
                io_config = "&update=config"
                
            mysql_execute(f"UPDATE TB_DOM_PERIF SET Update_Config = 0 WHERE MAC = '{hw_mac_addr}'")
    # Devuelvo todas las configuraciones juntas
    return firmware + wiegand + io_config + wifi_config

def get_assign_status_id(id, planta):
    if id:
        query_result = mysql_query(f"SELECT Id, Objeto, Port, Icono_Apagado, Icono_Encendido, Estado, Tipo, Perif_Data, Analog_Mult_Div_Valor FROM TB_DOM_ASSIGN WHERE Id = {id};")
    else:
        if planta:
            query_result = mysql_query(f"SELECT Id, Objeto, Port, Icono_Apagado, Icono_Encendido, Estado, Tipo, Perif_Data, Analog_Mult_Div_Valor FROM TB_DOM_ASSIGN WHERE Planta = {planta};")
        else:  
            query_result = mysql_query("SELECT Id, Objeto, Port, Icono_Apagado, Icono_Encendido, Estado, Tipo, Perif_Data, Analog_Mult_Div_Valor FROM TB_DOM_ASSIGN")
    return {"error": 0, "message": "Ok", "response": query_result if query_result else []}
    
def get_assign_info_id(id, planta):
    if id:
        query_result = mysql_query(f"SELECT Id,Objeto,Tipo,Icono_Apagado,Icono_Encendido,Grupo_Visual,Planta,Cord_x,Cord_y FROM TB_DOM_ASSIGN WHERE Id = {id};")
    else:
        if planta:
            query_result = mysql_query(f"SELECT Id,Objeto,Tipo,Icono_Apagado,Icono_Encendido,Grupo_Visual,Planta,Cord_x,Cord_y FROM TB_DOM_ASSIGN WHERE Planta = {planta};")
        else:
            query_result = mysql_query("SELECT Id,Objeto,Tipo,Icono_Apagado,Icono_Encendido,Grupo_Visual,Planta,Cord_x,Cord_y FROM TB_DOM_ASSIGN;")

    return {"error": 0, "message": "Ok", "response": query_result if query_result else []}
