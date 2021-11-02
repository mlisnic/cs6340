================================================================================
                    HOW TO USE THE SCORING PROGRM
================================================================================

     USAGE: perl score-ie.pl <output_templates> <gold_templates>

This program produces two forms of output:

1) It prints (to standard output) a table showing the recall,
   precision, and F scores for the output templates by comparing them
   with the gold answer key templates.

2) It prints a file named <output_templates>.trace in the working
   directory that displays the recall, precision, and F scores for
   each individual story. This should help you understand the behavior
   of your system and scores with respect to each story.  The overall
   score across ALL stories is also appended at the end, so you do not
   need to save that output separately.
    
================================================================================
                      SCORING FUNCTION
================================================================================

The scoring program will compute recall, precision, and F score for
each of the event roles ("slots") separately and display that
information. The system's output string for a slot must exactly match
a string in the answer key to be counted as correct. The order of
strings in each slot does not matter.

The overall ("TOTAL") scores are computed as micro-averaged recall and
precision. This means that recall and precision are computed based on
the total number of true/false positives and negatives across all of
the slots. The overall F score is computed directly from the
micro-averaged recall and precision. 

For example, suppose your system produces the following scores for
SlotX and SlotY:

    SlotX: Recall = .50 (5/10)  Precision = 1.0 (5/5)   F-score = .67
    SlotY: Recall = .80 (4/5)   Precision = .13 (4/30)  F-score = .22

The overall scores would be: 

    TOTAL: Recall = .60 (9/15)  Precision = .26 (9/35)  F-score = .36

Note that the F-score is computed as (2 * .60 * .26) / (.60 + .26) =
.36 whereas averaging the F-scores for SlotX and SlotY would produce a
different value. The micro-averaging approach takes the number of
instances for each slot into account, instead of giving each slot
equal weight.


