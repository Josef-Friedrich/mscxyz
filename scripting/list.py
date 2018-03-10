#! /usr/bin/env python


from collections import OrderedDict

dirs = [
    '/tmp/1.mscx',
    '/tmp/2.mscx',
    '/tmp/a/1.mscx',
    '/tmp/b/1.mscx',
]

ordered = OrderedDict()

for score in dirs:
    print(score)
    segments = score.split('/')
    for segment in segments:
        if segment:
            print(segment)
