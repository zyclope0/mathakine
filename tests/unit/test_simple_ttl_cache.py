"""Tests pour app.utils.simple_ttl_cache."""

import asyncio

import pytest

from app.utils.simple_ttl_cache import clear_all, get_or_set


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    """Vide le cache entre chaque test pour éviter les fuites."""
    clear_all()
    yield
    clear_all()


@pytest.mark.asyncio
async def test_get_or_set_caches_value():
    """Cache hit retourne la valeur mise en cache."""
    call_count = 0

    async def factory():
        nonlocal call_count
        call_count += 1
        return {"result": 42}

    val1 = await get_or_set("k", 60.0, factory)
    val2 = await get_or_set("k", 60.0, factory)

    assert val1 == val2 == {"result": 42}
    assert call_count == 1


@pytest.mark.asyncio
async def test_get_or_set_different_keys():
    """Des clés différentes ont des entrées séparées."""

    async def factory_a():
        return "A"

    async def factory_b():
        return "B"

    a = await get_or_set("key_a", 60.0, factory_a)
    b = await get_or_set("key_b", 60.0, factory_b)

    assert a == "A"
    assert b == "B"


@pytest.mark.asyncio
async def test_clear_all_invalidates_cache():
    """clear_all invalide toutes les entrées."""
    call_count = 0

    async def factory():
        nonlocal call_count
        call_count += 1
        return "x"

    await get_or_set("k", 60.0, factory)
    clear_all()
    await get_or_set("k", 60.0, factory)

    assert call_count == 2


@pytest.mark.asyncio
async def test_get_or_set_respects_ttl():
    """Entrée expirée déclenche un nouvel appel à factory."""
    call_count = 0

    async def factory():
        nonlocal call_count
        call_count += 1
        return call_count

    v1 = await get_or_set("k", 0.05, factory)
    await asyncio.sleep(0.06)
    v2 = await get_or_set("k", 0.05, factory)

    assert v1 == 1
    assert v2 == 2


@pytest.mark.asyncio
async def test_concurrent_calls_invoke_factory_once():
    """Régression M6 : des appels concurrents ne doivent appeler factory() qu'une seule fois.

    Vérifie que le lock protège correctement la section critique :
    avec l'ancien _get_lock() (lazy init), deux coroutines pouvaient
    potentiellement obtenir des instances de lock différentes et entrer
    simultanément dans la section critique.
    """
    call_count = 0

    async def slow_factory():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.02)  # simule une factory lente (ex: DB query)
        return {"data": "result"}

    # Lance 5 coroutines simultanément sur la même clé
    results = await asyncio.gather(
        get_or_set("concurrent_key", 60.0, slow_factory),
        get_or_set("concurrent_key", 60.0, slow_factory),
        get_or_set("concurrent_key", 60.0, slow_factory),
        get_or_set("concurrent_key", 60.0, slow_factory),
        get_or_set("concurrent_key", 60.0, slow_factory),
    )

    # factory() ne doit avoir été appelée qu'une seule fois malgré la concurrence
    assert call_count == 1
    # Toutes les coroutines reçoivent la même valeur
    assert all(r == {"data": "result"} for r in results)
