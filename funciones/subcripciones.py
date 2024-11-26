# Standard library imports
import aiohttp
import json
import os
from typing import Dict
import asyncio
from datetime import datetime, time
import pytz

# Third-party imports
from highrise import BaseBot, GetMessagesRequest

class AdministradorSuscripciones:
    def __init__(self):
        self.archivo_suscriptores = "suscriptores.json"
        self.suscriptores = self.cargar_suscriptores()
        self.esperando_mensaje_admin = {}  # Diccionario de {user_id: bool}
        self.esperando_mensaje_masivo = {}  # Diccionario de {user_id: bool}
        self.esperando_nuevo_admin = {}  # Diccionario de {user_id: bool}
        self.esperando_eliminar_admin = {}  # Diccionario de {user_id: bool}
        
        self.mensaje_manana = """🌅 ¡Buenos días! 

Esperamos que hayas descansado bien. Que este nuevo día te traiga mucha alegría, felicidad, y momentos especiales. 

Nuestra sala siempre está abierta para ti 🤗
https://high.rs/room?id=6694de2ee40b58ae179d8ddf&invite_id=6744912d5edd6cffc721c64c"""

        self.mensaje_noche = """🌟 ¡Hola! Buenas noches ¿Ya visitaste nuestra sala hoy? 🌟

¡Ven a divertirte con nosotros!
https://high.rs/room?id=6694de2ee40b58ae179d8ddf&invite_id=6744912d5edd6cffc721c64c"""
        
    def cargar_suscriptores(self) -> Dict:
        """Carga la lista de suscriptores del archivo"""
        estructura_inicial = {
            "suscriptores": {},  # Diccionario username: {id: user_id, conv_id: conversation_id}
            "admins": {
                "Joshe11": "62b0bd2242167d511940de44"
            }
        }
        
        try:
            if os.path.exists(self.archivo_suscriptores):
                with open(self.archivo_suscriptores, 'r') as archivo:
                    data = json.load(archivo)
                    
                    # Limpiar y migrar datos
                    new_subs = {}
                    
                    # Procesar suscriptores existentes
                    for username, value in data.get("suscriptores", {}).items():
                        # Si el username empieza con "Usuario_", intentar obtener el ID real
                        if username.startswith("Usuario_"):
                            user_id = username.replace("Usuario_", "")
                            # No agregamos aquí, se agregará cuando el usuario interactúe
                            continue
                            
                        # Si es un string (formato antiguo)
                        if isinstance(value, str):
                            new_subs[username] = {
                                "id": value,
                                "conv_id": None
                            }
                        # Si ya está en el formato nuevo
                        elif isinstance(value, dict):
                            new_subs[username] = value
                    
                    data["suscriptores"] = new_subs
                    
                    # Asegurarse de que existe la estructura correcta
                    if "admins" not in data:
                        data["admins"] = estructura_inicial["admins"]
                    
                    return data
            return estructura_inicial
        except Exception as e:
            print(f"Error al cargar suscriptores: {e}")
            return estructura_inicial
    
    def guardar_suscriptores(self) -> None:
        """Guarda la lista de suscriptores en el archivo"""
        try:
            with open(self.archivo_suscriptores, 'w') as archivo:
                json.dump(self.suscriptores, archivo, indent=4)
        except Exception as e:
            print(f"Error al guardar suscriptores: {e}")

    async def obtener_username_webapi(self, user_id: str) -> str:
        """Obtiene el username usando la Web API de Highrise"""
        try:
            url = f"https://webapi.highrise.game/users/{user_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["user"]["username"]
                    return f"Usuario_{user_id}"
        except Exception as e:
            print(f"Error al obtener username de API: {e}")
            return f"Usuario_{user_id}"

    async def mostrar_menu(self, bot, id_usuario: str, id_conversacion: str) -> None:
        """Muestra el menú de opciones al usuario"""
        menu = """
        🌟 ¡Bienvenido al Sistema de Suscripción! 🌟
        
        Comandos disponibles:
        sub - Suscribirse para recibir noticias
        unsub - Cancelar suscripción
        status - Ver estado de suscripción
        
        ¡Suscríbete para no perderte ninguna novedad!
        """
        await bot.highrise.send_message(id_conversacion, menu)

    async def manejar_mensaje(self, bot, id_usuario: str, id_conversacion: str, mensaje: str) -> None:
        try:
            mensaje = mensaje.lower().strip()
            username = await self.obtener_username_webapi(id_usuario)
            
            # Verificar y actualizar la estructura si es necesario
            if username in self.suscriptores["suscriptores"]:
                if isinstance(self.suscriptores["suscriptores"][username], str):
                    old_id = self.suscriptores["suscriptores"][username]
                    self.suscriptores["suscriptores"][username] = {
                        "id": old_id,
                        "conv_id": id_conversacion
                    }
                else:
                    self.suscriptores["suscriptores"][username]["conv_id"] = id_conversacion
                self.guardar_suscriptores()

            if mensaje == "/adm":
                # Verificar si el usuario es admin por ID o es Joshe11
                es_admin = (id_usuario in self.suscriptores["admins"].values() or 
                          username in self.suscriptores["admins"])
                
                if es_admin:
                    self.esperando_mensaje_admin[id_usuario] = True
                    await self.manejar_mensaje_admin(bot, id_usuario, id_conversacion)
                else:
                    await bot.highrise.send_message(id_conversacion, "Función solo disponible para moderadores.")
                return
            
            # Si estamos esperando un mensaje masivo de este usuario
            elif self.esperando_mensaje_masivo.get(id_usuario, False):
                await self.enviar_mensaje_masivo(bot, mensaje)
                self.esperando_mensaje_masivo[id_usuario] = False
                await bot.highrise.send_message(id_conversacion, "✅ Mensaje enviado a todos los suscriptores.")
                await self.manejar_mensaje_admin(bot, id_usuario, id_conversacion)
                return
            
            # Si estamos esperando un comando de admin de este usuario
            elif self.esperando_mensaje_admin.get(id_usuario, False):
                if mensaje == "msg":
                    await bot.highrise.send_message(id_conversacion, "Por favor, ingresa el mensaje que quieres enviar a todos los suscriptores:")
                    self.esperando_mensaje_masivo[id_usuario] = True
                elif mensaje == "masivo":
                    menu_masivo = """
                    Selecciona el mensaje a enviar:
                    1 - Mensaje de buenos días
                    2 - Mensaje de noche
                    """
                    await bot.highrise.send_message(id_conversacion, menu_masivo)
                    self.esperando_mensaje_masivo[id_usuario] = "seleccion"
                elif self.esperando_mensaje_masivo.get(id_usuario) == "seleccion":
                    if mensaje == "1":
                        await self.enviar_mensaje_masivo(bot, self.mensaje_manana)
                        await bot.highrise.send_message(id_conversacion, "✅ Mensaje de buenos días enviado a todos los suscriptores.")
                    elif mensaje == "2":
                        await self.enviar_mensaje_masivo(bot, self.mensaje_noche)
                        await bot.highrise.send_message(id_conversacion, "✅ Mensaje de noche enviado a todos los suscriptores.")
                    else:
                        await bot.highrise.send_message(id_conversacion, "❌ Opción no válida. Por favor, selecciona 1 o 2.")
                        return
                    self.esperando_mensaje_masivo[id_usuario] = False
                    await self.manejar_mensaje_admin(bot, id_usuario, id_conversacion)
                elif mensaje == "listsub":
                    if not self.suscriptores["suscriptores"]:
                        await bot.highrise.send_message(id_conversacion, "📋 No hay suscriptores registrados aún.")
                    else:
                        total = len(self.suscriptores["suscriptores"])
                        mensaje = f"📋 Lista de Suscriptores ({total}):\n"
                        for username in self.suscriptores["suscriptores"].keys():
                            mensaje += f"• {username}\n"
                        await bot.highrise.send_message(id_conversacion, mensaje)
                elif mensaje == "listadm":
                    admins_list = "\n".join([f"• {username}" for username in self.suscriptores["admins"].keys()])
                    await bot.highrise.send_message(id_conversacion, f"📋 Administradores actuales:\n{admins_list}")
                elif mensaje == "addadm":
                    if id_usuario == "62b0bd2242167d511940de44":  # Solo Joshe11 puede agregar admins
                        await bot.highrise.send_message(id_conversacion, "Por favor, ingresa el ID del nuevo administrador:")
                        self.esperando_nuevo_admin[id_usuario] = True
                    else:
                        await bot.highrise.send_message(id_conversacion, "Solo Joshe11 puede agregar administradores.")
                elif mensaje == "deladm":
                    if id_usuario == "62b0bd2242167d511940de44":  # Solo Joshe11 puede eliminar admins
                        await bot.highrise.send_message(id_conversacion, "Por favor, ingresa el username del administrador a eliminar:")
                        self.esperando_eliminar_admin[id_usuario] = True
                    else:
                        await bot.highrise.send_message(id_conversacion, "Solo Joshe11 puede eliminar administradores.")
                elif mensaje == "salir":
                    self.esperando_mensaje_admin[id_usuario] = False
                    await bot.highrise.send_message(id_conversacion, "Has salido del panel de administración. 👋")
                elif self.esperando_nuevo_admin.get(id_usuario, False):
                    # Procesar nuevo admin
                    nuevo_admin_id = mensaje.strip()
                    try:
                        nuevo_admin_username = await self.obtener_username_webapi(nuevo_admin_id)
                        self.suscriptores["admins"][nuevo_admin_username] = nuevo_admin_id
                        self.guardar_suscriptores()
                        await bot.highrise.send_message(id_conversacion, f"✅ {nuevo_admin_username} ha sido agregado como administrador.")
                    except Exception as e:
                        await bot.highrise.send_message(id_conversacion, "❌ Error al agregar administrador. Verifica el ID.")
                    self.esperando_nuevo_admin[id_usuario] = False
                    await self.manejar_mensaje_admin(bot, id_usuario, id_conversacion)
                elif self.esperando_eliminar_admin.get(id_usuario, False):
                    # Procesar eliminación de admin
                    admin_username = mensaje.strip()
                    # Convertir a minúsculas para comparación
                    admin_username_lower = admin_username.lower()
                    
                    # Buscar el admin sin importar mayúsculas/minúsculas
                    admin_encontrado = None
                    for admin in self.suscriptores["admins"].keys():
                        if admin.lower() == admin_username_lower:
                            admin_encontrado = admin
                            break
                    
                    if admin_encontrado:
                        if admin_encontrado != "Joshe11":  # No permitir eliminar a Joshe11
                            del self.suscriptores["admins"][admin_encontrado]
                            self.guardar_suscriptores()
                            await bot.highrise.send_message(id_conversacion, f"✅ {admin_encontrado} ha sido eliminado de administradores.")
                        else:
                            await bot.highrise.send_message(id_conversacion, "❌ No se puede eliminar al administrador principal.")
                    else:
                        await bot.highrise.send_message(id_conversacion, "❌ Administrador no encontrado.")
                    
                    self.esperando_eliminar_admin[id_usuario] = False
                    await self.manejar_mensaje_admin(bot, id_usuario, id_conversacion)
                else:
                    await self.manejar_mensaje_admin(bot, id_usuario, id_conversacion)
                return
            
            # Comandos normales
            elif not self.esperando_mensaje_admin.get(id_usuario, False):
                if mensaje == "menu":
                    await self.mostrar_menu(bot, id_usuario, id_conversacion)
                elif mensaje == "sub":
                    await self.manejar_suscripcion(bot, id_usuario, id_conversacion)
                elif mensaje == "unsub":
                    await self.manejar_desuscripcion(bot, id_usuario, id_conversacion)
                elif mensaje == "status":
                    await self.mostrar_estado(bot, id_usuario, id_conversacion)
                else:
                    await self.mostrar_menu(bot, id_usuario, id_conversacion)
                
        except Exception as e:
            print(f"Error en manejar_mensaje: {e}")

    async def manejar_suscripcion(self, bot, id_usuario: str, id_conversacion: str) -> None:
        """Maneja la suscripción de un usuario"""
        try:
            username = await self.obtener_username_webapi(id_usuario)
            
            # Verificar si el username ya está suscrito
            if username not in self.suscriptores["suscriptores"]:
                self.suscriptores["suscriptores"][username] = {
                    "id": id_usuario,
                    "conv_id": id_conversacion
                }
                self.guardar_suscriptores()
                mensaje = """¡Te has suscrito exitosamente! 🎉
                
Nos alegra mucho tenerte con nosotros en la familia Paseito!! 💫
https://high.rs/room?id=6694de2ee40b58ae179d8ddf&invite_id=6744912d5edd6cffc721c64c"""
                await bot.highrise.send_message(id_conversacion, mensaje)
            else:
                await bot.highrise.send_message(id_conversacion, "¡Ya estás suscrito! 📫")
                
        except Exception as e:
            print(f"Error en manejar_suscripcion: {e}")
            await bot.highrise.send_message(id_conversacion, "Hubo un error al procesar tu suscripción. Por favor, intenta nuevamente.")

    async def manejar_desuscripcion(self, bot, id_usuario: str, id_conversacion: str) -> None:
        """Maneja la cancelación de suscripción"""
        try:
            username = await self.obtener_username_webapi(id_usuario)
            
            if username in self.suscriptores["suscriptores"]:
                del self.suscriptores["suscriptores"][username]
                self.guardar_suscriptores()
                await bot.highrise.send_message(id_conversacion, "Has cancelado tu suscripción. ¡Esperamos verte pronto! 👋")
            else:
                await bot.highrise.send_message(id_conversacion, "No estabas suscrito. 🤔")
                
        except Exception as e:
            print(f"Error en manejar_desuscripcion: {e}")
            await bot.highrise.send_message(id_conversacion, "Hubo un error al procesar tu desuscripción. Por favor, intenta nuevamente.")

    async def mostrar_estado(self, bot, id_usuario: str, id_conversacion: str) -> None:
        """Muestra el estado de suscripción del usuario"""
        try:
            username = await self.obtener_username_webapi(id_usuario)
            
            # Verificar si el username está en los suscriptores
            if username in self.suscriptores["suscriptores"]:
                await bot.highrise.send_message(id_conversacion, "✅ Estás suscrito y recibirás todas las novedades.")
            else:
                await bot.highrise.send_message(id_conversacion, "❌ No estás suscrito. Usa 'sub' para suscribirte.")
        except Exception as e:
            print(f"Error en mostrar_estado: {e}")
            await bot.highrise.send_message(id_conversacion, "Hubo un error al verificar tu estado.")

    async def manejar_mensaje_admin(self, bot, id_usuario: str, id_conversacion: str) -> None:
        """Maneja el envío de mensajes administrativos"""
        if id_usuario in self.suscriptores["admins"].values():
            menu_admin = """
        🌟 ¡Bienvenido al Panel de Administración! 🌟
        
        Comandos disponibles:
        msg - Enviar mensaje masivo personalizado
        masivo - Enviar mensaje predefinido (mañana/noche)
        listsub - Ver lista de suscriptores
        listadm - Ver lista de administradores
        addadm - Añadir nuevo administrador (Solo Joshe11)
        deladm - Eliminar administrador (Solo Joshe11)
        salir - Salir del panel de administración
        
        ¡Escribe el comando que desees usar!
        """
            self.esperando_mensaje_admin[id_usuario] = True
            await bot.highrise.send_message(id_conversacion, menu_admin)
        else:
            await bot.highrise.send_message(id_conversacion, "No tienes permisos de administrador. 🚫")

    async def enviar_mensaje_masivo(self, bot, mensaje: str) -> None:
        """Envía un mensaje a todos los suscriptores"""
        for username, datos in self.suscriptores["suscriptores"].items():
            try:
                if datos["conv_id"] is None:
                    print(f"⚠️ No hay ID de conversación para {username}")
                    continue
                
                # Si el mensaje es el mensaje_diario, enviarlo tal cual
                if mensaje == self.mensaje_diario:
                    mensaje_completo = mensaje
                else:
                    # Si es un mensaje personalizado del admin, agregar la invitación
                    mensaje_completo = f"""📢 Anuncio:
{mensaje}

Nos encantaría verte por nuestra sala, siempre es un gusto compartir contigo ✨
https://high.rs/room?id=6694de2ee40b58ae179d8ddf&invite_id=6744912d5edd6cffc721c64c"""
                
                await bot.highrise.send_message(datos["conv_id"], mensaje_completo)
                print(f"✅ Mensaje enviado a {username}")
                
            except Exception as e:
                print(f"❌ Error al enviar mensaje a {username}: {e}")
