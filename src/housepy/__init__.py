from importlib.metadata import version

# Reads the installed package's metadata, not pyproject.toml directly — a
# version bump needs `poetry install` to take effect here.
__version__ = version("housepy")
