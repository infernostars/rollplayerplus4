import random
import re
from abc import ABC, abstractmethod
from enum import StrEnum, Enum, auto
from typing import TypeVar, Generic, Type, Any, Optional, List, Tuple
from discord import Colour


def interpolate_color_hsv(value, min_val, max_val):
    """
    Interpolates between red and green in HSV space to avoid brown-like shades.
    Converts the result to RGB for discord.Colour.
    """
    # Ensure value is within bounds
    value = max(min_val, min(value, max_val))

    # Calculate interpolation ratio
    ratio = (value - min_val) / (max_val - min_val)

    # Interpolate hue from red (0°) to green (120°) in HSV
    hue = ratio * 120  # Red to green transition

    # Convert HSV to RGB
    red, green, blue = hsv_to_rgb(hue, 0, 1)  # Saturation and value are maxed (1)

    # Create and return discord.Colour object
    return Colour.from_rgb(int(red * 255), int(green * 255), int(blue * 255))


def hsv_to_rgb(h, s, v):
    """
    Convert HSV color space to RGB color space.
    """
    if s == 0.0: return v, v, v
    i = int(h * 6.)  # Assume hue is in [0, 6)
    f = (h * 6.) - i
    p, q, t = v * (1. - s), v * (1. - s * f), v * (1. - s * (1. - f))
    i %= 6
    if i == 0: return v, t, p
    if i == 1: return q, v, p
    if i == 2: return p, v, t
    if i == 3: return p, q, v
    if i == 4: return t, p, v
    if i == 5: return v, p, q


ABCBonusTypeVar = TypeVar('ABCBonusTypeVar', bound='ABCBonus')


class OperationEnum(StrEnum):
    ADD = '+'
    SUBTRACT = '-'
    MULTIPLY = '*'
    DIVIDE = '/'

class FormatEnum(StrEnum):
    LIST = 'l'
    SUM = 's'
    GREATER = '>'
    LESS = '<'

class RollException(BaseException):
    def __init__(self, information):
        super().__init__()
        self.information = information


class ABCBonus(ABC, Generic[ABCBonusTypeVar]):
    @abstractmethod
    def apply_bonus(self, rolled_dice: list[int]) -> list[int]: ...

    @classmethod
    @abstractmethod
    def parse(cls, input_string: str) -> ABCBonusTypeVar: ...


class Bonus(ABCBonus):
    def __init__(self, operation, value):
        self.operation = operation
        self.value = value

    def __repr__(self):
        return f"Bonus(operation={self.operation}, value={self.value})"

    def apply_bonus(self, rolled_dice: list[int]) -> list[int]:
        new_dice = []
        for i in rolled_dice:
            if self.operation == "+":
                new_dice.append(i + self.value)
            if self.operation == "-":
                new_dice.append(i - self.value)
            if self.operation == "/":
                new_dice.append(i / self.value)
            if self.operation == "*":
                new_dice.append(i * self.value)
        return new_dice

    @classmethod
    def parse(cls, input_string) -> 'Bonus':
        bonuses = []
        current_num = ''
        current_op = None

        for char in input_string:
            if char in [op.value for op in OperationEnum]:  # Check if char is an operation
                if current_num:  # If there's a number buffered, create a Bonus
                    bonuses.append(Bonus(current_op, float(current_num)))
                    current_num = ''  # Reset current number
                current_op = OperationEnum(char)  # Set current operation
            else:
                current_num += char  # Buffer the number

        # Handle the last buffered number
        if current_num and current_op:
            bonuses.append(Bonus(current_op, float(current_num)))

        return bonuses


