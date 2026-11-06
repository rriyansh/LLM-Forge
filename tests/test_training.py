"""Unit tests for training (mocked heavy dependencies)."""

from unittest.mock import MagicMock, patch

import pytest


@patch("src.models.qlora_trainer.torch", None)
def test_train_raises_without_torch() -> None:
    from src.models.qlora_trainer import train

    with pytest.raises(RuntimeError, match="torch/transformers/peft/trl are required"):
        train("configs/training_config.yaml")


def test_merge_adapter_raises_without_deps() -> None:
    from src.models.merge_adapter import merge_adapter

    with pytest.raises(RuntimeError, match="transformers/peft are required"):
        merge_adapter("base", "adapter", "out")
