FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# Prepare ENV variables
ENV PATH=/miniconda/bin:${PATH}

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential wget ca-certificates

# Install dependencies
RUN conda update -y -n base -c defaults conda  # Conda 4.10 *cannot* install python 3.10
RUN conda install -y -c conda-forge -c defaults mamba "python=3.8"  # <3.10 for scikit-learn =1.0 else python<3.9=0.22.1
# scikit-learn *must* be 0.22.1 to avoid UserWarnings and AttributeErrors due to updates in package dependencies
RUN mamba install -y -c conda-forge -c bioconda "scikit-learn=0.22.1" \
    imbalanced-learn "pandas=1.3.1" seaborn "hmmer!=3.3.1" prodigal \
    "screed=1.0.5" ruamel.yaml "snakemake>=5.18,<=5.26" "click>=7" nose last ncbi-genome-download

RUN git clone https://github.com/jiarong/VirSorter2.git && cd VirSorter2 && pip install .  # python -m pip

RUN pip install jsonrpcbase

RUN conda clean -y --all

# generate template-config.yaml; db_dir ONLY for KBase app
RUN virsorter config --init-source --db-dir /data/db

# Clean up
RUN apt-get clean && conda clean -y --all
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