class TargetedBonus(ABCBonus):
    def __init__(self, rolls, ops):
        self.rolls = rolls
        self.operations = ops

    def __repr__(self):
        return f"TargetedBonus(numbers={self.rolls}, operations={self.operations})"

    def apply_bonus(self, rolled_dice: list[int]) -> list[int]:
        new_dice = rolled_dice[:]

        # Apply each operation in sequence
        for operation in self.operations:
            temp_dice = new_dice[:]  # Copy the current state of new_dice for modification
            for i, dice_val in enumerate(new_dice):
                # Check if the dice index + 1 is in the targeted rolls
                if i + 1 in self.rolls:
                    # Apply the operation based on the operation type
                    if operation[0] == "+":
                        temp_dice[i] = dice_val + operation[1]
                    elif operation[0] == "-":
                        temp_dice[i] = dice_val - operation[1]
                    elif operation[0] == "/":
                        temp_dice[i] = dice_val / operation[1]
                    elif operation[0] == "*":
                        temp_dice[i] = dice_val * operation[1]
            # Update new_dice with the results of the current operation
            new_dice = temp_dice[:]

        # Return the final modified dice
        return new_dice

    @classmethod
    def parse_string(cls, input_string):
        # Split the input string into two parts: the numbers and the operations
        parts = input_string.split(':')
        numbers_str = parts[0][1:]  # Remove the leading 'i' from the numbers part
        ops_str = parts[1]  # Get the operations string

        # Convert the numbers part into a list of integers
        numbers = [int(num) for num in numbers_str.split(',')]

        # Convert the operations string into a list of tuples (OperationEnum, value)
        ops = []
        current_op = ''
        for char in ops_str:
            if char == 'i':
                if current_op:
                    op_enum, value = OperationEnum(current_op[0]), float(current_op[1:])
                    ops.append((op_enum, value))
                    current_op = ''
                break
            elif char in [op.value for op in OperationEnum]:
                if current_op:
                    op_enum, value = OperationEnum(current_op[0]), float(current_op[1:])
                    ops.append((op_enum, value))
                    current_op = char
                else:
                    current_op = char
            else:
                current_op += char

        if current_op:
            op_enum, value = OperationEnum(current_op[0]), float(current_op[1:])
            ops.append((op_enum, value))

        return TargetedBonus(numbers, ops)

    @classmethod
    def parse(cls, input_text) -> 'TargetedBonus':
        parsed_data_list = []
        # Find the position of the last semicolon
        last_semicolon_idx = input_text.rfind(';')
        # If there's no semicolon, use the entire text; otherwise, use text up to the last semicolon
        text_to_parse = input_text if last_semicolon_idx == -1 else input_text[:last_semicolon_idx]

        segment_starts = [i for i, char in enumerate(text_to_parse) if char == 'i']  # Find all 'i' positions

        for i, start_idx in enumerate(segment_starts):
            # Determine the end of the current segment
            if i < len(segment_starts) - 1:
                next_start = segment_starts[i + 1]
                end_idx = text_to_parse.rfind(';', start_idx, next_start)
                if end_idx == -1:  # If no semicolon is found before the next 'i', use the next 'i' as the end
                    end_idx = next_start
            else:
                # For the last segment, the end is the position of the last semicolon or the end of the text
                end_idx = len(text_to_parse)

            # Parse the segment into a TargetedBonus object
            segment = text_to_parse[start_idx:end_idx]
            parsed_data = cls.parse_string(segment)
            parsed_data_list.append(parsed_data)

        return parsed_data_list


class BasicDice:
    def __init__(self, count, start, end):
        self.count = count
        self.start = start
        self.end = end

    def __repr__(self):
        return f"BasicDice(count={self.count}, range={self.start}:{self.end})"

    @classmethod
    def parse(cls, input_string):
        # Check if the string starts directly with 'd', implying a single die
        if input_string.startswith('d'):
            count = 1
            range_part = input_string[1:]  # Exclude the 'd' to get the range part
        else:
            count_part, range_part = input_string.split('d')
            count = min(int(count_part), 10001) if count_part.isdigit() else 1

        if count == 10001:
            raise RollException("Dice count limit exceeded [max 10000]")

        # Check if there's a colon in the range part
        if not range_part:
            start, end = 1, 100
        elif ':' in range_part:
            start, end = range_part.split(':')
            start, end = int(start), int(end)  # Convert start and end to integers
        else:
            start, end = 1, int(range_part)  # If no colon, range is from 1 to the specified number

        # Flip the start and end values if end is less than start
        if end < start:
            start, end = end, start  # Swap the values

        return BasicDice(count, start, end)

class FormatType(StrEnum):
    FORMAT_DEFAULT = auto()
    FORMAT_SUM = auto()
    FORMAT_LIST = auto()
    FORMAT_LIST_SPLIT = auto()

class ThresholdType(StrEnum):
    GREATER = auto()
    LESS = auto()

