from housepy.models.name import Name


def test_str_full_format():
    name = Name(given="Ludwig", family="Hesse-Darmstadt", prefix="of", format=Name.FULL)
    assert str(name) == "Ludwig of Hesse-Darmstadt"


def test_str_house_format_default():
    name = Name(given="Ludwig", family="Hesse-Darmstadt")
    assert str(name) == "Ludwig Hesse-Darmstadt"


def test_str_regnal_format():
    name = Name.regnal("Ludwig IX", family=None, given=None)
    assert str(name) == "Ludwig IX"


def test_str_regnal_format_with_group():
    name = Name(chosen="Ludwig IX", group="Hesse-Darmstadt", format=Name.REGNAL)
    assert str(name) == "Ludwig IX Hesse-Darmstadt"


def test_first_prefers_chosen():
    name = Name(chosen="Ludwig", given="Ludwig Georg")
    assert name.first == "Ludwig"


def test_first_falls_back_to_given():
    name = Name(given="Ludwig Georg")
    assert name.first == "Ludwig"


def test_first_empty_when_no_names():
    name = Name()
    assert name.first == ""


def test_regnal_factory_sets_format_and_fields():
    name = Name.regnal("Ludwig IX", "Hesse-Darmstadt", "Ludwig")
    assert name.format == Name.REGNAL
    assert name.chosen == "Ludwig IX"
    assert name.family == "Hesse-Darmstadt"
    assert name.given == "Ludwig"
    assert name.title is None
    assert name.prefix is None
    assert name.group is None
