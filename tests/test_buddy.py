from BOOKzMA import texts


def test_buddy_name_escapes_html_and_newlines():
    assert texts.buddy_name("<b>علی</b>\nروزخوان") == "&lt;b&gt;علی&lt;/b&gt; روزخوان"
    assert texts.buddy_name(None) == "کتاب‌خوان"
    assert texts.buddy_name("   ") == "کتاب‌خوان"


def test_buddy_screen_shows_status_and_streak():
    screen = texts.buddy_screen("علی", 12, True)
    assert "علی" in screen
    assert "۱۲" in screen
    assert "ثبت کرده" in screen
    waiting = texts.buddy_screen("علی", 0, False)
    assert "هنوز امروز نخونده" in waiting
