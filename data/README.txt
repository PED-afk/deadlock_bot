

This was my first idea but this takes too long to find things:

if <!tipp> is used it will send a message contaning all <!tipp X> command suggestions where X is all keys in the first layer of the .json
if <!tipp X> is used it will send a message contaning all <!tipp X Y> command suggestions where Y is all keys in the X's "subs" dictionary in the .json
  if X <isCatagory> is true
  else X <tipp> is sent
<!tipp X/Y/Z> is the same (categories are connected with '/')



Faster:

if <!tipp> is used it will send a message contaning all <!tipp X> command suggestions where X is all keys in the first layer of the .json
if <!tipp X> is used
  if len of X's <subs>!=0: <tipp> + <!tipp Y> command suggestions where Y is all keys in the X's <subs> dictionary in the .json
  else: X <tipp> is sent
Only the before last category/thing is needed in the command. Eg.: if path is X/Y and this lists Z,V,W if we want to see Z only <!tipp Z>
Code will find the path to Z

