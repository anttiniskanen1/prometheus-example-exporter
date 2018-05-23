import argparse
import logging
import random
import re
import signal
import sys
import time

from jog import JogFormatter
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.core import REGISTRY

from prometheus_example_exporter import example1_parser
from prometheus_example_exporter import example2_parser

metric_invalid_chars = re.compile(r'[^a-zA-Z0-9_:]')
metric_invalid_start_chars = re.compile(r'^[^a-zA-Z_:]')
label_invalid_chars = re.compile(r'[^a-zA-Z0-9_]')
label_invalid_start_chars = re.compile(r'^[^a-zA-Z_]')
label_start_double_under = re.compile(r'^__+')

def format_label_key(label_key):
    label_key = re.sub(label_invalid_chars, '_', label_key)
    label_key = re.sub(label_invalid_start_chars, '_', label_key)
    label_key = re.sub(label_start_double_under, '_', label_key)
    return label_key

def format_label_value(value_list):
    return '_'.join(value_list)

def format_metric_name(name_list):
    metric = '_'.join(name_list)
    metric = re.sub(metric_invalid_chars, '_', metric)
    metric = re.sub(metric_invalid_start_chars, '_', metric)
    return metric

def collector_up_gauge(name_list, description, succeeded=True):
    metric_name = format_metric_name(name_list + ['up'])
    description = 'Did the {} fetch succeed.'.format(description)
    return GaugeMetricFamily(metric_name, description, value=int(succeeded))

def group_metrics(metrics):
    metric_dict = {}
    for (name_list, label_dict, value) in metrics:
        metric_name = format_metric_name(name_list)
        label_dict = {format_label_key(k): format_label_value(v)
                      for k, v in label_dict.items()}

        if metric_name not in metric_dict:
            metric_dict[metric_name] = (tuple(label_dict.keys()), {})

        label_keys = metric_dict[metric_name][0]
        label_values = tuple([label_dict[key]
                              for key in label_keys])

        metric_dict[metric_name][1][label_values] = value

    return metric_dict

def gauge_generator(metrics):
    metric_dict = group_metrics(metrics)

    for metric_name, (label_keys, value_dict) in metric_dict.items():
        # If we have label keys we may have multiple different values,
        # each with their own label values.
        if label_keys:
            gauge = GaugeMetricFamily(metric_name, '', labels=label_keys)

            for label_values, value in value_dict.items():
                gauge.add_metric(label_values, value)

        # No label keys, so we must have only a single value.
        else:
            gauge = GaugeMetricFamily(metric_name, '', value=list(value_dict.values())[0])

        yield gauge

class Example1Collector():

    """Metric collector for example 1.

    Collectors have a no-argument method 'collect' that returns a list of
    Metric objects.

    """

    def __init__(self):
        """Init.

        Metric_name_list is used to uniquely identify (prefix) a set of metrics.
        Description is used mainly for logging purposes.

        """
        self.metric_name_list = ['example1', 'random']
        self.description = 'Random'

    def collect(self):
        """Collect.

        In the collect function, the metric is collected, and parsed
        for Prometheus consumption.

        Description is used mainly for logging.

        """

        try:
            # In here you would actually fetch data from an external system.
            # Response could be JSON-ish like in this case.
            response = {
                           "smalls": {
                                         "first": random.randint(1,11),
                                         "second": random.randint(1,21)
                                     },
                           "bigs": {
                                       "first": random.randint(1,101),
                                       "second": random.randint(1,201)
                                   }
                       }

            # Give the response to a parser best suited for these kinds of metrics
            metrics = example1_parser.parse_response(response, self.metric_name_list)
        except Exception:
            # Log all anomalies
            logging.exception('Error while fetching %s.', self.description)
            # If the fetch did not succeed, make a metric out of that
            yield collector_up_gauge(self.metric_name_list, self.description, succeeded=False)
        else:
            # Otherwise generate a Gauge from the parsed metrics and yield that
            yield from gauge_generator(metrics)
            # Likewise, make a metric out of succeeded collections as well
            yield collector_up_gauge(self.metric_name_list, self.description)

class Example2Collector():

    """Metric collector for example 2.

    Collectors have a no-argument method 'collect' that returns a list of
    Metric objects.

    """

    def __init__(self):
        """Init.

        Metric_name_list is used to uniquely identify (prefix) a set of metrics.
        Description is used mainly for logging purposes.

        """
        self.metric_name_list = ['example2', 'sporadic']
        self.description = 'Sporadic metrics'

    def collect(self):
        """Collect.

        In the collect function, the metric is collected, and parsed
        for Prometheus consumption.

        Description is used mainly for logging.

        """

        try:
            # In here you would actually fetch data from an external system.
            # Response could be JSON-ish like in this case.
            
            # Simulate a service which only responds "most" of the time
            if random.random() > 0.2:
                response = {
                               "result": 100
                           }
            else:
                response = {}

            # Give the response to a parser best suited for these kinds of metrics
            metrics = example2_parser.parse_response(response, self.metric_name_list)
        except ValueError:
            # This will happen sometimes
            logging.exception('Erroneous value while fetching %s.', self.description)
            yield collector_up_gauge(self.metric_name_list, self.description, succeeded=False)
        except Exception:
            # Log all anomalies
            logging.exception('Error while fetching %s.', self.description)
            # If the fetch did not succeed, make a metric out of that
            yield collector_up_gauge(self.metric_name_list, self.description, succeeded=False)
        else:
            # Otherwise generate a Gauge from the parsed metrics and yield that
            yield from gauge_generator(metrics)
            # Likewise, make a metric out of succeeded collections as well
            yield collector_up_gauge(self.metric_name_list, self.description)

def shutdown():
    logging.info('Shutting down')
    sys.exit(1)

def signal_handler(signum, frame):
    shutdown()

def main():
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description='Export example metrics for Prometheus consumption.')
    parser.add_argument('-p', '--port', type=int, default=9900,
                        help='port to serve the metrics endpoint on. (default: 9900)')
    parser.add_argument('-c', '--config-file', default='example.cfg',
                        help='path to query config file. Can be absolute, or relative to the current working directory. (default: example.cfg)')
    parser.add_argument('--example1-disable', action='store_true',
                        help='disable example 1 monitoring.')
    parser.add_argument('--example2-disable', action='store_true',
                        help='disable example 2 monitoring.')
    parser.add_argument('-j', '--json-logging', action='store_true',
                        help='turn on json logging.')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='detail level to log. (default: INFO)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='turn on verbose (DEBUG) logging. Overrides --log-level.')
    args = parser.parse_args()

    log_handler = logging.StreamHandler()
    log_format = '[%(asctime)s] %(name)s.%(levelname)s %(threadName)s %(message)s'
    formatter = JogFormatter(log_format) if args.json_logging else logging.Formatter(log_format)
    log_handler.setFormatter(formatter)

    log_level = getattr(logging, args.log_level)
    logging.basicConfig(
        handlers=[log_handler],
        level=logging.DEBUG if args.verbose else log_level
    )
    logging.captureWarnings(True)

    port = args.port
    
    scheduler = None

    if not args.example1_disable:
        REGISTRY.register(Example1Collector())

    if not args.example2_disable:
        REGISTRY.register(Example2Collector())

    logging.info('Starting server...')
    start_http_server(port)
    logging.info('Server started on port %s', port)

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass

    shutdown()
