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
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .utils import extract_payment_methods

import logging

logger = logging.getLogger(__name__)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_client = self._create_http_client()

    def _create_http_client(self):
        """Crea un cliente HTTP con retries y headers personalizados"""
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.headers.update({"User-Agent": "HodlWatcher/1.0 (+https://tudominio.com)", "Accept": "application/json"})
        return session

    def get_average_price(self, currency):
        """Obtiene el precio promedio de BTC con cache y manejo de errores"""
        cache_key = f"average_price_{currency}"
        cached_price = cache.get(cache_key)

        if cached_price:
            logger.info(f"Average price for {currency} retrieved from cache")
            return cached_price

        exchanges = self._get_exchange_data(currency)
        prices = self._fetch_prices_from_exchanges(exchanges)

        average_price = self._calculate_average_price(prices)
        cache.set(cache_key, average_price, 300)  # 5 minutos
        return average_price

    def _get_exchange_data(self, currency):
        """Define exchange data"""
        return [
            ("Binance", f"https://api.binance.com/api/v3/avgPrice?symbol=BTC{currency}", "price", 1),
            ("Coinbase", f"https://api.coinbase.com/v2/prices/BTC-{currency}/spot", "data.amount", 1),
            ("Kraken", f"https://api.kraken.com/0/public/Ticker?pair=XBT{currency}", "result.XXBTZ{currency}.c.0", 1),
            ("Gemini", f"https://api.gemini.com/v1/pubticker/btc{currency.lower()}", "last", 1),
        ]

    def _fetch_prices_from_exchanges(self, exchanges):
        """Fetch prices from exchanges"""
        prices = []
        for name, url, price_key, factor in exchanges:
            try:
                price = self._fetch_price_from_exchange(url, price_key)
                if price:
                    price_value = float(price) * factor
                    if price_value > 0:
                        prices.append(price_value)
            except Exception as e:
                print(f"Error en {name}: {str(e)}")
        return prices

    def _fetch_price_from_exchange(self, url, price_key):
        """Fetch price from a single exchange"""
        response = self.http_client.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()

        price = data
        for key in price_key.split("."):
            if key.startswith("[") and key.endswith("]"):
                index = int(key[1:-1])
                price = price[index]
            else:
                price = price.get(key, None)
                if price is None:
                    break
        return price

    def _calculate_average_price(self, prices):
        """Calculate average price with filtering"""
        if len(prices) >= 2:
            try:
                prices_array = np.array(prices)
                mean = np.mean(prices_array)
                std = np.std(prices_array)
                filtered_prices = [p for p in prices if mean - 2 * std <= p <= mean + 2 * std]
                return sum(filtered_prices) / len(filtered_prices) if filtered_prices else None
            except:
                return sum(prices) / len(prices) if prices else None
        return None

    def calculate_price_deviation(self, offers, average_price):
        """Calcula la desviación con manejo de errores mejorado"""
        if not offers or not average_price or average_price <= 0:
            return [{"error": "Invalid input data"}]

        processed_offers = []
        for offer in offers:
            try:
                offer_price = float(offer.get("price", 0))
                percent_deviation = ((offer_price - average_price) / average_price) * 100
                offer["percent_deviation"] = round(percent_deviation, 2)
            except (TypeError, ValueError, KeyError) as e:
                offer["percent_deviation"] = None
                print(f"Error calculando desviación: {e}")
            processed_offers.append(offer)

        return processed_offers if processed_offers else [{"error": "No valid offers processed"}]

    def _cached_payment_methods(self):
        """Obtiene los métodos de pago con cache"""
        cache_key = "payment_methods"
        cached_payment_methods = cache.get(cache_key)

        if cached_payment_methods:
            logging.info("Payment methods retrieved from cache")
            return cached_payment_methods

        paymet_methods = extract_payment_methods()
        cache.set(cache_key, paymet_methods, 60 * 60 * 24 * 1)  # 1 día
        return paymet_methods

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request

        # Configuración inicial
        context.update(
            {
                "payment_methods": self._cached_payment_methods(),
                "assets": [{"code": "BTC", "name": "Bitcoin"}],
                "currencies": [
                    {"code": "EUR", "name": "Euros"},
                    {"code": "USD", "name": "American Dolar"},
                ],
            }
        )

        params = {
            "side": self.request.GET.get("side", "sell"),
            "payment_method_id": self.request.GET.get("payment_method_id", "52"),
            "asset_code": self.request.GET.get("asset_code", "BTC"),
            "currency_code": self.request.GET.get("currency_code", "EUR"),
            "amount": self.request.GET.get("amount", "150"),
        }
        context["form_data"] = params

        if any(self.request.GET.get(param) for param in params.keys()):
            try:
                # Obtener precio promedio (con cache)
                average_price = self.get_average_price(params["currency_code"])
                context["average_price"] = average_price

                # Obtener ofertas
                response = self.http_client.get(
                    "https://hodlhodl.com/api/v1/offers",
                    params={
                        **{f"filters[{k}]": v for k, v in params.items()},
                        "filters[include_global]": "true",
                        "pagination[limit]": "100",
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Filtrar y procesar ofertas
                offers = [
                    offer for offer in data.get("offers", []) if offer.get("trader", {}).get("trades_count", 0) >= 1
                ]
                context["offers"] = self.calculate_price_deviation(offers, average_price)
                context["meta"] = data.get("meta", {})

            except requests.RequestException as e:
                context["error"] = f"Error al obtener datos: {str(e)}"
                context["offers"] = []
                context["average_price"] = None

        return context
