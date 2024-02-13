import frmb_gui.core


def test__slugify():
    source = "Wow !! (crescendo?), such_fancy🐍."
    expected = "Wow--crescendo--such_fancy."
    result = frmb_gui.core.slugify(source)
    assert result == expected

    source = "file:FOO@team-76(owner).f"
    expected = "file-FOOteam-76owner.f"
    result = frmb_gui.core.slugify(source)
    assert result == expected

    source = "Όταν λείπει η γάτα🐈, χορεύουν τα ποντίκια🐭."
    expected = "Όταν-λείπει-η-γάτα--χορεύουν-τα-ποντίκια."
    result = frmb_gui.core.slugify(source, allow_unicode=True)
    assert result == expected
