#! /bin/bash

update_yum()
{
    cd /etc/yum.repos.d/
    sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
    yum update -y
}
install_python()
{
    yum install -y python3
}
install_databricks_cli() 
{
    pip3 install databricks-cli --upgrade
}

update_yum
install_python
install_databricks_cli

if [ $ENV == "dev" ];
then
    cd /builds/AVASOFTWAREINC/rac_dataops_cicd
    touch dev_token_file
    echo $dev_token >dev_token_file
    ls -al
    #configure Databricks credentials
    databricks configure --jobs-api-version 2.1 --host $Dev_url -f dev_token_file --profile Dev 
    touch job.txt

    #Update the databricks repos to the latest commit
    databricks repos update --repo-id 2415403591490274 --branch development --profile Dev 

    #create master job which creates ETL jobs
    databricks jobs create --json-file ./master_job_creation_notebook/master_job_creation_notebook.json --profile Dev >job.txt
    job_id=$(cat job.txt | grep job_id | cut -d ":" -f 2)
    echo $job_id

    #run the master job to create ETL jobs
    databricks jobs run-now --job-id $job_id --profile Dev
    
fi

# if [ $ENV == "prod" ];
# then
#      update_yum
#      install_python
#      install_databricks_cli
#      ls -al
#      pwd
#      echo $PROD_token | databricks configure --host $PROD_url -t --profile PROD
#      databricks workspace import_dir -o --exclude-hidden-files --profile PROD "." "/"

# fi