class Threshold:
    def __init__(self, limit: int, threshold_type: ThresholdType):
        self.limit = limit
        self.threshold_type = threshold_type

    def passing(self, number):
        if self.threshold_type == ThresholdType.GREATER:
            return number >= self.limit
        elif self.threshold_type == ThresholdType.LESS:
            return number <= self.limit
        else:
            raise RollException("Invalid threshold type (how did you get here?)")

class Format:
    def __init__(self, format_type: FormatType, format_args = None, threshold: Threshold = None):
        self.format_type = format_type
        self.format_args = format_args
        self.threshold = threshold

    @classmethod
    def parse(cls, expression):
        formatting = Format(FormatType.FORMAT_DEFAULT, 20, None)
        format_regex = r'(' + '|'.join(re.escape(op.value) for op in FormatEnum) + r')'
        strip, *formats = re.split(format_regex, expression)
        idx = 0
        while idx < len(formats):
            format_char = formats[idx]
            if idx == len(formats) - 1:
                arg = False
            else:
                arg = formats[idx + 1]
                if re.match(format_regex, arg):
                    arg = False
            match format_char:
                case FormatEnum.LIST:
                    if arg:
                        formatting.format_type = FormatType.FORMAT_LIST_SPLIT
                        try:
                            formatting.format_args = int(arg)
                        except ValueError:
                            raise RollException("Attempted to split with non-integer")
                    else:
                        formatting.format_type = FormatType.FORMAT_LIST
                case FormatEnum.SUM:
                    formatting.format_type = FormatType.FORMAT_SUM
                case FormatEnum.GREATER:
                    if arg:
                        try:
                            formatting.threshold = Threshold(int(arg), ThresholdType.GREATER)
                        except ValueError:
                            raise RollException("Attempted to use > with non-integer")
                    else:
                        raise RollException("'Greater than' needs a number to work")
                case FormatEnum.LESS:
                    if arg:
                        try:
                            formatting.threshold = Threshold(int(arg), ThresholdType.LESS)
                        except ValueError:
                            raise RollException("Attempted to use < with non-integer")
                    else:
                        raise RollException("'Less than' needs a number to work")
            idx += 2 if arg else 1
        return strip, formatting #temporary!!!!!!!!!


class RollResult:
    def __init__(self, roll_string: str, rolls: list[int], original_rolls: list[int]):
        self.roll_string = roll_string
        self.rolls = rolls
        self.original_rolls = original_rolls
        self.threshold = None

    def _format_numbers(self, numbers: list[int]):
        # Convert numbers close to an integer to int, then to string
        rounded_nums = [int(x) if abs(x - round(x)) < 0.000000001 else x for x in numbers]
        if self.threshold is not None:
            return [f'**{x}**' if self.threshold.passing(x) else str(x) for x in rounded_nums]
        else:
            return [str(x) for x in rounded_nums]

    def _format_rolls(self, rolls: list[int]):
        # Convert numbers close to an integer to int, then to string
        formatted_nums = self._format_numbers(rolls)
        # Join the stringified numbers with commas
        return ', '.join(formatted_nums)

    def _format_and_split_rolls(self, rolls: list[int], n: int):
        # Convert numbers close to an integer to int, then to string
        formatted_nums = self._format_numbers(rolls)
        # Split the list into chunks of size n, join each chunk with commas, then join chunks with newlines
        return '\n'.join(', '.join(formatted_nums[i:i + n]) for i in range(0, len(formatted_nums), n))

    def _format_and_split_rolls__repr__(self, rolls: list[int], n: int):
        # Convert numbers close to an integer to int, then to string
        formatted_nums = self._format_numbers(rolls)
        # Split the list into chunks of size n, join each chunk with commas, then join chunks with newlines
        return '\n┃ '.join(', '.join(formatted_nums[i:i + n]) for i in range(0, len(formatted_nums), n))

    def _format_sum(self, rolls: list[int]):
        # Convert close to an integer to int, then to string
        formatted_sum = str(int(sum(rolls))) if abs(sum(rolls) - round(sum(rolls))) < 0.000000001 else str(sum(rolls))
        return formatted_sum

    def __repr__(self):
        return f"┏━━━━ {self.roll_string} ━━━━ \n┃ {self._format_and_split_rolls__repr__(self.rolls, 20)}\n┃ sum: {self._format_sum(self.rolls)}"

    def format(self, formatting: Format) -> List[tuple[str, str]]:
        # roll_icon = "<:roll_icon:1223801360273903656>"
        roll_icon = ""

        results = []
        format_type = formatting.format_type
        format_args = formatting.format_args
        self.threshold = formatting.threshold

        if format_type == FormatType.FORMAT_DEFAULT:
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_rolls(self.rolls) + (f" (sum: {self._format_sum(self.rolls)})" if len(self.rolls) > 1 else "")
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_rolls(self.original_rolls) + (f" (sum: {self._format_sum(self.original_rolls)})" if len(self.original_rolls) > 1 else "")
                ))
        elif format_type == FormatType.FORMAT_SUM:
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_sum(self.rolls)
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_sum(self.original_rolls)
                ))
        elif format_type == FormatType.FORMAT_LIST:
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_rolls(self.rolls)
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_rolls(self.original_rolls)
                ))
        elif format_type == FormatType.FORMAT_LIST_SPLIT:
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_and_split_rolls(self.rolls, format_args)
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_and_split_rolls(self.original_rolls, format_args)
                ))
        else:
            # base case
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_rolls(self.rolls)
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_rolls(self.original_rolls)
                ))

        return results


