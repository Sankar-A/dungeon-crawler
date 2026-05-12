# Unique Rare Weapons with Lore
RARE_WEAPONS = [
    {
        "id": "shadowfang",
        "name": "Shadowfang",
        "type": "dagger",
        "min_level": 10,
        "damage": 45,
        "crit_chance": 0.25,
        "lore": "Forged in the Abyss by the Nightblade Cult, this dagger drinks the light around it. Whispers say it was used to assassinate the Sun King."
    },
    {
        "id": "stormbringer",
        "name": "Stormbringer",
        "type": "sword",
        "min_level": 15,
        "damage": 65,
        "lightning_damage": 30,
        "lore": "A blade crackling with eternal lightning. Legend tells of a warrior who challenged the Storm God and claimed this weapon from the heavens themselves."
    },
    {
        "id": "frostmourne",
        "name": "Frostmourne",
        "type": "greatsword",
        "min_level": 20,
        "damage": 80,
        "freeze_chance": 0.20,
        "lore": "The Lich King's cursed blade. Those who wield it feel their soul slowly freezing, trading warmth for unimaginable power."
    },
    {
        "id": "phoenix_bow",
        "name": "Phoenix Bow",
        "type": "bow",
        "min_level": 18,
        "damage": 55,
        "fire_damage": 40,
        "ranged": True,
        "range": 7,
        "lore": "Crafted from the tailfeathers of the Eternal Phoenix. Each arrow ignites with rebirth flames that never truly die."
    },
    {
        "id": "voidreaver",
        "name": "Voidreaver",
        "type": "axe",
        "min_level": 25,
        "damage": 95,
        "void_damage": 35,
        "lore": "An axe that cuts through reality itself. Miners found it in a meteor crater, still humming with cosmic energy."
    },
    {
        "id": "serpents_fang",
        "name": "Serpent's Fang",
        "type": "spear",
        "min_level": 12,
        "damage": 50,
        "poison_damage": 25,
        "lore": "The fang of Jörmungandr, the World Serpent. Its venom can corrupt even the purest souls."
    },
    {
        "id": "soulstealer",
        "name": "Soulstealer",
        "type": "scythe",
        "min_level": 30,
        "damage": 100,
        "lifesteal": 0.30,
        "lore": "Death's own harvesting tool, stolen by a mortal who dared to bargain with the Reaper. Each kill extends the wielder's life."
    },
    {
        "id": "dragonheart",
        "name": "Dragonheart Hammer",
        "type": "hammer",
        "min_level": 22,
        "damage": 85,
        "fire_damage": 30,
        "stun_chance": 0.15,
        "lore": "Forged in dragon's breath and cooled in dragon's blood. The heart of an ancient wyrm beats within its core."
    },
    {
        "id": "moonlight_blade",
        "name": "Moonlight Blade",
        "type": "katana",
        "min_level": 16,
        "damage": 60,
        "crit_damage": 2.5,
        "lore": "A blade that only appears under the full moon. Samurai legends speak of its ability to cut through darkness itself."
    },
    {
        "id": "chaos_staff",
        "name": "Staff of Chaos",
        "type": "staff",
        "min_level": 28,
        "damage": 70,
        "magic_damage": 60,
        "ranged": True,
        "range": 6,
        "lore": "Carved from the World Tree during the Age of Madness. Reality bends around those who master its chaotic energies."
    },
    {
        "id": "bloodletter",
        "name": "Bloodletter",
        "type": "sword",
        "min_level": 14,
        "damage": 55,
        "bleed_damage": 20,
        "lore": "A cursed blade that thirsts for blood. Warriors who wield it report hearing whispers urging them to spill more."
    },
    {
        "id": "starfall",
        "name": "Starfall",
        "type": "bow",
        "min_level": 26,
        "damage": 75,
        "holy_damage": 45,
        "ranged": True,
        "range": 8,
        "lore": "Blessed by the Celestial Council. Arrows fired from this bow streak like falling stars, bringing divine judgment."
    },
    {
        "id": "earthshaker",
        "name": "Earthshaker",
        "type": "mace",
        "min_level": 24,
        "damage": 90,
        "aoe_damage": 40,
        "lore": "The weapon of the Titan Grom. Each strike sends shockwaves through the earth, toppling mountains."
    },
    {
        "id": "whisperwind",
        "name": "Whisperwind",
        "type": "dagger",
        "min_level": 19,
        "damage": 50,
        "speed_bonus": 0.40,
        "lore": "So light it seems to float. Assassins of the Wind Temple use it to strike before their victims even know they're there."
    },
    {
        "id": "eternity",
        "name": "Eternity",
        "type": "longsword",
        "min_level": 35,
        "damage": 120,
        "all_stats": 15,
        "lore": "The First Blade, forged at the dawn of time. It has witnessed the rise and fall of countless civilizations."
    }
]


