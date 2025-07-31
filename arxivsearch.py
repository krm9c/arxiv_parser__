##########################################################################################
# This python programs selects relevant abstracts from the daily arxiv digest.
###########################################################################################

#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
import os
import re
import sys
import time
import glob
import shutil
import numpy as np
import pandas as pd
import glob

np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(linewidth=1000)

__author__      =   "Paolo Molignini"
__copyright__   =   "Copyright 2022, University of Cambridge"
__version__     =   "1.0.1"


####################
# GLOBAL VARIABLES
####################

preprint_delimiter = "----------"
replaced_preprints_delimiter = "%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%"
keyword_list_filename = "keyword_list.txt"



##############################################################################
def get_files(verbose):
    """
    Returns a list with all the files to parse.
    
    """

    list_of_files_with_path = []
    folder = os.getcwd()
    list_of_files = glob.glob("queue/" + '*.eml')
    
    for file in list_of_files:
        if verbose==True:
            print(f"Working on file {file}")
        list_of_files_with_path.append(folder + "/" + str(file))
    return list_of_files_with_path
##############################################################################


##############################################################################
def read_through_file(filename, verbose=True):
    """
    Returns a list containing the text corresponding to each preprint.
    
    """
    
    # Counters, variables etc:
    del_counter = 0
    preprint = ""
    preprints = []
    save_line = False

    # Display some information:
    print("================================")
    print(f"Reading through file {filename}...")
    print("================================")
    # Open the file:
    # Read file line by line:
    with open(filename, "r") as file:
        for line in file:
            # print(line)
            if preprint_delimiter in line:
                del_counter+=1
                if del_counter>=10:
                    save_line = True
            # After the sixth delimiter, start saving the file content into a string
            # (this is where the preprints begin):
            # Add line by line to the current preprint string:
            if save_line==True:
                preprint = preprint + line
                if preprint_delimiter in line and del_counter >= 10:
                    if verbose:
                        print(f"preprint number {del_counter - 9}")
                        print("========================================")
                        print(preprint)
                        print("========================================")                 
                    preprints.append(preprint)
                    preprint = ""
            if replaced_preprints_delimiter in line:
                break
    # Display some information:
    # print(f"Parsed {del_counter} total preprints.")
    return preprints
##############################################################################

