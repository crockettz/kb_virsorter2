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
RUN apt-get update && apt-get install -y build-essential

# Install dependencies
RUN conda install -y -c conda-forge mamba python=3.6
RUN mamba install -y "python>=3.6" scikit-learn=0.22.1 imbalanced-learn pandas seaborn hmmer==3.3 prodigal screed ruamel.yaml "snakemake>=5.18,<=5.26" click

RUN git clone https://github.com/jiarong/VirSorter2.git && cd VirSorter2 && pip install .  # python -m pip

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
