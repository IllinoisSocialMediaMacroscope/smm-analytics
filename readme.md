[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 

## Social Media Macroscope Analytics Repository
This repository hosts all the analytics and computation scripts for SMM tools. Short running algorithms with 
small dependency libraries are deployed on [AWS Lambda](https://aws.amazon.com/lambda/), while long running processes with large libraries 
required are deployed on [AWS Batch](https://aws.amazon.com/batch/)

### Setting up nginx
- modify rabbitmg/nginx/nginx.conf to have <<server_name>>:8001
- modify rabiitmg/nginx_wo_ssl/nginx_wo_ssl.conf to have <<server_name>>:8001

Contact us the **[SRTI lab](https://srtilab.techservices.illinois.edu/about/)** if you have any question: <a href="mailto:srti-lab@illinois.edu">srti-lab@illinois.edu</a>