##############################################################################
def create_basic_dataframe(preprints, verbose):
    """
    Creates basic dataframe from all preprints in files.
    
    """
    
    # Counters, variables, lists etc.
    arxiv_num = ""
    date = ""
    title = ""
    authors = ""
    categories = ""
    comments = ""
    abstract = ""
    
    arxiv_num_list = []
    date_list = []
    title_list = []
    authors_list = []
    categories_list = []
    abstract_list = []
    comments_list = []
    
    token = None
    break_counter = 0
    double_slash_counter = 0
    PreprintsDf = pd.DataFrame()
    
    # Display some information:
    print("================================")
    print("  Creating basic dataframe...   ")
    print("================================")

    
    # Loop over all preprints parsed before:
    for p, preprint in enumerate(preprints):

        # Loop over every line in each preprint entry:
        for line in preprint.split("\n"):
            
            # Count the number of line breaks:
            break_counter += 1
            
            # Count the number of \\\\ in the file
            # (they indicate certain pieces of information):
            if "\\\\" in line:
                double_slash_counter += 1

            # Save the content of the line in different tokens:
            if "Title" in line:
                token = "title"
            elif "Authors" in line:
                token = "authors"
            elif "Categories" in line:
                token = "categories"
            elif "Comments" in line:
                token = "comments"
            if double_slash_counter==2:
                token = ""
                if line == "\\\\":
                    continue
                else:
                    abstract = abstract + line + " "
                
            # Save the parsed lines in different variables depending on
            # what they refer to:
            if break_counter==2:
                arxiv_num = arxiv_num + line
            if break_counter==3:
                date = date + line
            if token == "title":
                title = title + line
            elif token == "authors":
                authors = authors + line
            elif token == "categories" and double_slash_counter==1:
                categories = categories + line
            elif token == "comments" and double_slash_counter==1:
                comments = comments + line + " "
                   
        # Appending lines to the different lists:
        date_list.append(date.replace("Date: ",""))
        arxiv_num_list.append(arxiv_num)
        title_list.append(title.replace("Title: ",""))
        authors_list.append(authors.replace("Authors: ",""))
        categories_list.append(categories.replace("Categories: ",""))
        comments_list.append(comments.replace("Comments: ",""))
        abstract_list.append(abstract.replace("Abstract: ",""))

        # Create the dictionary to append to the dataframe:
        preprint_dict = {"date": date.replace("Date: ","")[:29],
                         "arxiv_num": arxiv_num,
                         "title": title.replace("Title: ",""),
                         "authors": authors.replace("Authors: ",""),
                         "categories": categories.replace("Categories: ",""),
                         "comments": comments.replace("Comments: ",""),
                         "abstract": abstract.replace("Abstract: ","")
                }
        CurrentPreprintDf = pd.DataFrame([preprint_dict])
        PreprintsDf = pd.concat([PreprintsDf, CurrentPreprintDf], ignore_index=True)

        # Resetting the variables and counters:
        arxiv_num = ""
        date = ""
        title = ""
        authors = ""
        categories = ""
        comments = ""
        abstract = ""
        break_counter = 0
        double_slash_counter = 0
        
        # Output some information:
        if verbose==True:
            print("========================================")
            print(f"Date: {date_list[p]}")
            print(f"ID: {arxiv_num_list[p]}")
            print(f"Title: {title_list[p]}")
            print(f"Authors: {authors_list[p]}")
            print(f"Categories: {categories_list[p]}")
            print(f"Comments: {comments_list[p]}")
            print(f"Abstract: {abstract_list[p]}")
            print("========================================")

    # Define a filename with the date of the first entry
    print(date_list)
    filename = "all_preprints_" + str(date_list[3])[:16].replace(" ", "_") + ".csv"
    # check if folder dataframes exists:
    if not os.path.exists(os.getcwd() + "/all_preprints/"):
        os.mkdir("all_preprints")

    # Save data to dataframe
    PreprintsDf.to_csv(os.getcwd() + "/all_preprints/" + filename)

    return filename
##############################################################################



##############################################################################
def create_relevant_dataframes(all_preprints_filename):
    """
    Creates a relevant dataframe that contains only preprints which mention the given keywords
    and saves it into a .csv file.
    
    """

    # Read in keyword list:
    keywords = open(keyword_list_filename, "r")
    
    # Output some information:
    print("================================")
    print(" Creating relevant dataframe... ")
    print("================================")
    print(all_preprints_filename)
    # Read in .csv file containing all parsed preprints:
    RelevantPreprintsDf = pd.read_csv(os.getcwd() + "/all_preprints/" + all_preprints_filename)
    
    # Iterate over all keywords:
    for keyword in keywords:
        #Remove linebreak:
        keyword = keyword.replace("\n", "")
        print(keyword)
        # Check if the keywords are present in each title:
        for t, title in RelevantPreprintsDf["title"].items():
            if title is np.nan: 
                # If the title is NaN, skip this iteration:
                continue    
            # Add keyword column if it doesn't exist and fill it with one/zero
            # depending whether the keyword is matched or not:
            if keyword not in RelevantPreprintsDf.columns:
                # first creates a column filled with zero for the corresponding keyword
                # if it doesn't exist
                RelevantPreprintsDf[keyword] = np.zeros(len(RelevantPreprintsDf)).tolist()
                # If the keyword is in the title, add one to the corresponding keyword column
                if re.search(keyword, title, re.IGNORECASE):
                    RelevantPreprintsDf.loc[RelevantPreprintsDf.index[t], keyword] = 1

            else:
                # Otherwise add one to the row to count numbers of keywords mentioned if
                # matched (do nothing if no match is found):
                if re.search(keyword, title, re.IGNORECASE):
                    RelevantPreprintsDf.loc[RelevantPreprintsDf.index[t], keyword] += 1

        # Same procedure for the abstract:
        for a, abstract in RelevantPreprintsDf["abstract"].items():
            if abstract is np.nan:
                # If the abstract is NaN, skip this iteration:
                continue
            
            if keyword not in RelevantPreprintsDf.columns:
                RelevantPreprintsDf[keyword] = np.zeros(len(RelevantPreprintsDf)).tolist()
                if re.search(keyword, abstract, re.IGNORECASE):
                    RelevantPreprintsDf.loc[RelevantPreprintsDf.index[a], keyword] = 1
            else:
                if re.search(keyword, abstract, re.IGNORECASE):
                    RelevantPreprintsDf.loc[RelevantPreprintsDf.index[a], keyword] += 1
    
    # Replace all NaN's with zeros
    RelevantPreprintsDf = RelevantPreprintsDf.fillna(0)
    
    # Get only keywords columns:
    KeywordsDf = RelevantPreprintsDf.iloc[:,8:]
    # Construct a boolean version of the keyword dataframe:
    BooleanKeywordsDf = (KeywordsDf == 0)
    
    # Remove all entries (rows) which have no matches with the keywords:
    for i in range(len(BooleanKeywordsDf)):

        # Remove the rows only if all the keyword columns are == 0:
        boolean_row = BooleanKeywordsDf.iloc[[i]].all(axis=1)
        if boolean_row[i] == True:
            RelevantPreprintsDf.drop(i, inplace=True)
    
    # Drop the first column of the preprint (index) and reset the index:
    RelevantPreprintsDf.drop(columns=RelevantPreprintsDf.columns[0], axis=1, inplace=True)
    RelevantPreprintsDf.reset_index()
    
    # Count total number of keyword occurrence for every row:
    keyword_count = np.sum(KeywordsDf.applymap(lambda x: 1 if int(x)>=1 else 0), axis=1)
    
    # Sort all rows in terms of how many total keywords were mentioned:
    RelevantPreprintsDf["keyword count"] = keyword_count
    RelevantPreprintsDf = RelevantPreprintsDf.sort_values("keyword count", ascending=False)

    # Create the filename for the current file:
    filename = "relevant_preprints_" + all_preprints_filename[-20:]
    filename_with_path = os.getcwd() + "/relevant_preprints/" + filename

    # Check if folder where to save processed dataframe exists, if not create it:
    if not os.path.exists(os.getcwd() + "/relevant_preprints/"):
        os.mkdir("relevant_preprints")

    # Save data to dataframe
    RelevantPreprintsDf.to_csv(filename_with_path, index=False)

    # Output some information:
    print("================================")
    print(f" Created relevant .csv file {filename_with_path}. ")
    print("================================")

    return
