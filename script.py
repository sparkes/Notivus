import time
import board #for the pin defs
from analogio import AnalogIn
import busio #for i2c
import adafruit_ssd1306 #display
import audiomp3 #mp3
import audiobusio #i2s

#settings
#set the sample size for getting the average voltage reading sample size = loops*size
loops = 16 #16 fits the screen so lets go with that
size = 8192 #8k of samples

#globals
old_noise = 0

"""
The very strange list of words that allegedly are contained in the v1 Ovulus devices
They say much more about the culture that created them than any attempt at communication
"""
wordlist = ('PLACEBO', 'ENTIRE', 'UNDER', 'MUSE', 'D', 'SUPPER', 'LIGHT', 'CARRIER', 'SHOULD', 'HUMAN', 'AWARD', 'RECORDS', 'PLUTO', 'WORM', 'PAUL', 'EAT', 'TREE', 'MOMMY', 'COUNTRY', 'STORY', 'LAY', 'BUSINESS', 'SENT', 'HIGHWAY', 'APPLE', 'RABBIT', 'FOLIAGE', 'WIDE', 'OUTSIDE', 'DOWN', 'TIN', 'METAL', 'COMPOUND', 'SQUEEZE', 'KISS', 'HOLIDAY', 'SAW', 'HASTE', 'ALTHOUGH', 'PROPERTY', 'FIFTEEN', 'WAVE', 'OBSERVE', 'DISASTER', 'THINK', 'MARKER', 'CLIMB', 'SOLO', 'JIM', 'BIKE', 'RUN', 'GREEN', 'AFRICA', 'POSSIBLE', 'FACTORS', 'VIDEO', 'NIGHT', 'DEPLETE', 'COARSE', 'LOVING', 'CHANGE', 'SIZE','INITIAL', 'BEAT', 'REWIND', 'GLANCE', 'ZOO', 'PLACATE', 'ENOUGH', 'UNCLE', 'MURPHY', 'MAIN', 'SUNRISE', 'LIFE', 'CAROL', 'SHORT', 'HUG', 'AUTOMATIC', 'FLY', 'WHOLE', 'PARANORMAL', 'PAT', 'EAST', 'TRAVEL', 'MOMENT', 'COUNT', 'STORE', 'LAUGH', 'BURY', 'SEND', 'HIDE', 'APPEAR', 'QUITE', 'FOE', 'ELECTRIC', 'OURS', 'DOUBLE', 'TIME', 'MERCURY', 'COMPETE', 'SPRING', 'KIND', 'BOTTLE', 'SATURN', 'HARVEST', 'ALRIGHT', 'PROJECTION', 'FIDDLE', 'WATER', 'OAR', 'DIRT', 'THING', 'MARCH', 'CLEANSING', 'SOLDIERS', 'JESUS', 'BIBLE', 'AMOUNT', 'GREATER', 'AFFAIR', 'POSE', 'FACT', 'VERONICA', 'NICK', 'DEMON', 'TEACHER', 'LOUD', 'CHAIR', 'SIX', 'INFORMATION', 'BET', 'REVEREND', 'GIRL', 'ZERO', 'PINE', 'ENGLISH', 'TYPE', 'MULTIPLE', 'DECEND', 'SUMMER', 'LICK', 'CARE', 'SHOOT', 'HOW', 'AUNT', 'REASON', 'GENERAL', 'WORDS', 'PAST', 'EARTHEN', 'TRAP', 'MOIST', 'COUGH', 'CATTLE', 'LESSER', 'BURN', 'SELF', 'HI', 'APART', 'QUILL', 'WASH', 'NOW', 'DIME', 'DOOR', 'TILT', 'MEN', 'COMPANY', 'SPOT', 'KILLED', 'BORN', 'SEE', 'HARRIET', 'ALPHABET', 'PROGRAM', 'FEMALE', 'WASTE', 'TOM', 'DIRECT', 'TICKLE', 'MANY', 'CLASSIC', 'SOLD', 'JERK', 'BETWEEN', 'ROUND', 'GRAY', 'ADJUST', 'PORT', 'F', 'VERB', 'NEXT', 'DEEP', 'TASTE', 'LOST', 'CESIUM', 'SIT', 'INDIRECT VOICE', 'BEACH', 'RETURN', 'GET', 'YOURSELF', 'PIERCE', 'ENGINE', 'TWIST', 'MUCH', 'CURRENT', 'SULTRY', 'LEVITATION', 'CARD', 'SHOCK', 'HOURS', 'AU', '7', 'FRIEND', 'WOODS', 'PASS', 'EARS', 'TRAIL', 'MOAT', 'COTTON', 'STONES', 'LAST', 'BUILT', 'SEEM', 'HERNIA', 'ANY', 'QUICKLY', 'FLOWER', 'WHITE', 'ORDER', 'DON', 'TIGHT', 'MEMORIES', 'COMMON', 'SPIRITS', 'SEVEN', 'BOOT', 'SANDRA', 'HARD', 'ALMOST', 'PRODUCE', 'FELON', 'NEW', 'DID', 'TALKING', 'THEY', 'MANOR', 'CLAP', 'SOFT', 'JAPANESE', 'BETTER', 'ROSES', 'GRAVE YARD', 'ADDITION', 'POPPA', 'EXPRESS', 'VECTOR', 'NEWER', 'DECIMAL', 'TAPE', 'LOSE', 'CENTURY', 'SIR', 'INDIAN', 'BATTERY', 'RESTORED', 'GENTLY', 'YOUNG', 'PIE', 'ENEMY', 'TWELVE', 'TENSE', 'CUP', 'SUGGESTED', 'LETTER', 'CAR', 'SHIP', 'HOT', 'ATTIC', 'READY', 'FRENCH', 'WONT', 'PART', 'EAR', 'TRAFFIC', 'MITTEN', 'CORRECT', 'STOMACH', 'LARRY', 'BUILD', 'SEEDS', 'HERD', 'ANTHONY', 'QUESTIONS', 'PEN', 'WHICH', 'ORANGE', 'DOLLARS', 'TIE', 'MELODY', 'COME', 'SPIN', 'KEPT', 'BONES', 'SAMPLE', 'HAPPINESS', 'ALLEY', 'PROBLEM', 'FEET', 'WARS', 'NOUN', 'DIGGING', 'THERMAL', 'MANDY', 'CITY', 'SOBER', 'JAN', 'HIGH', 'ROSE', 'GRASS', 'ADAM', 'POOR', 'EXPECT', 'VASE', 'CRUST', 'SUCH', 'LENS', 'LOOSE', 'CENTRAL', 'SINK', 'S', 'BATH', 'REST', 'GRAND', 'YIELD', 'PICKED', 'EMULATE', 'TURNOVER', 'MOUTH', 'CRYSTAL', 'SUFFIX', 'LOCATED', 'CAPITAL', 'SHIFT', 'HORRIBLE', 'ATOM', 'REACT', 'FREE', 'WON', 'PERSON', 'E', 'TRACK', 'MISTRESS', 'LIMP', 'STILL', 'LARGE', 'BRUSH', 'SHAPE', 'HEMATAUS', 'ANOMALIES', 'QUEST', 'FLAT', 'WHERE', 'OR', 'DOG', 'TOP', 'MEET', 'COLOR', 'SPEED', 'KEEP', 'BODY', 'SAM', 'HAPPENED', 'ALL', 'PRINTED', 'FEEL', 'DRAW', 'NOTHING', 'DIFFICULT', 'THEN', 'MAMMY', 'CHURCH', 'SO', 'JAM', 'BESIDE', 'ROOT', 'GRANDPA', 'ACTION', 'POLTERGEIST', 'ODD', 'VAPOR', 'NERVE', 'DECEIT', 'TAKE', 'LOOK', 'CENT', 'SING', 'INCLUDE', 'BASE', 'RESENT', 'GEEK', 'YES', 'PHONE', 'EMPATH', 'TURN', 'MOUNTAIN', 'STEP', 'LAMB', 'BROKEN', 'CANNON', 'SHEPHERD', 'HOP', 'GLOVE', 'REACH', 'FRANCE', 'WOLF', 'PARAGRAPH', 'DUTY', 'TOWN', 'MIST', 'CORD', 'STICK', 'LAND', 'BROUGHT', 'SECRET', 'HELP', 'ANN', 'QUARANTINES', 'FIT', 'WHEELS', 'OPENING', 'DOCTOR', 'TICK', 'MEDICINE', 'COINS', 'BUT', 'KAREN', 'BOARD', 'SALLY', 'HANG', 'ALIGNMENT', 'PRIDE', 'FEBUARY', 'WARM', 'NOT', 'DIFFERENCE', 'THEM', 'MALICIOUS', 'CHOOSE', 'SNEAK', 'JACKIE', 'BELOW', 'RONDA', 'GRANDMA', 'ACROSS', 'POLE', 'EXAMPLE', 'VALUE', 'NEED', 'DEBBIE', 'TAG', 'LOGICAL', 'CEMENT', 'SIMPLE', 'IN', 'BARREL', 'REPORT', 'GAUZE', 'YELL', 'PETER', 'ELSE', 'DERICK', 'MOSTLY', 'CROSSOVER', 'SUBSTANCES', 'LEND', 'CANDLE', 'SHARP', 'HOMICIDE', 'ASSAULT', 'RAVINE', 'FRACTION', 'WITHIN', 'PAPER', 'DURING', 'TOUCH', 'MISS', 'COPPER', 'JUPITER', 'BLOG', 'SAIL', 'SEAT', 'HELL', 'ANGRY', 'WORLD', 'FISH', 'WHAT', 'ONLY', 'DO RUN', 'THURIFER', 'MEASURE', 'COFFIN', 'SPEAK', 'JUSTICE', 'BRIDGE', 'SALIRAN', 'HAMMER', 'ALICE', 'PRESS', 'FAY', 'WANTED', 'NORTHERN', 'DIVES', 'THE', 'MALEVOLENT', 'CHLORIDE', 'SMOOTH', 'JACK', 'BELL', 'ROLLED', 'HAD', 'ABOVE', 'POEM', 'EVIL', 'V', 'NECESSARY', 'DEAL', 'TABLE', 'MAGIC', 'CELLAR', 'BIG', 'IMMERSION', 'BAR', 'RENT', 'GATEWAY', 'YEAR', 'PLATE', 'ELEVEN', 'TUB', 'MOSS', 'CROPS', 'SUB', 'LEGS', 'CAN YOU', 'SHY', 'HOLY', 'ASHES', 'RATE', 'FOUND', 'WITCH', 'PANEL', 'DUG', 'TROOP', 'SUN', 'COOK', 'STEAMY', 'LAGOON', 'BRITISH', 'SCRUPLE', 'HEAVY', 'ANGLE', 'PUSHED', 'FIRE', 'WEST', 'ONCE', 'DO', 'THROUGH', 'ME', 'COAT', 'SOUTHERN', 'BEGIN', 'ROCKET', 'GOVERNMENT', 'HALO', 'AKASHA', 'PRESENT', 'FATE', 'WALTER', 'NORMAN', 'DICTION', 'THANK', 'MAKE', 'CHILLS', 'SMELL', 'ITS', 'BEING', 'RODGER', 'GRACE', 'ABORT', 'WATCH', 'EVERY', 'USED', 'NEAR', 'DAY', 'SYNN', 'LIVING', 'CEILING', 'SIGN', 'IDLE', 'BANK', 'REMOVE', 'GASP', 'YANK', 'PERIOD', 'ELEMENTAL', 'TRUTH', 'MORES', 'CRESCENT', 'STUFF', 'LEG', 'CAMERA', 'SHAKEN', 'REVEAL', 'AS', 'RAPTURE', 'FORTY', 'WISH', 'PAM', 'DRUNK', 'TOOL', 'MINUTE', 'CONTRITION', 'STAY', 'LADY', 'BRIGHT', 'SCREW', 'HEAT', 'AND', 'PURIFIED', 'FINISH', 'WENT', 'OLDER', 'DIVIDED', 'THRESHOLD', 'MAYBE', 'LASTING', 'SOUP', 'JUMPED', 'BLIND', 'SAFE', 'HAIR', 'AIM', 'PREACHER', 'FASTER', 'WALK', 'NOR', 'DEVIL', 'TEXT', 'SPOON', 'CHILDREN', 'SLUR', 'ISLAND', 'RELIGION', 'GAIL', 'WRITING', 'ALONE', 'PLEASE', 'EVENING', 'US', 'NATION', 'DAVID', 'SYLLABLES', 'LITTLE', 'CAUSE', 'SIFT', 'IDA', 'BAND', 'REMEMBER', 'GARDEN', 'WRONG', 'PERCENT', 'NEWS', 'TRUCK', 'MOP', 'CREEK', 'STUDENTS', 'LEDGE', 'CALM', 'SH', 'HOLD', 'ARRIVED', 'RAN', 'FORM', 'WIRE', 'PALACE', 'DROP', 'TONE', 'MINI', 'CONTINUED', 'STATEMENT', 'L', 'CABLE', 'SCRATCH', 'HEARD', 'FRESH', 'PUNCTURE', 'FINGER', 'WELL', 'OK', 'DRESS', 'THREAT', 'MAXIMUM', 'CLUB', 'SOUL', 'JULY', 'BLAZE', 'SAD', 'HAZE', 'AHEAD', 'PRAY', 'FARMERS', 'WAGON', 'NONE', 'DEVELOPED', 'TESLA', 'MASTER', 'CHIEF', 'SLOWER', 'IRON', 'BEG', 'ROBERT', 'GOT', '9', 'POUNDS', 'EUROPE', 'UPON', 'NANA', 'DATE', 'SWIM', 'LIST', 'JANUARY', 'SLAIN', 'I', 'BAIL', 'FOREIGN', 'WINDOW', 'PAGE', 'PEOPLE', 'EIGHTY', 'UNHOLY', 'MONUMENT', 'CRAYON', 'STRONG', 'LEAVEN', 'CALL', 'SEVERAL', 'HOBBLE', 'AROUND', 'RAISED', 'FOREVER', 'WINGS', 'PAINT', 'DRIVE', 'CUBE', 'MIND', 'CONSTANT', 'STARVE', 'KNOWN', 'BREAKER', 'SCORE', 'HEALER', 'AMERICAN', 'PULLED', 'FIND', 'WEEPS', 'OI', 'DISTURB', 'THOUGHT', 'MATTER', 'CLOUD', 'SOON', 'JUDGE', 'BLACK', 'SACRIFICE', 'GUY', 'AGRESSION', 'POWER', 'FAR', 'VOWEL', 'NOISE', 'DETAILS', 'TERMS', 'MAD', 'CHEST', 'SLIGHT', 'INTERRUPT', 'BEFORE TIME', 'ROADWAY', 'GOOD', 'FEELING', 'PLANTS', 'ESPECIALLY', 'UP', 'NAIL', 'DASH', 'SURPRISE', 'LISA', 'CATCH', 'SHOWN', 'HURT', 'BACON', 'RELEASE', 'GAG', 'WRENCH', 'PENDANT', 'EGGS', 'TRIP', 'MONTH', 'CRASH', 'STRETCHED', 'LEATHER', 'CAKE', 'BASEMENT', 'HISTORY', 'ARMS', 'RAIN', 'WEAR', 'OFF', 'DISK', 'DRIFT', 'TOGETHER', 'MILK', 'CONSOLE', 'STARS', 'KNOT', 'BRAVE', 'SCIENCE', 'HEAD', 'AMELINE', 'PUDDLE', 'FILTER', 'WED', 'OFTEN', 'DISREGARD', 'THOSE', 'MATERIAL', 'CLOSET', 'SON', 'JOKE', 'BISHOP', 'SACRA RES', 'GUESS', 'AGO', 'POVERTY', 'FAMOUS', 'VOICE', 'NOD', 'DESK', 'COLD', 'M', 'CHEAT', 'SLAVE', 'INTEREST', 'BEER', 'RIVER', 'GONE', '5', 'PLANET', 'ERASE', 'UNLOCK', 'MYSELF', 'DARK', 'SURFACE', 'LINGER', 'CASTLE', 'SHOW', 'HUNTING', 'BABY', 'REGION', 'FUZZY', 'WOW', 'VAN', 'EERIE', 'TRIED', 'MONITOR', 'COW', 'STRENGTH', 'LEARN', 'CARPET', 'SET', 'HIPID HOP', 'AREA', 'RAID', 'FOR ME', 'WIN', 'PACE', 'EASY', 'TO', 'MIKE', 'CONGRUISM', 'STAND', 'KNIFE', 'BRANCHES', 'SCARED', 'REMOTE', 'AMBITION', 'PSYCHIC', 'FILE', 'NINE', 'DESCRIBE', 'TELEPATHY', 'THIS', 'MESSENGER', 'CLOISTER', 'SOMETHING', 'JOHNNY', 'BIRDS', 'ANIMAL', 'GROUP', 'AGE', 'PROP', 'FAME', 'VIOLENT', 'NO', 'DESIGN', 'TEMPERATURE', 'LUST', 'CHART', 'SOLID', 'INTENT', 'BED', 'RING', 'GOD', '3', 'PLAN', 'EQUATION', 'VERY', 'MUSTARD', 'DAN', 'SURE', 'SNAP', 'CASKET', 'SHOVE', 'HUNT', 'AXE', 'REEL', 'FUNERAL', 'WOUND', 'PEACE', 'EDISON', 'TRIANGLE', 'MONEY', 'COVER', 'STREAM', 'LEADER', 'BUY', 'SEPTEMEBR', 'HIM', 'AQUA', 'RADIO', 'FOOT', 'WILL', 'OXYGEN', 'MOST', 'TIP', 'MIDDLE', 'CONDITIONS', 'STAIR', 'KNEE', 'BRACELET', 'SCAN', 'HAUNTING', 'AM NOT', 'PROVIDENCE', 'FIGHT', 'WE', 'TOTAL', 'DISEASE', 'THIRTEEN', 'MASON', 'CLOCK', 'SOME', 'JOG', 'BIND', 'RUST', 'GRIND', 'AGAIN', 'POTENTIAL', 'FALL', 'VINEGAR', 'CYCLE', 'SUNSET', 'LIFT', 'LUCK', 'CHARACTER', 'SKIP', 'INSIDE', 'BECKON', 'RIDE', 'PRESIDENTS', '1', 'PLAIN', 'EQUAL', 'UNDERLINE', 'MUSIC', 'DADDY', 'SUPPLY', 'LIKE', 'CARRY', 'SHOULDER', 'HUNDRED', 'AWAY', 'RECUSE', 'FULL', 'WORRY', 'PAULA', 'ED', 'TREMOR', 'MONACHI', 'COURSE', 'STRAIGHT', 'LEAD', 'IF', 'SENTENCE', 'HIKE', 'APPLET', 'RACE', 'FOLLOW', 'WIFE', 'OVER', 'DRAG', 'TINA', 'METAPHYSICS', 'COMPUTER', 'STAB', 'KITE', 'BOY', 'SAY', 'HAT', 'ALWAYS', 'PROTON', 'FIFTY', 'WAVES', 'OCEAN', 'DISCERNMENT', 'THIRD', 'MARRY', 'CLIMBED', 'SOLSTICE', 'JO', 'BILL', 'RUNNING', 'GREGG', 'AFTER', 'POSSIBLY', 'FADE', 'VIEW', 'NIGHT TIME', 'MAZE', 'TEASE', 'LOW', 'CHANNELING', 'SKILL', 'INNER', 'BECAME', 'RHYTHM', 'GLASS', 'ADJECTIVE', 'PLACE', 'ENTERED', 'UNCLEAR', 'MUSCLE', 'STOP', 'LATER', 'BURNING', 'CERTAIN', 'SHOT', 'HUGE', 'AVERAGE', 'RECORD', 'FRONT', 'EVER', 'PATTERN', 'ENERGY', 'TRAVERSE', 'MOMMA', 'COUNTER', 'STORM', 'LAW', 'BUSH', 'SENSE', 'HOUR', 'APPETITE', 'R', 'FOG', 'WICKED', 'OUT', 'DOUBT', 'TIMID', 'MOAN', 'COMPLETE', 'SQUARE', 'KING', 'BOTTOM', 'SAVE', 'HAS', 'ALTER', 'QUICK', 'FIELD', 'WATERS', 'OBJECT', 'DIRTY', 'THINGS', 'MARK', 'CLEAR', 'SPIRIT', 'JEWELRY', 'HEART', 'RULE', 'GREEK', 'AFRAID', 'POSITION', 'FACTORIES', 'WAS', 'NICKEL', 'DENSITY', 'TEAM', 'LOVE', 'CHANCE', 'SIXTY', 'INFORMED', 'BEAST', 'REVOKED', 'GIVE', 'ZINC', 'PINKIE', 'ENJOY', 'U', 'MURDER', 'CUT', 'CHILD', 'LIE', 'CARESS', 'SHOP', 'HOWEVER', 'AURA', 'REBECA', 'FRIGID', 'WORK', 'PASTOR', 'EASE', 'TRAPPED', 'MOLECULES', 'COULD', 'KILL', 'BOOTS', 'SANDY', 'SELL', 'HIDDEN', 'APOCALYPSE', 'QUILT', 'FOCUS', 'WHOSE', 'OUR', 'DOPE', 'TIM', 'MEND', 'COMPARE', 'SPREAD', 'KIM', 'BOTH', 'SATAN', 'HARRY', 'ALREADY', 'PROJECT', 'FEW', 'DRONE', 'NUMBERS', 'DIRECTION', 'THIN', 'MAP', 'CLEAN', 'SOLDIER', 'JESS', 'BEWARE', 'ROW', 'GREAT', 'ADULTERY', 'PORTAL', 'FACE', 'VERN', 'NICE', 'DEMAND', 'TEA', 'LOT', 'CHAIN', 'SITE', 'INDUSTRY', 'BEANS', 'AH', 'GHOST', 'Z', 'PILLOW', 'ENGLAND', 'TWO', 'MUDDY', 'CURSE', 'SUM', 'LIBERTY', 'CARDS', 'SHOES', 'HOUSE', 'AUGUST', 'REAP', 'FRIENDLY', 'WORD', 'PASSED', 'EARTH', 'TRAIN', 'MODERN', 'COUCH', 'STOOD', 'SHUTTLE', 'BUNNY', 'SEEN', 'HEY', 'ANYTHING', 'QUIET', 'FLOWERS', 'WHO', 'OREMUS', 'DONE', 'TILDE', 'MEMORY', 'COMMUNICATE', 'CALCIUM', 'BETH', 'ROSE LINE', 'GRAVE', 'HARMONIC', 'ALONG', 'PRODUCTS', 'FELT', 'WASHINGTON', 'NUMB', 'DINNER', 'THICK', 'MANUAL', 'CLASS', 'SOIL', 'JEN', 'BETTY', 'ROT', 'GRAVITY', 'ALIVE', 'PORCH', 'EYE', 'VENUS', 'THOUGH', 'DECOMPOSE', 'TASK', 'LOSS', 'CHRIS', 'SISTER', 'INDICATE', 'BE', 'RESULT', 'GEORGE', 'YOURS', 'PIECE', 'EXCEL', 'TWENTY', 'MOVIE', 'CUPCAKE', 'SUIT', 'LEVEL', 'CARBON', 'SHIRT', 'INCHES', 'ATTITUDE', 'REAL', 'PLANT', 'WOOD', 'PARTY', 'EARLY', 'TRAGIC', 'MOTHER', 'COST', 'STONE', 'LASH', 'BUILDING', 'SEEK', 'HERE', 'ANTI', 'RAW', 'FLOW', 'WHILE', 'ORB', 'DOMINATE', 'TIED', 'MEMBERS', 'COMFORT', 'STEVEN', 'KEY', 'BOOK', 'SAND', 'HAPPY', 'ALLOW', 'PROCESS', 'FELL', 'WHEAT', 'NOVEMBER', 'DIGITAL', 'THESE', 'MANIFEST', 'CLAIRVOYANT', 'SOCCER', 'SCHOOL', 'RESERVATION', 'GENDER', 'YET', 'ADD', 'POP', 'EXPLAIN', 'VAST', 'NEW MOON', 'DECIDED', 'TALL', 'LORD', 'CENTS', 'SIP', 'INDEX', 'BATTERIES', 'RESTORE', 'GENTLE', 'YOU', 'PICTURE', 'END', 'TWEAK', 'MOVE', 'LYNN', 'SUGAR', 'LET', 'CAPTAIN', 'SHINNING', 'HORSE', 'ATTACK', 'READ', 'FREEZE', 'WONDER', 'PARK', 'EACH', 'TRADE', 'MITE', 'CORNER', 'STIRRED', 'LARK', 'BUDAH', 'SEED', 'HER', 'ANSWER', 'QUESTION', 'FLOAT', 'WHETHER', 'ORACLE', 'DOLLAR', 'TIDE', 'MELINE', 'COLUMN', 'SPELL', 'KELLY', 'BOMB', 'SAME', 'HAPPENS', 'ALL RIGHT', 'PROBABLY', 'P', 'WARRIOR', 'NOTICE', 'DIG', 'THERE', 'MAN', 'CIRCLE', 'SOAK', 'JAMES', 'BEST', 'ROPE', 'GRASP', 'ACTUALLY', 'POND', 'EXIT', 'VARIOUS', 'NEVER', 'DECEMBER', 'TALK', 'LOOP', 'CENTER', 'SINGLE', 'INCREASE', 'GROUND', 'FRAME', 'WITHOUT', 'PAPPY', 'PHRASE', 'EMPTY', 'TURNING', 'MOUSE', 'CRY', 'SUDDENLY', 'LESS', 'CANNOT', 'SHEPPARD', 'HOPE', 'ATE', 'REACHED', 'FRANK', 'WOMAN', 'PARALYSIS', 'DWINDLE', 'TRACE', 'MISTAKE', 'CORE', 'STIGMATA', 'LANGUAGE', 'BROWN', 'SECTION', 'HELPFUL', 'ANNA', 'QUARTER', 'FIVE', 'WHEN', 'OPPOSITE', 'DOES', 'TICKET', 'MEDIUM', 'LEADED', 'SPECULAR', 'KATE', 'BOAT', 'SALVATION', 'HAPPEN', 'ANGER', 'PRIEST', 'FEED', 'WARP', 'NOTE', 'DIFFERENT', 'THEMSELVES', 'MAMMOTH', 'COAST', 'SNOW', 'JADE', 'BEND', 'ROOM', 'GRANDMOTHER', 'ACT', 'POLICE', 'FATAL', 'DISCOVERED', 'NERD', 'DEBRA', 'TAIL', 'LONG', 'CENSURES', 'SINCE', 'IT', 'BARRY', 'REPRESENT', 'GAVE', 'YELLOW', 'PHANTOM', 'EMBARK', 'TUNE', 'NATURAL', 'CROWD', 'SUBTRACT', 'LENGTH', 'CANDY', 'SHE', 'HONOR', 'ASTRAL', 'FIRST', 'WESTERN', 'ONE', 'DO NOT', 'DUST', 'TOWARD', 'MISSION', 'COPY', 'STUDY', 'LAMP', 'BROTHER', 'SECOND', 'HELLO', 'FRUIT', 'QUARANTINE', 'FIST', 'WISDOM', 'OPEN', 'DOCK', 'THUS', 'MEAT', 'COIN', 'SPECIAL', 'KANSAS', 'BLUE', 'SALLIES', 'HAND', 'ALIEN', 'PRETTY', 'FEAR', 'WAR', 'NOSE', 'DIED', 'THEIR', 'MALICE', 'CHOKE', 'BOX', 'JACKET', 'BELONG', 'RON', 'GRANDFATHER', 'ABYSS', 'POINT', 'EVOLUTION', 'VALLEY', 'NECK', 'DEATH', 'TABLET', 'LOCK', 'CELLS', 'SIMILAR', 'IMPORTANT', 'BARN', 'REPEATED', 'GATHER', 'YEILD', 'PET', 'ELIAS', 'TUBE', 'TEAR', 'CROSS', 'SUBJECT', 'LEMON', 'CANCER', 'SHARE', 'HOME', 'ASK', 'RATES', 'FOUR', 'WITH', 'PANTS', 'DUNE', 'CUTE', 'MIRROR', 'COOL', 'STEEL', 'LAKE', 'BROAD', 'SEA', 'HELD', 'ANGLES', 'PUT', 'WALL', 'NORMAL', 'DIABLO', 'THAN', 'THROW', 'MEAN', 'COFFEE', 'SPACE', 'JUST', 'BLOOD', 'SAINT', 'HALT', 'ALCOHOL', 'WHY', 'FATHER', 'WANT', 'NORTH', 'DICTIONARY', 'THAT', 'MALE', 'CHIMP', 'SMILE', 'ITSELF', 'BELIEVE', 'ROLL', 'GRAIN', 'ABOUT', 'PM', 'EVERYTHING', 'USUALLY', 'NEAR DEATH', 'DEAD', 'SYSTEM', 'LMAO', 'CELEBRATION', 'SIGNAL', 'RUB', 'BANSHEE', 'RENDER', 'GATE', 'YARD', 'PERIODICAL', 'ELEMENTS', 'TRY', 'MORNING', 'CRIED', 'STUNT', 'LEGION', 'CAN', 'SHALL', 'HOLLOWED', 'ASCEND', 'RASTER', 'FORWARD', 'WISHING', 'PAN', 'DRY', 'TOOLS', 'MINUTES', 'CONTROL', 'STEAM', 'LAG', 'BRING', 'SCRIPT', 'HEAVEN', 'ARMY', 'PUSH', 'FINISHED', 'WERE', 'ON', 'DIVISION', 'THROAT', 'STOOL', 'CONSONANT', 'SOUTH', 'JUNE', 'BLOCK', 'SAID', 'HALLOW', 'AIR', 'PREPARED', 'FINALLY', 'NANCY', 'DAVE', 'SWITCH', 'LISTEN', 'MAJOR', 'CHILL', 'SMALL', 'JON', 'BEHIND', 'ROCKS', 'GRAB', 'ABLE', 'PLURAL', 'NUMBER', 'USE', 'NODE', 'DAWN', 'SYMBOLS', 'LIVE', 'CAVE', 'SIGHT', 'IDEA', 'BANG', 'ROAD', 'GAS', 'WROTE', 'PERHAPS', 'ELEMENT', 'TRUST', 'MORE', 'CREMATE', 'SURGE', 'LEFT', 'CAME', 'SHADOWS', 'HOLE', 'ART', 'RANDY', 'FORMAT', 'WRECK', 'PALATINE', 'DROWN', 'TOOK', 'MINISTER', 'CONTRACT', 'STATIC', 'LABOR', 'BRIDLE', 'SCREAM', 'REALLY', 'AN', 'PURGATORY', 'FINGERS', 'WENCH', 'OLD', 'DIVIDE', 'THREE', 'MAY', 'CLUTTER', 'SOUND', 'JUMP', 'BLED', 'SADNESS', 'HAIL', 'AI', 'PRAYER', 'FAST', 'WAIT', 'NOON', 'DEVICE', 'TEST', 'MAGNET', 'KID', 'SLOWLY', 'IS', 'BEGAN', 'ROCK', 'GOUGE', 'A', 'PLAY', 'EVEN', 'UPSTAIRS', 'CRAWL', 'STRING', 'LEAVE', 'INCUBUS', 'CAUGHT', 'SIDE', 'ICE', 'BALL', 'REMAIN', 'GAME', 'WRITTEN', 'PER', 'EITHER', 'TROUBLE', 'MOON', 'CREATE', 'STRUCK', 'LED', 'CALLED', 'SEX', 'HOCKEY', 'ARREST', 'RAMP', 'FORK', 'WINTER', 'PAIR', 'MOVEMENT', 'TOMB', 'MINE', 'CONTAIN', 'STATE', 'KORAN', 'BREAKFAST', 'SCRAPE', 'HEAR', 'AMONG', 'PULSE', 'FINE', 'WEIGHT', 'OIL', 'DIVE', 'THOUSAND', 'MATTRESS', 'CLOUDED', 'SORRY', 'JUDGMENT', 'BLANKET', 'SACRILEGE', 'H', 'FLOOR', 'PRACTICE', 'FARM', 'W', 'NONA', 'DETERMINE', 'TERRY', 'MADE', 'CHICKEN', 'SLIP', 'INTO', 'BEFRIEND', 'ROBB', 'GOODBYE', '8', 'PLASTIC', 'ETCH', 'UPHOLD', 'NAME', 'DATA', 'SWELL', 'LISP', 'CATHY', 'BLOW', 'HUSBAND', 'BAD', 'RELICS', 'GAGE', 'WRITE', 'PENNY', 'EIGHT', 'TROLL', 'MONTHS', 'STAR', 'KNIT', 'BRASS', 'AT', 'SEVENTY', 'HIT', 'AWKWARD', 'RAISE', 'FOREST', 'WINDS', 'PAIN', 'DRINK', 'TOLD', 'MILLION', 'COUSIN', 'START', 'KNOW', 'BREAK', 'SCIENTISTS', 'HEAD STONE', 'AMERICA', 'PULL', 'FOOD', 'WEEK', 'OH', 'DISTANCE', 'CORN', 'MATRIX', 'CLOTHES', 'SONG', 'KITTY', 'BIT', 'SACRED', 'GUN', 'AGREED', 'POWDER', 'FAN', 'VOID', 'OCTOBER', 'DESOLATE', 'TENT', 'MACHINE', 'CHECK', 'SLEEP', 'INTERN', 'BEFORE', 'RUSS', 'GONG', '6', 'WARRANT', 'ERROR', 'UNTIL', 'N', 'DARKNESS', 'TEEN', 'LIQUID', 'CAT', 'SHOWERS', 'HURRY', 'BACK', 'RELAX', 'G', 'EXCEPT', 'PENCIL', 'EFFECT', 'TRILLION', 'MONO', 'COWS', 'STREP', 'LEAST', 'CAGE', 'SETTLED', 'HIS', 'ARM', 'RAIL', 'FORCE', 'WIND', 'PACK', 'DRESSER', 'TODAY', 'MILE', 'CONSIDER', 'JOHN', 'BIRD', 'RUSTS', 'QUANTUM', 'HE', 'AMBULATORY', 'PUCK', 'FILLED', 'WEATHER', 'OFFICE', 'DISPOSE', 'THOMAS', 'MATCH', 'CLOSE', 'SOMETIME', 'JOINED', 'BIRTH', 'SACK', 'GROW', 'AGENT', 'POUT', 'FAMILY', 'VISIT', 'NOAH', 'DESIGNATE', 'TEN', 'SPECTER', 'CHAT', 'SLAM', 'INTENTION', 'BEEN', 'RISE', 'GOLD', '4', 'PLANE', 'EQUATOR', 'UNIT', 'MY', 'DANCE', 'SURELY', 'LINE', 'CAST', 'SHOVEL', 'HUNTED', 'B', 'REFICIO', 'FURY', 'WOVEN', 'PEGGY', 'EDNA', 'TRICK', 'MONICA', 'COVERED', 'STREET', 'LEAN', 'BY', 'SERVE', 'HIMSELF', 'ARE', 'RAGE', 'FOR', 'WILLIAM', 'TUG', 'DRAWING', 'TISSUE', 'MIGHT', 'CONFESS', 'STALK', 'KNEW', 'BRAD', 'SCARE', 'HAVE', 'AMANDA', 'PROVIDER', 'FIGURE', 'WEAPON', 'OF', 'DISEMBODIED', 'THIRTY', 'MASS', 'CLOCKWISE', 'SOMEONE', 'BECAUSE', 'RICH', 'GLORY', 'AGAINST', 'POUND', 'FALLS', 'VIOLENCE', 'NINETY', 'DESERT', 'TELL', 'LUNCH', 'CHARLES', 'SKY', 'INSTEAD', 'BECOME', 'RIGHT', 'GO', '2', 'PLAINS', 'EQUATE', 'UNDERSTAND', 'MUST', 'DAM', 'SUPPOSE', 'LIMIT', 'CASE', 'SHOUTED', 'HUNG', 'BEAR', 'RED', 'FUN', 'WOULD', 'PAY', 'EDGE', 'TRIAL', 'MONDAY', 'CURT', 'STRANGE', 'SILENT', 'BUTTON', 'SEPARATE', 'HILL', 'APRIL', 'RADICAL', 'FRIENDS', 'WILD', 'OWN', 'DRANK', 'TINY', 'METHOD', 'CONCENTRATE', 'STABBED', 'LATE', 'BRACE', 'SCALE', 'HATE', 'AM', 'PROVIDE', 'FIG', 'WAY', 'OTHER', 'MIRA', 'THIRST', 'MARS', 'CLIP', 'SOLUTION', 'JOB', 'BILLION', 'SAT', 'GREW', 'AFTERLIFE', 'POST', 'FAITH', 'VILLAGE', 'NIGHTMARE', 'DERRICK', 'THIGH', 'LOWER', 'CHANT', 'SKIN', 'INSECTS', 'RECEIVED', 'FROM', 'WORKERS', '0')

