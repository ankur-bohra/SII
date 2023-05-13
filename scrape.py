import csv
import urllib.request

from bs4 import BeautifulSoup

main_page = r"https://studyinindia.gov.in/choose-your-insitute?descipline_id=1011&programme_id=14&institute_type=0&selected_Programme_Name=Under%20Graduate%20(UG)&selected_states=0&selected_subjects=0&selected_nature_of_course=47,45&selected_states_names=0&selected_subjects_name=0&selected_nature_of_course_name=Bachelor%20of%20Technology%20(B.Tech%20-%20Evening),Bachelor%20of%20Technology%20(B.Tech)"
main_page = r"https://studyinindia.gov.in/choose-your-insitute?descipline_id=1011&programme_id=14&institute_type=0&selected_Programme_Name=Under%20Graduate%20(UG)&selected_states=0&selected_subjects=0&selected_nature_of_course=26,47,45&selected_states_names=0&selected_subjects_name=0&selected_nature_of_course_name=Bachelor%20of%20Engineering%20(B.E.),Bachelor%20of%20Technology%20(B.Tech%20-%20Evening),Bachelor%20of%20Technology%20(B.Tech)"
# Filters applied: Engineering, UG, B.Tech + B.Tech Evening
print(".")
httpResponse = urllib.request.urlopen(main_page)
html = httpResponse.read().decode("utf8")
httpResponse.close()
print("..")
soup = BeautifulSoup(html, "html.parser")
course_and_fee_details_a_tags = soup.select(".pr-0 > a")
course_and_fee_details_links = [(a.parent.parent.parent.find(
    "h4").text, a['href']) for a in course_and_fee_details_a_tags]
print("...")
data = []
scraped = 0
courses = 0
for (institute, link) in course_and_fee_details_links:
    institute = institute.strip().strip("\"")
    print("Scraping: " + institute)
    httpResponse = urllib.request.urlopen(link)
    html = httpResponse.read().decode("utf8")
    httpResponse.close()
    soup = BeautifulSoup(html, "html.parser")
    panels = soup.find_all("div", class_="panel-collapse")
    for panel in panels:
        associated_a = soup.find("a", href="#"+panel['id'])
        course = associated_a.text
        if "B.Tech" not in course and "B.E" not in course:
            # This is a hack to filter out the non-engineering related courses.
            continue

        # Panel independent values
        panel_data = {
            "Institute": institute,
            "Course": course.strip()
        }

        # Directly available key-value pairs
        for li in panel.find_all("li"):
            key = li.find("strong").text
            value = li.find("span").text
            panel_data[key] = value

        # Indirect additions
        eligibility_criteria = panel.select(
            ".institue-eligi:nth-child(1)")[0].text
        eligibility_criteria = eligibility_criteria.split(
            ":").pop().replace("\r\n", "").strip()
        panel_data['Eligibility Criteria'] = eligibility_criteria

        additional_criteria = panel.select(
            ".institue-eligi:nth-child(2)")[0].text.split(":").pop().strip()
        panel_data['Additional Criteria'] = additional_criteria

        # Add link in last column
        panel_data['SII Institute Link'] = link.replace(
            "&active_tab_index=1", "#Section2")

        panel_data.pop('Program Level')  # Always undergraduate
        panel_data.pop('Discipline')  # Always engineering
        data.append(panel_data)

        if "Branch/Subject" in panel_data:
            print("\t", panel_data["Branch/Subject"])
        courses += 1
    scraped += 1

with open("SII BTech Courses.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)

print(f"Scraped and saved {courses} courses from {scraped} institutes.")