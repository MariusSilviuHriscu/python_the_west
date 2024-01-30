import re
import time
import typing
from bs4 import BeautifulSoup
from dataclasses import dataclass
import os

from requests_handler import requests_handler


def extract_items(input_js_string:str) -> typing.Dict[int,int]:
    """
    Extracts the item data from a JavaScript string.
    
    Args:
    - input_js_string: the JavaScript string to extract the data from.
    
    Returns:
    - a dictionary mapping item IDs to the number of each item obtained.
    """
    
    # Compile regular expressions for finding the item data in the string
    item_pattern = r"ItemManager\.get\((.*?)\)"
    number_of_items_pattern = r"setCount\((.*?)\)"
    
    # Find all instances of the item and number of items data in the string
    items = re.findall(item_pattern, input_js_string)
    number_of_items = re.findall(number_of_items_pattern, input_js_string)
    
    # Initialize an empty dictionary to store the results
    results = {}
    
    # Iterate through the item and number of items data, adding each item and its count to the dictionary
    for number,item in zip(number_of_items,items):
        results[int(item)] = int(number)
        
    # Return the dictionary
    return results
def extract_job_xhtml_data(input_xhtml:str)->typing.Dict[str,int]:
    """
    Extract job data from the input xhtml string and return a dictionary with the extracted data.
    Parameters:
    - input_xhtml (str): The input xhtml string containing the job data to be extracted.

    Returns:
    - data (dict): A dictionary containing the extracted job data, with the keys being the names of the data and the values being the corresponding values.
    """
    # Remove all characters that are not word characters, white space, angle brackets, or the slash or equals signs.
    cleaned_html = re.sub(r'[^\w\s<>\/="]', '', input_xhtml).format()
    # Create a BeautifulSoup object from the cleaned html string
    report_soup = BeautifulSoup(cleaned_html, 'html.parser')
    
    # Initialize an empty dictionary to store the extracted data
    data = {}
    
    # Find all elements with the class 'rp_row_jobdata'
    data_to_extract = report_soup.find_all(class_='rp_row_jobdata')
    
    # Iterate over the found elements
    for piece_of_data in data_to_extract:
        # Find the element with the class 'rp_jobdata_label_icon'
        label_icon = piece_of_data.find(class_='rp_jobdata_label_icon')
        # Extract the 'src' attribute of the img element within the label_icon element
        icon_src = label_icon.img['src']
        # Extract the base name of the src path and remove the 'png' string
        icon_name = os.path.basename(icon_src).replace("png","")
        # Find the element with the class 'rp_jobdata_label' and extract its text
        label = piece_of_data.find(class_='rp_jobdata_label').text
        # Find the element with the class 'rp_jobdata_text' and extract its text
        value = piece_of_data.find(class_='rp_jobdata_text').text
        
        # Add the extracted data to the dictionary, using the icon_name as the key and the value as the value
        data[icon_name] = value
        
    # Return the dictionary with the extracted data
    return data
@dataclass
class Job_report_reward_data():
    """
    A data class representing the rewards data for a job report.
    
    Fields:
    - job_duration: typing.Union[15,600,3600]
        The duration of the job in seconds. Can be 15, 600, or 3600.
    - experience: int
        The amount of experience gained from the job.
    - dollars: int
        The amount of dollars gained from the job.
    - luck: int
        The value of items dropped gained from the job.
    - oup: int
        The OUP points gained from the job.
    - item_drop: typing.Dict[int,int]
        A dictionary of items dropped during the job, with keys being the item IDs and values being the quantities.
    """
    job_duration : int
    experience : int
    dollars : int
    luck : int
    oup : int
    item_drop : typing.Dict[int,int]
    def __add__(self, other: "Job_report_reward_data") -> "Job_report_reward_data":
        """
        Overloads the `+` operator to allow adding two `Job_report_reward_data` objects together.
        
        Args:
        - other: the `Job_report_reward_data` object to add to this object.
        
        Returns:
        - a new `Job_report_reward_data` object containing the combined rewards from both objects.
        """
        # Add the job durations.
        job_duration = self.job_duration + other.job_duration
        
        # Add the experience points.
        experience = self.experience + other.experience
        
        # Add the dollars.
        dollars = self.dollars + other.dollars
        
        # Add the luck points.
        luck = self.luck + other.luck
        
        # Add the OUP points.
        oup = self.oup + other.oup
        
        # Create a new empty dictionary to store the combined item drop data.
        item_drop = {}
        
        # Iterate through the keys in both dictionaries.
        for key in set(self.item_drop.keys()).union(other.item_drop.keys()):
            # If the key exists in both dictionaries, add the values together.
            if key in self.item_drop and key in other.item_drop:
                item_drop[key] = self.item_drop[key] + other.item_drop[key]
            # If the key only exists in one dictionary, use the value from that dictionary.
            elif key in self.item_drop:
                item_drop[key] = self.item_drop[key]
            elif key in other.item_drop:
                item_drop[key] = other.item_drop[key]
        
        # Return a new `Job_report_reward_data` object with the combined values.
        return Job_report_reward_data(
            job_duration=job_duration,
            experience=experience,
            dollars=dollars,
            luck=luck,
            oup=oup,
            item_drop=item_drop
        )

