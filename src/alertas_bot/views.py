import numpy as np
import requests
from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator
from allauth.mfa.utils import is_mfa_enabled
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from django.views.generic.edit import CreateView

from bot.models import UsuarioTelegram

from .forms import ConfiguracionForm, ContactForm
from .models import Configuracion, ContactMessage


class ResumeView(TemplateView):
    template_name = "resume.html"


class ProjectsView(TemplateView):
    template_name = "projects.html"


class ContactView(CreateView):
    template_name = "contact.html"
    form_class = ContactForm
    model = ContactMessage
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        # Save the form data to database
        form.save()

        # Here you could add email sending logic
        # send_contact_email(contact_message)

        # Add success message
        messages.success(self.request, "Thank you for your message! We'll get back to you soon.")
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Configuracion
    form_class = ConfiguracionForm
    template_name = "profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        try:
            usuario_telegram = UsuarioTelegram.objects.filter(username=self.request.user.username).first()

            configuracion, created = Configuracion.objects.get_or_create(
                user=self.request.user, defaults={"user_telegram": usuario_telegram if usuario_telegram else None}
            )
            return configuracion
        except UsuarioTelegram.DoesNotExist:
            # Si no se encuentra usuario de Telegram, crea configuración sin él
            configuracion, created = Configuracion.objects.get_or_create(user=self.request.user)
            return configuracion

    def form_valid(self, form):
        form.instance.user = self.request.user

        try:
            usuario_telegram = UsuarioTelegram.objects.filter(username=self.request.user.username).first()
            if usuario_telegram:
                form.instance.user_telegram = usuario_telegram
        except UsuarioTelegram.DoesNotExist:
            pass

        if self.object.image and form.cleaned_data["image"]:
            self.object.image.delete()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        authenticators = {}
        for auth in Authenticator.objects.filter(user=self.request.user):
            if auth.type == Authenticator.Type.WEBAUTHN:
                auths = authenticators.setdefault(auth.type, [])
                auths.append(auth.wrap())
            else:
                authenticators[auth.type] = auth.wrap()
        ret["authenticators"] = authenticators
        ret["MFA_SUPPORTED_TYPES"] = app_settings.SUPPORTED_TYPES
        ret["is_mfa_enabled"] = is_mfa_enabled(self.request.user)
        return ret


class ConfiguracionUpdateView(LoginRequiredMixin, UpdateView):
    model = Configuracion
    form_class = ConfiguracionForm
    template_name = "configuracion.html"
    success_url = reverse_lazy("modificar_rate_fee")

    def get_object(self, queryset=None):
        # Siempre retornamos el primer objeto de Configuracion
        return Configuracion.objects.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Crear un parámetro de referencia (ejemplo: ID de usuario)
        # referencia = "usuario_123"
        # param_base64 = base64.urlsafe_b64encode(referencia.encode()).decode()

        # Construir la URL del bot con el parámetro
        telegram_url = "https://t.me/HodlWatcher_bot?startgroup=false"

        # Añadir la URL al contexto
        context["telegram_url"] = telegram_url

        return context


@login_required
def delete_account(request):
    try:
        u = User.objects.get(username=request.user.username)
        u.delete()
        messages.success(request, f"The user {request.user.username} was deleted")

    except User.DoesNotExist:
        messages.error(request, "User doesnot exist")
        return redirect("home")

    except Exception as e:
        messages.error(request, e.message)
        return redirect("profile")

    return redirect("account_login")


