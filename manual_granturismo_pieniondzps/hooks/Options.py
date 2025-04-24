# Object classes from AP that represent different types of options that you can create
from Options import FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value



####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#

class TrophyHunt(Toggle):
    """
    Enables Trophy Hunt.
    In addition to winning GT World Cup, you'll also need to collect a certain amount of Trophies to win.
    """

class TrophyTotal(Range):
    """
    Set how many Trophies should be added to the item pool.
    Applies only if Trophy Hunt is enabled.
    """
    display_name = "Trophy total"
    range_start = 1
    range_end = 100
    default = 20

class TrophyRequired(Range):
    """
    Set how many Trophies will be required to win the seed.
    Note that if it's set higher than trophy total it will increase the total count so it matches the required count.
    Applies only if Trophy Hunt is enabled.
    """
    display_name = "Trophy required"
    range_start = 1
    range_end = 100
    default = 15

class LimitStarterCars(Toggle):
    """
    Limits your starting car to one of the following brand permits:
    Honda, Mazda, Mitsubishi, Nissan, Toyota
    Each of these brands feature a reasonably powerful car you can buy with your starting 10,000 Credits.
    If disabled, any brand can be your starting item. You won't be able to progress without having millions of Credits.
    """
    display_name = "Limit starter cars"
    default = 1

class ProgressiveTires(Toggle):
    """
    Makes Tires progressive instead of being individual items for every tire type and combination.
    No impact on progression but may make the playthrough more difficult.
    """
    display_name = "Make Tires progressive"

class SimulationHeadStart(Toggle):
    """
    Adds following upgrades to your starting items:
    Semi Racing Tires - Hard-Hard, one Weight Reduction, one NA Tune and one Turbo.
    """
    display_name = "Simulation mode head start"

class LicenseTests(Toggle):
    """
    Adds license tests to the location pool.
    """
    display_name = "License tests"

class EnduranceEvents(Toggle):
    """
    Adds the following in Special Events to the location pool:
    300km Grand Valley, All-night I, All-night II
    Each event enabled with this option will take 1-2 hours depending on your car.
    """
    display_name = "Endurance events"

class Qualifiers(Toggle):
    """
    Adds qualifiers to the location pool.
    """
    display_name = "Qualifiers"

class TimeTrial(Choice):
    """
    Adds Time Trials to the location pool.
    [none] - disables Time Trials
    [normal] - only Time Trials in normal variants will be enabled
    [reverse] - only Time Trials in reversed variants will be enabled
    [both] - both normal and reversed Time Trials will be enabled
    """
    display_name = "Time trials"
    option_none = 0
    option_normal = 1
    option_reverse = 2
    option_both = 3
    default = 0

class ArcadeMode(Toggle):
    """
    If enabled, adds Arcade mode related items and locations to the pool.
    """
    display_name = "Arcade mode content"

class ArcadeHeadStart(Toggle):
    """
    If enabled, adds a random arcade car permit and track pass to your starting items.
    This option will only take effect if Arcade mode content is enabled.
    """
    display_name = "Arcade mode head start"

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict) -> dict:
    options["trophy_hunt"] = TrophyHunt
    options["trophy_total"] = TrophyTotal
    options["trophy_required"] = TrophyRequired
    options["limit_starter_cars"] = LimitStarterCars
    options["simulation_head_start"] = SimulationHeadStart
    options["progressive_tires"] = ProgressiveTires
    options["license_tests"] = LicenseTests
    options["endurance_events"] = EnduranceEvents
    options["qualifier"] = Qualifiers
    options["time_trial"] = TimeTrial
    options["arcade"] = ArcadeMode
    options["arcade_head_start"] = ArcadeHeadStart
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: dict) -> dict:
    return options