import time
from datetime import datetime, timedelta
from functools import partial
import argparse
import csv
from scrapinghub import ScrapinghubClient
import schedule


def load_schedule(path):

    args = []
    schedule = []

    with open(path) as file:
        rows = csv.reader(file, delimiter=',')
        
        for i, r in enumerate(rows):
            if i == 0:
                args = r
            else:
                schedule.append({k.strip(' '): v.strip(' ') for k, v in zip(args, r)})
    
    return schedule


def scrap(key, query):

    print('scraping query: {};'.format(query))

    try:
        client = ScrapinghubClient(key)
        project = client.get_project(client.projects.list()[0])
        spider = project.spiders.get('newsapi_spider')

        now = datetime.now()
        from_date = datetime.strftime(datetime.strftime(now.date(), '%Y-%m-%d'))
        to_date = datetime.strftime(datetime.strftime((now - timedelta(days=1)).date(), '%Y-%m-%d'))

        spider.jobs.run(query=query, from_date=from_date, to_date=to_date)

        while spider.jobs.summary()[1]['count'] > 0:
            time.sleep(1)
            
        client.close(10)
    
    except Exception as e:
        print(e)


def eod_cleanup(key):

    print('End of day clean-up;')

    try:
        client = ScrapinghubClient(key)
        project = client.get_project(client.projects.list()[0])
        spider = project.spiders.get('newsapi_spider')
        # clean up finished jobs
        for j in spider.jobs.summary()[2]['summary']:
            job = client.get_job(j['key'])
            job.delete()
            
        client.close(10)
    
    except Exception as e:
        print(e)


def main():

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--scrapinghub-key', required=True, help='scrapinghub access key')
    parser.add_argument('-f', '--file', required=True, help='schedule file')
    args = parser.parse_args()

    # load schedule file
    schedule_input = load_schedule(args.file)
    
    # setup schedule
    for itm in schedule_input:
        schedule.every().day.at(itm['time']).do(
            partial(
                scrap,
                key=args.scrapinghub_key,
                query=itm['query']
            )
        )

    # setup clean-up job
    schedule.every().day.at('23:59').do(eod_cleanup)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()