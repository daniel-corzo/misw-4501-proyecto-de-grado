import uuid
from sqlalchemy import inspect as sa_inspect
from travelhub_common.models import BaseModel, TimestampMixin
from travelhub_common.database import Base


def test_base_model_is_abstract():
    assert BaseModel.__abstract__ is True


def test_base_model_inherits_base():
    assert issubclass(BaseModel, Base)


def test_base_model_inherits_timestamp_mixin():
    assert issubclass(BaseModel, TimestampMixin)


def test_timestamp_mixin_has_created_at():
    assert "created_at" in TimestampMixin.__annotations__


def test_timestamp_mixin_has_updated_at():
    assert "updated_at" in TimestampMixin.__annotations__


def test_base_model_has_id_annotation():
    assert "id" in BaseModel.__annotations__


def test_base_model_id_is_uuid_type():
    import typing
    annotation = BaseModel.__annotations__["id"]
    args = typing.get_args(annotation)
    assert uuid.UUID in args
