import random

RUN_STRINGS = (
    "Where do you think you're going?",
    "Huh? what? did they get away?",
    "ZZzzZZzz... Huh? what? oh, just them again, nevermind.",
    "Get back here!",
    "Not so fast...",
    "Look out for the wall!",
    "Don't leave me alone with them!!",
    "You run, you die.",
    "Jokes on you, I'm everywhere",
    "You're gonna regret that...",
    "You could also try /kickme, I hear that's fun.",
    "Go bother someone else, no-one here cares.",
    "You can run, but you can't hide.",
    "Is that all you've got?",
    "I'm behind you...",
    "You've got company!",
    "We can do this the easy way, or the hard way.",
    "You just don't get it, do you?",
    "Yeah, you better run!",
    "Please, remind me how much I care?",
    "I'd run faster if I were you.",
    "That's definitely the droid we're looking for.",
    "May the odds be ever in your favour.",
    "Famous last words.",
    "And they disappeared forever, never to be seen again.",
    '"Oh, look at me! I\'m so cool, I can run from a bot!" - this person',
    "Yeah yeah, just tap /kickme already.",
    "Here, take this ring and head to Mordor while you're at it.",
    "Legend has it, they're still running...",
    "Unlike Harry Potter, your parents can't protect you from me.",
    "Fear leads to anger. Anger leads to hate. Hate leads to suffering. If you keep running in fear, you might "
    "be the next Vader.",
    "Multiple calculations later, I have decided my interest in your shenanigans is exactly 0.",
    "Legend has it, they're still running.",
    "Keep it up, not sure we want you here anyway.",
    "You're a wiza- Oh. Wait. You're not Harry, keep moving.",
    "NO RUNNING IN THE HALLWAYS!",
    "Hasta la vista, baby.",
    "Who let the dogs out?",
    "It's funny, because no one cares.",
    "Ah, what a waste. I liked that one.",
    "Frankly, my dear, I don't give a damn.",
    "My milkshake brings all the boys to yard... So run faster!",
    "You can't HANDLE the truth!",
    "A long time ago, in a galaxy far far away... Someone would've cared about that. Not anymore though.",
    "Hey, look at them! They're running from the inevitable banhammer... Cute.",
    "Han shot first. So will I.",
    "What are you running after, a white rabbit?",
    "As The Doctor would say... RUN!",
)

SLAP_BOT_TEMPLATES = (
    "Slap me one more time and I'll mute you!",
    "Stop slapping me.........",
    [
        "I am muting you for a minute.",  # normal reply
        "Stop slapping me just because I can't mute you......",  # reply to admin
        "tmute",  # command
    ],
)

SLAP_TEMPLATES = (
    "{user2} was shot by {user1}.",
    "{user2} walked into a cactus while trying to escape {user1}.",
    "{user2} drowned whilst trying to escape {user1}.",
    "{user2} fell into a patch of cacti.",
    "{user2} went up in flames.",
    "{user2} burned to death.",
    "{user2} was burnt to a crisp whilst fighting {user1}.",
    "{user2} was struck by lightning.",
    "{user2} was slain by {user1}.",
    "{user2} was killed by magic.",
    "{user2} starved to death.",
    "{user2} fell out of the world.",
    "{user2} was knocked into the void by {user1}.",
    "{user2}'s bones are scraped clean by the desolate wind.",
    "{user2} fainted.",
    "{user2} is out of usable Pokemon! {user2} whited out!.",
    "{user2} is out of usable Pokemon! {user2} blacked out!.",
    "{user2} says goodbye to this cruel world.",
    "{user2} got rekt.",
    "{user2} was sawn in half by {user1}.",
    "{user2}'s melon was split by {user1}.",
    "{user2} was sliced and diced by {user1}.",
    "{user2}'s death put another notch in {user1}'s axe.",
    "{user2} died from {user1}'s mysterious tropical disease.",
    "{user2} played hot-potato with a grenade.",
    "{user2} was knifed by {user1}.",
    "{user2} ate a grenade.",
    "{user2} is what's for dinner!",
    "{user2} was terminated by {user1}.",
    "{user2} was shot before being thrown out of a plane.",
    "{user2} has encountered an error.",
    "{user2} died and reincarnated as a goat.",
    "{user1} threw {user2} off a building.",
    "{user2} got a premature burial.",
    "{user1} spammed {user2}'s email.",
    "{user1} hit {user2} with a small, interstellar spaceship.",
    "{user1} put {user2} in check-mate.",
    "{user1} RSA-encrypted {user2} and deleted the private key.",
    "{user1} put {user2} in the friendzone.",
    "{user1} slaps {user2} with a DMCA takedown request!",
    "{user2} died of hospital gangrene.",
    "{user2} got a house call from Doctor {user1}.",
    "{user1} beheaded {user2}.",
    "{user2} got stoned...by an angry mob.",
    "{user1} sued the pants off {user2}.",
    "{user2} was one-hit KO'd by {user1}.",
    "{user1} sent {user2} down the memory hole.",
    "{user2} was a mistake. - '{user1}' ",
    "{user1} checkmated {user2} in two moves.",
    "{user2} was made redundant.",
    "{user1} {hits} {user2} with a bat!.",
    "{user1} {hits} {user2} with a Taijutsu Kick!.",
    "{user1} {hits} {user2} with X-Gloves!.",
    "{user1} {hits} {user2} with a Jet Punch!.",
    "{user1} {hits} {user2} with a Jet Pistol!.",
    "{user1} {hits} {user2} with a United States of Smash!.",
    "{user1} {hits} {user2} with a Detroit Smash!.",
    "{user1} {hits} {user2} with a Texas Smash!.",
    "{user1} {hits} {user2} with a California Smash!.",
    "{user1} {hits} {user2} with a New Hampshire Smash!.",
    "{user1} {hits} {user2} with a Missouri Smash!.",
    "{user1} {hits} {user2} with a Carolina Smash!.",
    "{user1} {hits} {user2} with a King Kong Gun!.",
    "{user1} {hits} {user2} with a baseball bat - metal one.!.",
    "*Serious punches {user2}*.",
    "*Normal punches {user2}*.",
    "*Consecutive Normal punches {user2}*.",
    "*Two Handed Consecutive Normal Punches {user2}*.",
    "*Ignores {user2} to let them die of embarassment*.",
    "*points at {user2}* What's with this sassy... lost child?.",
    "*Hits {user2} with a Fire Tornado*.",
    "{user1} pokes {user2} in the eye !",
    "{user1} pokes {user2} on the sides!",
    "{user1} pokes {user2}!",
    "{user1} pokes {user2} with a needle!",
    "{user1} pokes {user2} with a pen!",
    "{user1} pokes {user2} with a stun gun!",
    "{user2} is secretly a Furry!.",
    "Hey Everybody! {user1} is asking me to be mean!",
    "( ･_･)ﾉ⌒●~* (･.･;) <-{user2}",
    "Take this {user2}\n(ﾉﾟДﾟ)ﾉ ))))●~* ",
    "Here {user2} hold this\n(｀・ω・)つ ●~＊",
    "( ・_・)ノΞ●~*  {user2},Shinaeeeee!!.",
    "( ・∀・)ｒ鹵~<≪巛;ﾟДﾟ)ﾉ\n*Bug sprays {user2}*.",
    "( ﾟДﾟ)ﾉ占~<巛巛巛.\n-{user2} You pest!",
    "( う-´)づ︻╦̵̵̿╤── \(˚☐˚”)/ {user2}.",
    "{user1} {hits} {user2} with a {item}.",
    "{user1} {hits} {user2} in the face with a {item}.",
    "{user1} {hits} {user2} around a bit with a {item}.",
    "{user1} {throws} a {item} at {user2}.",
    "{user1} grabs a {item} and {throws} it at {user2}'s face.",
    "{user1} launches a {item} in {user2}'s general direction.",
    "{user1} starts slapping {user2} silly with a {item}.",
    "{user1} pins {user2} down and repeatedly {hits} them with a {item}.",
    "{user1} grabs up a {item} and {hits} {user2} with it.",
    "{user1} ties {user2} to a chair and {throws} a {item} at them.",
    "{user1} gave a friendly push to help {user2} learn to swim in lava.",
    "{user1} bullied {user2}.",
    "Nyaan ate {user2}'s leg. *nomnomnom*",
    "{user1} {throws} a master ball at {user2}, resistance is futile.",
    "{user1} hits {user2} with an action beam...bbbbbb (ง・ω・)ง ====*",
    "{user1} ara ara's {user2}.",
    "{user1} ora ora's {user2}.",
    "{user1} muda muda's {user2}.",
    "{user2} was turned into a Jojo reference!",
    "{user1} hits {user2} with {item}.",
    "Round 2!..Ready? .. FIGHT!!",
)

