import pytest

from whisper.normalizers import EnglishTextNormalizer
from whisper.normalizers.english import (
    EnglishNumberNormalizer,
    EnglishSpellingNormalizer,
)


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
def test_number_normalizer(std):
    assert std("two") == "2"
    assert std("thirty one") == "31"
    assert std("five twenty four") == "524"
    assert std("nineteen ninety nine") == "1999"
    assert std("twenty nineteen") == "2019"

    assert std("two point five million") == "2500000"
    assert std("four point two billions") == "4200000000s"
    assert std("200 thousand") == "200000"
    assert std("200 thousand dollars") == "$200000"
    assert std("$20 million") == "$20000000"
    assert std("€52.4 million") == "€52400000"
    assert std("£77 thousands") == "£77000s"

    assert std("two double o eight") == "2008"

    assert std("three thousand twenty nine") == "3029"
    assert std("forty three thousand two hundred sixty") == "43260"
    assert std("forty three thousand two hundred and sixty") == "43260"

    assert std("nineteen fifties") == "1950s"
    assert std("thirty first") == "31st"
    assert std("thirty three thousand and three hundred and thirty third") == "33333rd"

    assert std("three billion") == "3000000000"
    assert std("millions") == "1000000s"

    assert std("july third twenty twenty") == "july 3rd 2020"
    assert std("august twenty sixth twenty twenty one") == "august 26th 2021"
    assert std("3 14") == "3 14"
    assert std("3.14") == "3.14"
    assert std("3 point 2") == "3.2"
    assert std("3 point 14") == "3.14"
    assert std("3 point 1") == "3.1"
    assert std("fourteen point 4") == "14.4"
    assert std("one point five") == "1.5"
    assert std("two point two five dollars") == "$2.25"
    assert std("two hundred million dollars") == "$200000000"
    assert std("$20.1 million") == "$20100000"

    assert std("ninety percent") == "90%"
    assert std("seventy six per cent") == "76%"
    assert std("one percent") == "1%"

    assert std("double oh seven") == "007"
    assert std("double zero seven") == "007"
    assert std("nine one one") == "911"
    assert std("nine double one") == "911"
    assert std("one triple oh one") == "10001"

    assert std("two thousandth") == "2000th"
    assert std("thirty two thousandth") == "32000th"

    assert std("minus 500") == "-500"
    assert std("positive twenty thousand") == "+20000"
    assert std("minus one") == "-1"

    assert std("two dollars and seventy cents") == "$2.70"
    assert std("3 cents") == "¢3"
    assert std("$0.36") == "¢36"
    assert std("three euros and sixty five cents") == "€3.65"
    assert std("one dollar and one cent") == "$1.01"

    assert std("three and a half million") == "3500000"
    assert std("forty eight and a half dollars") == "$48.5"
    assert std("b747") == "b 747"
    assert std("10 th") == "10th"
    assert std("10th") == "10th"

    assert std("one") == "one"
    assert std("ones") == "ones"


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
def test_number_normalizer_requires_a_literal_decimal_point_for_cents(std):
    assert std("$0 36") == "$0 36"


def test_number_normalizer_does_not_treat_a_hyphen_as_a_decimal_point():
    assert EnglishNumberNormalizer()("$0-36") == "$0-36"
    assert EnglishTextNormalizer()("$0-36") == "$0 36"


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [("1,000", "1000"), ("1,2,3", "123")],
)
def test_number_normalizer_removes_digit_adjacent_commas(std, text, expected):
    assert std(text) == expected


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("and a half", "and a half"),
        ("2 and a half", "2.5"),
        ("$2 and a half", "$2.5"),
    ],
)
def test_number_normalizer_preserves_or_converts_half_expressions(std, text, expected):
    assert std(text) == expected


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [("point one", "0.1"), ("0 point one", "0.1"), ("0 zero", "00")],
)
def test_number_normalizer_preserves_zero_values(std, text, expected):
    assert std(text) == expected


def test_spelling_normalizer():
    std = EnglishSpellingNormalizer()

    assert std("mobilisation") == "mobilization"
    assert std("cancelation") == "cancellation"


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ninth", "9th"),
        ("twenty ninth", "29th"),
        ("one hundred and ninth", "109th"),
    ],
)
def test_number_normalizer_recognizes_ninth_ordinals(std, text, expected):
    assert std(text) == expected