@dataclass
class Report_data :
    """
    A data class representing a report.
    
    Fields:
    - report_type: str
        The type of the report.
    - date_received: str
        The date the report was received.
    - isOwnReport: bool
        Whether the report is owned by the current player.
    - report_id: int
        The ID of the report.
    - publishHash: str
        The hash of the report.
    - publishMode: typing.Union[0,1,2,3]
        The publish mode of the report. Can be 0, 1, 2, or 3.
    - title: str
        The title of the report.
    - js: str
        A string containing JavaScript code.
    - page: str
        A string containing HTML code.
    - xhtml: str
        A string containing XHTML code.
    - reportInfo: dict
        A dictionary containing information about the report.
    """
    report_type:str
    date_received:str
    isOwnReport:bool
    owner_id : int
    owner_name : str
    report_id:int
    publishHash:str
    publishMode: int
    title:str
    js:str
    page:str
    xhtml:str
    reportInfo:dict
    
    def __repr__(self):
        """
        Returns a string representation of the object.
        """
        return f"{self.report_type}({self.report_id})"
    
    def __str__(self):
        """
        Returns a human-readable string representation of the object.
        """
        return f"{self.report_type}({self.report_id})"
    
    @property
    def own_report(self):
        """
        Returns the value of the `isOwnReport` field.
        """
        return self.isOwnReport
    
class Job_report_data(Report_data):
    """
    A subclass of `Report_data` representing a job report.
    """
    def __init__(self,**kwargs):
        """
        Initializes the object and calls the `__init__` method of the parent class.
        
        Parameters:
        - **kwargs: dict
            Keyword arguments to pass to the parent class's `__init__` method.
        """
        super().__init__(**kwargs)
    
    def decrypt_job_data(self)->Job_report_reward_data:
        """
        Extracts data from the `js` and `xhtml` fields of the object and returns a `Job_report_reward_data` object with the extracted data.
        
        Raises:
        - Exception: if the `clock`, `star`, `dollar`, `luck`, or `upb` keys are not present in the extracted data.
        
        Returns:
        - Job_report_reward_data: the extracted data as a `Job_report_reward_data` object.
        """
        # Extract data from the 'js' field using the 'extract_items' function
        job_data_item_reward_dict = extract_items(input_js_string=self.js)
        
        # Extract data from the 'xhtml' field using the 'extract_job_xhtml_data' function
        job_reward_dict = extract_job_xhtml_data(input_xhtml=self.xhtml)
        
        # Check if the 'clock', 'star', 'dollar', 'luck', and 'upb' keys are present in the extracted data
        if 'clock' not in job_reward_dict:
            raise Exception("No clock key in dict")
        if 'star' not in job_reward_dict:
            raise Exception("No star key in dict")
        if 'dollar' not in job_reward_dict:
            raise Exception("No dollar key in dict")
        if 'luck' not in job_reward_dict:
            raise Exception("No luck key in dict")
        if 'upb' not in job_reward_dict:
            raise Exception("No upb key in dict")
        
        # Return a 'Job_report_reward_data' object with the extracted data
        return Job_report_reward_data(
            #This field is set to 15 if the clock key in the extracted data contains the character 's', 3600 if it contains the character 'h', or 600 otherwise.
            job_duration = 15 if 's' in job_reward_dict['clock'] else 3600 if 'h' in job_reward_dict['clock'] else 600 ,
            #This field is set to an integer obtained by applying a lambda function to the value of the star key in the extracted data. 
            #The lambda function removes all non-digit characters from the value, and then returns the resulting string as an integer.
            experience = int ( (lambda s: ''.join(c for c in s if c.isdigit()))(job_reward_dict['star'])) ,
            #This field is set to an integer obtained by splitting the value of the dollar key in the extracted data at the space character, 
            # and then taking the second element of the resulting list and converting it to an integer.
            dollars= int( job_reward_dict['dollar'].split(" ")[1] ) ,
            #This field is set to an integer obtained by stripping leading and trailing white space from the value of the luck key in the extracted data and converting it to an integer.
            luck = int(job_reward_dict['luck'].strip() ) ,
            oup= int(job_reward_dict['upb'].strip() ) ,
            item_drop= job_data_item_reward_dict
        )

