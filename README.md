# prometheus-example-exporter
Prometheus Example Exporter

Based on https://github.com/braedon/prometheus-es-exporter

====
This Prometheus exporter "collects" predefined example metrics.

This is to demonstrate some of the features of production-ready Prometheus exporters, such as modular, run-on-scrape custom collectors and very general, reusable data transformations.

Primarily meant for people new to Prometheus monitoring or even Python in general, and as a base/inspiration for other custom exporters.

## Metrics
On scrape, the exporter collects some samples (if possible) and exports the results as Prometheus gauge metrics.

Values are parsed automatically by the modules best suited for the task.

# Usage
Once installed (see Development), you can run the exporter with the `prometheus-example-exporter` command.

By default, it will bind to port 9900 and "run" the sample queries (if not disabled). You can change the defaults as required by passing in options:
```
> prometheus-example-exporter -p <port>
```
Run with the `-h` flag to see details on all the available options.

# Development
To install directly from the git repo, run the following in the root project directory:
```
> pip3 install .
```
The exporter can be installed in "editable" mode, using pip's `-e` flag. This allows you to test out changes without having to re-install.
```
> pip3 install -e .
```
To build a docker image directly from the git repo, run the following in the root project directory:
```
> sudo docker build -t <your repository name and tag> .
```
