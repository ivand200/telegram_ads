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
    "TAMILROCKERS",
    "نيمار ابن الانبار || iraqedu",
    "Samoylovaoxana",
    "Дмитрий Медведев",
]

NO_VIEWS = [
    "PUNTER KI PANCHAYAT",
]

NO_ER = [
    "PUNTER KI PANCHAYAT",
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
    logger.info("Starting populate channels table")
    r = requests.get(SITE)
    soup = BeautifulSoup(r.text, "html.parser")
    titles = [item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")]
    des = [
        des["data-cont"]
        for des in soup.find_all(
            class_="btn btn-outline-warning btn-sm btn-xs kt-font-dark"
        )
    ]
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
        i.get_text(strip=True)
        for i in soup.find_all(
            class_=[
                "kt-number kt-number-small kt-font-success",
                "kt-number kt-number-small kt-font-danger",
            ]
        )
    ]
    month_change = month_change_raw[2::3]

    count = 1
    while count <= 5:
        track_des = 0
        track_week = 0
        track_er = 0
        for item in range(30):
            new_title = str(titles[item])
            if titles[item] in NO_DESCRIPTION:
                new_des = ""
                track_des += 1
            else:
                new_des = des[item - track_des]
            if titles[item] in NO_VIEWS:
                week = 0
                track_week += 1
            else:
                week = week_views[item - track_week]
            if titles[item] in NO_ER:
                new_er = ""
                track_er +=1 
            else:
                new_er = er[item-track_er]
            channel = Channels(
                title=new_title,
                description=new_des,
                subscribers=subs[item],
                week_views=week,
                er=new_er,
                month_change=month_change[item],
            )
            logger.info(f"Populate channel | title: {new_title}")
            with Session(engine) as session:
                session.add(channel)
                session.commit()

        count += 1
        r = requests.get(f"{SITE}/?page={count}")
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [
            item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")
        ]
        des = [
            des["data-cont"]
            for des in soup.find_all(
                class_="btn btn-outline-warning btn-sm btn-xs kt-font-dark"
            )
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
            i.get_text(strip=True)
            for i in soup.find_all(
                class_=[
                    "kt-number kt-number-small kt-font-success",
                    "kt-number kt-number-small kt-font-danger",
                ]
            )
        ]
        month_change = month_change_raw[2::3]
    logger.info("Populate channels table is done!")
    return True


# app.conf.beat_schedule = {
#     "every-1-minute": {
#         "task": "worker.populate_channel_table",
#         "schedule": crontab(minute=30, hour=22),
#     }
# }
