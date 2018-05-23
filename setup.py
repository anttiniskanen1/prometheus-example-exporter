from setuptools import setup, find_packages

setup(
    name='prometheus-example-exporter',
    version='0.1.0.dev1',
    description='Example Prometheus exporter',
    url='https://github.com/anttiniskanen1/prometheus-example-exporter',
    author='Antti Niskanen',
    author_email='antti.niskanen@cybercom.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='monitoring prometheus exporter',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'jog',
        'prometheus-client'
    ],
    entry_points={
        'console_scripts': [
            'prometheus-example-exporter=prometheus_example_exporter:main',
        ],
    },
)
