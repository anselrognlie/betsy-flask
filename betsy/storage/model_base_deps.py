# pylint: disable=missing-module-docstring

class ModelBaseDeps:
    def __init__(self):
        self.db = None  # pylint: disable=invalid-name
        self.transaction = None

model_base_deps = ModelBaseDeps()
