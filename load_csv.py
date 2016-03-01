import csv
import datetime

from people.models import Waiver


def load(path):
    carriers = dict([item[::-1] for item in Waiver.CARRIERS])
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
                carrier=carriers.get(row[6].strip(' '), row[6].strip(' ')),
                signature=row[-2],
                football=False,
                dob=dob,
            )
