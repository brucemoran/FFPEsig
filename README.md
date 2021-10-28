# FFPEsig

As per the original [FFPEsig](https://github.com/QingliGuo/FFPEsig) with changes:
- Docker support
- GRCh37 and 38 support (requires fasta input)
- VCF input (creates input in correct format)
- VCF output (with FFPE mutations removed)
- Wrapper shell script to run 'freestanding' or using Nextflow/Snakemake.

## Run from commandline 'freestanding' (requires Docker running):
```
sh FFPEsig_run.sh \
  --VCF /path/to/input.vcf \
  --fasta /path/to/input.vcf \
  --sample_name string_sample_id \
  --repair_status <Unrepaired|Repaired>
```

## Run within Docker using Nextflow/Snakemake
```
python3 /FFPEsig/src/vcf2input.py \
  --vcf /path/to/input.vcf \
  --fasta /path/to/fasta.fa \
  --sample_name string_sample_id \
  --output_dir ./

python3 /FFPEsig/src/FFPEsig.py \
  --input string_sample_id.FFPEsig_input.csv \
  --sample string_sample_id \
  --label <Unrepaired|Repaired> \
  --output_dir ./
```

## Label
Label option, [--label], must be either of them <Unrepaired|Repaired>. This specifies whether the FFPE sample had UDG treatment prior to library construction which will affect the signature of FFPE-induced mutations and how they should be corrected.

## Citation

The preprint of the tool is avaiable in bioRxiv. [Check it out](https://www.biorxiv.org/content/10.1101/2021.03.11.434918v1).