class Other_report_data(Report_data):
    """
    Subclass of `Report_data` for reports that are not job reports.
    """
    
    def __init__(self,**kwargs):
        """
        Initializes the object by calling the parent class's `__init__` method with the keyword arguments passed to it.
        """
        super().__init__(**kwargs)
@dataclass
class Report():
    """
    Class representing a report.
    """
    
    report_id : int
    """The ID of the report."""
    
    data_id : int
    """The data ID of the report."""
    
    date_received : str
    """The date the report was received, as a string."""
    
    hash : str
    """The hash of the report."""
    
    popup_data : str
    """The popup data of the report."""
    
    read : bool
    """A boolean indicating whether the report has been read."""
    
    title : str
    """The title of the report."""
    
    publish_mode : int
    """The publish mode of the report, as a union of 0, 1, 2, or 3."""
    
    def read_report(self, handler:requests_handler) -> None :
        """
        Reads the report.
        
        Args:
        - handler: an object that can send HTTP requests.
        
        Raises:
        - Exception: if the report could not be read.
        
        Returns:
        - None
        """
        # Send a request to read the report
        response = handler.post(
            window= "reports",
            action= "show_report",
            action_name= "mode",
            payload= {
                'report_id': f'{self.report_id}' ,
                'hash': f'{self.hash}' ,
                'animated': '0' }
        )
        
        # Check if the request was successful
        if 'report_id' not in response and response['report_id'] != self.report_id:
            raise Exception('Could not read report')
            
        # Determine the correct class to use for the report data
        correct_report_data_class = Job_report_data if response["reportType"] == "job" else Other_report_data
        
        # Return an instance of the correct report data class
        return correct_report_data_class(
                    report_type = response['reportType'],
                    date_received = response['date_received'],
                    isOwnReport = response['isOwnReport'],
                    owner_id = response['ownerId'],
                    owner_name = response['ownerName'],
                    report_id = response['report_id'],
                    publishHash = response['publishHash'],
                    publishMode = response['publishMode'],
                    title = response['title'],
                    js = response['js'],
                    page = response['page'],
                    xhtml = response['xhtml'],
                    reportInfo = response['reportInfo'],
                )
class Reports_list():
    """
    Class representing a list of reports.
    """
    
    def __init__(self,report_list:typing.List[Report]) :
        """
        Initializes the object with a list of `Report` objects.
        
        Args:
        - report_list: a list of `Report` objects.
        
        Returns:
        - None
        """
        self.reports = report_list
        
    def __iter__(self):
        """
        Makes the object iterable.
        
        Returns:
        - an iterator over the `Report` objects in the list.
        """
        return iter(self.reports)
        
    def __add__(self,other):
        """
        Overloads the `+` operator to allow adding `Reports_list` objects, `Report` objects, or lists of `Report` objects.
        
        Args:
        - other: the object to add.
        
        Raises:
        - TypeError: if `other` is not a `Reports_list`, `Report`, or list of `Report` objects.
        
        Returns:
        - a new `Reports_list` object containing the combined list of `Report` objects.
        """
        if isinstance(other,Reports_list):
            return Reports_list(self.reports + other.reports)
        elif isinstance(other,Report):
            return Reports_list(self.reports + [other])
        elif isinstance(other,list) and len(other) != 0 and isinstance(other[0],Report):
            return Reports_list(self.reports + other)
        else:
            raise TypeError("Can only add Reports_list, Report or list of Report")
        
    def __len__(self):
        """
        Overloads the `len` function to return the number of `Report` objects in the list.
            
        Returns:
        - the number of `Report` objects in the list.
        """
        return len(self.reports)
            
    def get_unread_reports(self):
        """
        Returns a new `Reports_list` object containing only the unread `Report` objects in the list.
        
        Returns:
        - a new `Reports_list` object containing only the unread `Report` objects in the list.
        """
        return Reports_list([report for report in self.reports if not report.read])
    def __str__(self):
        """
        Returns a human-readable string representation of the object.
        
        Returns:
        - a string representation of the object.
        """
        return f"Reports_list with {len(self.reports)} reports"
        
    def __repr__(self):
        """
        Returns a string representation of the object that can be used to recreate the object.
        
        Returns:
        - a string representation of the object.
        """
        return f"Reports_list({self.reports})"
    def __getitem__(self, index:typing.Union[int,slice]) -> typing.Union[Report,typing.Self]:
        """
        Returns the `Report` object at the given index, or a new `Reports_list` object containing a slice of the list.
        
        Args:
        - index: the index of the `Report` object to return, or a slice object.
        
        Returns:
        - the `Report` object at the given index, or a new `Reports_list` object containing a slice of the list.
        """
        if isinstance(index, int):
            return self.reports[index]
        elif isinstance(index, slice):
            return Reports_list(self.reports[index])
    def job_rewards(self, handler: requests_handler) -> Job_report_reward_data:
        """
        Returns the combined rewards from all job reports in the list.
        
        Args:
        - handler: a `requests_handler` object to use for making HTTP requests.
        
        Returns:
        - a `Job_report_reward_data` object containing the combined rewards from all job reports in the list.
        """
        # Create a new `Job_report_reward_data` object to store the combined rewards.
        reward = Job_report_reward_data(
            job_duration=0,
            experience=0,
            dollars=0,
            luck=0,
            oup=0,
            item_drop={},
        )
        
        # Iterate through the `Report` objects in the list.
        for report in self.reports:
            # Read the report using the provided `handler`.
            read_report = report.read_report(handler=handler)
            
            # If the report is a job report, decrypt the report data and add the rewards to the `reward` object.
            if isinstance(read_report, Job_report_data):
                reward += read_report.decrypt_job_data()
        
        # Return the `reward` object.
        return reward


