#!/bin/bash

IMAGES_DIR=images
CSV_FILE=animes.csv
PKL_FILE=animes.pkl
COMPRESSED_FILE=anime_dataset.tar.xz

# Check if the images directory exists
if [ ! -d "${IMAGES_DIR}" ]; then
    echo -e "\e[31mERROR\e[0m: Directory ${IMAGES_DIR} does not exist"
    exit 1
fi

# Check if the CSV exists
if [ ! -f "${CSV_FILE}" ]; then
    echo -e "\e[31mERROR\e[0m: File ${CSV_FILE} does not exist"
    exit 1
fi

# Check if the PKL file exists (optional!)
if [ ! -f "${PKL_FILE}" ]; then
    echo -e "\e[33mWARN\e[0m: File ${PKL_FILE} does not exist"
    # Ask the user if they want to continue
    read -p "This file is optional. Do you want to continue? [y/N] " -n 1 -r
    # If no, exit
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Compress the dataset as .tar.xz
echo "Compressing..."
tar cf ${COMPRESSED_FILE} --use-compress-program='xz -6kT0' ${IMAGES_DIR} ${CSV_FILE} ${PKL_FILE}
echo "Done!"
