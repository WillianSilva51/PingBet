"""Módulo de gerenciamento de cache usando Redis.

Este módulo fornece uma interface para armazenar e recuperar dados em cache
utilizando Redis, com suporte a serialização JSON e decoradores para
automatizar o caching de funções assíncronas.
"""

from collections.abc import Callable
from functools import wraps
from json import dumps, loads

from loguru import logger
from redis import ConnectionError
from redis.asyncio import Redis

from app.core.config import settings


class RedisCache:
    """Gerenciador de cache assíncrono baseado em Redis.

    Esta classe centraliza a comunicação com o Redis e oferece operações
    básicas de leitura, escrita e remoção de dados em cache. Também fornece
    um decorador para automatizar o cache de funções assíncronas, gerando a
    chave com base no nome da função e nos argumentos informados.
    """

    def __init__(self) -> None:
        """Inicializa o cliente Redis com as configurações da aplicação.

        A instância do cliente é criada com os valores definidos em
        ``api.core.config.settings``. Caso ocorra falha de conexão, o erro é
        registrado no logger.
        """
        try:
            self.client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
            )
        except ConnectionError as e:
            logger.error(e)

    def ping(self):
        """Verifica se o servidor Redis está respondendo.

        Returns:
            O retorno da operação ``PING`` realizada pelo cliente Redis.
        """
        try:
            return self.client.ping()
        except ConnectionError as e:
            logger.error(f"Erro de conexão com o Redis: {e}")

    async def set(self, key: str, value, expire: int):
        """Armazena um valor no Redis com tempo de expiração.

        Args:
            key: Chave sob a qual o valor será salvo.
            value: Conteúdo a ser armazenado no cache.
            expire: Tempo de expiração da chave, em segundos.

        Returns:
            Resultado da operação de gravação no Redis.
        """
        try:
            return await self.client.set(name=key, value=value, ex=expire, get=True)
        except ConnectionError as e:
            logger.error(e)

    async def get(self, key: str):
        """Recupera um valor armazenado no Redis.

        Args:
            key: Chave do item a ser consultado.

        Returns:
            Valor associado à chave ou ``None`` caso ela não exista.
        """
        try:
            return await self.client.get(name=key)
        except ConnectionError as e:
            logger.error(e)

    async def delete(self, keys):
        """Remove uma ou mais chaves do Redis.

        Args:
            keys: Chave única ou coleção de chaves a serem removidas.

        Returns:
            Quantidade de chaves removidas.
        """
        try:
            if isinstance(keys, (list, tuple, set)):
                return await self.client.delete(*keys)
            else:
                return await self.client.delete(keys)
        except ConnectionError as e:
            logger.error(e)

    def _normalize_cache_value(self, value):
        """Normaliza um valor para permitir serialização em JSON.

        Valores primitivos são retornados sem alteração. Listas, tuplas e
        dicionários são processados recursivamente. Tipos não suportados são
        convertidos para ``str``.

        Args:
            value: Valor a ser normalizado.

        Returns:
            Valor compatível com serialização JSON.
        """
        if isinstance(value, (str, int, float, bool, type(None))):
            return value

        if isinstance(value, (list, tuple)):
            return [self._normalize_cache_value(v) for v in value]

        if isinstance(value, dict):
            return {k: self._normalize_cache_value(v) for k, v in value.items()}

        return str(value)

    def _is_cacheable(self, value):
        """Indica se o valor pode ser usado para compor a chave do cache.

        Args:
            value: Valor a ser avaliado.

        Returns:
            ``True`` quando o valor puder ser normalizado e serializado para
            compor a chave; caso contrário, ``False``.
        """
        return isinstance(value, (str, int, float, bool, type(None), list, dict))

    def cacheable(self, expire: Callable[[], int] | int = 3600):
        """Cria um decorador para cache automático de funções assíncronas.

        A chave de cache é construída com o nome da função e os argumentos
        nomeados filtrados e normalizados. Se houver um valor já armazenado no
        Redis, ele é retornado. Caso contrário, a função original é executada
        e seu resultado é salvo no cache.

        Args:
            expire: Tempo de expiração em segundos ou uma função que retorne
                dinamicamente esse valor.

        Returns:
            Um decorador aplicável a funções assíncronas.
        """

        def decorator(func):
            """Aplica o comportamento de cache à função informada."""

            @wraps(func)
            async def wrapper(*args, **kwargs):
                """Executa a leitura e a gravação do cache ao redor da função.

                Args:
                    *args: Argumentos posicionais recebidos pela função.
                    **kwargs: Argumentos nomeados recebidos pela função.

                Returns:
                    O resultado recuperado do cache ou calculado pela função.
                """
                clean_kwargs = {
                    k: self._normalize_cache_value(v)
                    for k, v in kwargs.items()
                    if self._is_cacheable(v)
                }

                cache_key = f"{func.__name__}:{dumps(clean_kwargs, sort_keys=True)}"

                cache_data = await self.get(cache_key)

                if cache_data:
                    logger.info(f"Cache encontrado para a chave: {cache_key}")

                    return loads(cache_data.decode("utf-8"))

                result = await func(*args, **kwargs)

                if result is not None:
                    if isinstance(result, list):
                        serializable_result = [
                            self._normalize_cache_value(model.model_dump(mode="json"))
                            for model in result
                        ]
                    elif hasattr(result, "model_dump"):
                        serializable_result = self._normalize_cache_value(
                            result.model_dump(mode="json")
                        )
                    else:
                        serializable_result = self._normalize_cache_value(result)

                    logger.info(f"Armazenando no cache para a chave: {cache_key}")

                    await self.set(
                        key=cache_key,
                        value=dumps(serializable_result),
                        expire=expire() if callable(expire) else expire,
                    )

                return result

            return wrapper

        return decorator
