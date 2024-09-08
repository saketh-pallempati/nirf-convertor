import tabula
import PyPDF2
import re
import pandas as pd


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        first_page = reader.pages[0]
        text = first_page.extract_text()
    return text


def extract_college_info(text):
    lines = text.split('\n')
    match = re.match(r"(.+)\s\[(.+)\]", lines[4])
    if match:
        college_name = match.group(1).strip()
        university_id = match.group(2).strip()
    else:
        raise ValueError(
            "The format of the institute name and ID is not as expected.")
    return college_name, university_id


def convert_pdf_to_dataframe(pdf_path):
    ls = tabula.read_pdf(pdf_path, pages='all')
    return ls


def convert_earnings_to_dict(df, s, earnings_row_index=2):
    earnings_row = df.iloc[earnings_row_index]

    earnings_dict = {}
    for year in earnings_row.index[1:]:
        earnings = int(earnings_row[year])
        formatted_earnings = f"₹ {earnings:,.2f}"
        earnings_dict[f"{s} ({year})"] = formatted_earnings
    return earnings_dict


def extract_and_sum_expenditures(df, year_index):
    total_expenditure = 0
    for i in range(2, len(df)):
        expenditure_str = df.iloc[i, year_index].split('(')[0].strip()
        expenditure = int(expenditure_str.replace(',', ''))
        total_expenditure += expenditure
    return total_expenditure


def calculate_annual_expenditure(df):
    years = df.columns[1:]

    annual_capital_expenditure = {}
    for year_index, year in enumerate(years, start=1):
        year_label = f"{' '.join(df.iloc[1].values[0].split()[:3])} ({year})"
        annual_capital_expenditure[year_label] = extract_and_sum_expenditures(
            df, year_index)

    return annual_capital_expenditure


def process_dataframe(ls, college_name, university_id):
    data = {}
    data['Name of the Institute'] = college_name
    data['Institute / University ID (as per NIRF)'] = university_id
    data['Category'] = "Overall"
    data['Number of students (including Ph.D. students)'] = ls[1]['Total Students'].sum(
    )
    data['Number of faculty members'] = ls[-1].columns[1]

    Annual_capital_expenditure = calculate_annual_expenditure(ls[-8])
    data.update(Annual_capital_expenditure)

    Annual_operating_expenditure = calculate_annual_expenditure(ls[-7])
    data.update(Annual_operating_expenditure)

    data['Online education'] = "-"
    data['Number of students offered online courses'] = "-"
    data['Number of credits transferred'] = "-"
    data['Number of courses'] = "-"

    data['Number of students who are economically backward'] = ls[1][
        'Economically\rBackward\r(Including male\r& female)'].sum()

    data['Number of students who are socially challenged'] = ls[1][
        'Socially\rChallenged\r(SC+ST+OBC\rIncluding male\r& female)'].sum()

    data['Number of students who are not receiving full tuition fee reimbursement'] = ls[
        1]['No. of students\rwho are not\rreceiving full\rtuition fee\rreimbursement'].sum()

    data['Number of full-time Ph.D. awarded in the last 3 years'] = sum(
        map(int, ls[7].iloc[5].values[1:]))

    data['Number of part-time Ph.D. awarded in the last 3 years'] = sum(
        map(int, ls[7].iloc[6].values[1:]))

    years = ls[-3].columns[1:]
    for year in years:
        data[f'Publications ({year})'] = "-"

    for year in years:
        data[f'Citations ({year})'] = "-"

    data.update(convert_earnings_to_dict(
        ls[-5], "Sponsored projects - Total amount received", earnings_row_index=1))
    data.update(convert_earnings_to_dict(
        ls[-4], "Consultancy projects - Total amount received"))
    data.update(convert_earnings_to_dict(
        ls[-3], "Earnings from Executive Development Programme"))

    data['Valid NBA Accreditation'] = "-"
    data['Valid NAAC Accreditation'] = "-"

    output_df = pd.DataFrame(list(data.items()), columns=None)

    output_csv_path = "output.csv"
    output_df.to_csv(output_csv_path, index=False, header=False)

    return output_csv_path


def main(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    college_name, university_id = extract_college_info(text)
    df = convert_pdf_to_dataframe(pdf_path)
    output_csv_path = process_dataframe(df, college_name, university_id)
    return output_csv_path
