from astral import sun, LocationInfo, SunDirection
import datetime
import math
from dateutil import rrule
from round_dt import floor_dt, ceil_dt


def calc_shadow(elevation):
    """the given elevation angle must be in degrees"""
    return 1 / math.tan(elevation * math.pi / 180)


def calc_x_shadow(shadow_length, azimuth):
    """the given azimuth angle must be in degrees"""
    if 180 < azimuth < 270:  # northern hemosphere
        theta = 90 - (azimuth - 180)
        return shadow_length * math.cos(theta * math.pi / 180)
    elif 270 < azimuth < 360:  # southern hemosphere
        theta = azimuth - 270
        return shadow_length * math.cos(theta * math.pi / 180)
    else:
        print('the provided azimuth angle is not between noon and sunset')


# change as needed
loc = LocationInfo(name='Alrumailah',
                   region='KSA/Alahsa',
                   timezone='Asia/Riyadh',
                   latitude=25.408661,
                   longitude=49.725459)
loc = LocationInfo(name='Najaf',
                   region='Iraq',
                   timezone='Asia/Baghdad',
                   latitude=31.995829,
                   longitude=44.314863)

o = loc.observer
date = datetime.datetime(2022, 10, 1).date()
# date = datetime.datetime.now().date()  # date has to be in datetime.date() format
s = sun.sun(observer=o, date=date, tzinfo=loc.timezone)

noon_shadow = calc_shadow(sun.elevation(o, s['noon']))
# وقت فضيلة الظهر بين الزوال و بلوغ الظل أربعة أسباع الشاخص
fadelat_dhuhur_shadow = noon_shadow + (4 / 7)
x_fadelat_dhuhur_shadow = (4 / 7)

# وقت فضيلة العصر من بلوغ الظل سبعي الشاخص إلى بلوغه ستة أسباعه
fadelat_aser_shadow = noon_shadow + (6 / 7)
x_fadelat_aser_shadow = (6 / 7)

# وقت فضيلة المغرب من المغرب إلى ذهاب الشفق أي الحمرة المغربية
fadelat_maghrib_elevation = -18

noon_to_sunset = [dt for dt in rrule.rrule(rrule.MINUTELY, dtstart=s['noon'], until=s['sunset'])]

# _________________ METHOD 3 ____________________
shadow = calc_shadow(sun.elevation(o, noon_to_sunset[1]))
count = 2
while shadow < fadelat_dhuhur_shadow:
    shadow = calc_shadow(sun.elevation(o, noon_to_sunset[count]))
    count += 1

fadelat_dhuhur_m3 = floor_dt(noon_to_sunset[count - 1], datetime.timedelta(minutes=1))  # round down to nearest minute

shadow = calc_shadow(sun.elevation(o, noon_to_sunset[count]))  # start count from fadelat_dhuhur
while shadow < fadelat_aser_shadow:
    shadow = calc_shadow(sun.elevation(o, noon_to_sunset[count]))
    count += 1

fadelat_aser_m3 = floor_dt(noon_to_sunset[count - 1], datetime.timedelta(minutes=1))  # round down to nearest minute

# _________________ METHOD 1 ____________________
x_shadow = calc_x_shadow(calc_shadow(sun.elevation(o, noon_to_sunset[1])),
                         sun.azimuth(o, noon_to_sunset[1]))
count = 2
while x_shadow < x_fadelat_dhuhur_shadow:
    azimuth = sun.azimuth(o, noon_to_sunset[count])
    shadow_length = calc_shadow(sun.elevation(o, noon_to_sunset[count]))
    x_shadow = calc_x_shadow(shadow_length, azimuth)
    # shadow_table['datetime'] += [dt]
    # shadow_table['shadow_length'] += [shadow_length]
    # shadow_table['x_shadow'] += [x_shadow]
    count += 1

fadelat_dhuhur_m1 = floor_dt(noon_to_sunset[count - 1], datetime.timedelta(minutes=1))  # round down to nearest minute

x_shadow = calc_x_shadow(calc_shadow(sun.elevation(o, noon_to_sunset[count])),
                         sun.azimuth(o, noon_to_sunset[count]))  # start count from fadelat_dhuhur
