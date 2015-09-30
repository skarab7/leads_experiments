=================
Plotting
=================

pcp - system performance metrics
================================

1. Get data:
   
   .. code:: bash

     bash get_pcp_data.sh


2. Prepare for plotting

   .. code:: bash

     mkvirtualenv  d5.8-plotting
     pip install -U -r requirements.txt


3. Generate plots

   .. code:: bash

     export LEADS_PCP_DATA_DIR=$(pwd)/pcp
     export LEADS_PCP_FIGURE_DIR=$(pwd)/pcp-figures
     mkdir -p ${LEADS_PCP_FIGURE_DIR}

tcpflow -- TBD
================================

TBD