class Reports_data_reader():
    """A class for reading reports data.

    Attributes:
        handler: An instance of the requests_handler class.

    Methods:
        __init__: Initializes the Reports_data_reader instance.
        get_data_by_page: Gets reports data for a given page number.
        get_data: Gets all reports data (optionally reading all pages).
    """
    def __init__(self, handler: requests_handler) :
        """Initializes the Reports_data_reader instance.

        Args:
            handler: An instance of the requests_handler class.
        """

        self.handler = handler
    def get_data_by_page(self, page_number: int) -> typing.Dict[str, typing.Union[int, Reports_list]]:
        """Gets reports data for a given page number.
        Args:
            page_number: An integer representing the page number to get reports data for.

        Returns:
            A dictionary containing the total number of pages and a list of reports data for the given page number.

        Raises:
            Exception: If there is an error getting the reports data for the given page number.
        """

        # Make a post request to get the reports data for the given page number
        response = self.handler.post(
            window="reports",
            action="get_reports",
            payload={
                "page": f"{page_number}",
                "folder": "all",
            },
            use_h=True,
        )

        # Raise an exception if there is an error getting the reports data for the given page number
        if response["error"]:
            raise Exception(
                f"Getting the reports data for the page number {page_number} did not work!"
            )

        # Create a list of Report instances using the reports data from the response
        reports_list = []
        for report in response["reports"]:
            report = Report(
                report_id = report['report_id'],
                data_id = report['data_id'],
                date_received = report['date_received'],
                hash = report['hash'],
                popup_data = report['popupData'],
                read = report['read'],
                title = report['title'],
                publish_mode = report['publish_mode']
            )
            reports_list.append(report)
        # Return the total number of pages and the list of Report instances
        return {"num_max_pages": response["count"], "reports_list": Reports_list(reports_list)}
    def get_data(self, read_all_pages: bool = False):
        """Gets all reports data (optionally reading all pages).
        Args:
            read_all_pages: A boolean indicating whether to read all pages of reports data (defaults to False).

        Returns:
            A list of reports data.
        """

        # Get the reports data for the first page
        first_page_response = self.get_data_by_page(page_number=1)

        # Initialize the reports_list with the reports data from the first page
        reports_list = first_page_response["reports_list"]

        # If read_all_pages is True, get the reports data for all pages and append it to the reports_list
        if read_all_pages:
            for i in range(2, first_page_response["num_max_pages"] + 1):
                page_response = self.get_data_by_page(page_number=i)
                reports_list += page_response["reports_list"]

        # Return the reports_list
        return reports_list
    def read_pages_until_id(self, report_id: int) -> Reports_list:
        """
        Reads pages of reports data until a report with the given report ID is found.
        
        Args:
        - report_id: the ID of the report to search for.
        
        Returns:
        - a `Reports_list` object containing all of the reports read up until the report with the given report ID is found.
        """
        # Initialize the page number, num_max_pages, and reports_list
        page_number = 1
        num_max_pages = 1
        reports_list = Reports_list([])
        
        # Keep reading pages until the report with the given report ID is found or all pages have been read
        while page_number <= num_max_pages:
            # Get the reports data for the current page
            page_response = self.get_data_by_page(page_number=page_number)
            
            # Update the num_max_pages
            num_max_pages = page_response["num_max_pages"]
            
            # Iterate through the reports in the current page
            for report in page_response["reports_list"]:
                # If the report has the given report ID, return the reports_list
                if report.report_id == report_id:
                    return reports_list
                # Otherwise, add the report to the reports_list
                else:
                    reports_list += report
            
            # Increment the page number
            page_number += 1
        
        # If the report with the given report ID is not found, return the reports_list
        return reports_list

