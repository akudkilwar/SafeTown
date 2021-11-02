from haversine import haversine, Unit

cpdef checkSeverity(df, list route1, list route2):
    cdef int i
    cdef int j
    cdef int k
    cdef (double, double) crashSite
    cdef int severityCount1 = 0
    cdef int severityCount2 = 0
    cdef (double, double) start # C double has same 64-bit precison as Py float.
    cdef (double, double) end


    for i in df.index:
            crashSite = (float(df["Start_Lat"][i]), float(df["Start_Lng"][i]))

            for j in range(0, len(route2)-1):
                start = route2[j]
                end = route2[j+1]
                if checkHaversineEquality(start, end, crashSite):
                    severityCount2 += df["Severity"][i]
                    continue

            for k in range(0, len(route1)-1):
                start = route1[k]
                end = route1[k+1]
                if checkHaversineEquality(start, end, crashSite):
                    severityCount1 += df["Severity"][i]
                    continue

    return severityCount1, severityCount2;


def checkHaversineEquality(start, end, crashpoint, error=0.5):
    if abs(haversine(crashpoint, start, unit=Unit.KILOMETERS) + haversine(crashpoint, end, unit=Unit.KILOMETERS) - haversine(start, end)) <= error*(haversine(start, end, unit=Unit.KILOMETERS)):
        return True
    return False