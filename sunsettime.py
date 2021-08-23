from SimplePythonSunPositionCalculator import getSEA

deg_4_dates = []
deg_0_96_dates = []
deg_4_ele = []
deg_0_96_ele = []
for mth in range(1, 13):
    end_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    for dy in range(1, end_day[mth-1]):
        is_sunset = False
        is_less_than_4 = False
        for hr in range(1, 10):
            if is_sunset and is_less_than_4:
                break
            ele, date = getSEA(25.414084, 49.723500, 3, 2020, mth, dy, hr + 12, 0)
            i = 0
            for mn in range(0, 60):
                ele, date = getSEA(25.414084, 49.723500, 3, 2020, mth, dy, hr + 12, mn)
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

diff_minutes = [(deg_4_dates[i] - deg_0_96_dates[i]).total_seconds() / 60 for i in range(0, len(deg_0_96_dates))]
diff_deg_4_ele = [abs(4 - abs(deg_4_ele[i])) for i in range(0, len(deg_4_ele))]
diff_deg_0_96_ele = [abs(0.96 - abs(deg_0_96_ele[i])) for i in range(0, len(deg_0_96_ele))]

print("minimum time difference (minutes): %d" % min(diff_minutes))
print("maximun time difference (minutes): %d" % max(diff_minutes))
print('\n')
print("minimum ele difference for 0.96 deg (deg): %.3f" % max(diff_deg_4_ele))
print("maximun ele difference for 4 deg (deg): %.3f" % max(diff_deg_0_96_ele))
