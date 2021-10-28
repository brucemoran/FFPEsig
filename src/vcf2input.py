#! python3

import argparse
import time
import allel
import re
import concurrent.futures
import os
import sys
import pandas as pd
import numpy as np

from Bio import SeqIO
from multiprocessing import Pool

##help
parser = argparse.ArgumentParser(
    description='''Parse VCF into format for use with predict_cancer.py script ''')
parser.add_argument('--fasta', help='FASTA file for genome used to align VCF', required = True)
parser.add_argument('--vcf', help='VCF file from which to run predict_cancer.py', required = True)
parser.add_argument('--output_dir', help='Path to directory in which to write output')
parser.add_argument('--sample_name', help='Sample naming to tag output')
args=parser.parse_args()

if args.output_dir == None:
    args.output_dir = "./"

if args.sample_name == None:
    args.sample_name = "unnamed"

def reverse_complement(seq):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    reverse_complement = "".join(complement.get(base, base)
                                 for base in reversed(seq))
    return(reverse_complement)


def fasta_reader(fastafile):
    seq_list = {}
    for index, record in enumerate(SeqIO.parse(fastafile, "fasta")):
        unw = ["X", "Y", "MT", "_", "GL", "KI"]
        if not any([ss in record.name for ss in unw]):
            seq_list[record.name] = record.seq
    return(seq_list)


def vcf2df(filename, seq_list):
    # read VCF files
    # filter variants in chromosomes in fasta
    # count only SNVs
    df = allel.vcf_to_dataframe(filename, fields='*', alt_number=2)
    print("--- %s Total Variants in the VCF file ---" % len(df))
    ##test for chr on seq_list, then add if not found in VCF or vice-versa
    seq_list_chr = "TRUE"
    try:
        seq_list["chr1"]
    except KeyError:
        seq_list_chr = "FALSE"
    chr_list = list(dict.keys(seq_list))
    if df['CHROM'].iloc[0].find("chr") < 0:
        if seq_list_chr == "FALSE":
            print("Fasta and VCF have no \'chr\' prefix...")
        else:
            print("Fasta has \'chr\' prefix, but VCF doesn't, fixing...")
            df['CHROM'] = "chr" + df['CHROM']
    else:
        if seq_list_chr == "FALSE":
            print("Fasta has no \'chr\' prefix, but VCF does, fixing...")
            df['CHROM'] = df['CHROM'].str.replace("chr", "")
    vcf_df = df[(df['is_snp'] == True) & (df['CHROM'].isin(chr_list) == True)]
    print("--- %s SNVs in the VCF file ---" % len(vcf_df))
    return(vcf_df)


def df2mut(tmp1, header, seq_list, sample_name):
    # Mutation types
    # Setup Dataframe
    # load header
    mut_df_header = pd.read_csv(header)
    changes = []
    ref_vcf = []
    ref_grch = []
    tmp2 = tmp1.reset_index()
    tmp3 = tmp2.to_numpy()
    for i in range(len(tmp3)):
        ref = tmp3[i, 4]
        ch = tmp3[i, 1]
        st = tmp3[i, 2]
        alt = tmp3[i, 5]
        ref_vcf.append(ref)
        ref_base = seq_list[ch][st - 1].upper()
        ref_grch.append(ref_base)
        ref_cont = seq_list[ch][st - 2:st + 1].upper()
        if(not ref == ref_base):
            print("Mismatch in VCF and fasta genome versions, please ensure they are the same\n")
            print(ch, ":", st, "_", ref, "-", ref_base, "..", ref_cont)
        if (re.search('[GT]', ref)):
            ref = reverse_complement(ref)
            ref_cont = reverse_complement(ref_cont)
            alt = reverse_complement(alt)
        change_tri = ref_cont + ".." + ref_cont[0] + alt + ref_cont[2]
        changes.append(change_tri)
    mutdf_tmp = pd.DataFrame({"MutationType": pd.Series(
        pd.Categorical(changes, categories=mut_df_header.iloc[:, 0]), dtype=object)})
    mut_df = mutdf_tmp.groupby('MutationType').size().reset_index(name=sample_name)
    return(mut_df)


if __name__ == '__main__':
    # load FASTA Files:
    print("--- Loading FASTA File ---")
    start_time1 = time.time()
    seq_list = fasta_reader(args.fasta)
    print("--- %s seconds to load %s FASTA File ---" %
      ((time.time() - start_time1), len(seq_list)))

    # load VCF file:
    vcf_df = vcf2df(args.vcf, seq_list)
    sample_name = args.sample_name

    # convert VCF to Bin counts
    start_time = time.time()

    print("--- %s seconds to make SNV Counts Data Frame ---" %
          (time.time() - start_time))

    # convert VCF to Mutation Types
    start_time = time.time()
    header = "/FFPEsig/data/Mut-Type-Header.csv"
    mut_df = df2mut(vcf_df, header, seq_list, sample_name)

    print("--- %s seconds to make Mutation Type Data Frame ---" %
          (time.time() - start_time))
    output_dir = args.output_dir
    mut_df.to_csv(output_dir + "/" + sample_name + '.FFPEsig_input.csv', header=True, index=False)

    print("total --- %s seconds ---" % (time.time() - start_time1))
