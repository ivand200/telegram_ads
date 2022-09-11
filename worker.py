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


@app.task
def update_channels(session = Session(engine)):
    """
    TODO: ...
    """
    logger.info("Start updating channels")
    query = select(Channel)
    channels = session.exec(query).all()
    logger.info("Done, updating channels")
    return channels
   

@app.task
def populate_channel_table():
    """
    TODO: ...
    """
    r = requests.get(SITE)
    soup = BeautifulSoup(r.text, "html.parser")
    titles = [item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")]
    raw_subs = [int(sub.get_text(strip=True).replace("'", "")) for sub in soup.find_all(class_="kt-number kt-font-brand text-cursor")]
    subs = raw_subs[0::2]
    des = [des["data-cont"] for des in soup.find_all(class_="btn btn-outline-warning btn-sm btn-xs kt-font-dark")]
    count = 1
    while count <= 5:
        for item in range(29):
            # if isinstance(titles[item], str):
            try:
                new_title = str(titles[item])
            except:
                new_title = ""

            # if titles[item] == "Telegram-zh_CN 简体中文语言包":
            #     new_des = ""
            # else:
            #     new_des = des[item]
            # channel = Channel(title=new_title, description=new_des)
            channel = Channel(title=new_title, subscribers=subs[item])  # description=des[item],
            with Session(engine) as session:
                session.add(channel)
                session.commit()
        count += 1
        r = requests.get(f"{SITE}/?page={count}")
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")]
        raw_subs = [int(sub.get_text(strip=True).replace("'", "")) for sub in soup.find_all(class_="kt-number kt-font-brand text-cursor")]
        subs = raw_subs[0::2]
        des = [des["data-cont"] for des in soup.find_all(class_="btn btn-outline-warning btn-sm btn-xs kt-font-dark")]
    return True

    # count = 1
    # while count <= 20:
    #     for title in titles:
    #         if isinstance(title, str):
    #             channel = Channel(title=title, description=des)
    #             with Session(engine) as session:
    #                 session.add(channel)
    #                 session.commit()
    #     count += 1
    #     r = requests.get(f"{SITE}/?page={count}")
    #     soup = BeautifulSoup(r.text, "html.parser")
    #     titles = [item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")]
    # return True





    # logger.info("Start populate Channels table")
    # with engine.connect().execution_options(autocommit=True) as conn:
    #     r = requests.get(SITE)
    #     soup = BeautifulSoup(r.text, "html.parser")
    #     titles = [item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")]
    #     for item in titles:
    #         if isinstance(item, str):
    #             query = conn.execute("INSERT INTO channel (title, description, subscribers) VALUES (:title)", title=item)
        # r = requests.get(f"{SITE}/?page={count}")
        # soup = BeautifulSoup(r.text, "html.parser")
        # titles = [item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")]


# channels = conn.execute(text("SELECT title FROM channel"))
# all = channels.fetchall()



    # logger.info("Start populate Channels table")
    # r = requests.get(SITE)
    # soup = BeautifulSoup(r.text, "html.parser")

    # titles = [item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")]
    # count = 1
    # while count <= 50:
    #     with Session(engine) as session:
    #         for title in titles:
    #             if isinstance(title, str):
    #                 channel = Channel(title=title)
    #                 session.add(channel)
    #                 count += 1
    #                 session.commit()
    #         r = requests.get(f"{SITE}/?page={count}")
    #         soup = BeautifulSoup(r.text, "html.parser")
    #         titles = [item.get_text(strip=True) for item in soup.find_all(class_="kt-ch-title")]
        


    # for title in titles:
    #     if isinstance(title, str):
    #         channel = Channel(title=title)
    #         session.add(channel)
    #         session.commit()
    # logger.info("Done populate Chanels table")
    

    # raw_subscribers = [int(sub.get_text(strip=True).replace("'", "")) for sub in soup.find_all(class_="kt-number kt-font-brand text-cursor")]
    # subscribers = raw_subscribers[0::2]


# app.conf.beat_schedule = {
#     "every-1-minute": {
#         "task": "worker.populate_channel_table",
#         "schedule": crontab(minute=30, hour=22),
#     }
# }

# channels = conn.execute(text("SELECT title FROM channel"))
# all = channels.fetchall()
# print(all)