from enum import Enum

class Directions(Enum):
    down = "down"
    up = "up"

class Flavors(Enum):
    positive = "positive"
    negative = "negative"

class SimpleHysteresis(object):

    def __init__(self, upper_bound: float, lower_bound: float,
                 direction: Directions = "up", flavor: Flavors = "positive"):

        assert direction in Directions._value2member_map_, f"'{direction}' is not in {Directions._member_names_}"
        assert flavor in Flavors._value2member_map_, f"'{flavor}' is not in {Flavors._member_names_}"

        self.last_answer = False
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.direction = direction
        self.flavor = flavor

    def _hysteresis_bigger_than_upperbound_pos(self, value: float, upper_bound: float, lower_bound: float) -> bool:
        if value >= upper_bound:
            answer = True
            self.last_answer = answer
        elif value < lower_bound:
            answer = False
            self.last_answer = answer
        else:
            answer = self.last_answer

        return answer

    def _hysteresis_bigger_than_upperbound_neg(self, value: float, upper_bound: float, lower_bound: float) -> bool:
        return not self._hysteresis_bigger_than_upperbound_pos(value=value, upper_bound=upper_bound,
                                                               lower_bound=lower_bound)

    def _hysteresis_lower_than_lowerbound_pos(self, value: float, upper_bound: float, lower_bound: float) -> bool:
        if value <= lower_bound:
            answer = True
            self.last_answer = answer
        elif value > upper_bound:
            answer = False
            self.last_answer = answer
        else:
            answer = self.last_answer

        return answer

    def _hysteresis_lower_than_lowerbound_neg(self, value: float, upper_bound: float, lower_bound: float) -> bool:
        return not self._hysteresis_lower_than_lowerbound_pos(value=value, upper_bound=upper_bound,
                                                              lower_bound=lower_bound)

    def test(self, value: float, upper_bound: float = None, lower_bound: float = None):

        if upper_bound is None:
            upper_bound = self.upper_bound
        if lower_bound is None:
            lower_bound = self.lower_bound

        if self.direction == Directions.up.value:
            if self.flavor == Flavors.positive.value:
                answer = self._hysteresis_bigger_than_upperbound_pos(value=value, upper_bound=upper_bound,
                                                            lower_bound=lower_bound)
            else:
                answer = self._hysteresis_bigger_than_upperbound_neg(value=value, upper_bound=upper_bound,
                                                            lower_bound=lower_bound)
        else:
            if self.flavor == Flavors.positive.value:
                answer = self._hysteresis_lower_than_lowerbound_pos(value=value, upper_bound=upper_bound,
                                                           lower_bound=lower_bound)
            else:
                answer = self._hysteresis_lower_than_lowerbound_neg(value=value, upper_bound=upper_bound,
                                                           lower_bound=lower_bound)

        return answer