while x_shadow < x_fadelat_aser_shadow:
    azimuth = sun.azimuth(o, noon_to_sunset[count])
    shadow_length = calc_shadow(sun.elevation(o, noon_to_sunset[count]))
    x_shadow = calc_x_shadow(shadow_length, azimuth)
    # shadow_table['datetime'] += [dt]
    # shadow_table['shadow_length'] += [shadow_length]
    # shadow_table['x_shadow'] += [x_shadow]
    count += 1

fadelat_aser_m1 = floor_dt(noon_to_sunset[count - 1], datetime.timedelta(minutes=1))  # round down to nearest minute

# ______________ COMMON __________________
fadelat_maghrib = sun.time_at_elevation(o, fadelat_maghrib_elevation,
                                        date=date, direction=SunDirection.SETTING, tzinfo=loc.timezone)

s_next_day = sun.sun(observer=o, date=date + datetime.timedelta(days=1), tzinfo=loc.timezone)
# sunset + (time difference between sunset and sunrise of next day divided by 3) .. added 1 day to get diff in seconds

fajr_prayer_next_day = sun.time_at_elevation(o, -15.5,
                                             date=date + datetime.timedelta(days=1),
                                             direction=SunDirection.RISING,
                                             tzinfo=loc.timezone)

# وقت فضيلة العشاء من ذهاب الشفق إلى ثلث الليل
# رأي السيد السيستاني: ثلث الليل هو ثلث الوقت ما بين سقوط قرص الشمس وبين طلوع الفجر
# السيد الخوئي: ثلث الليل هو ثلث الوقت ما بين سقوط قرص الشمس وبين طلوع الشمس
fadelat_isha_khoei = s['sunset'] + ((s['sunset'] - s_next_day['sunrise'] + datetime.timedelta(days=1)) / 3)
fadelat_isha_sistani = s['sunset'] + ((s['sunset'] - fajr_prayer_next_day + datetime.timedelta(days=1)) / 3)

midnight_khoei = s['sunset'] + ((s['sunset'] - s_next_day['sunrise'] + datetime.timedelta(days=1)) / 2)
midnight_sistani = s['sunset'] + ((s['sunset'] - fajr_prayer_next_day + datetime.timedelta(days=1)) / 2)


def dt2txt(dt):
    if dt.date() == date:
        return dt.strftime('%I:%M %p')
    elif dt.date() == date + datetime.timedelta(days=1):
        return dt.strftime('%I:%M %p اليوم التالي')


print(loc)
print('\ndate: ' + str(date) + '\n')
print('## METHOD 1 (مركبة الظل باتجاه الشرق):')
print('نهاية فضيلة صلاة الظهر: {}\n'
      'نهاية فضيلة صلاة العصر: {}\n'
      'نهاية فضيلة صلاة المغرب: {}\n'
      'نهاية فضيلة صلاة العشاء (الخوئي): {}\n'
      'نهاية فضيلة صلاة العشاء (السيستاني): {}\n'
      'منتصف الليل (الخوئي): {}\n'
      'منتصف الليل (السيستاني): {}\n'.format(dt2txt(fadelat_dhuhur_m1), dt2txt(fadelat_aser_m1),
                                             dt2txt(fadelat_maghrib),
                                             dt2txt(fadelat_isha_khoei), dt2txt(fadelat_isha_sistani),
                                             dt2txt(midnight_khoei), dt2txt(midnight_sistani)))

print('## METHOD 3 (الظل + ظل الزوال):')
print('نهاية فضيلة صلاة الظهر: {}\n'
      'نهاية فضيلة صلاة العصر: {}\n'
      'نهاية فضيلة صلاة المغرب: {}\n'
      'نهاية فضيلة صلاة العشاء (الخوئي): {}\n'
      'نهاية فضيلة صلاة العشاء (السيستاني): {}\n'
      'منتصف الليل (الخوئي): {}\n'
      'منتصف الليل (السيستاني): {}\n'.format(dt2txt(fadelat_dhuhur_m3), dt2txt(fadelat_aser_m3),
                                             dt2txt(fadelat_maghrib),
                                             dt2txt(fadelat_isha_khoei), dt2txt(fadelat_isha_sistani),
                                             dt2txt(midnight_khoei), dt2txt(midnight_sistani)))