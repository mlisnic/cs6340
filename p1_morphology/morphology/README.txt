I tested the program on lab2-11.

Notes about my program:
- There's an empty line at the end of my outputs
- I use the collections library for defaultdict, I hope that is allowed
- My code generally assumes "clean" inputs, I only check that the type of affix is one of PREFIX,SUFFIX and throw an error
- I also don't check for the arrow (->) in the rules file. I simply split on whitespace and skip the "word" between POS tags
  So any other symbol works as long as it doesn't have a space
