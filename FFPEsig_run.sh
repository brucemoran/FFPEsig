#! bash

##wrapper to run vcf2input.py, predict_cancer.py inside docker

if [[ $(docker --version | wc -l) != 1 ]]; then
  echo "Docker doesn't seem to be running, exiting..."
else

  DOCKER="brucemoran/ffpesig"
  FOUND=$(docker images | grep ${DOCKER} | wc -l)

  if [[ $FOUND < 1 ]]; then
    docker pull ${DOCKER}
  fi

    ##input flags
    while getopts "v:f:s:r:" flag; do
      case "${flag}" in
          v) VCF=${OPTARG};;
          f) fasta=${OPTARG};;
          s) sample_name=${OPTARG};;
          r) repair_status=${OPTARG};;
      esac
    done

  ##need to mount dirs of input and output
  MNL="--mount type=bind,source="
  MNT="$(echo -e "$MNL"$(dirname $VCF)",target=/mnt/vcf\n$MNL"$(dirname $fasta)",target=/mnt/fasta\n" | sort | uniq)"
  CMD="python3 /FFPEsig/src/vcf2input.py \
        --vcf /mnt/vcf/$(basename "${VCF}") \
        --fasta /mnt/fasta/$(basename "${fasta}") \
        --sample_name ${sample_name} \
        --output_dir /mnt/vcf; \
       python3 /FFPEsig/src/FFPEsig.py \
        --input /mnt/vcf/${sample_name}.FFPEsig_input.csv \
        --sample ${sample_name} \
        --label ${repair_status} \
        --output_dir /mnt/vcf"
  echo -e "Command to be run:\n$CMD"
  echo -e "Mounting:\n"${MNT}

  docker run ${MNT} ${DOCKER} bash -c "${CMD}"

fi
