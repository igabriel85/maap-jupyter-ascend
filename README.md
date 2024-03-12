# Docker container for MAAP Eclipse Che Jupyter workspace

This repository contains the Dockerfile and associated files for building a Docker container for the MAAP Eclipse Che workspace.
It is based on the Universal developer image UBI8 provided by Red Hat.
Workspace is running on Python 3.10.13 and conda environment.


# Building the Docker container

## List of files in Container

- `Dockerfile`: The Dockerfile for building the Docker container.
- `README.md`: This file.
- `LICENSE`: The license file for this repository.
- `entrypoint.sh`: The entrypoint script for the Docker container.
- `environment.yml`: The environment file for the conda environment.
- `initTemplates.sh`: ?? (decompresez an arhive with templates for Eclipse non Che)
- `sharedAlgorythms.sh`: Script for cloning git repository, guides user through git configuration.
- `ingestData.sh`: Script for fetching data based on configuration from project template.
- `ingestData.py`: Python script for fetching data based on configuration from project template.
- `maap-s3.py`: Python script for fetching data from MAAP S3 bucket.
- `RestClient.py`: ??.
- `installLib.sh`: fetches requirements.txt file from url and installs the packages. Packages are:
    - property
    - requests
    - namedlist==1.7
    - scikit-image
    - equi7grid==0.0.10
    - numpydoc==0.8.0
    - packaging==19.0
    - pyproj
    - pytileproj
    - scipy
    - matplotlib
    - pillow
    - pandas
    - Shapely
    - octave_kernel
    - fiona
    - scikit-learn
- 
# IDEs
This container is desogned to run under Eclipse Che Jupyter lab IDE

## ToDos