# Unique Rare Bosses with Lore
RARE_BOSSES = [
    {
        "id": "shadow_king",
        "name": "The Shadow King",
        "level": 10,
        "hp": 500,
        "damage": 35,
        "abilities": [
            {
                "name": "shadow_strike",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "shadow",
                "damage_multiplier": 1.5,
                "special_effects": {
                    "armor_penetration": 0.5
                }
            },
            {
                "name": "darkness_aura",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "circle",
                    "radius": 3
                },
                "element": "shadow",
                "damage_multiplier": 1.0,
                "special_effects": {
                    "blind": True
                }
            }
        ],
        "attack_pattern": {
            "type": "predictable",
            "sequence": ["shadow_strike", "normal_attack", "darkness_aura"]
        },
        "lore": "Once a noble ruler, he made a pact with darkness to save his dying kingdom. Now he rules an empire of shadows, forever bound to the Abyss.",
        "drops": ["shadowfang"]
    },
    {
        "id": "storm_titan",
        "name": "Volthar the Storm Titan",
        "level": 15,
        "hp": 800,
        "damage": 50,
        "abilities": [
            {
                "name": "lightning_bolt",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "none"
                },
                "element": "lightning",
                "damage_multiplier": 2.0,
                "special_effects": {}
            },
            {
                "name": "chain_lightning",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "line",
                    "range": 5,
                    "width": 1
                },
                "element": "lightning",
                "damage_multiplier": 2.0,
                "special_effects": {}
            },
            {
                "name": "thunder_clap",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "circle",
                    "radius": 2
                },
                "element": "lightning",
                "damage_multiplier": 1.3,
                "special_effects": {
                    "stun": True
                }
            }
        ],
        "attack_pattern": {
            "type": "predictable",
            "sequence": ["lightning_bolt", "chain_lightning", "normal_attack", "thunder_clap"]
        },
        "lore": "A primordial being born from the first thunderstorm. Volthar believes mortals have grown too arrogant and seeks to humble them with nature's fury.",
        "drops": ["stormbringer"]
    },
    {
        "id": "lich_king",
        "name": "Kel'Thuzad the Eternal",
        "level": 20,
        "hp": 1200,
        "damage": 65,
        "abilities": [
            {
                "name": "frost_nova",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "circle",
                    "radius": 2
                },
                "element": "frost",
                "damage_multiplier": 1.0,
                "special_effects": {
                    "freeze": True
                }
            },
            {
                "name": "death_coil",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "shadow",
                "damage_multiplier": 1.2,
                "special_effects": {
                    "heal_boss": 0.5
                }
            },
            {
                "name": "raise_dead",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "shadow",
                "damage_multiplier": 0,
                "special_effects": {
                    "summon": True
                }
            }
        ],
        "attack_pattern": {
            "type": "predictable",
            "sequence": ["frost_nova", "death_coil", "normal_attack", "raise_dead"]
        },
        "lore": "A brilliant mage who sought immortality through necromancy. His heart froze centuries ago, but his ambition burns colder still.",
        "drops": ["frostmourne"]
    },
    {
        "id": "phoenix_queen",
        "name": "Pyralis the Phoenix Queen",
        "level": 18,
        "hp": 1000,
        "damage": 55,
        "abilities": [
            {
                "name": "flame_burst",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "cone",
                    "range": 3
                },
                "element": "fire",
                "damage_multiplier": 1.8,
                "special_effects": {
                    "burn": True
                }
            },
            {
                "name": "inferno",
                "telegraph_turns": 2,
                "attack_zone": {
                    "type": "circle",
                    "radius": 5
                },
                "element": "fire",
                "damage_multiplier": 2.5,
                "special_effects": {
                    "burn": True
                }
            },
            {
                "name": "rebirth",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "fire",
                "damage_multiplier": 0,
                "special_effects": {
                    "heal_on_low_hp": 0.3
                }
            }
        ],
        "attack_pattern": {
            "type": "predictable",
            "sequence": ["flame_burst", "normal_attack", "flame_burst", "inferno"]
        },
        "lore": "Guardian of the Eternal Flame. She has died and been reborn a thousand times, each rebirth making her wiser and more powerful.",
        "drops": ["phoenix_bow"]
    },
    {
        "id": "void_horror",
        "name": "Xal'atath the Void Horror",
        "level": 25,
        "hp": 1800,
        "damage": 80,
        "abilities": [
            {
                "name": "void_tentacles",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "random_tiles",
                    "count": 4
                },
                "element": "void",
                "damage_multiplier": 0.5,
                "special_effects": {
                    "hits": 3
                }
            },
            {
                "name": "reality_tear",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "line",
                    "range": 8,
                    "width": 1
                },
                "element": "void",
                "damage_multiplier": 2.5,
                "special_effects": {
                    "armor_penetration": 1.0
                }
            },
            {
                "name": "madness",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "void",
                "damage_multiplier": 0,
                "special_effects": {
                    "confusion": True
                }
            }
        ],
        "attack_pattern": {
            "type": "random"
        },
        "lore": "An entity from beyond the stars. It exists in multiple dimensions simultaneously, driving those who gaze upon it to insanity.",
        "drops": ["voidreaver"]
    },
    {
        "id": "world_serpent",
        "name": "Jörmungandr",
        "level": 12,
        "hp": 650,
        "damage": 45,
        "abilities": [
            {
                "name": "poison_breath",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "cone",
                    "range": 4
                },
                "element": "poison",
                "damage_multiplier": 1.0,
                "special_effects": {
                    "poison": True
                }
            },
            {
                "name": "venom_spit",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "circle",
                    "radius": 1
                },
                "element": "poison",
                "damage_multiplier": 1.0,
                "special_effects": {
                    "poison": True
                }
            },
            {
                "name": "constrict",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "circle",
                    "radius": 1
                },
                "element": "physical",
                "damage_multiplier": 1.5,
                "special_effects": {
                    "adjacent_only": True
                }
            }
        ],
        "attack_pattern": {
            "type": "predictable",
            "sequence": ["poison_breath", "venom_spit", "normal_attack", "constrict"]
        },
        "lore": "The serpent so large it encircles the world. Ancient prophecies say when it releases its tail, the world will end.",
        "drops": ["serpents_fang"]
    },
    {
        "id": "death_incarnate",
        "name": "Thanatos the Reaper",
        "level": 30,
        "hp": 2500,
        "damage": 100,
        "abilities": [
            {
                "name": "soul_harvest",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "none"
                },
                "element": "shadow",
                "damage_multiplier": 1.5,
                "special_effects": {
                    "execute_threshold": 0.3
                }
            },
            {
                "name": "death_mark",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "shadow",
                "damage_multiplier": 0,
                "special_effects": {
                    "damage_amp": 0.25,
                    "duration": 3
                }
            },
            {
                "name": "reap",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "shadow",
                "damage_multiplier": 1.5,
                "special_effects": {}
            }
        ],
        "attack_pattern": {
            "type": "predictable",
            "sequence": ["death_mark", "normal_attack", "soul_harvest", "reap", "normal_attack"]
        },
        "lore": "Death itself given form. Thanatos walks the mortal realm when the balance between life and death is threatened.",
        "drops": ["soulstealer"]
    },
    {
        "id": "ancient_dragon",
        "name": "Ignaroth the Ancient",
        "level": 22,
        "hp": 1500,
        "damage": 75,
        "abilities": [
            {
                "name": "dragon_breath",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "cone",
                    "range": 5
                },
                "element": "fire",
                "damage_multiplier": 2.2,
                "special_effects": {}
            },
            {
                "name": "tail_sweep",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "cone",
                    "range": 2,
                    "direction": "behind"
                },
                "element": "physical",
                "damage_multiplier": 1.4,
                "special_effects": {
                    "knockback": True
                }
            },
            {
                "name": "wing_buffet",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "circle",
                    "radius": 3
                },
                "element": "physical",
                "damage_multiplier": 1.4,
                "special_effects": {
                    "knockback": True
                }
            }
        ],
        "attack_pattern": {
            "type": "predictable",
            "sequence": ["dragon_breath", "normal_attack", "tail_sweep", "wing_buffet"]
        },
        "lore": "The last of the Elder Dragons. Ignaroth has hoarded knowledge and treasure for millennia, growing more powerful with each passing age.",
        "drops": ["dragonheart"]
    },
    {
        "id": "moon_spirit",
        "name": "Tsukuyomi the Moon Spirit",
        "level": 16,
        "hp": 900,
        "damage": 60,
        "abilities": [
            {
                "name": "lunar_slash",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "arc",
                    "range": 3,
                    "width": 3
                },
                "element": "holy",
                "damage_multiplier": 1.5,
                "special_effects": {}
            },
            {
                "name": "moonlight",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "tiles"
                },
                "element": "holy",
                "damage_multiplier": 1.0,
                "special_effects": {
                    "heal_boss": True,
                    "damage_in_light": True
                }
            },
            {
                "name": "eclipse",
                "telegraph_turns": 2,
                "attack_zone": {
                    "type": "aoe"
                },
                "element": "shadow",
                "damage_multiplier": 2.0,
                "special_effects": {}
            }
        ],
        "attack_pattern": {
            "type": "predictable",
            "sequence": ["lunar_slash", "moonlight", "lunar_slash", "normal_attack", "eclipse"]
        },
        "lore": "A celestial being who descended to punish those who disrespect the night. Beautiful and terrifying in equal measure.",
        "drops": ["moonlight_blade"]
    },
    {
        "id": "chaos_lord",
        "name": "Azaroth the Chaos Lord",
        "level": 28,
        "hp": 2200,
        "damage": 90,
        "abilities": [
            {
                "name": "chaos_bolt",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "void",
                "damage_multiplier": "random",
                "special_effects": {
                    "random_multiplier_min": 0.5,
                    "random_multiplier_max": 3.0
                }
            },
            {
                "name": "reality_warp",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "void",
                "damage_multiplier": 0,
                "special_effects": {
                    "teleport_player": True
                }
            },
            {
                "name": "entropy",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "circle",
                    "radius": 4
                },
                "element": "void",
                "damage_multiplier": 1.8,
                "special_effects": {
                    "decay": True
                }
            }
        ],
        "attack_pattern": {
            "type": "random"
        },
        "lore": "Born from the primordial chaos before creation. Azaroth seeks to return all existence to the beautiful disorder of the void.",
        "drops": ["chaos_staff"]
    },
    {
        "id": "blood_god",
        "name": "Khorne the Blood God",
        "level": 14,
        "hp": 750,
        "damage": 55,
        "abilities": [
            {
                "name": "blood_rage",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "physical",
                "damage_multiplier": 0,
                "special_effects": {
                    "boss_damage_buff": 0.5,
                    "duration": 3
                }
            },
            {
                "name": "crimson_wave",
                "telegraph_turns": 1,
                "attack_zone": {
                    "type": "line",
                    "range": 5,
                    "width": 1
                },
                "element": "fire",
                "damage_multiplier": 1.5,
                "special_effects": {}
            },
            {
                "name": "berserker",
                "telegraph_turns": 0,
                "attack_zone": {
                    "type": "none"
                },
                "element": "physical",
                "damage_multiplier": 2.0,
                "special_effects": {
                    "self_damage": 0.25
                }
            }
        ],
        "attack_pattern": {
            "type": "predictable",
            "sequence": ["blood_rage", "crimson_wave", "normal_attack", "berserker", "normal_attack"]
        },
        "lore": "A deity sustained by violence and bloodshed. Every battle fought in his name makes him stronger.",
        "drops": ["bloodletter"]
    }
]


# Element type mappings for abilities
ABILITY_ELEMENTS = {
    # Shadow abilities
    "shadow_strike": "shadow",
    "darkness_aura": "shadow",
    "death_coil": "shadow",
    "soul_harvest": "shadow",
    "death_mark": "shadow",
    "reap": "shadow",
    "eclipse": "shadow",
    
    # Lightning abilities
    "lightning_bolt": "lightning",
    "chain_lightning": "lightning",
    "thunder_clap": "lightning",
    
    # Frost abilities
    "frost_nova": "frost",
    
    # Fire abilities
    "flame_burst": "fire",
    "inferno": "fire",
    "rebirth": "fire",
    "dragon_breath": "fire",
    "crimson_wave": "fire",
    
    # Void abilities
    "void_tentacles": "void",
    "reality_tear": "void",
    "madness": "void",
    "chaos_bolt": "void",
    "reality_warp": "void",
    "entropy": "void",
    
    # Poison abilities
    "poison_breath": "poison",
    "venom_spit": "poison",
    
    # Holy abilities
    "lunar_slash": "holy",
    "moonlight": "holy",
    
    # Physical (no element)
    "constrict": "physical",
    "tail_sweep": "physical",
    "wing_buffet": "physical",
    "blood_rage": "physical",
    "berserker": "physical",
    "raise_dead": "physical"
}


def get_ability_element(ability_name):
    """
    Get element type for an ability
    
    Args:
        ability_name: Name of the ability
    
    Returns:
        str: Element type (fire, frost, lightning, poison, shadow, holy, void, physical)
    """
    return ABILITY_ELEMENTS.get(ability_name, "physical")


import logging

# Valid element types
VALID_ELEMENTS = {"fire", "frost", "lightning", "poison", "shadow", "holy", "void", "physical"}

# Valid zone types
VALID_ZONE_TYPES = {"none", "circle", "cone", "line", "aoe", "random_tiles", "arc", "tiles"}

# Zone parameter requirements
ZONE_PARAM_REQUIREMENTS = {
    "circle": ["radius"],
    "cone": ["range"],
    "line": ["range", "width"],
    "arc": ["range", "width"],
    "random_tiles": ["count"]
}


def validate_boss_abilities():
    """
    Validate boss ability data completeness and correctness
    
    Returns:
        dict: Validation report with warnings and errors
    """
    report = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "bosses_checked": 0,
        "abilities_checked": 0
    }
    
    for boss in RARE_BOSSES:
        report["bosses_checked"] += 1
        boss_id = boss.get("id", "unknown")
        boss_name = boss.get("name", "Unknown Boss")
        
        # Check if boss has abilities array
        if "abilities" not in boss:
            msg = f"{boss_name} ({boss_id}): Missing abilities array"
            report["errors"].append(msg)
            logging.error(msg)
            report["valid"] = False
            continue
        
        if not isinstance(boss["abilities"], list) or len(boss["abilities"]) == 0:
            msg = f"{boss_name} ({boss_id}): Abilities array is empty or invalid"
            report["errors"].append(msg)
            logging.error(msg)
            report["valid"] = False
            continue
        
        # Validate each ability
        for ability in boss["abilities"]:
            report["abilities_checked"] += 1
            ability_name = ability.get("name", "unnamed")
            
            # Check required fields
            if "name" not in ability:
                msg = f"{boss_name} ({boss_id}): Ability missing 'name' field"
                report["errors"].append(msg)
                logging.error(msg)
                report["valid"] = False
            
            if "telegraph_turns" not in ability:
                msg = f"{boss_name} ({boss_id}) - {ability_name}: Missing 'telegraph_turns' field, using default 0"
                report["warnings"].append(msg)
                logging.warning(msg)
                ability["telegraph_turns"] = 0
            
            if "attack_zone" not in ability:
                msg = f"{boss_name} ({boss_id}) - {ability_name}: Missing 'attack_zone' field, using default 'none'"
                report["warnings"].append(msg)
                logging.warning(msg)
                ability["attack_zone"] = {"type": "none"}
            
            if "element" not in ability:
                msg = f"{boss_name} ({boss_id}) - {ability_name}: Missing 'element' field, using default 'physical'"
                report["warnings"].append(msg)
                logging.warning(msg)
                ability["element"] = "physical"
            
            if "damage_multiplier" not in ability:
                msg = f"{boss_name} ({boss_id}) - {ability_name}: Missing 'damage_multiplier' field, using default 1.0"
                report["warnings"].append(msg)
                logging.warning(msg)
                ability["damage_multiplier"] = 1.0
            
            # Validate attack_zone structure
            attack_zone = ability.get("attack_zone", {})
            if not isinstance(attack_zone, dict):
                msg = f"{boss_name} ({boss_id}) - {ability_name}: attack_zone must be a dict"
                report["errors"].append(msg)
                logging.error(msg)
                report["valid"] = False
                continue
            
            # Check attack_zone has type field
            if "type" not in attack_zone:
                msg = f"{boss_name} ({boss_id}) - {ability_name}: attack_zone missing 'type' field"
                report["errors"].append(msg)
                logging.error(msg)
                report["valid"] = False
                continue
            
            zone_type = attack_zone["type"]
            
            # Validate zone type
            if zone_type not in VALID_ZONE_TYPES:
                msg = f"{boss_name} ({boss_id}) - {ability_name}: Invalid zone type '{zone_type}'"
                report["warnings"].append(msg)
                logging.warning(msg)
            
            # Check zone parameters match zone type
            if zone_type in ZONE_PARAM_REQUIREMENTS:
                required_params = ZONE_PARAM_REQUIREMENTS[zone_type]
                for param in required_params:
                    if param not in attack_zone:
                        msg = f"{boss_name} ({boss_id}) - {ability_name}: Zone type '{zone_type}' missing required parameter '{param}'"
                        report["warnings"].append(msg)
                        logging.warning(msg)
            
            # Validate element type
            element = ability.get("element", "physical")
            if element not in VALID_ELEMENTS:
                msg = f"{boss_name} ({boss_id}) - {ability_name}: Invalid element type '{element}'"
                report["warnings"].append(msg)
                logging.warning(msg)
            
            # Validate damage_multiplier is numeric (or "random" for chaos_bolt)
            damage_mult = ability.get("damage_multiplier")
            if damage_mult != "random" and not isinstance(damage_mult, (int, float)):
                msg = f"{boss_name} ({boss_id}) - {ability_name}: damage_multiplier must be numeric or 'random', got {type(damage_mult).__name__}"
                report["errors"].append(msg)
                logging.error(msg)
                report["valid"] = False
            
            # Provide default for special_effects if missing
            if "special_effects" not in ability:
                ability["special_effects"] = {}
    
    # Log summary
    if report["valid"]:
        logging.info(f"Boss ability validation passed: {report['bosses_checked']} bosses, {report['abilities_checked']} abilities checked")
    else:
        logging.error(f"Boss ability validation failed with {len(report['errors'])} errors")
    
    if report["warnings"]:
        logging.warning(f"Boss ability validation completed with {len(report['warnings'])} warnings")
    
    return report
