"""Errors whose codes name the Quality Engine defect a caller must correct."""


class QualityError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
