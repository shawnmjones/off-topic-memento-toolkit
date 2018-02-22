import os
import string
import random
import unittest
import shutil
import pprint

pp = pprint.PrettyPrinter(indent=4)

from offtopic import collectionmodel, compute_bytecount_across_TimeMap, \
    compute_wordcount_across_TimeMap, compute_jaccard_across_TimeMap, \
    compute_cosine_across_TimeMap, compute_sorensen_across_TimeMap, \
    compute_levenshtein_across_TimeMap, compute_nlevenshtein_across_TimeMap

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

same_scores = {
    # "cosine": 1,
    "bytecount": 0,
    "wordcount": 0,
    # "tfintersection": 0,
    "jaccard": 0,
    "sorensen": 0,
    "levenshtein": 0,
    "nlevenshtein": 0
}

class TestingTimeMapMeasures(unittest.TestCase):

    def test_all_mementos_same(self):

        working_directory = "/tmp/test_all_mementos_same"

        if os.path.exists(working_directory):
            shutil.rmtree(working_directory)

        cm = collectionmodel.CollectionModel(working_directory=working_directory)

        headers = {
            "key1": "value1",
            "key2": "value2"
        }

        contents = []

        contents.append(b"<html><body>Content1 is wonderful</body></html>")
        contents.append(b"<html><body>Content2 is great</body></html>")

        timemap1_content ="""<original1>; rel="original",
<timemap1>; rel="self"; type="application/link-format"; from="Tue, 21 Mar 2016 15:45:06 GMT"; until="Tue, 21 Mar 2018 15:45:12 GMT",
<timegate1>; rel="timegate",
<memento11>; rel="first memento"; datetime="Tue, 21 Jan 2016 15:45:06 GMT",
<memento12>; rel="memento"; datetime="Tue, 21 Jan 2017 15:45:06 GMT",
<memento13>; rel="last memento"; datetime="Tue, 21 Jan 2018 15:45:12 GMT"
"""

        timemap2_content ="""<original1>; rel="original",
<timemap2>; rel="self"; type="application/link-format"; from="Tue, 21 Mar 2016 15:45:06 GMT"; until="Tue, 21 Mar 2018 15:45:12 GMT",
<timegate1>; rel="timegate",
<memento21>; rel="first memento"; datetime="Tue, 21 Mar 2016 15:45:06 GMT",
<memento22>; rel="memento"; datetime="Tue, 21 Mar 2017 15:45:06 GMT",
<memento23>; rel="last memento"; datetime="Tue, 21 Mar 2018 15:45:12 GMT"
"""

        cm.addTimeMap("timemap1", timemap1_content, headers)
        cm.addTimeMap("timemap2", timemap2_content, headers)

        urits = cm.getTimeMapURIList()

        for i in range(0, 2):

            timemap = cm.getTimeMap(urits[i])

            for memento in timemap["mementos"]["list"]:
            
                urim = memento["uri"]

                cm.addMemento(urim, contents[i], headers)

        scores = compute_bytecount_across_TimeMap(
            cm, scores=None, tokenize=False, stemming=False
        )

        scores = compute_wordcount_across_TimeMap(
            cm, scores=scores, stemming=True
        )

        scores = compute_jaccard_across_TimeMap(
            cm, scores=scores, tokenize=True, stemming=True
        )

        # scores = compute_cosine_across_TimeMap(
        #     cm, scores=scores, stemming=True
        # )

        scores = compute_sorensen_across_TimeMap(
            cm, scores=scores, tokenize=False, stemming=False
        )

        scores = compute_levenshtein_across_TimeMap(
            cm, scores=scores, tokenize=False, stemming=False
        )

        scores = compute_nlevenshtein_across_TimeMap(
            cm, scores=scores, tokenize=False, stemming=False
        )

        pp.pprint(scores)

        self.assertTrue( "timemap1" in scores["timemaps"] )
        self.assertTrue( "timemap2" in scores["timemaps"] )

        self.assertTrue( "memento11" in scores["timemaps"]["timemap1"] )
        self.assertTrue( "memento12" in scores["timemaps"]["timemap1"] )
        self.assertTrue( "memento13" in scores["timemaps"]["timemap1"] )

        self.assertTrue( "memento21" in scores["timemaps"]["timemap2"] )
        self.assertTrue( "memento22" in scores["timemaps"]["timemap2"] )
        self.assertTrue( "memento23" in scores["timemaps"]["timemap2"] )

        for urit in scores["timemaps"]:

            for urim in scores["timemaps"][urit]:

                self.assertTrue( "bytecount" in scores["timemaps"][urit][urim] )
                self.assertTrue( "wordcount" in scores["timemaps"][urit][urim] )
                self.assertTrue( "jaccard" in scores["timemaps"][urit][urim] )
                self.assertTrue( "sorensen" in scores["timemaps"][urit][urim] )
                self.assertTrue( "levenshtein" in scores["timemaps"][urit][urim] )
                self.assertTrue( "nlevenshtein" in scores["timemaps"][urit][urim] )

        for measure in same_scores:

            for urit in scores["timemaps"]:

                for urim in scores["timemaps"][urit]:

                    self.assertEqual(
                        scores["timemaps"][urit][urim][measure]["comparison score"],
                        same_scores[measure],
                        "measure {} does not compute the correct score "
                        "for document sameness"
                    )

        shutil.rmtree(working_directory)

    def test_one_memento(self):

        working_directory = "/tmp/test_all_mementos_same"

        if os.path.exists(working_directory):
            shutil.rmtree(working_directory)

        cm = collectionmodel.CollectionModel(working_directory=working_directory)

        headers = {
            "key1": "value1",
            "key2": "value2"
        }

        contents= b"<html><body>Content1 is wonderful</body></html>"

        timemap_content ="""<original1>; rel="original",
<timemap1>; rel="self"; type="application/link-format"; from="Tue, 21 Mar 2016 15:45:06 GMT"; until="Tue, 21 Mar 2018 15:45:12 GMT",
<timegate1>; rel="timegate",
<memento11>; rel="first last memento"; datetime="Tue, 21 Jan 2016 15:45:06 GMT"
"""

        cm.addTimeMap("timemap1", timemap_content, headers)

        urits = cm.getTimeMapURIList()

        timemap = cm.getTimeMap(urits[0])

        for memento in timemap["mementos"]["list"]:
        
            urim = memento["uri"]

            cm.addMemento(urim, contents, headers)

        scores = compute_bytecount_across_TimeMap(
            cm, scores=None, tokenize=False, stemming=False
        )

        scores = compute_wordcount_across_TimeMap(
            cm, scores=scores, stemming=True
        )

        scores = compute_jaccard_across_TimeMap(
            cm, scores=scores, tokenize=True, stemming=True
        )

        # scores = compute_cosine_across_TimeMap(
        #     cm, scores=scores, stemming=True
        # )

        scores = compute_sorensen_across_TimeMap(
            cm, scores=scores, tokenize=False, stemming=False
        )

        scores = compute_levenshtein_across_TimeMap(
            cm, scores=scores, tokenize=False, stemming=False
        )

        scores = compute_nlevenshtein_across_TimeMap(
            cm, scores=scores, tokenize=False, stemming=False
        )

        pp.pprint(scores)

        self.assertTrue( "timemap1" in scores["timemaps"] )

        self.assertTrue( "memento11" in scores["timemaps"]["timemap1"] )

        for urim in scores["timemaps"]["timemap1"]:

            self.assertTrue( "bytecount" in scores["timemaps"]["timemap1"][urim] )
            self.assertTrue( "wordcount" in scores["timemaps"]["timemap1"][urim] )
            self.assertTrue( "jaccard" in scores["timemaps"]["timemap1"][urim] )
            self.assertTrue( "sorensen" in scores["timemaps"]["timemap1"][urim] )
            self.assertTrue( "levenshtein" in scores["timemaps"]["timemap1"][urim] )
            self.assertTrue( "nlevenshtein" in scores["timemaps"]["timemap1"][urim] )

        for measure in same_scores:

            for urit in scores["timemaps"]:

                for urim in scores["timemaps"][urit]:

                    self.assertEqual(
                        scores["timemaps"][urit][urim][measure]["comparison score"],
                        same_scores[measure],
                        "measure {} does not compute the correct score "
                        "for document sameness".format(measure)
                    )

        shutil.rmtree(working_directory)

    def test_all_mementos_different(self):

        working_directory = "/tmp/test_all_mementos_same"

        if os.path.exists(working_directory):
            shutil.rmtree(working_directory)

        cm = collectionmodel.CollectionModel(working_directory=working_directory)

        headers = {
            "key1": "value1",
            "key2": "value2"
        }

        timemap1_content ="""<original1>; rel="original",
<timemap1>; rel="self"; type="application/link-format"; from="Tue, 21 Mar 2016 15:45:06 GMT"; until="Tue, 21 Mar 2018 15:45:12 GMT",
<timegate1>; rel="timegate",
<memento11>; rel="first memento"; datetime="Tue, 21 Jan 2016 15:45:06 GMT",
<memento12>; rel="memento"; datetime="Tue, 21 Jan 2017 15:45:06 GMT",
<memento13>; rel="last memento"; datetime="Tue, 21 Jan 2018 15:45:12 GMT"
"""

        timemap2_content ="""<original1>; rel="original",
<timemap2>; rel="self"; type="application/link-format"; from="Tue, 21 Mar 2016 15:45:06 GMT"; until="Tue, 21 Mar 2018 15:45:12 GMT",
<timegate1>; rel="timegate",
<memento21>; rel="first memento"; datetime="Tue, 21 Mar 2016 15:45:06 GMT",
<memento22>; rel="memento"; datetime="Tue, 21 Mar 2017 15:45:06 GMT",
<memento23>; rel="last memento"; datetime="Tue, 21 Mar 2018 15:45:12 GMT"
"""

        cm.addTimeMap("timemap1", timemap1_content, headers)
        cm.addTimeMap("timemap2", timemap2_content, headers)

        urits = cm.getTimeMapURIList()

        # see: https://en.wikipedia.org/wiki/Pangram
        full_sentence = ['The', 'quick', 'brown', 'fox', 'jumps', 'over', 
            'the', 'lazy', 'dog', 'etaoin', 'shrdlu', 'Now','is', 'the', 
            'time', 'for', 'all', 'good', 'men', 'to', 'come', 'to', 'the', 
            'aid', 'of', 'their', 'country',
            'Jived', 'fox', 'nymph', 'grabs', 'quick', 'waltz',
            'Glib', 'jocks', 'quiz', 'nymph', 'to', 'vex', 'dwarf',
            'Sphinx', 'of', 'black', 'quartz,', 'judge', 'my', 'vow',
            'How', 'vexingly', 'quick', 'daft', 'zebras', 'jump',
            'The', 'five', 'boxing', 'wizards', 'jump', 'quickly',
            'Pack', 'my', 'box', 'with', 'five', 'dozen', 'liquor', 'jugs'
            ]

        for i in range(0, 2):

            timemap = cm.getTimeMap(urits[i])
            index = i + 1

            for memento in timemap["mementos"]["list"]:

                index += 1
            
                urim = memento["uri"]
                mdt = memento["datetime"]

                innercontent = urim

                for j in range(0, index):
                    innercontent += "\n" + " ".join(full_sentence[(i + j + index):]) + " "

                innercontent += "\n" + str(mdt)

                pp.pprint(innercontent)

                print("\n")

                # for j in range(0, randindex):
                #     innercontent += " " + (
                #         urim + " " +
                #         (string.printable[(randindex * 2):(randindex**2) + 1] * randindex) +
                #         " " + str(mdt)
                #     )

                content = "<html><body>{}</body></html>".format(innercontent)

                cm.addMemento(urim, bytes(content, "utf8"), headers)

        scores = compute_bytecount_across_TimeMap(
            cm, scores=None, tokenize=False, stemming=False
        )

        scores = compute_wordcount_across_TimeMap(
            cm, scores=scores, stemming=True
        )

        scores = compute_jaccard_across_TimeMap(
            cm, scores=scores, tokenize=True, stemming=True
        )

        # scores = compute_cosine_across_TimeMap(
        #     cm, scores=scores, stemming=True
        # )

        scores = compute_sorensen_across_TimeMap(
            cm, scores=scores, tokenize=False, stemming=False
        )

        scores = compute_levenshtein_across_TimeMap(
            cm, scores=scores, tokenize=False, stemming=False
        )

        scores = compute_nlevenshtein_across_TimeMap(
            cm, scores=scores, tokenize=False, stemming=False
        )

        pp.pprint(scores)

        self.assertTrue( "timemap1" in scores["timemaps"] )
        self.assertTrue( "timemap2" in scores["timemaps"] )

        self.assertTrue( "memento11" in scores["timemaps"]["timemap1"] )
        self.assertTrue( "memento12" in scores["timemaps"]["timemap1"] )
        self.assertTrue( "memento13" in scores["timemaps"]["timemap1"] )

        self.assertTrue( "memento21" in scores["timemaps"]["timemap2"] )
        self.assertTrue( "memento22" in scores["timemaps"]["timemap2"] )
        self.assertTrue( "memento23" in scores["timemaps"]["timemap2"] )

        for urit in scores["timemaps"]:

            for urim in scores["timemaps"][urit]:

                self.assertTrue( "bytecount" in scores["timemaps"][urit][urim] )
                self.assertTrue( "wordcount" in scores["timemaps"][urit][urim] )
                self.assertTrue( "jaccard" in scores["timemaps"][urit][urim] )
                self.assertTrue( "sorensen" in scores["timemaps"][urit][urim] )
                self.assertTrue( "levenshtein" in scores["timemaps"][urit][urim] )
                self.assertTrue( "nlevenshtein" in scores["timemaps"][urit][urim] )

        expected_scores = {   'timemaps': {   'timemap1': {   'memento11': {   'bytecount': {   'comparison score': 0.0,
                                                                      'individual score': 723},
                                                     'jaccard': {   'comparison score': 0.0},
                                                     'levenshtein': {   'comparison score': 0},
                                                     'nlevenshtein': {   'comparison score': 0.0},
                                                     'sorensen': {   'comparison score': 0.0},
                                                     'wordcount': {   'comparison score': 0.0,
                                                                      'individual score': 94}},
                                    'memento12': {   'bytecount': {   'comparison score': -0.43015214384508993,
                                                                      'individual score': 1034},
                                                     'jaccard': {   'comparison score': 0.11363636363636365},
                                                     'levenshtein': {   'comparison score': 324},
                                                     'nlevenshtein': {   'comparison score': 0.3220675944333996},
                                                     'sorensen': {   'comparison score': 0.011235955056179803},
                                                     'wordcount': {   'comparison score': -0.43617021276595747,
                                                                      'individual score': 135}},
                                    'memento13': {   'bytecount': {   'comparison score': -0.8409405255878284,
                                                                      'individual score': 1331},
                                                     'jaccard': {   'comparison score': 0.15555555555555556},
                                                     'levenshtein': {   'comparison score': 612},
                                                     'nlevenshtein': {   'comparison score': 0.4700460829493088},
                                                     'sorensen': {   'comparison score': 0.0337078651685393},
                                                     'wordcount': {   'comparison score': -0.8723404255319149,
                                                                      'individual score': 176}}},
                    'timemap2': {   'memento21': {   'bytecount': {   'comparison score': 0.0,
                                                                      'individual score': 1019},
                                                     'jaccard': {   'comparison score': 0.0},
                                                     'levenshtein': {   'comparison score': 0},
                                                     'nlevenshtein': {   'comparison score': 0.0},
                                                     'sorensen': {   'comparison score': 0.0},
                                                     'wordcount': {   'comparison score': 0.0,
                                                                      'individual score': 133}},
                                    'memento22': {   'bytecount': {   'comparison score': -0.28655544651619236,
                                                                      'individual score': 1311},
                                                     'jaccard': {   'comparison score': 0.09302325581395354},
                                                     'levenshtein': {   'comparison score': 315},
                                                     'nlevenshtein': {   'comparison score': 0.24570982839313574},
                                                     'sorensen': {   'comparison score': 0.01098901098901095},
                                                     'wordcount': {   'comparison score': -0.30827067669172936,
                                                                      'individual score': 174}},
                                    'memento23': {   'bytecount': {   'comparison score': -0.5593719332679097,
                                                                      'individual score': 1589},
                                                     'jaccard': {   'comparison score': 0.13636363636363635},
                                                     'levenshtein': {   'comparison score': 594},
                                                     'nlevenshtein': {   'comparison score': 0.38101347017318793},
                                                     'sorensen': {   'comparison score': 0.022222222222222254},
                                                     'wordcount': {   'comparison score': -0.593984962406015,
                                                                      'individual score': 212}}}}}

        for measure in same_scores:

            for urit in scores["timemaps"]:

                for urim in scores["timemaps"][urit]:

                    # comparisons with themselves should match
                    if urim == "memento11" or urim == "memento21":
                        self.assertEqual(
                            scores["timemaps"][urit][urim][measure]["comparison score"],
                            same_scores[measure],
                            "measure {} does not compute the correct score "
                            "for document sameness".format(measure)
                        )
                    else:
                        self.assertNotEqual(
                            scores["timemaps"][urit][urim][measure]["comparison score"],
                            same_scores[measure],
                            "measure {} does not compute the correct score "
                            "for document differentness for URI-M {}".format(
                                measure, urim)
                        )

                    # for regression
                    self.assertAlmostEqual(
                            scores["timemaps"][urit][urim][measure]["comparison score"],
                            expected_scores["timemaps"][urit][urim][measure]["comparison score"]
                    )

        shutil.rmtree(working_directory)