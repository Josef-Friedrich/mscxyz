#! /usr/bin/env python


from mscxyz.score_file_classes import list_scores, list_scores_grouped_by_alphabet

# scores = list_scores('/home/jf/git-repositories/alias/bitbucket/davklein/musescore-leadsheet-collection',
#                      'mscx')
#

scores = list_scores_grouped_by_alphabet()

for score in scores:
    print(score)