class Reports_manager():
    """
    Class representing a manager for reading reports.
    """
    def __init__(self, handler: requests_handler, last_read_report_id: int = None):
        """
        Initializes the object with a requests_handler object, and the ID of the last read report.
        
        Args:
        - handler: an object that can send HTTP requests.
        - last_read_report_id: the ID of the last read report. If None, it will be set to the ID of the last report in the data.
        
        Returns:
        - None
        """
        self.handler = handler
        self.reader = Reports_data_reader ( handler = handler)
        if last_read_report_id is None :
            self.last_read_report_id = self.reader.get_data()[0].report_id
        else :
            self.last_read_report_id = last_read_report_id
        
        
        self.rewards = Job_report_reward_data(
                        job_duration = 0,
                        experience = 0,
                        dollars = 0,
                        luck = 0,
                        oup = 0,
                        item_drop = {}
                    )
    
    def _set_last_read_report_id(self, report_id:int) -> None:
        """
        Sets the ID of the last read report.
        
        Args:
        - report_id: the ID of the last read report.
        
        Returns:
        - None
        """
        self.last_read_report_id = report_id
    #def _read_reports(self) -> Job_report_reward_data:
    #    """
    #    Reads reports until it reaches the ID of the last read report, updates the last read report ID with the ID of the first unread report, and returns the job rewards data.
    #    
    #    Returns:
    #    - Job_report_reward_data: the rewards data for the read job reports.
    #    """
    #    # Step 1: Read reports until the ID of the last read report is reached
    #    new_data = self.reader.read_pages_until_id(self.last_read_report_id)
    #    # Step 2: Update the last read report ID with the ID of the first unread report
    #    if len(new_data) != 0:
    #        print('found new reports...working fine')
    #        self._set_last_read_report_id(report_id= new_data[0].report_id)
    #        # Step 3: Get the rewards data for the new job reports
    #        new_rewards = new_data.job_rewards( handler=self.handler)
    #        # Step 4: Add the new rewards data to the rewards variable
    #        self.rewards += new_rewards
    #        # Step 5: Return the rewards data for the read job reports
    #        return self.rewards
    #    return self.rewards
    def _read_reports(self, retry_times: int = 0) -> Job_report_reward_data:
        """
        Reads reports until it reaches the ID of the last read report, updates the last read report ID with the ID of the first unread report,
        and returns the job rewards data. Retries the read operation if new_data is empty.
        
        Args:
        - retry_times: the number of times to retry if new_data is empty. Default is 0.
        
        Returns:
        - Job_report_reward_data: the rewards data for the read job reports.
        """
        # Step 1: Read reports until the ID of the last read report is reached
        new_data = self.reader.read_pages_until_id(self.last_read_report_id)
        
        # Step 2: Retry if new_data is empty and retries are allowed
        while retry_times > 0 and len(new_data) == 0:
            print('Retrying read operation...')
            time.sleep(1)  # Wait for 1 second
            new_data = self.reader.read_pages_until_id(self.last_read_report_id)
            retry_times -= 1

        # Step 3: Update the last read report ID with the ID of the first unread report
        if len(new_data) != 0:
            print('Found new reports...working fine')
            self._set_last_read_report_id(report_id=new_data[0].report_id)
            
            # Step 4: Get the rewards data for the new job reports
            new_rewards = new_data.job_rewards(handler=self.handler)
            
            # Step 5: Add the new rewards data to the rewards variable
            self.rewards += new_rewards
            
        # Step 6: Return the rewards data for the read job reports
        return self.rewards
