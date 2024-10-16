from typing import Any, Optional, Tuple, List, Dict
import traceback
import time

import requests
from bs4 import BeautifulSoup, NavigableString
from flask import request

from src.models.exceptions import MissingInformationError, WikipediaApiFetchError
from src.models.v2.job.ref_insights_job_v2 import RefInsightsJobV2
from src.models.v2.schema.ref_insights_schema_v2 import RefInsightsSchemaV2
from src.models.wikimedia.enums import RequestMethods

from src.views.v2.statistics import StatisticsViewV2

from src.helpers.get_version import get_poetry_version


class RefInsightsV2(StatisticsViewV2):

    """
    returns Wayback Medic/IABot statistical data
    """

    schema = RefInsightsSchemaV2()  # Defines expected parameters; Overrides StatisticsViewV2's "schema" property
    job: RefInsightsJobV2           # Holds usable variables, seeded from schema. Overrides StatisticsViewV2's "job"
    return_data: Dict[str, Any] = {}  # holds parsed data from page processing
    execution_errors: List[Dict[str, Any]] = None

    def get(self):
        """
        flask GET entrypoint for returning ref_insights results
        must return a tuple: (Any, response_code)
        """
        from src import app
        app.logger.debug(f"==> RefInsightsV2::get")

        return self.__process_request__(method=RequestMethods.get)


    def __process_request__(self, method=RequestMethods.post):  # default to POST

        from src import app
        app.logger.debug(f"==> RefInsightsV2::__process_request__, method = {method}")

        # Start the timer
        start_time = time.time()

        try:

            # validate and setup params
            self.__validate_and_get_job__(method)  # inherited from StatisticsViewV2

            # fetch the data, parse and return summary
            insight_data = self.__get_insight_data__()

            # Stop the timer and calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time
            #         timestamp = datetime.timestamp(datetime.utcnow())
            #         isodate = datetime.isoformat(datetime.utcnow())

            self.return_data = {
                "iari_version": get_poetry_version("pyproject.toml"),
                "iari_command": "insights",
                "endpoint": request.endpoint,
                "execution_errors": self.execution_errors,
                "execution_time": f"{execution_time:.4f} seconds"
            }


            # # request_props for debug to see what is returned
            # request_properties = dir(request)
            # filtered_properties = [prop for prop in request_properties if not prop.startswith('__')]
            # # self.return_data["request props"] = '<br>'.join(filtered_properties)
            # # self.return_data["request props"] = str(filtered_properties)
            # self.return_data["request props"] = filtered_properties


            self.return_data.update(insight_data)

            # and return results
            return self.return_data, 200


        except MissingInformationError as e:
            traceback.print_exc()
            return {"error": f"Missing Information Error: {str(e)}"}, 500

        except Exception as e:
            traceback.print_exc()
            return {"error": f"General Error: {str(e)}"}, 500


    def __get_insight_data__(self):
        """
        grabs appropriate data regarding media updates
        """

        soup = self.__get_stats_soup__()

        table_names = self.__get_table_names__(soup)
        table_list = self.__get_all_tables__(soup, table_names)
        table_totals = self.__get_table_totals__(table_list)

        return {
            "table_names": table_names,
            "table_totals": table_totals,
            "tables": table_list
        }


    def __get_stats_soup__(self):
        """
        returns data from LAMP statistics data fetch
        """
        url_stats_yearly = (
            "https://"
            "tools-static.wmflabs.org/"
            "botwikiawk/dashyearly.html"
        )

        from src import app
        app.logger.debug(f"url_stats_yearly = {url_stats_yearly}")

        # grab HTML of summary data
        # requests.get(url, params={key: value}, args)

        # TODO use a try/catch here
        r = requests.get(url_stats_yearly)
        # TODO use a try/catch here

        if r.status_code != 200:
            return None

        stats_data = r.text  # r.text is unicode, vs r.content, which is in bbytes
        return BeautifulSoup(stats_data, "html.parser")

    def __get_all_tables__(self, soup, table_names):
        tables = soup.find_all('table')
        table_index = 0
        table_list = []
        for table in tables:
            table_data = self.__parse_table_data__(table, table_names[table_index])
            table_index += 1
            table_list.append(table_data)

        return table_list


    def __get_table_names__(self, soup):
        """
        returns array of table names represented in the top of the html:

            ...
                <center>
                Tables: <a href="#Wayback Links added by IABot">A. Wayback by IABot</a>&nbsp;|&nbsp;<a href="#Wayback Links added by Users">B. Wayback by Users</a>&nbsp;|&nbsp;<a href="#Wayback Links added by User Bots">C. Wayback by User Bots</a>&nbsp;|&nbsp;<a href="#LAMP">D. LAMP</a>&nbsp;|&nbsp;<a href="#LAMP_SIM">E. LAMP SIM</a>&nbsp;|&nbsp;<a href="#Media Links (/details/) added by Users">F. Media by Users</a>
                <table class="sortable">
            ...

        """

        # the first <table> element caps the data at the end of the stuff
        # between the <center> tag and the forst table tag and
        table_tag = soup.find('table')

        # Find the <center> tag of interest, and extract the table names
        for center_element in soup.find_all('center'):

            first_content = center_element.contents[0]

            # proceed if "Tables" is at start of <center> content
            if "Tables:" in first_content:
                table_names = []
                for elem in center_element.children:

                    # stop when table element reached
                    if elem == table_tag:
                        break

                    # if elem is <a> tag, append text as table name
                    # text is in format: "A. Wayback by IABot"; strip first letter and dot
                    if elem.name == 'a':
                        parts = elem.get_text().split('.', 1)
                        if len(parts) > 1:
                            t_name = parts[1].strip()
                            table_names.append(t_name)

                return table_names


    def __get_table_totals__(self, tables):
        """
        returns summarized column data for each table:
        """
        totals_by_row = []

        # fetch totals array from each table and append to output array
        for table in tables:
            totals_by_row.append(
                {
                    "name": table["name"],
                    "cols": table["column_totals"],

                }
            )

        return {
            "column_names": tables[0]["column_names"],
            "tables": totals_by_row
        }

    def __parse_table_data__(self, table, table_name):
        """
        returns structured dict representing table structure, identity, and data
        """

        column_names = self.__get_column_names__(table)
        rows = self.__get_rows__(table)
        column_totals = self.__get_column_totals__(rows, column_names)

        return {
            "name": table_name,
            "column_names": column_names,
            "column_totals": column_totals,
            "rows": rows
        }


    def __get_column_names__(self, table):
        """
        return names of real data columns, i.e., all header columns that are not #, site, or total
        """

        # get all headers from thead in table
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]

        # return just the columns of real data (skip #, site, and total columns)
        # the first two entries are "#" and "site"
        return headers[2:-1]


    def __get_rows__(self, table):
        my_rows =[]
        for row in table.find('tbody').find_all('tr'):

            td_elements = row.find_all('td')

            col_index_counter = 0
            col_index_site = 1
            col_index_total = len(td_elements) - 1

            row_data ={}
            index = 0
            cols_list =[]

            for td in td_elements:

                if index == col_index_counter:
                    row_data["#"] = td.get_text(strip=True).replace(".", "")

                elif index == col_index_site:
                    row_data["site"] = td.get_text(strip=True)

                elif index == col_index_total:
                    row_data["total"] = td.get_text(strip=True)

                # else add to "cols" property of this row
                else:
                    cols_list.append(td.get_text(strip=True))

                index += 1

            row_data["cols"] = cols_list

            # Append the "local" dictionary of row data to the rows list
            my_rows.append(row_data)

        return my_rows


    def __get_column_totals__(self, rows, column_names):
        """
        init totals as list of counts, as many as there col_site +1, nlength-2
        or, just init list as big as headers, and incement only if sub-index (col-index) is NOT one of saved

        for row in rows:
            accumulate totals for each column of data cols in row
            only do the cols aith data
            which is determined by the headers(?) i think
            or just do it by coluymn:
            - sk

        """

        # seed totals array with zeroes for each column
        totals = [0] * len(rows[0]["cols"])

        # Loop through each row and sum the elements
        for row in rows:
            for i, value in enumerate(row["cols"]):
                # Remove commas and convert the value to an integer before adding
                totals[i] += int(value.replace(",", ""))

        return totals

