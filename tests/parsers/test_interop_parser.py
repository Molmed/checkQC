
import os

import unittest

import pandas as pd
import numpy as np

from interop import imaging

from checkQC.parsers.interop_parser import InteropParser


class TestInteropParser(unittest.TestCase):

    class Receiver(object):
        def __init__(self):
            self.metrics = {'error_rate': [],
                            'percent_q30': [],
                            'percent_q30_per_cycle': [],
                            'percent_phix': [],
                            }
            self.subscriber = self.subscribe()
            next(self.subscriber)

        def subscribe(self):
            while True:
                interop_stat = yield
                key = list(interop_stat)[0]
                self.metrics[key].append(interop_stat)

        def send(self, value):
            self.subscriber.send(value)

    runfolder = os.path.join(os.path.dirname(__file__), "..",
                             "resources",
                             "230825_M04034_0043_000000000-L6NVV")
    interop_parser = InteropParser(runfolder=runfolder,
                                   parser_configurations=None)
    subscriber = Receiver()
    interop_parser.add_subscribers(subscriber)
    interop_parser.run()

    def test_read_error_rate(self):
        error_rates = [x[1]['error_rate'] for x in self.subscriber.metrics['error_rate']]
        self.assertEqual(error_rates[0], 0.587182343006134)
        self.assertTrue(np.isnan(error_rates[1]))
        self.assertTrue(np.isnan(error_rates[2]))
        self.assertEqual(error_rates[3], 0.8676796555519104)

    def test_percent_phix(self):
        phix = [x[1]['percent_phix'] for x in self.subscriber.metrics['percent_phix']]
        self.assertEqual(phix[0], 15.352058410644531)
        self.assertTrue(np.isnan(phix[1]))
        self.assertTrue(np.isnan(phix[2]))
        self.assertEqual(phix[3], 14.5081205368042)

    def test_percent_q30(self):
        self.assertListEqual(self.subscriber.metrics['percent_q30'],
                             [('percent_q30',
                               {'lane': 1,
                                'read': 1,
                                'percent_q30': 95.3010025024414,
                                'is_index_read': False}),
                              ('percent_q30',
                               {'lane': 1,
                                'read': 2,
                                'percent_q30': 82.97042846679688,
                                'is_index_read': True}),
                              ('percent_q30',
                               {'lane': 1,
                                'read': 3,
                                'percent_q30': 97.44789123535156,
                                'is_index_read': True}),
                              ('percent_q30',
                               {'lane': 1,
                                'read': 4,
                                'percent_q30': 90.55824279785156,
                                'is_index_read': False})])

    def test_percent_q30_per_cycle_subscriber_output(self):
        percent_q30_per_cycle = self.subscriber.metrics['percent_q30_per_cycle']
        self.assertEqual(percent_q30_per_cycle[0][1]['read'], 1)
        self.assertAlmostEqual(
            percent_q30_per_cycle[0][1]['percent_q30_per_cycle'][10],
            96.68322,
            places=5,
        )

        self.assertEqual(percent_q30_per_cycle[1][1]['read'], 2)
        self.assertTrue(percent_q30_per_cycle[1][1]['is_index_read'])
        self.assertAlmostEqual(
            percent_q30_per_cycle[1][1]['percent_q30_per_cycle'][1],
            80.69179,
            places=5,
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
                6: 97.17214,
                18: 97.1332,
                25: 97.38965,
                50: 96.62786,
                75: 96.30572,
                100: 94.63465,
                136: 92.64536,
        }

        #Select cycles from the expected_out-dict.
        filtered_q30_per_cycle = {
            cycle: percent_q30_per_cycle[cycle]
            for cycle in expected_out
        }

        for cycle in filtered_q30_per_cycle:
            self.assertTrue(np.isclose(
                expected_out[cycle], filtered_q30_per_cycle[cycle]))
