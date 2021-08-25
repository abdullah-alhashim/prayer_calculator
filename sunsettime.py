import pandas as pd
from datetime import datetime
from SimplePythonSunPositionCalculator import getSEA

deg_4_dates = []
deg_0_96_dates = []
deg_4_ele = []
deg_0_96_ele = []
for yr in [2018, 2019]:
    for mth in range(1, 13):
        end_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # for non-leap years
        for dy in range(1, end_day[mth - 1] + 1):
            is_sunset = False
            is_less_than_4 = False
            for hr in range(1, 10):
                if is_sunset and is_less_than_4:
                    break
                ele, date = getSEA(25.414084, 49.723500, 3, yr, mth, dy, hr + 12, 0)
                i = 0
                for mn in range(0, 60):
                    ele, date = getSEA(25.414084, 49.723500, 3, yr, mth, dy, hr + 12, mn)
                    if (ele < -.96) and not is_sunset:
                        is_sunset = True
                        deg_0_96_dates.append(date)
                        deg_0_96_ele.append(ele)

                    if ele < -4 and not is_less_than_4:
                        is_less_than_4 = True
                        deg_4_dates.append(date)
                        deg_4_ele.append(ele)

                    if is_sunset and is_less_than_4:
                        break

calendar_df = pd.DataFrame({'g_day': [deg_0_96_dates[i].date() for i in range(0, len(deg_0_96_dates))],
                            'sunset': [deg_0_96_dates[i].time().strftime('%-I:%M')
                                       for i in range(0, len(deg_0_96_dates))],
                            'maghrib': [deg_4_dates[i].time().strftime('%-I:%M')
                                        for i in range(0, len(deg_4_dates))]})
calendar_df['maghrib'] = [datetime.strptime(str(calendar_df['g_day'][i]) + ' '
                                            + calendar_df['maghrib'][i]
                                            + ' PM', '%Y-%m-%d %I:%M %p') for i in range(0, len(calendar_df))]

zahra_calendar = pd.read_csv('./الزهراء 1440.csv')
zahra_calendar = zahra_calendar.rename(columns={'sunset': 'maghrib'})
zahra_calendar['g_day'] = [pd.to_datetime(zahra_calendar['g_day'], dayfirst=True)[i].date()
                           for i in range(0, len(zahra_calendar))]
zahra_calendar['maghrib'] = [datetime.strptime(str(zahra_calendar['g_day'][i]) + ' '
                                               + zahra_calendar['maghrib'][i]
                                               + ' PM', '%Y-%m-%d %I:%M %p') for i in range(0, len(zahra_calendar))]

diff_maghrib = pd.DataFrame({'zahra': zahra_calendar['maghrib'],
                             'new_calendar': calendar_df[calendar_df['g_day'].isin(zahra_calendar['g_day'])][
                                 'maghrib'].reset_index(drop=True)})
diff = calendar_df[calendar_df['g_day'].isin(zahra_calendar['g_day'])]['maghrib'].reset_index(drop=True)\
       - zahra_calendar['maghrib']
diff_maghrib['difference'] = pd.Series([diff[i].total_seconds() / 60 for i in range(0, len(diff_maghrib))])

diff_minutes = [(deg_4_dates[i] - deg_0_96_dates[i]).total_seconds() / 60 for i in range(0, len(deg_0_96_dates))]
diff_deg_4_ele = [abs(4 - abs(deg_4_ele[i])) for i in range(0, len(deg_4_ele))]
diff_deg_0_96_ele = [abs(0.96 - abs(deg_0_96_ele[i])) for i in range(0, len(deg_0_96_ele))]

print("minimum time difference (minutes): %d" % min(diff_minutes))
print("maximun time difference (minutes): %d" % max(diff_minutes))
print('\n')
print("minimum ele difference for 0.96 deg (deg): %.3f" % max(diff_deg_4_ele))
print("maximun ele difference for 4 deg (deg): %.3f" % max(diff_deg_0_96_ele))
