import json

GAME_NAME = 'Turbo Batlle City'
GAME_VERSION = 'Development patch' # Development patch

CONFIG_FILE = 'config.json'

ENCODING = 'utf-8'

f = open(CONFIG_FILE)
data = json.load(f)
f.close()

WIDTH = 800
HEIGHT = 800
MAX_NICKNAME_LENTH = 12
NICKNAME = data['NICKNAME'][:MAX_NICKNAME_LENTH:]
SERVER_IP = data['SERVER_IP']
SERVER_PORT = 25217

MAX_PLAYERS_ON_MAP = 8

OBJECT_MULTIPLYER_WIDTH = WIDTH // 400
OBJECT_MULTIPLYER_HEIGHT = HEIGHT // 400
AVERAGE_MULTIPLYER = (OBJECT_MULTIPLYER_WIDTH + OBJECT_MULTIPLYER_HEIGHT) // 2

FPS = 120
TICK_RATE = 64
MOVEMENT_TICKS = FPS / 60
BULLET_SPEED = (3.5*AVERAGE_MULTIPLYER) / MOVEMENT_TICKS
TANK_SPEED = (1*AVERAGE_MULTIPLYER) / MOVEMENT_TICKS
TANK_SPEED_BOOST_MULTIPLYER = 2 # when boost is on TANK_SPEED = TANK_SPEED * TANK_SPEED_BOOST_MULTIPLYER
TANK_SHOOT_SPEED = FPS
AMMUNITION_SIZE = 5
AMMUNITION_RELOAD_SPEED = 4.75 # Float
IMMUNITY_DURATION = 1.75 # Immunity after respawn
DEATH_DURATION = 2.0 # Time for being out after death
BOOST_DURATION = 2.25
BOOST_RECOVERY_DURATION = 5.0

START_BUTTON_SIZE = (165*OBJECT_MULTIPLYER_WIDTH, 75*OBJECT_MULTIPLYER_HEIGHT)
BLOCK_SIZE = (25*OBJECT_MULTIPLYER_WIDTH, 25*OBJECT_MULTIPLYER_HEIGHT)
LEAVE_SESSION_BUTTON_SIZE = BLOCK_SIZE
TANK_SIZE = (15*OBJECT_MULTIPLYER_WIDTH, 15*OBJECT_MULTIPLYER_HEIGHT)
IMMORTALITY_PATTERN_SIZE = (16*OBJECT_MULTIPLYER_WIDTH, 16*OBJECT_MULTIPLYER_HEIGHT)
SHOT_SIZE = (8*OBJECT_MULTIPLYER_WIDTH, 8*OBJECT_MULTIPLYER_HEIGHT)
BOOST_BAR_SIZE = (8*AVERAGE_MULTIPLYER, 32*AVERAGE_MULTIPLYER)
INFO_FONT_SIZE = 10*AVERAGE_MULTIPLYER
SCORE_FONT_SIZE = 32*AVERAGE_MULTIPLYER
NICK_FONT_SIZE = 7*AVERAGE_MULTIPLYER
AMMUNITION_FONT_SIZE = 28*AVERAGE_MULTIPLYER
RUNE_SIZE = (10*OBJECT_MULTIPLYER_WIDTH, 12*OBJECT_MULTIPLYER_HEIGHT)
SQUARE_RUNE_SIZE = (12*OBJECT_MULTIPLYER_WIDTH, 12*OBJECT_MULTIPLYER_HEIGHT)
WIDE_RUNE_SIZE = (12*OBJECT_MULTIPLYER_WIDTH, 9*OBJECT_MULTIPLYER_HEIGHT)

MAP_COORD_SHIFT = (25*AVERAGE_MULTIPLYER, 25*AVERAGE_MULTIPLYER) #25*AVERAGE_MULTIPLYER

AMMO_RUNE_BONUS = 2 # Additional bullet(s) after collecting ammo rune

# RUNES

BOOST_RUNE_NAME = 'haste'
IMMUNITY_RUNE_NAME = 'immortality'
REVEAL_RUNE_NAME = 'reveal'
AMMO_RUNE_NAME = 'ammo'

RUNES_CONFIG = {'spawn_timer':12, 'activity_times':{BOOST_RUNE_NAME:5, IMMUNITY_RUNE_NAME:4, REVEAL_RUNE_NAME:3.75, AMMO_RUNE_NAME:0}} # each time is in seconds
RUNES_CONFIG['runes'] = [rune for rune in RUNES_CONFIG['activity_times']]

GAME_FONT = 'Terminus.ttf'
SYS_FONT = 'Ubuntu'

CRASH_LOGGING_DIRECTORY = 'crash_logs'


# controllers and additional devices
CONTROLLER_SHOOT_BUTTON = 0
CONTROLLER_BOOST_BUTTON = 1
CONTROLLER_RELOAD_BUTTON = 2

CONTROL_AXIS_INDEX = 0
