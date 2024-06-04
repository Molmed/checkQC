
import os

import unittest

import pandas as pd
import numpy as np

from interop import imaging

from checkQC.parsers.interop_parser import InteropParser


class TestInteropParser(unittest.TestCase):

    class Receiver(object):
        def __init__(self):
            self.error_rate_values = []
            self.percent_q30_values = []
            self.percent_q30_per_cycle = []
            self.subscriber = self.subscribe()
            next(self.subscriber)

        def subscribe(self):
            while True:
                interop_stat = yield
                key = list(interop_stat)[0]
                if key == "error_rate":
                    self.error_rate_values.append(interop_stat)
                if key == "percent_q30":
                    self.percent_q30_values.append(interop_stat)
                if key == "percent_q30_per_cycle":
                    self.percent_q30_per_cycle.append(interop_stat)

        def send(self, value):
            self.subscriber.send(value)

    runfolder = os.path.join(os.path.dirname(__file__), "..", 
                             "resources",
                             "MiSeqDemo")
    interop_parser = InteropParser(runfolder=runfolder, 
                                   parser_configurations=None)
    subscriber = Receiver()
    interop_parser.add_subscribers(subscriber)
    interop_parser.run()

    def test_read_error_rate(self):
        self.assertListEqual(self.subscriber.error_rate_values,
                             [('error_rate', 
                                {'lane': 1, 
                                 'read': 1, 
                                 'error_rate': 1.5317546129226685}),
                              ('error_rate',
                                {'lane': 1,
                                 'read': 2,
                                 'error_rate': 1.9201501607894897})])


    def test_percent_q30(self):
        self.assertListEqual(self.subscriber.percent_q30_values,
                             [('percent_q30', 
                               {'lane': 1, 
                                'read': 1, 
                                'percent_q30': 93.42070007324219, 
                                'is_index_read': False}),
                              ('percent_q30', 
                               {'lane': 1, 
                                'read': 2, 
                                'percent_q30': 84.4270248413086, 
                                'is_index_read': False})])
        
    def test_percent_q30_per_cycle(self):
        percent_q30_per_cycle = self.subscriber.percent_q30_per_cycle
        self.assertEqual(percent_q30_per_cycle[0][1]['read'], 1)
        self.assertAlmostEqual(
            percent_q30_per_cycle[0][1]['percent_q30_per_cycle'][10],
            98.41526794433594
        )

        self.assertEqual(percent_q30_per_cycle[1][1]['read'], 2)
        self.assertAlmostEqual(
            percent_q30_per_cycle[1][1]['percent_q30_per_cycle'][10],
            95.20341491699219
        )
    
    def test_get_percent_q30_per_cycle(self):
        q_metrics = imaging(self.runfolder,
              valid_to_load=['Q'])
        
        percent_q30_per_cycle = InteropParser.get_percent_q30_per_cycle(
                q_metrics=q_metrics,
                lane_nr=0, 
                read_nr=0,
                is_index_read=False,
        )

        expected_out = {
                6: 98.76343,
                48: 97.841576,
                90: 96.81421,
                132: 95.90264,
                174: 94.69448,
                216: 91.90525,
                258: 87.162094,
        }

        #Select cycles from the expected_out-dict.
        filtered_q30_per_cycle = {
            cycle: percent_q30_per_cycle[cycle]
            for cycle in expected_out
        }

        for cycle in filtered_q30_per_cycle:
            self.assertTrue(np.isclose(
                expected_out[cycle], filtered_q30_per_cycle[cycle]))
