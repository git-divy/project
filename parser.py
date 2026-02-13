from bs4 import BeautifulSoup

def parse_attendance_html(html: str):
    soup = BeautifulSoup(html, "html.parser")

    result = {
        "student_info": {},
        "attendance": {
            "subjects": [],
            "summary": {}
        }
    }

    # ----------------------------
    # 1) Parse Student Info Table
    # ----------------------------

    info_table = soup.find("table", class_="table")

    if info_table:
        rows = info_table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")

            # Process in key-value pairs
            for i in range(0, len(cols), 2):
                if i + 1 < len(cols):
                    key = cols[i].get_text(strip=True).replace(":", "")
                    value = cols[i + 1].get_text(strip=True)

                    if key:
                        result["student_info"][key] = value

    # ----------------------------
    # 2) Parse Attendance Table
    # ----------------------------

    attendance_table = soup.find("table", id="grdAttdetail")

    if attendance_table:
        rows = attendance_table.find_all("tr")[1:]  # skip header row

        for row in rows:
            cols = row.find_all("td")

            if len(cols) < 6:
                continue

            values = [c.get_text(strip=True) for c in cols]

            # Detect TOTAL row
            if "Total" in values:
                result["attendance"]["summary"] = {
                    "total_lectures": values[3],
                    "attended_lectures": values[4],
                    "attendance_percentage": values[5]
                }
            else:
                subject = {
                    "sr_no": values[0],
                    "subject_name": values[1],
                    "subject_code": values[2],
                    "total_lectures": values[3],
                    "attended_lectures": values[4],
                    "attendance_percentage": values[5]
                }

                result["attendance"]["subjects"].append(subject)

    return result