#set up the i2c bus for the screen
i2c = busio.I2C(scl=board.GP17, sda=board.GP16)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

#the audio system
audio = audiobusio.I2SOut(board.GP11, board.GP12, board.GP13)

#name the source of all chaos in the universe
#or the analog pin connected to our circuit - whichever is easier
chaos = AnalogIn(board.A2)

#display items
headline = 'Not an Ovulus'
wordQueue = ['','','','','']
timeBetween = 0.0
heartbeat = False; 

def bring_the_noise():
    """
    YEAHHHHH BOY! an excuse to slip in a pop culture reference.
    Sample the analog pin
    """
    return chaos.value

def bring_some_chaos(): 
    """
    get a value from the noise source.  
    It needs to be different from the last value and we sleep if it's not
    """
    global old_noise 
    noise = bring_the_noise()
    if noise != old_noise:
        old_noise = noise
        return noise
    else:
        time.sleep(0.0001)
        return bring_some_chaos()

def rand_bits(count):
    """
    get a random number of bits
    """
    number = 0
    bitCount = 0
    while bitCount < count:
        noise = bring_some_chaos()

        if noise > mean:
            bitMask = (1 << bitCount)
            number += (1 << bitCount)

        bitCount+=1

    return number 

def rand_ubyte():
    """
    get a random byte from our source of noise.  This is the heart of our RNG
    """
    return rand_bits(8)
    
