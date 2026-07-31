from housepy.models.name import Name


def test_str_uses_given_when_no_chosen():
    name = Name(given="Ludwig", family="Hesse-Darmstadt", prefix="of")
    assert str(name) == "Ludwig of Hesse-Darmstadt"


def test_str_prefers_chosen_over_given():
    name = Name(given="Ludwig", chosen="Ludwig IX", family="Hesse-Darmstadt")
    assert str(name) == "Ludwig IX Hesse-Darmstadt"


def test_str_uses_first_token_of_multi_word_given():
    name = Name(given="Friederike Luise", family="Hesse-Darmstadt", prefix="of")
    assert str(name) == "Friederike of Hesse-Darmstadt"


def test_str_with_title():
    name = Name(title="King", given="Ludwig", family="Hesse-Darmstadt")
    assert str(name) == "King Ludwig Hesse-Darmstadt"


def test_str_with_suffix():
    name = Name(given="Ludwig", suffix="the Great")
    assert str(name) == "Ludwig the Great"


def test_str_omits_unset_parts():
    assert str(Name(given="Ludwig")) == "Ludwig"
    assert str(Name()) == ""


def test_first_prefers_chosen():
    name = Name(chosen="Ludwig", given="Ludwig Georg")
    assert name.first == "Ludwig"


def test_first_falls_back_to_given():
    name = Name(given="Ludwig Georg")
    assert name.first == "Ludwig"


def test_first_empty_when_no_names():
    name = Name()
    assert name.first == ""
