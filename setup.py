from setuptools import setup, find_packages

setup(
    name         = 'stonksense_scraper_scheduler',
    version      = '0.1',
    packages     = find_packages(),
    entry_points = {'console_scripts': ['schedule-stonksense-scraper = stonksense_scraper_scheduler.scheduler:main']},
    install_requires=[
        'schedule',
        'scrapinghub',
        'msgpack-python',
    ],
)