def rand_word_from_list():
    """
    get a random word using the quantum noise
    """
    index = rand_bits(11) #2048 possible words so we need 11 bits of noise
    return wordlist[index]
    
def update_screen():
    oled.fill(0)
    oled.text(headline,  0, 0,1)
    
    step = 10
    for word in wordQueue:
        oled.text(word,  0, step, 1)
        step+=8
    
    oled.text(f"{timeBetween:.2f}s",  0, 55, 1)
    if heartbeat == True:
        oled.text('#', 120,55, 1)
        
    oled.show()
    
def addWord(word):
    wordQueue[4] = wordQueue[3]
    wordQueue[3] = wordQueue[2]
    wordQueue[2] = wordQueue[1]
    wordQueue[1] = wordQueue[0]
    wordQueue[0] = word
    
def run_session():
    """
    Continuously picks a random 8-bit number, compares it with the next random 8-bit number,
    Repeats this process every tenth of a second.
    This is the 'heart' of the machine.  It gives it a similar timing to the random events seen on Ovulus devices
    """
    global timeBetween, heartbeat
    
    last_match_time = time.time()

    target = rand_ubyte()
    while True:
        update_screen()
        
        num = rand_ubyte()

        # Check if they match
        if num == target:
            current_time = time.time()
            timeBetween = current_time - last_match_time
            last_match_time = current_time
            target = rand_ubyte()
            
            #push a new word to the list
            word = rand_word_from_list()
            addWord(word)
            #make sure we can see it
            update_screen()
            
            try:
                #play the sample
                mp3 = audiomp3.MP3Decoder(open("/audio/sample_"+word+".mp3", "rb"))
                
                #now we only have the first 858 words installed
                audio.play(mp3)
                while audio.playing:
                    pass
            except:
                print ("for the want of a pr, https://github.com/adafruit/circuitpython/pull/7675")
                
            print (word)

        # Wait
        time.sleep(0.001*rand_ubyte()) 
        heartbeat =  not heartbeat
        
#set the scene
oled.fill(0)
oled.text(headline,  0, 0,1)
oled.text('Quantum Noise Warmup',  0, 10,1)
oled.show()

tests = []
#collect loops*size samples of the chaos to calculate the mean average
while len(tests) < loops:
    data = []
    while len(data) < size:
        data.append(bring_some_chaos())

    tests.append(sum(data) / len(data))

    #show progress on the screen
    oled.text('*', (len(tests)*8)-10, 20, 1)
    oled.show()

mean = sum(tests) / len(tests)
print (str(mean)) 

#starts the program loop
run_session()