class BuscadorView(TemplateView):
    template_name = "buscador.html"

    def get_average_price(self, currency):
        """Obtiene el precio promedio de BTC de los principales exchanges"""
        exchanges = [
            # Exchange, URL, clave de acceso al precio, factor de conversión (para exchanges con diferentes formatos)
            ("Binance", f"https://api.binance.com/api/v3/avgPrice?symbol=BTC{currency}", "price", 1),
            ("Coinbase", f"https://api.coinbase.com/v2/prices/BTC-{currency}/spot", "data.amount", 1),
            ("Kraken", f"https://api.kraken.com/0/public/Ticker?pair=XBT{currency}", "result.XXBTZ{currency}.c.0", 1),
            ("Gemini", f"https://api.gemini.com/v1/pubticker/btc{currency.lower()}", "last", 1),
        ]

        prices = []
        for name, url, price_key, factor in exchanges:
            try:
                response = requests.get(url, timeout=2, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                data = response.json()

                # Acceso al precio usando notación de puntos o índices
                price = data
                for key in price_key.split("."):
                    if key.startswith("[") and key.endswith("]"):
                        index = int(key[1:-1])
                        price = price[index]
                    else:
                        price = price.get(key, {})

                if isinstance(price, (int, float)) and price > 0:
                    prices.append(float(price) * factor)
                elif isinstance(price, str):
                    prices.append(float(price) * factor)

            except (requests.RequestException, ValueError, KeyError, IndexError, AttributeError) as e:
                print(f"Error obteniendo precio de {name}: {str(e)}")
                continue

        # Filtramos outliers (precios fuera de 2 desviaciones estándar)
        if len(prices) >= 3:
            prices_array = np.array(prices)
            mean = np.mean(prices_array)
            std = np.std(prices_array)
            filtered_prices = [p for p in prices if mean - 2 * std <= p <= mean + 2 * std]
            return sum(filtered_prices) / len(filtered_prices) if filtered_prices else None

        return sum(prices) / len(prices) if prices else None

    def calculate_price_deviation(self, offers, average_price):
        """
        Calcula la desviación porcentual de precio para cada oferta.

        :param offers: Lista de ofertas
        :param average_price: Precio promedio de mercado
        :return: Lista de ofertas con desviación porcentual añadida
        """
        if not average_price or average_price == 0:
            return offers

        for offer in offers:
            try:
                # Asegúrate de que el precio de la oferta es un número
                offer_price = float(offer.get("price", 0))

                # Calcula la desviación porcentual
                percent_deviation = ((offer_price - average_price) / average_price) * 100

                # Redondea a dos decimales
                offer["percent_deviation"] = round(percent_deviation, 2)
            except (TypeError, ValueError, KeyError) as e:
                # Manejo de errores si falta algún dato o hay problemas de conversión
                print(f"Error calculando desviación: {e}")
                offer["percent_deviation"] = 0

        return offers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request

        # Configuración inicial
        context["payment_methods"] = [
            {"id": "52", "name": "Transferencia Bancaria"},
            {"id": "37", "name": "PayPal"},
            {"id": "74", "name": "Revolut"},
            {"id": "75", "name": "Bizum"},
        ]

        context["assets"] = [
            {"code": "BTC", "name": "Bitcoin"},
            {"code": "ETH", "name": "Ethereum"},
            {"code": "USDT", "name": "Tether"},
        ]

        context["currencies"] = [
            {"code": "EUR", "name": "Euros"},
            {"code": "USD", "name": "Dólares"},
        ]

        # Obtener parámetros de la URL o valores por defecto
        params = {
            "side": self.request.GET.get("side", "sell"),
            "payment_method_id": self.request.GET.get("payment_method_id", "52"),
            "asset_code": self.request.GET.get("asset_code", "BTC"),
            "currency_code": self.request.GET.get("currency_code", "EUR"),
            "amount": self.request.GET.get("amount", "150"),
        }

        context["form_data"] = params

        # Si hay parámetros de búsqueda, hacer la llamada a la API
        if any(self.request.GET.get(param) for param in params.keys()):
            try:
                # Obtener precio promedio
                average_price = self.get_average_price(params["currency_code"])
                context["average_price"] = average_price

                # Obtener ofertas
                api_url = "https://hodlhodl.com/api/v1/offers"
                api_params = {f"filters[{key}]": value for key, value in params.items()}
                api_params["filters[include_global]"] = "true"
                api_params["pagination[limit]"] = "100"

                response = requests.get(api_url, params=api_params)
                response.raise_for_status()

                data = response.json()

                # Filtrar ofertas con al menos una transacción
                offers = [
                    offer for offer in data.get("offers", []) if offer.get("trader", {}).get("trades_count", 0) >= 1
                ]

                # Calcular desviación de precio
                context["offers"] = self.calculate_price_deviation(offers, average_price)
                context["meta"] = data.get("meta", {})

            except requests.RequestException as e:
                context["error"] = str(e)

        return context
