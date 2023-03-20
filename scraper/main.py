import logging
import os
from sqlalchemy import create_engine
from datetime import date
from job import Job, Base
from linkedin_jobs_scraper import LinkedinScraper
from sqlalchemy.orm import sessionmaker
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters, \
    OnSiteOrRemoteFilters

# Change root logger level (default is WARN)
logging.basicConfig(level=logging.INFO)

mysql_host = os.getenv('mysql_host')
mysql_user = os.getenv('mysql_user')
mysql_password = os.getenv('mysql_password')
mysql_url = 'mysql://' + mysql_user + ':' + mysql_password + '@' + mysql_host + '/jobs?charset=utf8'
engine = create_engine(mysql_url)

# engine = create_engine("mysql://springstudent:springstudent@localhost/jobs?charset=utf8")
# 创建会话类
DB_Session = sessionmaker(bind=engine)
# 创建会话对象
session = DB_Session()
Base.metadata.create_all(engine)


# Fired once for each successfully processed job
def on_data(data: EventData):
    des = str(data.description).lower()
    # print('[ON_DATA]', data.title, data.company, data.company_link, data.date, data.link)
    delimiter = '-'
    if 'it consulting' in [x.lower() for x in data.insights]:
        return
    if 'not' in data.h1bResult.lower():
        return
    job_type = []
    if 'c++' in des:
        job_type.append('c++')
    if 'java' in des:
        job_type.append('java')
        if 'spring' in des:
            job_type.append('spring')
        if 'react' in des:
            job_type.append('react')
            if 'javascript' in des:
                job_type.append('javascript')
    types = delimiter.join(job_type)
    if len(types) > 0:
        job = Job(title=data.title[0: min(len(data.title), 64)],
                  apply_link=data.link[0:min(len(data.link), 2048)],
                  date=str(date.today()) if data.date == '' else data.date,
                  company=data.company[0: min(len(data.title), 64)],
                  type=types)
        print('[ON_DATA]', data.title, data.company, data.company_link, data.date, data.link, data.insights)
        session.add(job)
        session.commit()


# Fired once for each page (25 jobs)
def on_metrics(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')
    session.close()


scraper = LinkedinScraper(
    chrome_executable_path="chromedriver/chromedriver",
    # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=2,  # Slow down the linkedin-scraper to avoid 'Too many requests 429' errors (in seconds)
    page_load_timeout=40  # Page load timeout (in seconds)
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        query='software engineer',
        options=QueryOptions(
            locations=['United States'],
            apply_link=True,
            # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page mus be navigated. Default to False.
            skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
            limit=10000,
            filters=QueryFilters(  # Filter by companies.
                relevance=RelevanceFilters.RELEVANT,
                time=TimeFilters.DAY,
                type=[TypeFilters.FULL_TIME, TypeFilters.INTERNSHIP],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL]
            )
        )
    ),
]

scraper.run(queries)