##############################################################################

def merge_csvs_and_remove_duplicates(directory, output_filename, subset=None):
    """
    Merges all CSV files in the given directory, removes duplicates, and saves the result.
    :param directory: Directory containing CSV files.
    :param output_filename: Output CSV filename.
    :param subset: List of columns to consider for identifying duplicates (optional).
    """
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    df_list = []
    for file in csv_files:
        df = pd.read_csv(file)
        df_list.append(df)
    if not df_list:
        print("No CSV files found in the directory.")
        return
    print(df.columns.tolist())
    merged_df = pd.concat(df_list, ignore_index=True)
    merged_df = merged_df.drop_duplicates(subset=subset)
    print(merged_df.columns.tolist())
    merged_df = merged_df.drop(['date', 'categories', 'comments', 'arxiv_num', 'abstract'], axis=1)
    merged_df.to_csv(os.path.join(directory, output_filename), index=False)
    print(f"Merged {len(csv_files)} files into {output_filename} with {len(merged_df)} unique rows.")






if __name__ == "__main__":

    # Check if folder where to archive processed data exists, if not create it:
    if not os.path.exists(os.getcwd() + "/archive/"):
        os.mkdir("archive")
    folder = os.getcwd()

    # Get the list of files to process:
    list_of_files = get_files(verbose=True)
    for file in list_of_files:
    
        # Parse the preprint .eml file:
        preprints = read_through_file(filename=file, verbose=False)
        if len(preprints) == 0:
            print(f"File {file} is empty, skipping...")
            continue
        
        # Create the dataframe from the parsed .eml file:
        all_preprints_filename = create_basic_dataframe(preprints=preprints, verbose=False)
        
        # Select only relevant entries and put them into the final dataframe:
        create_relevant_dataframes(all_preprints_filename=all_preprints_filename)
        
        # Put scraped files into archive:
        shutil.move(file, folder + "/archive/" + os.path.basename(file))

    merge_csvs_and_remove_duplicates("relevant_preprints", "merged_preprints.csv", subset=["title"])
