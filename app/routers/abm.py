import asyncio
from fastapi import APIRouter, Request, Form
from app.log_utils import get_daily_logger
from app.dom_utils import get_assign_status_id, get_assign_info_id
from app.abm.abm_hw import get_hardware_list, get_hardware, add_hardware, get_hardware_list_all, update_hardware, delete_hardware, set_hardware_update_flag, get_invalid_hardware_list
from app.abm.abm_sys import add_sys_config, get_sys_config
from app.abm.abm_assign import add_assign, get_assign_list, get_assign, get_assign_list_all, update_assign, delete_assign, change_assign_by_name, add_assign_to_planta, get_mobile_assign_list, switch_mobile_assign
from app.abm.abm_event import add_event, get_event_list, get_event_list_all, get_event, update_event, delete_event
from app.abm.abm_group import add_group, get_group_list, get_group_list_all, get_group, get_group_list_all, update_group, delete_group
from app.abm.abm_user import add_user, get_user_list, get_user, get_user_list_all, update_user, delete_user, get_invalid_card_list
from app.abm.abm_at import get_task_list, get_task_list_all, add_task, get_task, update_task, delete_task
from app.abm.abm_auto import get_auto_list, get_auto_list_all, add_auto, get_auto, update_auto, delete_auto
from app.abm.abm_touch import add_touch, delete_touch, get_touch, get_touch_list, get_touch_list_all, update_touch

logger = get_daily_logger()

router = APIRouter(prefix="/abm", tags=["abm"])

async def _run_docker_command(*args: str) -> str | None:
    command = ("docker", *args)
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError as exc:
        logger.exception("No se pudo iniciar el comando Docker: %s", command)
        return f"No se pudo iniciar Docker: {exc}"

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
    except asyncio.TimeoutError:
        process.kill()
        await process.communicate()
        logger.error("Tiempo de espera agotado para el comando Docker: %s", command)
        return f"Tiempo de espera agotado ejecutando: {' '.join(command)}"

    if process.returncode != 0:
        output = (stderr or stdout).decode(errors="replace").strip()
        logger.error(
            "Falló el comando Docker %s (código %s): %s",
            command,
            process.returncode,
            output,
        )
        return output or f"El comando terminó con código {process.returncode}"

    logger.info("Comando Docker ejecutado correctamente: %s", command)
    return None


### ABM de la configuración del sistema
@router.get("/abmsys")
async def abmsys_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmsys] Funcion: {funcion}")
        if funcion == "get_current":
            return get_sys_config()
        else:
            logger.info(f"[GET abmsys] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return {"error": 3, "message": "Función no informada"}

@router.post("/abmsys")
async def abmsys_post(request: Request):
    # Leer el POST
    form = await request.form()   # ← parsea x-www-form-urlencoded
    data = dict(form)
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmsys] Funcion: {funcion}")
        if funcion == "add":
            return add_sys_config(data)
        else:
            logger.info(f"[POST abmsys] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return {"error": 3, "message": "Función no informada"}

### ABM HW
@router.get("/abmhw")
async def abmhw_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    id = request_params.get("Id", 0)
    if funcion:
        #logger.info(f"[abmhw] Funcion: abmhw/{funcion}")
        if funcion == "get":
            return get_hardware(id)
        elif funcion == "delete":
            return delete_hardware(id)
        elif funcion == "list":
            return get_hardware_list()
        elif funcion == "listall":
            return get_hardware_list_all()
        elif funcion == "update_firmware":
            return set_hardware_update_flag(id, 1, 0, 0)
        elif funcion == "update_wifi":
            return set_hardware_update_flag(id, 0, 1, 0)
        elif funcion == "update_ioconfig":
            return set_hardware_update_flag(id, 0, 0, 1)
        elif funcion == "invalid_hw_list":
            return get_invalid_hardware_list()
        else:
            logger.info(f"[GET abmhw] Función desconocida: {funcion}")
            return {"error": 99, "message": f"Función: {funcion} no implementadad aún"}
    else:
        return get_hardware_list()

@router.post("/abmhw")
async def abmhw_post(request: Request):
    # Leer el POST
    form = await request.form()   # ← parsea x-www-form-urlencoded
    data = dict(form)
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmhw] Funcion: abmhw/{funcion}")
        if funcion == "add":
            return add_hardware(data)
        elif funcion == "update":
            return update_hardware(data)
        else:
            logger.info(f"[POST abmhw] Función desconocida: {funcion}")
            return {"error": 99, "message": f"Función: {funcion} no implementadad aún"}
    else:
        return {"error": 99, "message": "Función: no informada"}

