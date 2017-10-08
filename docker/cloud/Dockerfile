FROM jupyter/scipy-notebook

MAINTAINER Shogun Team <shogun-team@shogun-toolbox.org>

USER root

RUN echo "deb http://apt.shogun.ml jessie nightly" > /etc/apt/sources.list.d/shogun-toolbox-nightly-jessie.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3DD2174ACAB30365 && \
    apt-get update && \
    apt-get install -y --no-install-recommends python-shogun

RUN ln -s /usr/lib/python2.7/dist-packages/modshogun.py /opt/conda/envs/python2/lib/python2.7/modshogun.py && \
 ln -s /usr/lib/python2.7/dist-packages/_modshogun.so /opt/conda/envs/python2/lib/python2.7/_modshogun.so && \
 ln -s /usr/lib/python2.7/dist-packages/shogun /opt/conda/envs/python2/lib/python2.7/shogun

# we do not support it yet
RUN pip3 uninstall -y ipython && \
    rm /opt/conda/share/jupyter/kernels/python3/kernel.json && \
    rm /usr/local/share/jupyter/kernels/python2/kernel.json
COPY py2_nightly_kernel.json /usr/local/share/jupyter/kernels/python2/kernel.json

USER jovyan
ENV SHOGUN_DATA_DIR /home/jovyan/work/data

EXPOSE 8888
CMD ["start-singleuser.sh"]
