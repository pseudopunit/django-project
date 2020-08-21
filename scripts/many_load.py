import csv  # https://docs.python.org/3/library/csv.html

# https://django-extensions.readthedocs.io/en/latest/runscript.html

# python3 manage.py runscript many_load

from unesco.models import Site, Category, Description, Justification, Region, State, Iso

def run():
    fhand = open('whc.csv')
    reader = csv.reader(fhand)
    next(reader) # Advance past the header

    Site.objects.all().delete()
    Category.objects.all().delete()
    Description.objects.all().delete()
    Justification.objects.all().delete()
    Region.objects.all().delete()
    State.objects.all().delete()
    Iso.objects.all().delete()

    # Format    name-descp-justif-year-long-lat-area-category-state-region-iso

    for row in reader:


        try:
            y = int(row[3])
        except:
            y = None

        print(y)
        try:
            j, created = Justification.objects.get_or_create(name=row[2])
        except:
            j = None

        try:
            ahs = int(row[6])
        except:
            ahs = None

        try:
            lat = int(row[5])
        except:
            lat = None

        try:
            lon = int(row[4])
        except:
            lon = None

        try:
            nm = row[0]
        except:
            continue


        c, created = Category.objects.get_or_create(name=row[7])
        d, created = Description.objects.get_or_create(name=row[1])
        i, created = Iso.objects.get_or_create(name=row[10])
        sn,created = State.objects.get_or_create(name=row[8]) #
        r, created = Region.objects.get_or_create(name=row[9])  #
        s = Site(name=nm, year=y, latitude=lat, longitude=lon, area_hectares=ahs, category=c , description=d, region=r, justification=j, state=sn, iso=i)
        #
        s.save()

        #print(i)

        # p, created = Person.objects.get_or_create(email=row[0])
        # c, created = Course.objects.get_or_create(title=row[2])

        # r = Membership.LEARNER
        # if row[1] == 'I' : r = Membership.INSTRUCTOR
        # m = Membership(role=r,person=p, course=c)
        # m.save()