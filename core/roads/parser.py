from typing import TypedDict

from pyparsing import (
    CharsNotIn,
    DelimitedList,
    Optional,
    Literal,
    Word,
    nums,
    Combine,
    OneOrMore,
    Or
)

greet = (
        Combine(
            Word('МНРТОС') + OneOrMore(Or([Optional(' '), Optional('-')]) + Word(nums))
        ).setParseAction(lambda x: dict(type='ref', value=x[0].strip(' ')))
        | CharsNotIn('–').setParseAction(lambda x: dict(type='place', value=x[0].strip(' ')))
)

divider = Literal('–')
elements = DelimitedList(greet, delim=divider).setResultsName('results')


class Token(TypedDict):
    type: str
    value: str


def parse(name: str) -> list[Token]:
    return list(elements.parseString(name)['results'])
