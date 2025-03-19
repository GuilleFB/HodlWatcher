# Archivo: src/main/management/commands/run_telegram_bot.py

import logging
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler
from asgiref.sync import sync_to_async  # Importar sync_to_async

# Importa tus modelos
from alertas_bot.models import Configuracion
from bot.models import UsuarioTelegram
from constance import config


class Command(BaseCommand):
    help = "Inicia el bot de Telegram para monitoreo de rate_fee"

    def add_arguments(self, parser):
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Ejecutar el bot en modo debug",
        )

    def handle(self, *args, **options):
        # Configurar logs
        log_level = logging.DEBUG if options["debug"] else logging.INFO
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=log_level)
        logger = logging.getLogger(__name__)

        # Validar token
        TOKEN = config.TELEGRAM_BOT_TOKEN
        if not TOKEN:
            self.stdout.write(self.style.ERROR("Error: TELEGRAM_BOT_TOKEN no está configurado"))
            return

        self.stdout.write(self.style.SUCCESS("Iniciando bot de Telegram..."))
        if options["debug"]:
            self.stdout.write(self.style.WARNING("Ejecutando en modo DEBUG"))

        # Definir funciones síncronas que serán convertidas a asíncronas
        def get_or_create_user(chat_id, username):
            """Versión síncrona para crear o obtener un usuario"""
            return UsuarioTelegram.objects.get_or_create(chat_id=chat_id, defaults={"username": username})

        def get_configuracion():
            """Versión síncrona para obtener la configuración"""
            return Configuracion.objects.first()

        # Convertir las funciones síncronas a asíncronas
        get_or_create_user_async = sync_to_async(get_or_create_user)
        get_configuracion_async = sync_to_async(get_configuracion)

        # Definir los manejadores de comandos
        async def start(update: Update, context: CallbackContext) -> None:
            """Comando /start: Registra al usuario en la base de datos."""
            chat_id = update.effective_chat.id
            username = update.effective_user.username or "Usuario desconocido"

            try:
                # Usar la versión asíncrona de get_or_create
                _, created = await get_or_create_user_async(chat_id, username)

                if created:
                    message = f"👋 ¡Hola {username}! Te has registrado correctamente."
                    logger.info(f"Nuevo usuario registrado: {username} (ID: {chat_id})")
                else:
                    message = f"👋 ¡Hola {username}! Ya estabas registrado."
                    logger.info(f"Usuario existente conectado: {username} (ID: {chat_id})")

                await update.message.reply_text(message)
            except Exception as e:
                logger.error(f"Error en comando start: {e}", exc_info=True)
                await update.message.reply_text("❌ Error al procesar tu solicitud. Por favor, intenta de nuevo.")

        async def consultar_rate_fee(update: Update, context: CallbackContext) -> None:
            """Comando /ratefee: Consulta el rate_fee actual."""
            chat_id = update.effective_chat.id
            username = update.effective_user.username or "Usuario desconocido"
            logger.info(f"Usuario {username} consultó el rate_fee")

            try:
                # Usar la versión asíncrona para obtener la configuración
                config = await get_configuracion_async()
                if config:
                    await update.message.reply_text(f"El rate_fee actual es: {config.rate_fee}%")
                else:
                    await update.message.reply_text("❌ No se ha configurado el rate_fee aún.")
            except Exception as e:
                logger.error(f"Error en comando ratefee: {e}", exc_info=True)
                await update.message.reply_text("❌ Error al consultar el rate_fee.")

        async def alerta(update: Update, context: CallbackContext) -> None:
            """Comando /alerta: Envía una alerta con el rate_fee."""
            chat_id = update.effective_chat.id
            username = update.effective_user.username or "Usuario desconocido"
            logger.info(f"Usuario {username} solicitó una alerta")

            try:
                # Usar la versión asíncrona para obtener la configuración
                config = await get_configuracion_async()
                if config:
                    message = f"🚨 ALERTA: El rate_fee actual es {config.rate_fee}% 🚨"
                    await update.message.reply_text(message)
                else:
                    await update.message.reply_text("❌ No hay rate_fee configurado.")
            except Exception as e:
                logger.error(f"Error en comando alerta: {e}", exc_info=True)
                await update.message.reply_text("❌ Error al generar la alerta.")

        async def help_command(update: Update, context: CallbackContext) -> None:
            """Comando /help: Muestra la ayuda del bot."""
            help_text = (
                "📋 *Comandos disponibles:*\n\n"
                "/start - Registrarse en el sistema\n"
                "/ratefee - Consultar el rate fee actual\n"
                "/alerta - Enviar una alerta con el rate fee actual\n"
                "/help - Mostrar este mensaje de ayuda"
            )
            await update.message.reply_text(help_text, parse_mode="Markdown")

        # Inicializar la aplicación
        try:
            app = Application.builder().token(TOKEN).build()

            # Registrar los manejadores de comandos
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("ratefee", consultar_rate_fee))
            app.add_handler(CommandHandler("alerta", alerta))
            app.add_handler(CommandHandler("help", help_command))

            # Configurar manejador de errores
            async def error_handler(update, context):
                logger.error(f"Error manejando la actualización {update}: {context.error}", exc_info=True)
                if update and update.effective_message:
                    await update.effective_message.reply_text(
                        "Ocurrió un error al procesar tu solicitud. Intenta nuevamente."
                    )

            app.add_error_handler(error_handler)

            self.stdout.write(self.style.SUCCESS("✅ Bot de Telegram iniciado correctamente"))

            # Iniciar el bot
            app.run_polling()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al iniciar el bot: {e}"))
            logger.error(f"Error fatal: {e}", exc_info=True)
