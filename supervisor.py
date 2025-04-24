from datetime import datetime, timedelta

from decouple import config
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from mail import send_email
from models import Advertisement, Entry, Portal


if __name__ == "__main__":
    engine = create_engine(config("DATABASE_URL"))
    session = Session(engine)

    portals = {"ClicRBS", "Estadão", "Folha", "Globo", "IG", "Metropoles", "R7", "Terra"}

    last_24_h = datetime.now() - timedelta(hours=24)
    ads = session.query(
        Portal.name,
        func.count(Advertisement.id)
    ).join(
        Entry,
        Portal.id == Entry.portal_id
    ).join(
        Advertisement,
        Entry.id == Advertisement.entry_id
    ).filter(Advertisement.created_at >= last_24_h).group_by(Portal.name)

    print(f"Last 24h collecting: {list(ads)}")
    collected_portals = set([a[0] for a in ads])
    if portals != collected_portals:
        diff = ", ".join(portals - collected_portals)
        msg = "The following portals did not have ads collected in the "\
            f"last 24h:\n\n {diff}"
        print(msg)
        send_email(msg)
