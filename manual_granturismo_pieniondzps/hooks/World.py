# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove = [] # List of location names

    # Add your code here to calculate which locations to remove
    # Time Trials
    if (get_option_value(multiworld, player, "time_trial") == 0 or get_option_value(multiworld, player, "time_trial") == 2):
        # Remove normal Time Trials!
        locationNamesToRemove.extend([
            name for name, l in world.location_name_to_location.items()
                if "Time Trial" in l.get('category', [])
        ])
    
    if (get_option_value(multiworld, player, "time_trial") == 0 or get_option_value(multiworld, player, "time_trial") == 1):
        # Remove reversed Time Trials!
        locationNamesToRemove.extend([
            name for name, l in world.location_name_to_location.items()
                if "Time Trial Reverse" in l.get('category', [])
        ])


    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Goes through yaml option for trophy total as many times as the player defined in their yaml and for each go adds a trophy to the pool
    # It only does this if "Trophy Hunt" is enabled
    if get_option_value(multiworld, player, "trophy_hunt") == 1:
        trophy_count = get_option_value(multiworld, player, "trophy_total")
        trophy_required = get_option_value(multiworld, player, "trophy_required")

        # Replace trophy total with trophy required if options were set to have more required trophies than total
        if trophy_required > trophy_count:
            trophy_count = trophy_required

        for _ in range(trophy_count):
            item_pool.append(world.create_item("Trophy"))
    
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Sets up a starting inventory
    starting_items = []
    car_pool = []

    # Adds a random car permit to starting items, with the pool depending on the state of "Limit starter cars" and "Unlock cars individually"
    if get_option_value(multiworld, player, "limit_starter_cars") == 1:
        car_pool.extend([
            name for name, l in world.item_name_to_item.items()
                if "Starter Manufacturer" in l.get('category', [])
        ])
    else:
        car_pool.extend([
            name for name, l in world.item_name_to_item.items()
                if "Simulation - Cars" in l.get('category', [])
        ])
    multiworld.random.shuffle(car_pool)
    starting_items.append(car_pool[0])

    # If Simulation head start is enabled, adds Semi Hard Tyres, one Weight Reduction, one NA Tune and one Turbo to starting items
    if (get_option_value(multiworld, player, "simulation_head_start") == 1):
        if (get_option_value(multiworld, player, "progressive_tires") == 0):
            starting_items.append("Semi Racing Tires - Hard-Hard")
        else:
            starting_items.append("Progressive Tires")
        starting_items.append("Progressive Weight Reduction")
        starting_items.append("Progressive NA Tune")
        starting_items.append("Progressive Turbo")

    
    # If Arcade head start is enabled, adds one arcade car and one arcade track pass to starting items if arcade content is enabled
    if get_option_value(multiworld, player, "arcade") == 1 and get_option_value(multiworld, player, "arcade_head_start") == 1:
        car_pool = []
        track_pool = []
        car_pool.extend([
            name for name, l in world.item_name_to_item.items()
                if "Arcade - Cars" in l.get('category', [])
        ])
        multiworld.random.shuffle(car_pool)
        starting_items.append(car_pool[0])

        track_pool.extend([
            name for name, l in world.item_name_to_item.items()
                if "Arcade - Tracks" in l.get('category', [])
        ])
        multiworld.random.shuffle(track_pool)
        starting_items.append(track_pool[0])

    # Process starting items. Precollect them and remove them from item pool.
    for itemName in starting_items:
        start_inventory = next(item for item in item_pool if item.name == itemName)
        multiworld.push_precollected(start_inventory)
        item_pool.remove(start_inventory)

    # Use this hook to remove items from the item pool
    itemNamesToRemove = [] # List of item names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        item_pool.remove(item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location
    # Modify "GT World Cup" region when "Trophy Hunt" is set so it additionally requires the amount of required trophies set in "trophy_required" option
    if get_option_value(multiworld, player, "trophy_hunt") == 1:
        required_trophies = get_option_value(multiworld, player, "trophy_required")

        def gt_wc_requirements(state: CollectionState, count):
            return (state.has("Progressive License", player, 3) and state.has_group("Simulation - Milestones", player, 3) and state.has("Trophy", player, count))

        multiworld.get_entrance("iA-Class UnlocksToGT World Cup", player).access_rule = lambda state: gt_wc_requirements(state, required_trophies)

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int) -> list:
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    
    ### Example way to use this hook: 
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string
    
    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass
