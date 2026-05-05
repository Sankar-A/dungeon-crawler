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
        "abilities": ["shadow_strike", "darkness_aura"],
        "lore": "Once a noble ruler, he made a pact with darkness to save his dying kingdom. Now he rules an empire of shadows, forever bound to the Abyss.",
        "drops": ["shadowfang"]
    },
    {
        "id": "storm_titan",
        "name": "Volthar the Storm Titan",
        "level": 15,
        "hp": 800,
        "damage": 50,
        "abilities": ["lightning_bolt", "chain_lightning", "thunder_clap"],
        "lore": "A primordial being born from the first thunderstorm. Volthar believes mortals have grown too arrogant and seeks to humble them with nature's fury.",
        "drops": ["stormbringer"]
    },
    {
        "id": "lich_king",
        "name": "Kel'Thuzad the Eternal",
        "level": 20,
        "hp": 1200,
        "damage": 65,
        "abilities": ["frost_nova", "death_coil", "raise_dead"],
        "lore": "A brilliant mage who sought immortality through necromancy. His heart froze centuries ago, but his ambition burns colder still.",
        "drops": ["frostmourne"]
    },
    {
        "id": "phoenix_queen",
        "name": "Pyralis the Phoenix Queen",
        "level": 18,
        "hp": 1000,
        "damage": 55,
        "abilities": ["flame_burst", "rebirth", "inferno"],
        "lore": "Guardian of the Eternal Flame. She has died and been reborn a thousand times, each rebirth making her wiser and more powerful.",
        "drops": ["phoenix_bow"]
    },
    {
        "id": "void_horror",
        "name": "Xal'atath the Void Horror",
        "level": 25,
        "hp": 1800,
        "damage": 80,
        "abilities": ["void_tentacles", "reality_tear", "madness"],
        "lore": "An entity from beyond the stars. It exists in multiple dimensions simultaneously, driving those who gaze upon it to insanity.",
        "drops": ["voidreaver"]
    },
    {
        "id": "world_serpent",
        "name": "Jörmungandr",
        "level": 12,
        "hp": 650,
        "damage": 45,
        "abilities": ["poison_breath", "constrict", "venom_spit"],
        "lore": "The serpent so large it encircles the world. Ancient prophecies say when it releases its tail, the world will end.",
        "drops": ["serpents_fang"]
    },
    {
        "id": "death_incarnate",
        "name": "Thanatos the Reaper",
        "level": 30,
        "hp": 2500,
        "damage": 100,
        "abilities": ["soul_harvest", "death_mark", "reap"],
        "lore": "Death itself given form. Thanatos walks the mortal realm when the balance between life and death is threatened.",
        "drops": ["soulstealer"]
    },
    {
        "id": "ancient_dragon",
        "name": "Ignaroth the Ancient",
        "level": 22,
        "hp": 1500,
        "damage": 75,
        "abilities": ["dragon_breath", "tail_sweep", "wing_buffet"],
        "lore": "The last of the Elder Dragons. Ignaroth has hoarded knowledge and treasure for millennia, growing more powerful with each passing age.",
        "drops": ["dragonheart"]
    },
    {
        "id": "moon_spirit",
        "name": "Tsukuyomi the Moon Spirit",
        "level": 16,
        "hp": 900,
        "damage": 60,
        "abilities": ["lunar_slash", "moonlight", "eclipse"],
        "lore": "A celestial being who descended to punish those who disrespect the night. Beautiful and terrifying in equal measure.",
        "drops": ["moonlight_blade"]
    },
    {
        "id": "chaos_lord",
        "name": "Azaroth the Chaos Lord",
        "level": 28,
        "hp": 2200,
        "damage": 90,
        "abilities": ["chaos_bolt", "reality_warp", "entropy"],
        "lore": "Born from the primordial chaos before creation. Azaroth seeks to return all existence to the beautiful disorder of the void.",
        "drops": ["chaos_staff"]
    },
    {
        "id": "blood_god",
        "name": "Khorne the Blood God",
        "level": 14,
        "hp": 750,
        "damage": 55,
        "abilities": ["blood_rage", "crimson_wave", "berserker"],
        "lore": "A deity sustained by violence and bloodshed. Every battle fought in his name makes him stronger.",
        "drops": ["bloodletter"]
    }
]
