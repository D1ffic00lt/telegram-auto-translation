import asyncio
import functools
import inspect

from typing import Callable, Awaitable, Protocol, Any, Iterable

__all__ = (
    "requires",
    "skip_guard",
    "guard_commands",
)


class Check(Protocol):
    def __call__(
        self,
        ctx,
        *args,
        **kwargs,
    ) -> Awaitable[tuple[bool, str | None]] | tuple[bool, str | None]: ...


def requires(*checks: Check):
    def decorator(func):
        existing: list[Check] = getattr(func, "__checks__", [])
        func.__checks__ = [*existing, *checks]
        return func

    return decorator


def skip_guard(func):
    func.__skip_guard__ = True
    return func


def guard_commands(
    *,
    common_checks: Iterable[Check] = (),
    on_fail: Callable[[Any, str], Any] | None = None,
):
    async def _await_if_necessary(x):
        return await x if inspect.isawaitable(x) else x

    common_checks = tuple(common_checks)

    def wrap_callable(func):
        if getattr(func, "__skip_guard__", False) or getattr(func, "__guarded__", False):
            return func

        per_method_checks: list[Check] = getattr(func, "__checks__", [])
        checks = (*common_checks, *per_method_checks)
        if not checks:
            return func

        is_async = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            for check in checks:
                ok, reason = await _await_if_necessary(check(ctx, *args, **kwargs))
                if not ok:
                    if on_fail:
                        return await _await_if_necessary(on_fail(ctx, reason or "Access denied"))
                    return None
            if is_async:
                return await func(self, ctx, *args, **kwargs)
            return await asyncio.to_thread(func, self, ctx, *args, **kwargs)

        wrapper.__guarded__ = True
        return wrapper

    def class_decorator(cls):
        updates: list[tuple[str, Any]] = []
        for name, value in list(cls.__dict__.items()):
            if name.startswith("__") and name.endswith("__"):
                continue

            if inspect.isfunction(value):
                updates.append((name, wrap_callable(value)))
            elif isinstance(value, classmethod):
                updates.append((name, classmethod(wrap_callable(value.__func__))))
            elif isinstance(value, staticmethod):
                updates.append((name, staticmethod(wrap_callable(value.__func__))))

        for name, new_value in updates:
            setattr(cls, name, new_value)

        return cls

    return class_decorator
