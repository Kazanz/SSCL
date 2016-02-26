import csv
import datetime

from people.models import Waiver


def load(path):
    with open(path, 'rb') as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        for row in r:
            try:
                dob = datetime.datetime.strptime(
                    row[-1], '%d/%m/%Y'
                ).strftime('%Y-%m-%d')
            except:
                try:
                    dob = datetime.datetime.strptime(
                        row[-1], '%d/%M/%Y'
                    ).strftime('%Y-%m-%d')
                except:
                    dob = "2016-01-01"
            Waiver.objects.create(
                created=row[0],
                first=row[1],
                last=row[2],
                email=row[3],
                phone=row[5],
                carrier=row[6],
                signature=row[-2],
                football=False,
                dob=dob,
            )
