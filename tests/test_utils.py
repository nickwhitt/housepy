import pytest
from fastapi import HTTPException

from housepy.data import people
from housepy.utils import find_by_slug


def test_find_by_slug_found():
    person = find_by_slug(people, "hesse-darmstadt.ludwig-ix")
    assert person.slug == "hesse-darmstadt.ludwig-ix"


def test_find_by_slug_not_found():
    with pytest.raises(HTTPException) as exc_info:
        find_by_slug(people, "does-not-exist")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "not found"