### ABM Assign
@router.get("/abmassign")
async def abmassign_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)
    
    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmassign] Funcion: {funcion}")
        id = request_params.get("Id", None)
        planta = request_params.get("Planta", None)
        objeto = request_params.get("Objeto", None)
        if funcion == "status":
            return get_assign_status_id(id, planta)
        elif funcion == "info":
            return get_assign_info_id(id, planta)
        elif funcion == "switch":
            change_assign_by_name(objeto, 3)
            return {"error": 0, "message": "Ok"}
        elif funcion == "on":
            change_assign_by_name(objeto, 1)
            return {"error": 0, "message": "Ok"}
        elif funcion == "off":
            change_assign_by_name(objeto, 2)
            return {"error": 0, "message": "Ok"}
        elif funcion == "pulse":
            s = request_params.get("Segundos", None)
            change_assign_by_name(objeto, 4, s)
            return {"error": 0, "message": "Ok"}
        elif funcion == "get":
            return get_assign(id)
        elif funcion == "delete":
            return delete_assign(id)
        elif funcion == "list":
            return get_assign_list()
        elif funcion == "listall":
            return get_assign_list_all()
        elif funcion == "addassigntoplanta":
            return add_assign_to_planta(id, planta)
        else:
            logger.info(f"[GET abmassign] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return get_assign_list()

@router.post("/abmassign")
async def abmassign_post(request: Request):
    # Leer el POST
    form = await request.form()   # ← parsea x-www-form-urlencoded
    data = dict(form)
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmassign] Funcion: {funcion}")
        if funcion == "add":
            return add_assign(data)
        elif funcion == "update":
            return update_assign(data)
        else:
            logger.info(f"[POST abmassign] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return {"error": 3, "message": "Función no informada"}

### ABM Event
@router.get("/abmev")
async def abmevent_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmev] Funcion: {funcion}")
        id = request_params.get("Id", None)
        if funcion == "get":
            return get_event(id)
        elif funcion == "delete":
            return delete_event(id)
        elif funcion == "list":
            return get_event_list()
        elif funcion == "listall":
            return get_event_list_all()
        else:
            logger.info(f"[GET abmev] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return get_event_list()
    
@router.post("/abmev")
async def abmevent_post(request: Request):
    # Leer el POST
    form = await request.form()   # ← parsea x-www-form-urlencoded
    data = dict(form)
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmev] Funcion: {funcion}")
        if funcion == "add":
            return add_event(data)
        elif funcion == "update":
            return update_event(data)
        else:
            logger.info(f"[POST abmev] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return {"error": 3, "message": "Función no informada"}

### ABM Group
@router.get("/abmgroup")
async def abmgroup_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmgroup] Funcion: {funcion}")
        id = request_params.get("Id", None)
        if funcion == "get":
            return get_group(id)
        elif funcion == "delete":
            return delete_group(id)
        elif funcion == "list":
            return get_group_list()
        elif funcion == "listall":
            return get_group_list_all()
        else:
            logger.info(f"[GET abmgroup] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return get_group_list()
    
@router.post("/abmgroup")
async def abmgroup_post(request: Request):
    # Leer el POST
    form = await request.form()   # ← parsea x-www-form-urlencoded
    data = dict(form)
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmgroup] Funcion: {funcion}")
        if funcion == "add":
            return add_group(data)
        elif funcion == "update":
            return update_group(data)
        else:
            logger.info(f"[POST abmgroup] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return {"error": 3, "message": "Función no informada"}

### ABM User
@router.get("/abmuser")
async def abmuser_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmuser] Funcion: {funcion}")
        id = request_params.get("Id", None)
        if funcion == "get":
            return get_user(id)
        elif funcion == "delete":
            return delete_user(id)
        elif funcion == "list":
            return get_user_list()
        elif funcion == "listall":
            return get_user_list_all()
        elif funcion == "invalid_card_list":
            return get_invalid_card_list()
        else:
            logger.info(f"[GET abmuser] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return get_user_list()
    
@router.post("/abmuser")
async def abmuser_post(request: Request):
    # Leer el POST
    form = await request.form()   # ← parsea x-www-form-urlencoded
    data = dict(form)
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmuser] Funcion: {funcion}")
        if funcion == "add":
            return add_user(data)
        elif funcion == "update":
            return update_user(data)
        else:
            logger.info(f"[POST abmuser] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return {"error": 3, "message": "Función no informada"}
    

### ABM Task
@router.get("/abmat")
async def abmat_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmat] Funcion: {funcion}")
        id = request_params.get("Id", None)
        if funcion == "get":
            return get_task(id)
        elif funcion == "delete":
            return delete_task(id)
        elif funcion == "list":
            return get_task_list()
        elif funcion == "listall":
            return get_task_list_all(id)
        else:
            logger.info(f"[GET abmat] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return get_task_list()
    
@router.post("/abmat")
async def abmat_post(request: Request):
    # Leer el POST
    form = await request.form()   # ← parsea x-www-form-urlencoded
    data = dict(form)
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmat] Funcion: {funcion}")
        if funcion == "add":
            return add_task(data)
        elif funcion == "update":
            return update_task(data)
        else:
            logger.info(f"[POST abmat] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return {"error": 3, "message": "Función no informada"}

### ABM Automatizaciones
@router.get("/abmauto")
async def abmauto_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    tipo = request_params.get("Tipo", None)
    if funcion:
        #logger.info(f"[abmauto] Funcion: {funcion}")
        id = request_params.get("Id", None)
        if funcion == "get":
            return get_auto(id)
        elif funcion == "delete":
            return delete_auto(id)
        elif funcion == "list":
            return get_auto_list(tipo)
        elif funcion == "listall":
            return get_auto_list_all(tipo)
        else:
            logger.info(f"[GET abmauto] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return get_auto_list(tipo)
    
@router.post("/abmauto")
async def abmauto_post(request: Request):
    # Leer el POST
    form = await request.form()   # ← parsea x-www-form-urlencoded
    data = dict(form)
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmauto] Funcion: {funcion}")
        if funcion == "add":
            return add_auto(data)
        elif funcion == "update":
            return update_auto(data)
        else:
            logger.info(f"[POST abmauto] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return {"error": 3, "message": "Función no informada"}

### ABM Tactiles
@router.get("/abmtouch")
async def abmtouch_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    id = request_params.get("Id", None)
    pantalla = request_params.get("Pantalla", None)
    boton = request_params.get("Boton", None)
    if funcion:
        #logger.info(f"[abmtouch] Funcion: {funcion}")
        if funcion == "get":
            return get_touch(id, pantalla, boton)
        elif funcion == "delete":
            return delete_touch(id, pantalla, boton)
        elif funcion == "list":
            return get_touch_list(id, pantalla)
        elif funcion == "listall":
            return get_touch_list_all()
        elif funcion == "add":
            return add_touch(id, pantalla, boton)
        else:
            logger.info(f"[GET abmtouch] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return get_touch_list(id, pantalla)
    
@router.post("/abmtouch")
async def abmtouch_post(request: Request):
    # Leer el POST
    form = await request.form()   # ← parsea x-www-form-urlencoded
    data = dict(form)
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    if funcion:
        #logger.info(f"[abmtouch] Funcion: {funcion}")
        if funcion == "update":
            return update_touch(data)
        else:
            logger.info(f"[POST abmtouch] Función desconocida: {funcion}")
            return {"error": 3, "message": f"Función desconocida: {funcion}"}
    else:
        return {"error": 3, "message": "Función no informada"}

## dompi_mobile
@router.get("/mobile")
async def dompi_mobile_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)
    grupo = request_params.get("Grupo", None)
    objeto = request_params.get("Objeto", None)

    if funcion == "list":
        return get_mobile_assign_list(grupo)
    elif funcion == "touch":
        return switch_mobile_assign(objeto)
    else:
        return {"error": 3, "message": "Función no informada"}

@router.get("/update")
async def update_get(request: Request):
    # Parámetros GET (query string)
    request_params = dict(request.query_params)
    # Headers (variables del navegador)
    headers = dict(request.headers)

    # Me abro por función
    funcion = request_params.get("funcion", None)

    if funcion == "servicio":
        error = await _run_docker_command(
            "pull", "ghcr.io/wpirri/microdom:latest"
        )
        if error:
            return {"error": 5, "message": f"Error al descargar la imagen: {error}"}

        error = await _run_docker_command("restart", "microdom")
        if error:
            return {"error": 5, "message": f"Error al reiniciar microdom: {error}"}
        return {"error": 0, "message": "Comandos ejecutados correctamente"}
    elif funcion == "firmware":
        return {"error": 5, "message": "No implementado"}
    elif funcion == "web":
        return {"error": 5, "message": "No implementado"}
