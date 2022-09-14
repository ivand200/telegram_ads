from celery import Celery
from celery.schedules import crontab

from bs4 import BeautifulSoup
import requests
from sqlalchemy import select, text

from database.connection import engine_url as engine
from settings import Settings
from sqlmodel import Field, Session, select
from models.channels import Channels

settings = Settings()

app = Celery(broker=f"{settings.REDIS_URL}")

logger = app.log.get_default_logger()

SITE = "https://telemetr.me/channels/"  # /?page=2


NO_DESCRIPTION = [
    "Telegram-zh_CN 简体中文语言包",
    "ЛИТВИН",
    "Btok 1024.ETH Official Channel",
    "Дудь",
    "TAMILROCKERS"
]


@app.task
def update_channels(session=Session(engine)):
    """
    TODO: ...
    """
    logger.info("Start updating channels")
    query = select(Channels)
    channels = session.exec(query).all()
    logger.info("Done, updating channels")
    return channels
   

@app.task
def populate_channel_table():
    """
    Populate channels table
    """
    r = requests.get(SITE)
    soup = BeautifulSoup(r.text, "html.parser")
    titles = [item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")]
    raw_subs = [
        int(sub.get_text(strip=True).replace("'", "")) 
        for sub in soup.find_all(class_="kt-number kt-font-brand text-cursor")
    ]
    subs = raw_subs[0::2]
    week_views = raw_subs[1::2]
    raw_er = [
        i.get_text(strip=True) for i in soup.find_all(class_="kt-number kt-font-brand")
    ]
    er = [i for i in raw_er if "%" in i]
    month_change_raw = [
    i.get_text(strip=True) for i in soup.find_all(class_=["kt-number kt-number-small kt-font-success", "kt-number kt-number-small kt-font-danger"])
    ]
    month_change = month_change_raw[2::3]
    count = 1
    while count <= 5:
        for item in range(29):
            new_title = str(titles[item])
            channel = Channels(
                title=new_title,
                subscribers=subs[item],
                week_views=week_views[item],
                er=er[item],
                month_change=month_change[item]
            )
            with Session(engine) as session:
                session.add(channel)
                session.commit()
        count += 1
        r = requests.get(f"{SITE}/?page={count}")
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [
            item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")
        ]
        raw_subs = [
            int(sub.get_text(strip=True).replace("'", "")) 
            for sub in soup.find_all(class_="kt-number kt-font-brand text-cursor")
        ]
        subs = raw_subs[0::2]
        week_views = raw_subs[1::2]
        raw_er = [
            i.get_text(strip=True) 
            for i in soup.find_all(class_="kt-number kt-font-brand")
        ]
        er = [i for i in raw_er if "%" in i]
        month_change_raw = [
        i.get_text(strip=True) for i in soup.find_all(class_=["kt-number kt-number-small kt-font-success", "kt-number kt-number-small kt-font-danger"])
        ]
        month_change = month_change_raw[2::3]
    return True


# app.conf.beat_schedule = {
#     "every-1-minute": {
#         "task": "worker.populate_channel_table",
#         "schedule": crontab(minute=30, hour=22),
#     }
# }