class SolveMode(StrEnum):
    RANDOM = auto()
    MAX = auto()
    MIN = auto()


class UnifiedDice:

    def __init__(self):
        self.original_string = ""
        self.targeted_bonuses = []
        self.bonuses = []
        self.basic_dice = None

    def __repr__(self):
        return f"UnifiedDice(TargetedBonuses={self.targeted_bonuses}, Bonuses={self.bonuses}, BasicDice={self.basic_dice})"

    def solve(self, solve_mode: SolveMode):
        dice: list[int] = []
        if solve_mode == "random":
            dice = [random.randint(self.basic_dice.start, self.basic_dice.end) for _ in range(self.basic_dice.count)]
        if solve_mode == "max":
            dice = [self.basic_dice.end for _ in range(self.basic_dice.count)]
        if solve_mode == "min":
            dice = [self.basic_dice.start for _ in range(self.basic_dice.count)]
        orig_dice = dice
        for bonuslist in (self.bonuses, self.targeted_bonuses):
            for bonus in bonuslist:
                dice = bonus.apply_bonus(dice)
        return RollResult(self.original_string, dice, orig_dice)

    @classmethod
    def new(cls, input_string):
        dice = UnifiedDice()
        dice.original_string = input_string
        split_regex = r'(' + '|'.join(re.escape(op.value) for op in OperationEnum) + r'|i)'
        operations_regex = r'(' + '|'.join(re.escape(op.value) for op in OperationEnum) + r')'
        # Initial split to separate BasicDice, Bonus, and TargetedBonus parts
        dice_part, *bonus_parts = re.split(split_regex, input_string, 1)
        bonus_part = ''.join(bonus_parts) if bonus_parts else ''

        # Further split to isolate TargetedBonus if present
        if 'i' in bonus_part:
            bonus_part, targeted_bonus_part = bonus_part.split('i', 1)
            targeted_bonus_part = 'i' + targeted_bonus_part  # Prepend 'i' back for correct parsing
        else:
            targeted_bonus_part = ''

        # Parse BasicDice if present
        if 'd' in dice_part:
            dice.basic_dice = BasicDice.parse(dice_part)

        # Parse Bonus if present
        if bonus_part:
            # Split by operation symbols to handle multiple bonuses
            for part in re.split(operations_regex, bonus_part):
                if part in [op.value for op in OperationEnum]:
                    operation = part
                    continue
                if part:  # Check if part is not empty
                    operation = OperationEnum.ADD.value if not operation else operation
                    dice.bonuses.extend(Bonus.parse(operation + part))

        # Parse TargetedBonus if present
        if targeted_bonus_part:
            dice.targeted_bonuses.extend(TargetedBonus.parse(targeted_bonus_part))

        if dice.basic_dice is None:
            dice.basic_dice = BasicDice(1, 1, 100)
        return dice


if __name__ == "__main__":
    print(UnifiedDice.new("45d100i1:*20").solve(SolveMode.RANDOM))
