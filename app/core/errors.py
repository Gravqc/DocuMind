from __future__ import annotations


class AppError(Exception):
    """Base error for domain/application failures."""


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass

