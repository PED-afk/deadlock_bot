

import re
import cmudict


from debug import printLog
from constants import LOBBY_CODE_FUN_MESSAGES
from own_utils import chooseFaceFromCategory
from classes.bot_faces import Faces



BANNED_WORDS=set()
WORD_LIST=set(word.lower() for word in cmudict.words())


def edit_distance(a, b):
    """Levenshtein edit distance."""
    dp=[[0] * (len(b)+1) for _ in range(len(a)+1)]

    for i in range(len(a)+1):
        dp[i][0]=i

    for j in range(len(b)+1):
        dp[0][j]=j

    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            cost=0 if a[i-1]==b[j-1] else 1

            dp[i][j]=min(
                dp[i-1][j]+1,       # deletion
                dp[i][j-1]+1,       # insertion
                dp[i-1][j-1]+cost # substitution
            )

    return dp[-1][-1]


def has_number_sequence(s):
    """Returns True if 3+ digits ascend or descend consecutively."""
    digits=[int(c) for c in s if c.isdigit()]

    for i in range(len(digits)-2):
        if (digits[i+1]==digits[i]+1 and digits[i+2]==digits[i]+2):
            return True,1

        if (digits[i+1]==digits[i]-1 and digits[i+2]==digits[i]-2):
            return True,-1

    return False,0


def word_match(s):
    """Checks exact 3-letter words and approximate 4/5-letter words."""
    s=s.lower()

    for word in WORD_LIST:
        if word in BANNED_WORDS:
            continue
        # 3-letter words must match exactly
        if len(word)==3 and s==word:
            return word,0

        # 4 or 5 letter words can have one character difference
        if len(word) in (4, 5):
            dist=edit_distance(s, word)
            if dist<=1:
                return word,dist

    return None,0

def isValidCode(s)->bool:
    s=s.lower()
    if not re.fullmatch(r"[a-z0-9]{5}", s):
        return False
    return True
    
def analyze_string(s):
    s=s.lower()

    #Validate input
    if isValidCode(s):
        printLog("warning","Invalid input: must be exactly 5 letters/numbers.")
        return -1

    #Count repeated characters
    max_repeat=max(s.count(c) for c in set(s))
    repeated=(c for c in set(s) if s.count(c)==max_repeat)

    #Find longest consecutive numeric sequence
    digits=[int(c) for c in s if c.isdigit()]
    max_sequence=1
    for i in range(len(digits)-1):
        if abs(digits[i+1]-digits[i])==1:
            max_sequence+=1
        else:
            max_sequence=1

    # WORD priority: must be at least as long as the other match counts
    matched_word=word_match(s)
    if matched_word:
        word_length=len(matched_word)
        if word_length>=max_repeat and word_length>=max_sequence:
            return LOBBY_CODE_FUN_MESSAGES.START+LOBBY_CODE_FUN_MESSAGES.WORD.replace("#",str(word_length)).replace("$",matched_word)+LOBBY_CODE_FUN_MESSAGES.END.replace("÷",chooseFaceFromCategory(Faces.wink))

    # Number sequence takes priority over repeated characters
    hns,dir=has_number_sequence(s)
    if hns:
        return LOBBY_CODE_FUN_MESSAGES.START+LOBBY_CODE_FUN_MESSAGES.ORDER.replace("#",("ascending" if dir==1 else "descending"))+LOBBY_CODE_FUN_MESSAGES.END.replace("÷",chooseFaceFromCategory(Faces.wink))

    # 3+ repeated characters
    if max_repeat>=3:
        return LOBBY_CODE_FUN_MESSAGES.START+LOBBY_CODE_FUN_MESSAGES.REPEATS.replace("#",max_repeat)+LOBBY_CODE_FUN_MESSAGES.END.replace("÷",chooseFaceFromCategory(Faces.wink))
        return "Repeated characters"

    return None


