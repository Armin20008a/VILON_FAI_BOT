# Standard library imports
import random
import asyncio 
import os
import importlib.util

# Third-party imports
from deep_translator import GoogleTranslator
from highrise import BaseBot, Position, SessionMetadata, User, CurrencyItem, Item, Reaction, AnchorPosition

# Local imports
from funciones.loop import emote, loop_emote, stop_loop, loop, check_position_and_emote
from funciones.teleport import teleporter
from funciones.subcripciones import AdministradorSuscripciones

class Bot(BaseBot):
    # Constantes de clase
    GOODBYE_MESSAGES = [
        "¡Nos vemos! 🌴",
        "¡Cuídate, hasta luego! 🍃",
        "¡Gracias por venir! 🌟",
        "¡Hasta la próxima! 🌺",
        "¡Que tengas un buen día! 🍂",
    ]

    SUPPORTED_LANGUAGES = {
        'es': 'Español',
        'en': 'Inglés',
        'fr': 'Francés',
        'de': 'Alemán',
        'it': 'Italiano',
        'pt': 'Portugués',
        'ja': 'Japonés',
        'zh': 'Chino',
        'ar': 'Árabe',
        'hi': 'Hindi',
        'tr': 'Turco',
        'ru': 'Ruso',
        'ko': 'Coreano',
        'vi': 'Vietnamita',
        'id': 'Indonesio',
        'th': 'Tailandés',
        'ms': 'Malayo',
        'nl': 'Neerlandés',
        'pl': 'Polaco',
        'cs': 'Checo',
        'sk': 'Eslovaco',
        'sl': 'Esloveno',
        'bg': 'Búlgaro',
        'ro': 'Rumano',
        'hu': 'Húngaro',
        'fi': 'Finés',
        'sv': 'Sueco',
        'no': 'Noruego',
        'da': 'Danés',
        'is': 'Islandés',
        'gl': 'Gallego',
        'ca': 'Catalán',
        'eu': 'Euskera/Vasco',
        'la': 'Latín',
        'eo': 'Esperanto',
        'mk': 'Macedonio'
    }

    def __init__(self):
        super().__init__()
        self.room_users = []
        self.user_conversations = {}
        self.active_translation_users = {}
        self.bot_id = None
        self.admin_suscripciones = AdministradorSuscripciones()

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("INICIO")
        await self.highrise.teleport(session_metadata.user_id, Position(0.5, 8.25, 2.5, "FrontRight"))
        await self.highrise.chat("¡Bot iniciado!")
        asyncio.create_task(self.repeat_emote())
        asyncio.create_task(self.send_information())

    async def on_chat(self, user: User, message: str) -> None:
        """
        Maneja todos los mensajes del chat y sus comandos.
        """
        message_lower = message.lower().strip()

        try:
            if message_lower == "stop":
                await stop_loop(self, user)
            else:
                await loop(self, user, message_lower)

            # Comandos de traducción
            if message_lower.startswith("!text"):
                await self.activate_translation(user, message_lower)
            elif message_lower == "!stop":
                await self.deactivate_translation(user)
            elif user.id in self.active_translation_users:
                await self.translate_message(user, message)
            elif message_lower.startswith("ir "):
                await self.ir(user, message)
                return

            # Comandos especiales
            if message_lower == "paseito!":
                await self.start_tour(user)
            elif message_lower.startswith("wallet"):
                privileges = await self.highrise.get_room_privilege(user.id)
                if user.username != "Joshe11" and not (privileges.moderator or privileges.designer):
                    await self.highrise.chat("Función solo disponible para moderadores.")
                    return
                await self.handle_wallet_command(user)
            elif message_lower.startswith("all"):
                privileges = await self.highrise.get_room_privilege(user.id)
                if user.username != "Joshe11" and not (privileges.moderator or privileges.designer):
                    await self.highrise.chat("Función solo disponible para moderadores.")
                    return
                await self.handle_all_command(user, message_lower)
            elif message_lower.startswith("/tipme "):
                if user.username != "Joshe11":
                    pass
                else:
                    await self.handle_tipme_command(user, message)
            
            # Comandos de teleportación
            elif any(message_lower.startswith(cmd) for cmd in ["paseito"]):
                await teleporter(self, user, message_lower)
            elif message_lower == "vente!":
                privileges = await self.highrise.get_room_privilege(user.id)
                if user.username != "Joshe11" and not (privileges.moderator or privileges.designer):
                    await self.highrise.chat("Función solo disponible para moderadores.")
                    return
                await self.highrise.walk_to(Position(user.id.x + 1, user.id.y, user.id.z))

            # Comandos de interacción
            elif message_lower.startswith(("bailemos", "ansiedad", "salutacion", "volemos", "motomami", "encantar", "batalla")):
                await self.handle_interaction_command(user, message_lower)

            # Comandos con prefijo /
            elif message_lower.startswith("/"):
                await self.command_handler(user, message_lower)

        except Exception as e:
            await self.highrise.chat(f"Error en on_chat: {e}")

    async def on_message(self, user_id: str, conversation_id: str, is_new_conversation: bool) -> None:
        """Maneja los mensajes privados recibidos por el bot"""
        try:
            # Obtener el mensaje
            response = await self.highrise.get_messages(conversation_id)
            if not response.messages:  # Si no hay mensajes
                return
                
            message = response.messages[0].content
            
            # Obtener información del usuario usando get_room_users
            room_users = await self.highrise.get_room_users()
            user_info = None
            for user, pos in room_users.content:
                if user.id == user_id:
                    user_info = user
                    break
            
            print(f"👤 {user_info.username} escribió: {message}")
            await self.admin_suscripciones.manejar_mensaje(self, user_id, conversation_id, message)
            
        except Exception as e:
            print(f"Error en on_message: {e}")
            import traceback
            traceback.print_exc()

    async def on_user_join(self, user: User, position) -> None:
        """Maneja la entrada de usuarios a la sala."""
        try:
            print(f"{user.username} ENTRÓ.")
            wm = ["✨",
                  "🌺", 
                  "🌟", 
                  "🌴"]
            T = random.choice(wm)
            await self.highrise.chat(f"Bienvenid@ @{user.username} {T}")
            await self.show_help(user)
        except Exception as e:
            print(f"Error en on_user_join: {e}")

    async def on_user_leave(self, user: User) -> None:
        """Maneja la salida de usuarios de la sala."""
        while True:
            try:   
                goodbye_message = random.choice(self.GOODBYE_MESSAGES)
                await self.highrise.chat(f"\nSalió: @{user.username}\n{goodbye_message}")
                break  # Si el mensaje se envió correctamente, salir del bucle
                
            except Exception as e:
                if "connection with ID:" in str(e):
                    await asyncio.sleep(5)
                    continue  # Reintentar si es error de conexión
                else:
                    print(f"Error en on_user_leave: {e}")
                    break  # Salir si es otro tipo de error

    async def repeat_emote(self) -> None:
        while True:
            try:
                bailes = ["dance-weird", "idle-floating", "emote-timejump", "emote-robot", 
                         "emote-shrink", "emote-gordonshuffle"]
                await asyncio.sleep(5.55)
                await self.highrise.send_emote(random.choice(bailes))
            except Exception as e:
                await asyncio.sleep(5)
                continue

    async def handle_wallet_command(self, user: User) -> None:
        """Maneja el comando de wallet (solo para moderadores)."""
        if user.username != "Joshe11":
            await self.highrise.chat("Función sólo para moderadores.")
            return
        wallet = (await self.highrise.get_wallet()).content
        await self.highrise.send_whisper(user.id, f"La cartera del bot contiene {wallet[0].amount} {wallet[0].type}")

    async def handle_all_command(self, user: User, message: str) -> None:
        """Maneja el comando 'all' (solo para moderadores)."""
        if user.username != "Joshe11":
            await self.highrise.chat("Función sólo para moderadores.")
            return
        await emote(self, user, message)

    async def handle_interaction_command(self, user: User, message: str) -> None:
        """Maneja los comandos de interacción entre usuarios."""
        interaction_commands = {
            "bailemos": ("dance-weird", "dance-kawai", "bailando uoh-uoh!"),
            "salutacion": ("emote-bow", "emote-curtsy", "son distinguidos!"),
            "ansiedad": ("emote-creepycute", "emote-launch", "incomprensibles!"),
            "volemos": ("emote-astronaut", "emote-looping", "por los aires!"),
            "motomami": ("emote-sleigh", "emote-sleigh", "a rodar!"),
            "encantar": ("emote-telekinesis", "emote-gravity", "encantó a"),
            "batalla": ("emote-boxer", "emote-boxer", "batalla con")
        }

        try:
            # Validar formato básico del comando
            parts = message.lower().split()
            if len(parts) < 2 or not parts[1].startswith("@"):
                await self.highrise.chat("Uso correcto: comando @usuario")
                return

            # Obtener usuario objetivo
            target_name = parts[1][1:].lower()
            room_users = await self.highrise.get_room_users()
            target_user = next((content[0] for content in room_users.content 
                              if content[0].username.lower() == target_name), None)
            
            if not target_user:
                await self.highrise.chat(f"Usuario {target_name} no encontrado en la sala.")
                return

            # Ejecutar comando de interacción
            command = next((cmd for cmd in interaction_commands if message.lower().startswith(cmd)), None)
            if command:
                emote1, emote2, text = interaction_commands[command]
                await self.highrise.chat(f"\n@{user.username} {text} @{target_user.username}")
                await self.highrise.send_emote(emote1, user.id)
                await self.highrise.send_emote(emote2, target_user.id)

        except Exception as e:
            await self.highrise.chat(f"Error: {e}")

    # Métodos de traducción
    async def activate_translation(self, user: User, message_lower: str) -> None:
        """Activa la traducción automática para un usuario."""
        parts = message_lower.split()
        
        if len(parts) == 3:
            source_lang = parts[1]
            target_lang = parts[2]
            
            if source_lang in self.SUPPORTED_LANGUAGES and target_lang in self.SUPPORTED_LANGUAGES:
                self.active_translation_users[user.id] = {
                    'source': source_lang,
                    'target': target_lang
                }
                await self.highrise.chat(
                    f"Traducción activada para @{user.username} de "
                    f"{self.SUPPORTED_LANGUAGES[source_lang].upper()} a {self.SUPPORTED_LANGUAGES[target_lang].upper()}"
                )
            else:
                await self.highrise.chat(
                    f"@{user.username} Idiomas no soportados. Usa '/languages' para ver la lista de idiomas disponibles."
                )
        else:
            await self.highrise.chat(f"@{user.username} Uso: !text [idioma_origen] [idioma_destino]")

    async def deactivate_translation(self, user: User) -> None:
        """Desactiva la traducción automática para un usuario."""
        if user.id in self.active_translation_users:
            del self.active_translation_users[user.id]
            await self.highrise.chat(f"@{user.username} Traducción desactivada")
        else:
            await self.highrise.chat(f"@{user.username} La traducción no estaba activada")

    async def translate_message(self, user: User, message: str) -> None:
        """Traduce y envía un mensaje."""
        try:
            translation_config = self.active_translation_users[user.id]
            translator = GoogleTranslator(
                source=translation_config['source'],
                target=translation_config['target']
            )
            translated_text = translator.translate(message)
            await self.highrise.chat(
                f"@{user.username} dijo: \"{translated_text}\""
            )
        except Exception as e:
            await self.highrise.chat(f"Error en la traducción: {str(e)}")

    # Métodos de tour y teleportación
    async def start_tour(self, user: User) -> None:
        """Inicia un tour guiado por la sala."""
        try:
            # Datos del tour: posiciones y emotes
            tour_data = [
                {"position": Position(0.5, 1.5, 29.5), "emote": "idle-enthusiastic", "teleport": True},
                {"position": Position(2.0, 0.0, 4.5), "emote": "emote-confused", "teleport": True},
                {"position": Position(9.5, 11.0, 7.5), "emote": "emote-pose9", "teleport": True},
                {"position": Position(0.5, 8.25, 1.5), "emote": "emote-looping", "teleport": True},
                {"position": Position(16.5, 13.5, 19), "emote": "emote-astronaut", "teleport": True},
                {"position": Position(0.5, 6.75, 29.5), "emote": "emote-pose8", "teleport": True},
                {"position": Position(14.5, 2.25, 17.5), "emote": 'emote-teleporting', "teleport": True},
                {"position": Position(13.5, 17.75, 4.0), "emote": "idle-enthusiastic", "teleport": True},
                {"position": Position(16.5, 5, 23.5), "emote": "emote-hyped", "teleport": True},
                {"position": Position(12, 1, 10), "emote": "idle-enthusiastic", "teleport": False}
            ]

            await self.highrise.send_whisper(user.id, f"@{user.username} ¡Comenzando el tour!")
            
            for stop in tour_data:
                try:
                    # Teleportar al usuario a la posición
                    if stop["teleport"]:
                        await self.highrise.teleport(user.id, stop["position"])
                    
                    # Ejecutar el emote
                    await self.highrise.send_emote(stop["emote"], user.id)
                    
                    # Esperar antes de la siguiente posición
                    await asyncio.sleep(7)
                    
                except Exception as e:
                    print(f"Error durante una parada del tour: {e}")
                    continue  # Continuar con la siguiente parada si hay error
            
            await self.highrise.send_whisper(user.id, f"@{user.username} ¡Tour completado!")
            
        except Exception as e:
            print(f"Error durante el tour: {e}")
            await self.highrise.send_whisper(user.id, f"@{user.username} Lo siento, hubo un error durante el tour.")

    async def teleport_to_position(self, user: User, position: Position) -> None:
        """Teleporta a un usuario a una posición específica."""
        try:
            await self.highrise.teleport(user.id, position)
        except Exception as e:
            await self.highrise.send_whisper(user.id, f"Error al teleportar: {e}")

    # Métodos de manejo de tips y economía
    async def handle_tipme_command(self, user: User, message: str) -> None:
        """Procesa los comandos de propinas."""
        try:
            # Extraer la cantidad del mensaje
            amount = message.split()[1]
            if not amount.isdigit():
                await self.highrise.send_whisper(user.id, "Por favor, especifica una cantidad válida.")
                return

            amount = int(amount)
            if amount < 1:
                await self.highrise.send_whisper(user.id, "La cantidad debe ser mayor que 0.")
                return

            # Intentar realizar la transacción
            try:
                await self.highrise.tip_user(user.id, amount)
                await self.highrise.send_whisper(user.id, f"¡Se han enviado {amount} monedas a @{user.username}!")
            except Exception as e:
                await self.highrise.send_whisper(user.id, "No se pudo procesar la propina. Verifica tu saldo.")

        except Exception as e:
            await self.highrise.send_whisper(user.id, f"Error al procesar la propina: {e}")

    # Métodos de información y utilidad
    async def send_information(self) -> None:
        """Envía información periódica a la sala."""
        while True:
            try:
                await asyncio.sleep(300)
                messages = [
                    "¡Escribe ' /ayuda ' para ver todos los comandos disponibles!",
                    "¡Usa ' /info ' para conocer más sobre el bot!",
                    "¡Usa ' paseito! ' para dar un tour por la sala!",
                    "¡Usa ' ir @usuario ' para ir a la posición de un usuario!",
                    "¡Usa ' !text es en ' para activar la traducción!",
                    "¡Paseito, tu mejor compañía en Highrise!\n",
                    "¡En Paseito apoyamos el talento local en Highrise.🎤\nSi desea promocionar canciones en nuestra emisora, escríbale a @Joshe11!\n",
                    "¡Envíe 5g al Bot y reciba un poema especial como agradecimiento!\n",
                    "¡Para conocer los emotes disponibles, revise la descripción del bot!\n",
                    "¡No olvides revisar la descripción de la sala para más detalles y sorpresas!\n",
                    "¡Escriba un mensaje al DM (privado) del bot para suscribirse a nuestras notificaciones!\n"
                ]
                await self.highrise.chat(random.choice(messages))
            except Exception as e:
                if "connection with ID:" in str(e):
                    await asyncio.sleep(5)
                continue

    async def command_handler(self, user: User, message: str) -> None:
        """Maneja comandos especiales que comienzan con '/'."""
        try:
            cmd = message[1:].split()[0].lower()
            commands = {
                'ayuda': self.show_help,
                'info': self.show_info,
                'reglas': self.show_rules,
                'idiomas': self.show_languages,
                'emotes': self.show_emotes
            }

            if cmd in commands:
                await commands[cmd](user)
            else:
                await self.highrise.send_whisper(user.id, "Comando desconocido. Usa '/ayuda' para ver los comandos disponibles.")

        except Exception as e:
            await self.highrise.send_whisper(user.id, f"Error al procesar el comando: {e}")

    # Métodos de ayuda y documentación
    async def show_help(self, user: User) -> None:
        """Muestra la lista de comandos disponibles."""
        # Primer mensaje: Comandos de traducción
        help_text1 = (
            "📝 COMANDOS DE TRADUCCIÓN:\n"
            "• !text [origen] [destino] - Activa traducción\n"
            "• !stop - Desactiva traducción\n"
        )
        await self.highrise.send_whisper(user.id, help_text1)
        await asyncio.sleep(0.5)

        # Segundo mensaje: Comandos de información
        help_text2 = (
            "ℹ️ COMANDOS DE INFORMACIÓN:\n"
            "• /info - Información del bot\n"
            "• /emotes - Lista de emotes disponibles\n"
            "• /reglas - Reglas de la sala\n"
            "• /idiomas - Idiomas disponibles"
            "• Escriba un mensaje al DM (privado) del bot para suscribirse a nuestras notificaciones"
        )
        await self.highrise.send_whisper(user.id, help_text2)
        await asyncio.sleep(0.5)

        # Tercer mensaje: Comandos de interacción
        help_text3 = (
            "🎮 COMANDOS DE INTERACCIÓN:\n"
            "• bailemos @usuario - Bailan\n"
            "• volemos @usuario - Vuelan\n"
            "• encantar @usuario - Poder mágico\n"
            "• motomami @usuario - Motean\n"
            "• ansiedad @usuario - Random\n"
            "• batalla @usuario - Boxean\n"
            "• salutacion @usuario - Se saludan"
        )
        await self.highrise.send_whisper(user.id, help_text3)

    async def show_info(self, user: User) -> None:
        """Muestra información sobre el bot."""
        info_text = """
        🤖 Bot de Asistencia y Diversión
        Versión: 1.0
        Creado por: Joshe11
        ¡Estoy aquí para ayudarte y hacer la sala más divertida!
        """
        await self.highrise.send_whisper(user.id, info_text)

    async def show_rules(self, user: User) -> None:
        """Muestra las reglas de la sala."""
        rules_text = """
        📜 Reglas de la sala:
        1. Respeta a todos los usuarios
        2. No spam ni flood
        3. No acoso ni comportamiento tóxico
        4. Diviértete y haz amigos
        """
        await self.highrise.send_whisper(user.id, rules_text)

    async def show_languages(self, user: User) -> None:
        """Muestra la lista de idiomas disponibles con instrucciones."""
        # Parte 1: Instrucciones
        instructions = (
            "📝 INSTRUCCIONES DE TRADUCCIÓN:\n"
            "• Para activar: !text [origen] [destino]\n"
            "• Para desactivar: !stop\n\n"
            "💡 EJEMPLO:\n"
            "!text es en - (español a inglés)\n"
            "!text en es - (inglés a español)"
        )
        await self.highrise.send_whisper(user.id, instructions)
        await asyncio.sleep(0.5)

        # Parte 2: Primera sección de idiomas
        languages1 = (
            "📚 IDIOMAS (1/4):\n"
            "de: Alemán\n"
            "ar: Árabe\n"
            "bg: Búlgaro\n"
            "ca: Catalán\n"
            "zh: Chino\n"
            "ko: Coreano\n"
            "cs: Checo\n"
            "da: Danés\n"
            "sk: Eslovaco\n"
            "sl: Esloveno"
        )
        await self.highrise.send_whisper(user.id, languages1)
        await asyncio.sleep(0.5)

        # Parte 3: Segunda sección de idiomas
        languages2 = (
            "📚 IDIOMAS (2/4):\n"
            "es: Español\n"
            "eo: Esperanto\n"
            "eu: Euskera/Vasco\n"
            "fi: Finés\n"
            "fr: Francés\n"
            "gl: Gallego\n"
            "hi: Hindi\n"
            "nl: Holandés\n"
            "hu: Húngaro\n"
            "en: Inglés"
        )
        await self.highrise.send_whisper(user.id, languages2)
        await asyncio.sleep(0.5)

        # Parte 4: Tercera sección de idiomas
        languages3 = (
            "📚 IDIOMAS (3/4):\n"
            "id: Indonesio\n"
            "is: Islandés\n"
            "it: Italiano\n"
            "ja: Japonés\n"
            "la: Latín\n"
            "mk: Macedonio\n"
            "ms: Malayo\n"
            "no: Noruego\n"
            "pl: Polaco\n"
        )
        await self.highrise.send_whisper(user.id, languages3)
        await asyncio.sleep(0.5)

        # Parte 5: Última sección y ejemplos
        try:
            languages4 = (
                "📚 IDIOMAS (4/4):\n"
                "ro: Rumano\n"
                "ru: Ruso\n"
                "sv: Sueco\n"
                "th: Tailandes\n"
                "tr: Turco\n"
                "vi: Vietnamita\n"
            )
            await self.highrise.send_whisper(user.id, languages4)
            await asyncio.sleep(0.2)
            
            # Enviar portugués en un mensaje separado
            await self.highrise.send_whisper(user.id, "\npt: Portugues")
            
        except Exception as e:
            print(f"Error enviando languages4: {e}")

    async def show_emotes(self, user: User) -> None:
        """Muestra la lista de emotes disponibles."""
        from funciones.loop import emote_list
        
        # Instrucciones
        instructions = (
            "🎭 CÓMO USAR EMOTES:\n"
            "• Para repetir: escriba solo el nombre del emote\n"
            "• Para detener: escriba 'stop'"
        )
        await self.highrise.send_whisper(user.id, instructions)
        await asyncio.sleep(0.5)

        # Obtener y ordenar nombres de emotes
        emote_names = sorted([emote[0] for emote in emote_list])
        
        # Dividir en grupos de 23 para no exceder el límite de caracteres
        chunk_size = 23
        for i in range(0, len(emote_names), chunk_size):
            chunk = emote_names[i:i + chunk_size]
            emotes_text = "📝 EMOTES:\n• " + "\n• ".join(chunk)
            await self.highrise.send_whisper(user.id, emotes_text)
            await asyncio.sleep(0.5)

    async def check_position_and_emote(self) -> None:
        """Verifica la posición de los usuarios para el comando paseito."""
        while True:
            try:
                room_users = (await self.highrise.get_room_users()).content
                for room_user, position in room_users:
                    if isinstance(position, Position):
                        # Aquí puedes definir las coordenadas específicas para el paseito
                        # Por ejemplo:
                        if (0 <= position.x <= 10) and (0 <= position.y <= 10) and (0 <= position.z <= 10):
                            try:
                                await self.highrise.send_emote("dance-weird", room_user.id)
                            except Exception as e:
                                print(f"Error enviando emote a {room_user.username}: {e}")

            except Exception as e:
                if "Cannot write to closing transport" in str(e):
                    print("Conexión perdida en check_position_and_emote, esperando reconexión...")
                    await asyncio.sleep(5)
                else:
                    print(f"Error obteniendo usuarios de la sala: {e}")

            await asyncio.sleep(9.5)

    async def send_poemas_list(self, sender: User):
        """Envía un poema aleatorio al usuario que dio la propina."""
        while True:
            try:
                poemas = [
                """1:\n      Bajo el cielo estrellado y sereno,
            la brisa nocturna acaricia suave.
            El alma encuentra refugio en lo eterno,
            y en el silencio, se disipan las vanidades.\n
            Autor: Paseito_Bot""",

                """2:\n      En el murmullo del arroyo claro,
            fluye la calma como un cuento antiguo.
            Los susurros del viento, tan templados,
            nos envuelven en un manto de abrigo.\n
            Autor: Paseito_Bot""",

                """3:\n      Entre hojas doradas, un sendero
            se dibuja en la quietud del bosque.
            Cada paso es un verso en el suelo,
            y en la naturaleza, sonidos de redobles.\n
            Autor: Paseito_Bot""",

                """4:\n      Las olas del mar susurran historias,
            de mundos tranquilos y cielos claros.
            El alma navega en aguas de gloria,
            y el horizonte se pinta en paz, muy despacio.\n
            Autor: Paseito_Bot""",

                """5:\n      La luna llena ilumina el camino,
            reflejando un lago sereno y fiel.
            En cada estrella, un sueño divino,
            y en la noche, todo se vuelve miel.\n
            Autor: Paseito_Bot""",

                """6:\n      Un jardín florece en mil colores,
            en sus aromas se pierde el tiempo.
            Cada flor es un suspiro sin rumores,
            y en su quietud, el alma encuentra aliento.\n
            Autor: Paseito_Bot""",

                """7:\n      El rocío matutino acaricia las hojas,
            como un susurro de la naturaleza.
            En la frescura del amanecer, las cosas
            cobran vida con suave delicadeza.\n
            Autor: Paseito_Bot""",

                """8:\n      En la sombra del viejo roble, descanso,
            el mundo sigue su curso sin prisa.
            La vida fluye en un ciclo manso,
            y en el silencio, la mente se alisa.\n
            Autor: Paseito_Bot""",

                """9:\n      En el horizonte, un vuelo de aves,
            dibuja líneas de esperanza en el cielo.
            Con cada aleteo, el alma se enciende,
            y en su libertad, encuentra consuelo.\n
            Autor: Paseito_Bot""",

                """10:\n      Un río de plata serpentea tranquilo,
            reflejando el cielo en su espejo claro.
            Cada gota murmura un verso sencillo,
            y en su canto, todo se vuelve grato.\n
            Autor: Paseito_Bot""",

                """11:\n      Bajo el cielo nocturno, estrellas brillan,
            como faros en la inmensidad serena.
            Cada chispa es una esperanza que guía,
            y en la noche, el alma se enajena.\n
            Autor: Paseito_Bot""",

                """12:\n      En el campo abierto, el viento juega,
            susurra secretos a la hierba en calma.
            En su danza, la vida se despliega,
            y en la quietud, encuentra confianza.\n
            Autor: Paseito_Bot""",

                """13:\n      La montaña, majestuosa y firme,
            se alza como un guardián del paisaje.
            En su quietud, nos enseña a no temer,
            y a encontrar en la altura nuestro coraje.\n
            Autor: Paseito_Bot""",

                """14:\n      La tarde se despide con un suspiro,
            el sol se oculta tras las colinas.
            En ese instante, el día queda escrito,
            en tonos de oro y sombras divinas.\n
            Autor: Paseito_Bot""",

                """15:\n      Un prado verde se extiende sin fin,
            bajo un cielo azul, limpio y vasto.
            En cada flor, un mundo por descubrir,
            y en su fragancia, el tiempo se hace ratos.\n
            Autor: Paseito_Bot""",

                """16:\n      En la serenidad de un lago escondido,
            se refleja la paz de la naturaleza.
            Las ondas suaves acarician el oído,
            y en su murmullo, la mente se aquieta.\n
            Autor: Paseito_Bot""",

                """17:\n      Un sendero de piedra cruza el valle,
            guiando los pasos hacia la calma.
            Cada roca es un cuento que detalle,
            la historia de un alma en busca de calma.\n
            Autor: Paseito_Bot""",

                """18:\n      Al murmurar el arroyo, en su canto sereno,
            se escucha la melodía de la tierra.
            Cada gota narra un cuento,
            de promesas que en el silencio se encierran.\n
            Autor: Paseito_Bot""",

                """19:\n      Un atardecer dorado, lento y suave,
            pinta el cielo con pinceladas de oro.
            En ese instante, el día se vuelve nave,
            que conduce al alma a sollozos.\n
            Autor: Paseito_Bot""",

                """20:\n      La brisa suave acaricia la pradera,
            susurra cuentos de calma al viento.
            En cada hoja, una historia sincera,
            de días tranquilos sin ningún pensamiento.\n
            Autor: Paseito_Bot""",

                """21:\n      El susurro de las hojas en el bosque,
            canta melodías de serena calma.
            En cada rincón, un eco que se enrosque,
            abrazando al corazón con dulce esperanza.\n
            Autor: Paseito_Bot"""
            ]

                # Selecciona un poema al azar
                poema = random.choice(poemas)
                
                # Divide el poema en fragmentos si es necesario
                fragmentos = self.dividir_mensaje(poema, limite=500)
                for fragmento in fragmentos:
                    await self.highrise.chat(fragmento)
                break  # Si el poema se envió correctamente, salir del bucle
                
            except Exception as e:
                if "connection with ID:" in str(e):
                    await asyncio.sleep(5)
                    continue  # Reintentar si es error de conexión
                else:
                    print(f"Error en send_poemas_list: {e}")
                    break  # Salir si es otro tipo de error

    def dividir_mensaje(self, mensaje: str, limite: int = 500) -> list[str]:
        """Divide un mensaje largo en fragmentos más pequeños."""
        return [mensaje[i:i+limite] for i in range(0, len(mensaje), limite)]

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        """Maneja las propinas recibidas y envía poemas como agradecimiento."""
        try:
            # Comprobar si el tip es de 5 de oro Y si el receptor es el bot
            if isinstance(tip, CurrencyItem) and tip.amount == 5 and receiver.id == "665e310f16d318b8308f76d0":
                await self.highrise.chat(f"Con mucho cariño para {sender.username}\n")
                await self.send_poemas_list(sender)
        except Exception as e:
            print(f"Error en on_tip: {e}")

    async def ir(self, user: User, mensaje: str) -> None:
        # Extraer el nombre de usuario a teletransportarse
        parts = mensaje.split()
        if len(parts) < 2 or not parts[1].startswith("@"):
            await self.highrise.chat("Especifica un nombre de usuario que comienza con '@' para teletransportarte.")
            return

        target_username = parts[1][1:].lower()  # Eliminar '@' y convertir a minúsculas

        # Obtener la lista de usuarios en la sala
        room_users = (await self.highrise.get_room_users()).content
        user_found = False
        target_position = None

        # Verificar si el usuario objetivo está en la sala y obtener su posición
        for room_user, position in room_users:
            if room_user.username.lower() == target_username:
                target_position = position
                user_found = True
                break

        if not user_found:
            await self.highrise.chat(f"No se encontró al usuario con el nombre @{target_username}.")
            return

        # Teletransportar al usuario que ejecuta el comando a la posición del usuario objetivo
        if target_position:
            await self.highrise.teleport(user_id=user.id, dest=target_position)
            await self.highrise.chat(f"Te has teletransportado a la posición de {target_username}.")
        else:
            await self.highrise.chat("No se pudo encontrar la posición del usuario seleccionado.")