PING_STRING = (
    "PONG!!",
    "I am here!",
)



FRUIT = (
   "Apple",
   "Apricot",
   "Avocado",
   "Banana",
   "Bilberry",
   "Blackberry",
   "Blueberry",
   "Blackcurrant",
   "Boysenberry",
   "Currant",
   "Cherry",
   "Cherimoya",
   "Chico fruit",
   "Cloudberry",
   "Coconut",
   "Cranberry",
   "Cucumber",
   "Custard apple",
   "Damson",
   "Date",
   "Dragonfruit",
   "Durian",
   "Elderberry",
   "Feijoa",
   "Fig",
   "Goji berry",
   "Gooseberry",
   "Grape",
   "Raisin",
   "Grapefruit",
   "Guava",
   "Honeyberry",
   "Huckleberry",
   "Jabuticaba",
   "Jackfruit",
   "Jambul",
   "Jujube",
   "Juniper berry",
   "Kiwano",
   "Kiwifruit",
   "Kumquat",
   "Lemon",
   "Lime",
   "Loquat",
   "Longan",
   "Lychee",
   "Mango",
   "Mangosteen",
   "Marionberry",
   "Melon",
   "Cantaloupe",
   "Watermelon",
   "Miracle fruit",
   "Mulberry",
   "Nectarine",
   "Nance",
   "Orange",
   "Olive",
   "Blood orange",
   "Clementine",
   "Mandarine",
   "Tangerine",
   "Papaya",
   "Passionfruit",
   "Peach",
   "Pear",
   "Persimmon",
   "Physalis",
   "Plantain",
   "Plum",
   "Prune",
   "Pineapple",
   "Plumcot",
   "Pomegranate",
   "Pomelo",
   "Purple mangosteen",
   "Quince",
   "Raspberry",
   "Salmonberry",
   "Rambutan",
   "Redcurrant",
   "Salal berry",
   "Salak",
   "Satsuma",
   "Soursop",
   "Star fruit",
   "Solanum quitoense",
   "Strawberry",
   "Tamarillo",
   "Tamarind",
   "Ugli fruit",
   "Yuzu"
)

ITEMS = (
    "cast iron skillet",
    "angry meow",
    "cricket bat",
    "wooden cane",
    "shovel",
    "toaster",
    "book",
    "laptop",
    "rubber chicken",
    "spiked bat",
    "heavy rock",
    "chunk of dirt",
    "ton of bricks",
    "rasengan",
    "spirit bomb",
    "100-Type Guanyin Bodhisattva",
    "rasenshuriken",
    "Murasame",
    "ban",
    "chunchunmaru",
    "Kubikiribōchō",
    "rasengan",
    "spherical flying kat",
    random.choice(FRUIT)
)

THROW = (
    "throws",
    "flings",
    "chucks",
    "hurls",
)

HIT = (
    "hits",
    "whacks",
    "slaps",
    "smacks",
    "bashes",
    "pats",
)

ABUSE_STRINGS = (
    "Fuck off",
    "Stfu go fuck yourself",
    "Ur mum gey",
    "Ur dad lesbo",
    "Bsdk",
    "Nigga",
    "Ur granny tranny",
    "you noob",
    "Relax your Rear,ders nothing to fear,The Rape train is finally here",
    "Stfu bc",
    "Stfu and Gtfo U nub",
    "GTFO bsdk",
    "CUnt",
    " Gay is here",
    "Ur dad gey bc ",
)

DECIDE = ("Yes.", "NoU.", "Maybe.")

SHGS2 = (
    "(^_^)",
    "(^o^)",
    "(^^)/",
    "(^^)v",
    "(・∀・)",
    "(^_-)",
    "(^。^)",
    "(^o^;",
    "(^.^;",
    "(^^ゞ",
    "(･ัω･ั)",
    "( ･ั﹏･ั)"
)


ANIME_VILEN = (
    "Broly", #Dragon Ball
    "Kaguya Otsutsuki", #Naruto
    "Cowboy Vicious", 
    "Team Rocket", #pokemone
    "Gendo Akari", 
    "Johan Liebert",
    "Frieza", #Dragon Ball
    "Beast Titan", #ATO - Attack On Titan
    "Kenny", #ATO
    "Annie", #ATO
    "Reiner", #ATO
    "Cart Titan", #ATO
    "Mosquito Girl", #OPM - One Punch Man
    "Deep Sea King", #OPM
    "Garou", #OPM
    "Boros", #OPM
)

#taken from @saitamarobot // edited by @imDivu

#welcome msg
WEL_MSG = (
    "{first} Is Here!",  #Discord welcome messages copied
    "Ready Player {first}",
    "Genos, {first} Is Here.",
    "A Wild {first} Appeared.",
    "{first} Came In Like A Lion!",
    "{first} Has Joined Your Party.",
    "{first} Just Joined. Can I Get A Heal?",
    "{first} Just Joined The Chat - " + random.choice(SHGS2),
    "{first} Just Joined. Everyone, Look Busy!",
    "Welcome, {first}. Stay Awhile And Listen.",
    "Welcome, {first}. We Were Expecting You " + random.choice(SHGS2),
    "Welcome, {first}. We Hope You Brought " + random.choice(FRUIT),
    "Welcome, {first}. Leave Your Weapons By The Door.",
    "Swoooosh...... \n{first} Just Landed.",
    "Brace Yourselves. {first} Just Joined The Chat.",
    "{first} Just Joined. Hide Your " + random.choice(FRUIT) + "s.",
    "{first} Just Arrived. Seems OP - Please Nerf.",
    "{first} Just Slid Into The Chat.",
    "A {first} Has Spawned In The Chat.",
    "Big {first} Showed Up!",
    "Where’s {first}? In The Chat!",
    "{first} Hopped Into The Chat. Kangaroo!!",
    "{first} Just Showed Up. Hold My Beer.",
    "Challenger Approaching! {first} Has Appeared!",
    "It's A Bird! It's A Plane! Nevermind, It's Just {first}.",
    "It's {first}! Praise The Sun! \o/",
    "Never Gonna Give {first} Up. Never Gonna Let {first} Down.",
    "Ha! {first} has joined! You Activated My Trap Card!",
    "Hey! Listen! {first} Has Joined!",
    "We've Been Expecting You {first}",
    "It's Dangerous To Go Alone, Take {first}!",
    "{first} Has Joined The Chat! It's Super Effective!",
    "Cheers, Love! {first} Is Here!",
    "{first} Is Here, As The Prophecy Foretold.",
    "{first} Has Arrived. Party's Over.",
    "{first} Is Here To Kick Butt And Chew Bubblegum. And {first} Is All Out Of Gum.",
    "Hello. Is It {first} You're Looking For?",
    "{first} Has Joined. Stay A While And Listen!",
    "Roses Are Red, Violets Are Blue, {first} Joined This Chat With You",
    "Welcome {first}, Avoid " + random.choice(("Warns", "Ban", "Punch", "Kicks")) + " If You Can!",
    "It's A " + random.choice(FRUIT) + "! It's A " + random.choice(ITEMS) + "! - Nope, Its {first}!",
    "{first} Joined! - Ok.",  #Discord welcome messages end.
    "All Hail {first}!",
    "Hi, {first}. Don't Lurk, Only Villans Do That.",
    "{first} Has Joined The Battle Bus.",
    "A New Challenger Enters!",  #Tekken
    "{first} Just Fell Into The Chat!",
    "Something Just Fell From The Sky! \nOh.., Its {first}.",
    "{first} Just Teleported Into The Chat!",
    "Hi, {first}, Show Me Your Hunter License!",  #Hunter Hunter
    "I'm Looking For Garo, Oh Wait Nvm It's {first}.",  #One Punch man s2
    "Welcome {first}, Leaving Is Not An Option!",
    "Run Forest! ..I Mean...{first}.",
    "{first} - Do 100 Push-ups, 100 Sit-ups, 100 Squats, and 10km Running EVERY SINGLE DAY!!!",  #One Punch ma
    "Huh?\nDid Someone With The + random.choice(ANIME_VILEN) + Just Join?\nOh Wait, It's Just {first}.",  #One Punch ma 
    "Hey, {first}, Ever Heard The King Engine?",  #One Punch ma
    "Hey, {first}, Empty Your Pockets.",
    "Hey, {first}!, Are You Strong?",
    "Call The Avengers! - {first} Just Joined The Chat.",
    "{first} Joined. You Must Construct Additional Pylons.", 
    "Ermagherd. {first} Is Here.",
    "Come For The Snail Racing, Stay For The Chimichangas!",
    "Who Needs Google? You're Everything We Were Searching For.",
    "This Place Must Have Free WiFi, Cause I'm Feeling A Connection.",
    "Speak Friend And Enter.",
    "Welcome You Are", 
    "Hey {first}, \nDon't Forget To /sanitize Your Self!",
    "Welcome {first}, Your Princess Is In Another Castle.",
    "Hi {first}, Welcome To The Dark Side.",
    "Hola {first}, Beware Of People With " + random.choice(ANIME_VILEN),
    "Hey {first}, We Have The " + random.choice(ITEMS) + " You Are Looking For.",
    "Hi {first}\nThis Isn't A Strange Place, This Is My Home, It's The People Who Are Strange.",
    "Oh, Hey {first} What's The Password?",
    "Hey {first}, I Know What We're Gonna Do Today",
    "{first} Just Joined, Be At Alert They Could Be A Spy.",
    "{first} Joined The Group, Read By Mark Zuckerberg, FBI and 69 others.",
    "Welcome {first}, Watch Out For Falling Monkeys.",
    "Everyone Stop What You’re Doing, We Are Now In The Presence Of {first}.",
    "Hey {first}, Do You Wanna Know How I Got These Scars?",
    "Welcome {first}, Drop Your " + random.choice(ITEMS) + "s And Proceed To The Spy Scanner.",
    "Stay Safe {first}, Keep 3 Minutes Social Distances Between Your Messages.",  #Corona memes lmao
    "You’re Here Now {first}, Resistance Is Futile",
    "{first} Just Arrived, The Force Is Strong With This One.",
    "{first} Just Joined On President’s Orders.",
    "Hi {first}, Is The Glass Half Full Or Half Empty?",
    "Yipee Kayaye {first} Arrived.",
    "I Have Traveled 8 Region With My Master, \nBut I Have Never Seen Such An Pokémon Like {first}.", #Pokémon
    "Welcome {first}, If You’re A Secret Agent Press 🅵, Otherwise Start A Conversation",
    "{first}, I Have A Feeling We’re Not In KANSAS Anymore.",
    "They May Take Our Lives, But They’ll Never Take Our {first}.",
    "Coast Is Clear! You Can Come Out Guys, It’s Just {first}.",
    "Welcome {first}, Pay No Attention To That Guy Lurking.",
    "Welcome {first}, May The Force Be With You.",
    "May the {first} Be With You.",
    "{first} Just Joined.hey, Where's Perry?",
    "{first} Just Joined. Oh, There You Are, Perry.",
    "Ladies And Gentlemen, I Give You ...  {first}.",
    "Behold My New Evil Scheme, The {first}-Inator.",
    "Ah, {first} The Platypus, You're Just In Time... To Be Trapped.",
    "*Snaps Fingers And Teleports {first} Here*",
    "{first}! What Is A Fish And A Rabbit Combined?",  #Lifereload - kaizoku member.
    "{first} Just Arrived. Diable Jamble!",  #One Piece Sanji
    "{first} Just Arrived. Aschente!",  #No Game No Life
    "{first} Say Aschente To Swear By The Pledges.",  #No Game No Life
    "{first} Just Joined. El Psy Congroo!",  #Steins Gate
    "Mele Babu Ne Thana Thaya!?",  #nibba-nibbi shit
    "Hi {first}, What Is 1000-7?",  #tokyo ghoul
    "Come.. I Don't Want To Destroy This Place",  #hunter x hunter
    "I... Am... Whitebeard!...Wait..Wrong Anime.",  #one Piece
    "Hey {first}...Have You Ever Heard These Words?",  #BNHA
    "Can't A Guy Get A Little Sleep Around Here?",  #Kamina Falls – Gurren Lagann
    "It's Time Someone Put You In Your Place, {first}.",  #Hellsing
    "Unit-01's Reactivated..",  #Neon Genesis: Evangelion
    "Prepare For Trouble....And Make It Double",  #Pokemon
    "Hey {first}, Are You Challenging Me?",  #Shaggy
    "Oh? You're Approaching Me?",  #jojo
    "{first} Just Warped Into The Group!",
    "I..It's..It's Just {first}.",
    "Sugoi, Dekai. {first} Joined!",
    "{first}, Do You Know Gods Of Death Love Apples?",  #Death Note owo
    "I'll Take A Potato Chip.... And Eat It.",  #Death Note owo
    "Oshiete Oshiete Yo Sono Shikumi Wo!",  #Tokyo Ghoul 
    "{first} Just Joined! Gear.....Second!",  #Op
    "Omae Wa Mou....Shindeiru",
    "Hey {first}, The Leaf Village Lotus Blooms Twice!",  #Naruto stuff begins from here
    "{first} Joined! Omote Renge!",
    "{first}! I, Madara! Declare You The Strongest",
    "{first}, This Time I'll Lend You My Power. ",  #Kyuubi to naruto
    "{first}, Welcome To The Hidden Leaf Village!",  # Naruto thingies end here
    "In The Jungle You Must Wait...Until The Dice Read Five Or Eight.",  #Jumanji stuff
    "Dr.{first} Famed Archeologist And International Explorer,\nWelcome To Jumanji!\nJumanji's Fate Is Up To You Now.",
    "{first}, This Will Not Be An Easy Mission - Monkeys Slow The Expedition."  #End of jumanji stuff
)
 

BYE_MSG = (
    "{first} Will Be Missed.",
    "{first} Just Went Offline.",
    "{first} Has Left The " + random.choice(("Lobby!", "Clan!", "Game!")),
    "{first} Has Fled The Area.",
    "{first} Is Out Of The Running.",
    "Nice Knowing Ya, {first}!",
    "It Was A Fun Time {first}.",
    "We Hope To See You Again Soon, {first}.",
    "I Donut Want To Say Goodbye, {first}.",
    "Goodbye {first}! Guess Who's Gonna Miss You :')",
    "Goodbye {first}! It's Gonna Be Lonely Without Ya.",
    "Please Don't Leave Me Alone In This Place, {first}!",
    "Good-Luck Finding Better Shitposters Than Us, {first}!",
    "You Know We're Gonna Miss You {first}. Right? Right? Right?",
    "Congratulations, {first}! You're Officially Free Of This Mess.",
    "{first}. You Were An Opponent Worth Fighting.",
    "You're Leaving, {first}? Yare Yare Daze.",
    "Bring Him The " + random.choice(ITEMS),
    "Go Outside!",
    "Ask Again Later",
    "Think For Yourself",
    "Question Authority",
    "You Are Worshiping A Sun God",
    "Don't Leave The House Today",
    "Give Up!",
    "Marry And Reproduce",
    "Stay Asleep",
    "Look To La Luna",
    "Steven Lives",
    "Meet Strangers Without Prejudice",
    "A Hanged Man Will Bring You No Luck Today",
    "What Do You Want To Do Today?",
    "You Are Dark Inside",
    "Tussi Ja Rhe Ho!?",
    "Have You Seen The Exit?",
    "Get A Baby Pet It Will Cheer You Up.",
    "Your Princess Is In Another Castle.",
    "You Are Playing It Wrong Give Me The Controller",
    "Trust Good People",
    "Live To Die.",
    "When Life Gives You Lemons Reroll!",
    "Well That Was Worthless",
    "It's " + random.choice(("Her", "His")) + " Choice!",
    "I Feel Asleep!",
    "May Your Troubles Be Many",
    "Your Old Life Lies In Ruin",
    "Always Look On The Bright Side",
    "It Is Dangerous To Go Alone",
    "You Will Never Be Forgiven",
    "You Have Nobody To Blame But Yourself",
    "Only A Sinner",
    "Use Bombs Wisely",
    "Nobody Knows The Troubles You Have Seen",
    "You Look Fat You Should Exercise More",
    "Follow The Zebra",
    "Why So Blue?",
    "The Devil In Disguise",
    "Always Your Head In The Clouds"
)






