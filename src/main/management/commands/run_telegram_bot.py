import logging

from asgiref.sync import sync_to_async  # Importar sync_to_async
from constance import config
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler

# Importa tus modelos
from alertas_bot.models import Configuracion
from bot.models import UsuarioTelegram


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

        def update_rate_fee(username, ratefee: float) -> bool:
            """Versión síncrona para actualizar el rate_fee en la base de datos."""
            user = UsuarioTelegram.objects.get(username=username)
            if user and int(user.rate_fee) != ratefee:
                user.rate_fee = ratefee
                user.save()
                return True
            return False

        # Convertir las funciones síncronas a asíncronas
        get_or_create_user_async = sync_to_async(get_or_create_user)
        get_configuracion_async = sync_to_async(get_configuracion)
        update_rate_fee_async = sync_to_async(update_rate_fee)

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

        async def modificar_rate_fee(update: Update, context: CallbackContext) -> None:
            """Comando /ratefee: Modifica el rate_fee actual según el valor proporcionado por el usuario."""
            username = update.effective_user.username or "Usuario desconocido"

            # Verificar si el usuario proporcionó un argumento (nuevo rate_fee)
            if not context.args:
                await update.message.reply_text(
                    "❌ Debes proporcionar un nuevo valor para el rate_fee. Ejemplo: /ratefee 5"
                )
                return

            try:
                # Intentar convertir el argumento a número
                nuevo_rate_fee = float(context.args[0])
                if nuevo_rate_fee < 0:
                    await update.message.reply_text("❌ El rate_fee no puede ser un valor negativo.")
                    return

                # Actualizar rate_fee de manera asíncrona
                actualizado = await update_rate_fee_async(username, nuevo_rate_fee)
                if actualizado:
                    logger.info(f"Usuario {username} modificó el rate_fee a {nuevo_rate_fee}%")
                    await update.message.reply_text(f"✅ El rate_fee ha sido actualizado a {nuevo_rate_fee}%.")
                else:
                    await update.message.reply_text("❌ No se pudo actualizar el rate fee.")

            except ValueError:
                await update.message.reply_text("❌ Debes proporcionar un número válido. Ejemplo: /ratefee 5")

            except Exception as e:
                logger.error(f"Error al modificar el rate_fee: {e}", exc_info=True)
                await update.message.reply_text("❌ Ocurrió un error al modificar el rate_fee.")

        async def alerta(update: Update, context: CallbackContext) -> None:
            """Comando /alerta: Envía una alerta con el rate_fee."""
            username = update.effective_user.username or "Usuario desconocido"
            logger.info(f"Usuario {username} solicitó una alerta")

            try:
                # Usar la versión asíncrona para obtener la configuración
                config = await get_configuracion_async()
                if config:
                    message = f"🚨 ALERTA: El rate_fee actual es {config.user.rate_fee}% 🚨"
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
            app.add_handler(CommandHandler("ratefee", modificar_rate_fee))
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
