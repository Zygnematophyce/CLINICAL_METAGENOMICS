#coding: utf-8

"""
@author : Zygnematophyce
July. 2020
CLINICAL METAGENOMICS

Program get_list_of_classified_organism.py (obsoletes names GetIntFasta3.py or
get_id_taxo_from_report.py) is a script which makes it possible to retrieve the
sequence IDs (e.g NB552188:4:H353CBGXC:2:23310:15171:17832), obtained from the
FASTA / FASTQ header from either a particular taxon (example bacteria, virus)
or from all the classified sequences.

The output file therefore contains a list of all the id of selected sequences
in text format (e.g: -output_list results/list_taxon/bacteria.lst)
"""

import argparse
import os
import re
import sys


def arguments():
    """ Method that define all arguments ."""

    parser = argparse.ArgumentParser(description="get_list_of_classified_organism.py")

    parser.add_argument("-path_report",
                        help="(Input) The path of the *.report.txt file provided" \
                        " by the classification of kraken 2",
                        type=str)
    parser.add_argument("-path_output",
                        help="(Input) The path of the *.output.txt file provided" \
                        " by the classification of kraken 2",
                        type=str)
    parser.add_argument("-taxon",
                        help="(Input) Can specified a taxon e.g (Bacteria, Viruses)",
                        type=str)
    parser.add_argument("-output_list",
                        help="(Output) The path of the output text file which will" \
                        " contain only the classified sequences",
                        type=str)
    args = parser.parse_args()

    return args.path_report, args.path_output, args.taxon, args.output_list


def get_correct_taxon(taxon):
    """Check that this is the correct taxon based on top level of the taxonomy
    database by NCBI at https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi
    """

    list_taxon = ["Archaea",
                  "Viruses",
                  "Eukaryota",
                  "other sequences",
                  "cellular organisms",
                  "Bacteria",
                  "Fungi"]

    taxon_correct = ""

    for i, element in enumerate(list_taxon):
        if taxon.lower() in element.lower():
            taxon_correct = list_taxon[i]
            break

    if taxon_correct == "":
        print(list_taxon)
        sys.exit("You specified a taxon which is not part of the list. Exit!")

    return taxon_correct


def create_output_folder(filename):
    """ Method that create output folder."""

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise


def create_output_list_file(filename, header_sequences_id):
    """ Method that create the output list file."""

    try:
        with open(filename, "w") as output_list:
            for header in header_sequences_id:
                output_list.write(header+"\n")
    except IOError:
        print("Impossible to create output file")
        sys.exit("Error ! Can't create output file.")


def get_all_classified_organism(output_file):
    """ Method that return a list of classified organism."""

    with open(output_file) as output:
        for line in output:

            # Remove new line.
            line = line.strip()
            line_splitted = re.split(r"\t", line)

            # If each sequences is classified (classified = "C",
            # unclassified = "U"). see also standard kraken output format :
            # https://github.com/DerrickWood/kraken2/wiki/Manual#output-formats
            if line_splitted[0] == "C":
                # Display all classified sequences.
                print(line)


def get_specific_classified_taxonomic_id(report_file, taxon):
    """ Method that return a list of taxonomic id from *report.txt of Kraken 2
    for specific taxon (e.g: Bacteria) with a number of fragments assigned
    directly to this taxon > 0 """

    # Flag for the reseach of specific taxon.
    flag_domain = True

    # List of all taxonomic id.
    list_id_species = list()

    with open(report_file) as report:
        for line in report:

            # Remove new line.
            line = line.strip()

            if len(re.findall(taxon, line)) >= 1:
                #print(line)
                line_splitted = re.split(r"\t", line)
                list_id_species.append(line_splitted[4])
                while flag_domain:
                    line = report.readline()
                    # Remove new line.
                    line = line.strip()
                    line_splitted = re.split(r"\t", line)

                    # If end of file stop the process.
                    if line == "":
                        flag_domain = False
                    # Otherwise if there is another domain different from the
                    # initial taxon.
                    elif line_splitted[3] == "D" and len(re.findall(taxon, line)) == 0:
                        flag_domain = False
                        #print("stop")
                    elif line_splitted[2] != "0":
                        # Add taxonomic id in list where the number of fragments
                        # assigned directly to this taxon aren't egal to 0.
                        list_id_species.append(line_splitted[4])
                    else:
                        #print("Number of fragments assigned directly to this taxon are egal to 0")
                        continue
                #print("break")

        # If the length of list with id taxonomic egal 0.
        if len(list_id_species) == 0:
            print("Warning ! either the selected taxon '"+taxon+"' is not in " \
            "the list, or no fragment could be assigned to this taxon.")
            sys.exit("Error exit program !")

        return list_id_species


def get_all_specific_line_of_output_kraken2(taxonomic_id_list,
                                            output_kraken_file):
    """ Method that return a list of specific lines of *.output.txt from Kraken 2
    thank to all classified taxonomics id of specifis taxon """

    with open(output_kraken_file) as output_file:
        line = output_file.readline()

        # A list with all specific header sequences name from *.output.txt.
        list_header_sequences_name = list()

        while line:
            # status_classification = re.split("\t", line)[0]
            header_sequences_id = re.split("\t", line)[1]
            output_taxonomy_id = re.split("\t", line)[2]

            if output_taxonomy_id in taxonomic_id_list:
                list_header_sequences_name.append(header_sequences_id)

            # if status_classification == "U":
            #     print("problem unclassified output")
            #     print(line)

            line = output_file.readline()

    return list_header_sequences_name


if __name__ == "__main__":
    print("Get a list of classified organism !")

    # Get all parameters.
    REPORT_KRAKEN_FILE, OUTPUT_KRAKEN_FILE, TAXON, OUTPUT_LIST = arguments()

    if TAXON == None or TAXON.lower() == "all":
        print("No specific taxon was precised !")
        print("Get all classified organisms.")

        # Get all classified organisms.
        #LIST_CLASSIFIED_ORGANISM = get_all_classified_organism(OUTPUT_KRAKEN_FILE)
    else:
        # Verified the correct taxon parameter.
        TAXON = get_correct_taxon(TAXON)

        # Get all taxonomic id from specific taxon (bacteria, viral, fungi ...).
        LIST_CLASSIFIED_SPECIES = get_specific_classified_taxonomic_id(REPORT_KRAKEN_FILE,
                                                                       TAXON)

        # Recover each sequences from *output.txt of Kraken 2.
        ALL_HEADER_SEQUENCES_ID = get_all_specific_line_of_output_kraken2(LIST_CLASSIFIED_SPECIES,
                                                                          OUTPUT_KRAKEN_FILE)

        # create output folders if necessary.
        create_output_folder(OUTPUT_LIST)

        # create a output list.
        create_output_list_file(OUTPUT_LIST, ALL_HEADER_SEQUENCES_ID)

        print("Creation of list done !")
