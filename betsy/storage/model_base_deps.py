# pylint: disable=missing-module-docstring

class ModelBaseDeps:
    def __init__(self):
        self.db = None  # pylint: disable=invalid-name
        self.transactions = []

model_base_deps = ModelBaseDeps()
