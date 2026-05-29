"""Pacote `services` — submódulos são importados diretamente pelos consumidores.

Evita importações top-level para prevenir erros/circulares quando um
submódulo (ex: `services.plantoes_service`) é importado. Use imports explícitos
como `from services.financas import ...` ou `from services import financas` quando
necessário em runtime.
"""

__all__ = []
