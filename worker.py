from celery import Celery
from celery.schedules import crontab

from bs4 import BeautifulSoup
import requests
from sqlalchemy import select, text

from database.connection import engine_url as engine
from settings import Settings
from sqlmodel import Field, Session, select
from models.channels import Channel

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
    "Amazon Movies",
    "Btok 1024.ETH Official Channel",
    "Bollywood hd Movies",
]

NO_VIEWS = [
    "PUNTER KI PANCHAYAT",
]

NO_ER = [
    "PUNTER KI PANCHAYAT",
]

NO_MONTH_SUBS = [
    "NEXTA Live",
]


@app.task
def update_channels(session=Session(engine)):
    """
    TODO: ...
    """
    logger.info("Start updating channels")
    r = requests.get(SITE)
    soup = BeautifulSoup(r.text, "html.parser")
    titles = [
        item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")
    ]
    raw_subscribers = [
        int(sub.get_text(strip=True).replace("'", ""))
        for sub in soup.find_all(class_="kt-number kt-font-brand text-cursor")
    ]
    subscribers = raw_subscribers[0::2]
    week_views = raw_subscribers[1::2]
    raw_er = [
        i.get_text(strip=True) for i in soup.find_all(class_="kt-number kt-font-brand")
    ]
    e_r = [i for i in raw_er if "%" in i]
    subs_rate = [
        i.get_text(strip=True)
        for i in soup.find_all(
            class_=[
                "kt-number kt-font-success",
                "kt-number kt-font-danger",
                "kt-number kt-number-small kt-font-success",
                "kt-number kt-number-small kt-font-danger",
            ]
        )
    ]
    subs_today_rate = subs_rate[0::4]
    subs_yesterday_rate = subs_rate[1::4]
    subs_week_rate = subs_rate[2::4]
    subs_month_rate = subs_rate[3::4]

    count = 1
    while count <= 5:
        track_week = 0
        track_er = 0
        track_subs = 0
        for item in range(30):
            new_title = str(titles[item])
            with Session(engine) as session:
                query = select(Channel).where(Channel.title == new_title)
                if query:
                    result = session.exec(query)
                    channel = result.one()
    
                    channel.subscribers = 
                    logger.info("Channel: %s", channel)
        count += 1

        # with Session(engine) as session:
            # query = select(Channel).where(Channel.title == "title")
            # result = session.exec(query)
            # channel = result.one()
            # logger.info("Channel | name: %s", channel.title)
    # 
            # channel.subscribers = 16
            # session.add(channel)
            # session.commit()
            # session.refresh(channel)
            # logger.info("Updated channel: %", channel.title)
    # query = select(Channel)
    # channels = session.exec(query).all()
    logger.info("Done, updating channels")
    return True


@app.task
def populate_channel_table():
    """
    Populate channels table
    """
    logger.info("Starting populate channels table")
    r = requests.get(SITE)
    soup = BeautifulSoup(r.text, "html.parser")
    titles = [
        item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")
    ]
    avatars = [
        i["src"] for i in soup.find_all(class_="wd-50 rounded-circle")
    ]
    descriptions = [
        des["data-cont"]
        for des in soup.find_all(
            class_="btn btn-outline-warning btn-sm btn-xs kt-font-dark"
        )
    ]
    raw_subscribers = [
        int(sub.get_text(strip=True).replace("'", ""))
        for sub in soup.find_all(class_="kt-number kt-font-brand text-cursor")
    ]
    subscribers = raw_subscribers[0::2]
    week_views = raw_subscribers[1::2]
    raw_er = [
        i.get_text(strip=True) for i in soup.find_all(class_="kt-number kt-font-brand")
    ]
    e_r = [i for i in raw_er if "%" in i]
    subs_rate = [
        i.get_text(strip=True)
        for i in soup.find_all(
            class_=[
                "kt-number kt-font-success",
                "kt-number kt-font-danger",
                "kt-number kt-number-small kt-font-success",
                "kt-number kt-number-small kt-font-danger",
            ]
        )
    ]
    subs_today_rate = subs_rate[0::4]
    subs_yesterday_rate = subs_rate[1::4]
    subs_week_rate = subs_rate[2::4]
    subs_month_rate = subs_rate[3::4]
    # tags = [
    #  tag.get_text(strip=True)  for tag in soup.find_all(class_="pd-0-force td-info pt-1 td-cats")
    # ]


    count = 1
    while count <= 5:
        track_des = 0
        track_week = 0
        track_er = 0
        track_subs = 0
        for item in range(30):
            new_title = str(titles[item])
            if titles[item] in NO_DESCRIPTION:
                new_des = ""
                track_des += 1
            else:
                new_des = descriptions[item - track_des]
            if titles[item] in NO_VIEWS:
                week = 0
                track_week += 1
            else:
                week = week_views[item - track_week]
            if titles[item] in NO_ER:
                new_er = ""
                track_er +=1 
            else:
                new_er = e_r[item-track_er]
            if titles[item] in NO_MONTH_SUBS:
                new_month = ""
                track_subs += 1
            else:
                new_month = str(subs_month_rate[item-track_subs])
            channel = Channel(
                title=new_title,
                avatar=avatars[item],
                description=new_des,
                subscribers=str(subscribers[item]),
                subs_today_rate=str(subs_today_rate[item]),
                subs_yearsterday_rate=str(subs_yesterday_rate[item]),
                subs_week_rate=str(subs_week_rate[item]),
                subs_month_rate=new_month,
                week_views=week,
                e_r=new_er
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
        avatars = [
            i["src"] for i in soup.find_all(class_="wd-50 rounded-circle")
        ]
        descriptions = [
            des["data-cont"]
            for des in soup.find_all(
                class_="btn btn-outline-warning btn-sm btn-xs kt-font-dark"
        )
        ]
        raw_subscribers = [
            int(sub.get_text(strip=True).replace("'", ""))
            for sub in soup.find_all(class_="kt-number kt-font-brand text-cursor")
        ]
        subscribers = raw_subscribers[0::2]
        week_views = raw_subscribers[1::2]
        raw_er = [
            i.get_text(strip=True) for i in soup.find_all(class_="kt-number kt-font-brand")
        ]
        e_r = [i for i in raw_er if "%" in i]
        subs_rate = [
        i.get_text(strip=True)
        for i in soup.find_all(
            class_=[
                "kt-number kt-font-success",
                "kt-number kt-font-danger",
                "kt-number kt-number-small kt-font-success",
                "kt-number kt-number-small kt-font-danger",
            ]
        )
        ]
        subs_today_rate = subs_rate[0::4]
        subs_yesterday_rate = subs_rate[1::4]
        subs_week_rate = subs_rate[2::4]
        subs_month_rate = subs_rate[3::4]
        logger.info("Populate channels table is done!")
    return True


@app.task
def update_channels():
    """
    Update existing channels
    """
    logger.info("Update existing channels")
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
