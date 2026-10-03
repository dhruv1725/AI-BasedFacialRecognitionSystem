# ============================================================
# AI ATTENDANCE ANALYTICS
# ============================================================


def calculate_student_analytics(
    total_records,
    present_records,
    recent_records
):
    """
    Calculate attendance percentage,
    recent attendance, trend, risk score and insight.
    """

    # --------------------------------------------------------
    # BASIC ATTENDANCE
    # --------------------------------------------------------

    if total_records > 0:
        attendance_percentage = round(
            (present_records / total_records) * 100,
            2
        )
    else:
        attendance_percentage = 0


    # --------------------------------------------------------
    # RECENT ATTENDANCE
    # --------------------------------------------------------

    recent_total = len(recent_records)

    recent_present = sum(
        1
        for record in recent_records
        if str(record[2]).lower() == "present"
    )

    if recent_total > 0:
        recent_percentage = round(
            (recent_present / recent_total) * 100,
            2
        )
    else:
        recent_percentage = 0


    # --------------------------------------------------------
    # TREND
    # --------------------------------------------------------

    difference = recent_percentage - attendance_percentage

    if difference <= -10:
        trend = "Declining"

    elif difference >= 10:
        trend = "Improving"

    else:
        trend = "Stable"


    # --------------------------------------------------------
    # RISK SCORE
    # --------------------------------------------------------

    if attendance_percentage >= 85:
        risk_score = 10

    elif attendance_percentage >= 75:
        risk_score = 25

    elif attendance_percentage >= 60:
        risk_score = 60

    else:
        risk_score = 90


    # Adjust risk using trend

    if trend == "Declining":
        risk_score += 10

    elif trend == "Improving":
        risk_score -= 5


    # Keep score between 0 and 100

    risk_score = max(
        0,
        min(100, risk_score)
    )


    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if risk_score >= 75:
        risk_level = "High"

    elif risk_score >= 45:
        risk_level = "Medium"

    else:
        risk_level = "Low"


    # --------------------------------------------------------
    # AI INSIGHT
    # --------------------------------------------------------

    if attendance_percentage >= 85:

        insight = (
            "Excellent attendance. "
            "The student is maintaining a strong attendance record."
        )

    elif attendance_percentage >= 75:

        insight = (
            "Attendance is satisfactory, "
            "but maintaining regular attendance is recommended."
        )

    elif attendance_percentage >= 60:

        insight = (
            "Attendance needs attention. "
            "The student should improve regular attendance."
        )

    else:

        insight = (
            "Low attendance detected. "
            "The student is at high risk of attendance shortage."
        )


    # Add trend information

    if trend == "Declining":

        insight += (
            " Recent attendance is declining."
        )

    elif trend == "Improving":

        insight += (
            " Recent attendance is improving."
        )


    return {
        "attendance_percentage": attendance_percentage,
        "recent_percentage": recent_percentage,
        "trend": trend,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "insight": insight
    }


# ============================================================
# ATTENDANCE TIME ANALYSIS
# ============================================================

def analyze_attendance_times(attendance_records):

    """
    Analyze attendance times.

    attendance_records format:

    [
        (date, time, status),
        ...
    ]
    """

    present_times = []

    for record in attendance_records:

        if len(record) < 3:
            continue

        attendance_time = record[1]
        status = record[2]

        if (
            str(status).lower() == "present"
            and attendance_time is not None
        ):
            present_times.append(
                attendance_time
            )


    if not present_times:

        return {
            "total_present": 0,
            "average_time": None,
            "earliest_time": None,
            "latest_time": None
        }


    # Convert time values into seconds

    total_seconds = 0

    for time_value in present_times:

        total_seconds += (
            time_value.hour * 3600
            + time_value.minute * 60
            + time_value.second
        )


    average_seconds = (
        total_seconds // len(present_times)
    )


    hours = (
        average_seconds // 3600
    )

    minutes = (
        (average_seconds % 3600) // 60
    )

    seconds = (
        average_seconds % 60
    )


    average_time = (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds:02d}"
    )


    return {
        "total_present": len(present_times),

        "average_time": average_time,

        "earliest_time": min(
            present_times
        ).strftime("%H:%M:%S"),

        "latest_time": max(
            present_times
        ).strftime("%H:%M:%S")
    }

