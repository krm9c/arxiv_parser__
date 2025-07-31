# automated-arxiv-search

This repository contains a simply python script that selects relevant abstracts from the daily arxiv digest.


## Requirements/Disclaimer

You need to have python3 installed on your system for this script to run. The script was optimized for python3.11. Other versions might be unstable. 

The script requires the following packages to run:


**pandas** (optimized for version 1.5.3) \
**numpy** (optimized for version 1.24.1)


You can install them with


_python3 -m pip install pandas_ \
_python3 -m pip install numpy_


## Usage

To use this script, follow these simple steps.


1.  Download all the arxiv digest emails you are interested in parsing. Put the corresponding .eml files in the folder "queue".


2. Edit the file "keyword_list.txt" with the keywords you would like the script to search for. Both the title and the abstract of the papers will be parsed for these keywords. Write one keyword per line. Keywords can be composed of more than one word. The current version does not perfom natural language processing analysis, thus similar words must be added in full. Example:


topology \
topological \
topological insulator \
topological superconductor


3. Run


_python3 arxivsearch.py_


The script should do everything on its own. The information about the papers matching your queries is stored in relevant_preprints as .csv files. The filenames are dated with the date of submission. You can open these files with spreadsheet editors like Excel or Numbers.
The entries are ordered based on the number of hits in your keyword list and contain information about authorship, submission time etc. in separate columns. 


4. That's it! Parsed emails are automatically moved to the folder "archive". You can delete these files if you want to. 

Note: The folder "all_preprints" contains .csv files of *all* the parsed papers, independently whether they matched with your keywords or not.


## Authors and acknowledgment

Paolo Molignini, University of Stockholm.  

Please acknowledge the authors if you use and/or fork this repository.


## License

GNU General Public License
