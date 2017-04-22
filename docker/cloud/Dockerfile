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

# fetch juptyerhub-singleuser entrypoint
RUN wget -q https://raw.githubusercontent.com/jupyterhub/jupyterhub/0.6.1/scripts/jupyterhub-singleuser -O /usr/local/bin/jupyterhub-singleuser && \
    chmod 755 /usr/local/bin/jupyterhub-singleuser

# we do not support it yet
RUN pip3 uninstall -y ipython && \
    rm /opt/conda/share/jupyter/kernels/python3/kernel.json && \
    rm /usr/local/share/jupyter/kernels/python2/kernel.json
COPY py2_nightly_kernel.json /usr/local/share/jupyter/kernels/python2/kernel.json

ADD singleuser.sh /srv/singleuser/singleuser.sh
USER jovyan
# smoke test that it's importable at least
RUN sh /srv/singleuser/singleuser.sh -h

EXPOSE 8888
CMD ["sh", "/srv/singleuser/singleuser.sh"]