def test_spelling_normalizer_removes_markup_from_archaeology():
    std = EnglishSpellingNormalizer()

    assert std("archaeology") == "archeology"
    assert all("<" not in value and ">" not in value for value in std.mapping.values())


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("minus one dollar", "-$1"),
        ("minus $5", "-$5"),
        ("plus one euro", "+€1"),
        ("minus one dollar and fifty cents", "-$1.50"),
    ],
)
def test_number_normalizer_preserves_signs_with_currency(std, text, expected):
    assert std(text) == expected


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("-$5", "-$5"),
        ("+€5", "+€5"),
        ("-5 dollars", "-$5"),
        ("-$0.50", "-¢50"),
    ],
)
def test_number_normalizer_preserves_literal_signs_with_currency(std, text, expected):
    assert std(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [("point $5", "point $5"), ("point -5", "point -5")],
)
def test_number_normalizer_does_not_append_prefixed_values_to_decimals(text, expected):
    assert EnglishNumberNormalizer()(text) == expected


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("point -5", "point -5"),
        ("point  -5", "point -5"),
        ("point\t-5", "point -5"),
        ("point\n-5", "point -5"),
        ("point minus five", "point -5"),
        ("point +5", "point +5"),
        ("point plus five", "point +5"),
        ("point $5", "point $5"),
        ("2 point -5", "2 point -5"),
        ("checkpoint -5", "checkpoint -5"),
        ("endpoint +5", "endpoint +5"),
        ("score -5", "score -5"),
        ("1 -5", "one -5"),
        ("point five", "0.5"),
        ("2 point 5", "2.5"),
        ("eighth", "8th"),
        ("twenty eighth", "28th"),
        ("0 double zero", "000"),
        ("0 triple one", "0111"),
    ],
)
def test_signed_tokens_and_decimal_boundaries(std, text, expected):
    assert std(text) == expected


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("minus $5 dollars", "-$5"),
        ("minus $5 million dollars", "-$5000000"),
        ("minus $5 dollars and fifty cents", "-$5.50"),
        ("-$5 million", "-$5000000"),
        ("+$5 million", "+$5000000"),
        ("-€5 million", "-€5000000"),
        ("+€5 million euros", "+€5000000"),
        ("-£5 million pounds", "-£5000000"),
        ("+£5 million", "+£5000000"),
        ("plus €5 euros", "+€5"),
        ("negative £5 pounds", "-£5"),
        ("-$5 dollars and one cent", "-$5.01"),
        ("-$5 point two", "-$5.2"),
        ("$5 million", "$5000000"),
        ("-5 million", "-5000000"),
    ],
)
def test_composed_currency_prefixes(std, text, expected):
    assert std(text) == expected


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("$0.5", "¢50"),
        ("$0.05", "¢5"),
        ("$0.50", "¢50"),
        ("$0.1", "¢10"),
        ("$0.01", "¢1"),
        ("$0 and a half", "¢50"),
        ("minus $0 and a half", "-¢50"),
        ("-$0 and a half", "-¢50"),
        ("+$0 and a half", "+¢50"),
        ("point five dollars", "¢50"),
        ("minus point five dollars", "-¢50"),
        ("-€0.5", "-¢50"),
        ("+£0.5", "+¢50"),
    ],
)
def test_currency_fraction_scale(std, text, expected):
    assert std(text) == expected


@pytest.mark.parametrize("std", [EnglishNumberNormalizer(), EnglishTextNormalizer()])
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("-5%", "-5%"),
        ("+5%", "+5%"),
        ("-5th", "-5th"),
        ("+1st", "+1st"),
        ("-2nd", "-2nd"),
        ("-3rd", "-3rd"),
        ("-1960s", "-1960s"),
        ("-5.5%", "-5.5%"),
        ("minus 5%", "-5%"),
    ],
)
def test_literal_signs_with_numeric_suffixes(std, text, expected):
    assert std(text) == expected


@pytest.mark.parametrize(("text", "expected"), [("5-2", "5 2"), ("$0-36", "$0 36")])
def test_text_normalizer_keeps_internal_hyphens_as_separators(text, expected):
    assert EnglishTextNormalizer()(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("price is $", "price is"),
        ("% rate", "rate"),
        ("$1", "$1"),
        ("1%", "1%"),
    ],
)
def test_text_normalizer_removes_only_dangling_numeric_symbols(text, expected):
    assert EnglishTextNormalizer()(text) == expected


def test_text_normalizer():
    std = EnglishTextNormalizer()
    assert std("Let's") == "let us"
    assert std("he's like") == "he is like"
    assert std("she's been like") == "she has been like"
    assert std("10km") == "10 km"
    assert std("10mm") == "10 mm"
    assert std("RC232") == "rc 232"

    assert (
        std("Mr. Park visited Assoc. Prof. Kim Jr.")
        == "mister park visited associate professor kim junior"
    )
