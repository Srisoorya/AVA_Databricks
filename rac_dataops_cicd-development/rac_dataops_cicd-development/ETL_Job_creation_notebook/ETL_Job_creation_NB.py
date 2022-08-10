# Databricks notebook source
import requests
import json
import os

# COMMAND ----------

TOKEN = os.environ.get('TOKEN')
DOMAIN = 'dbc-07f92987-b420.cloud.databricks.com'
# ENVIRONMENT = os.environ.get('ENVIRONMENT')
# WORKSPACE = os.environ.get('WORKSPACE')
# CLUSTER_POLICY = dbutils.secrets.get(scope = "APP-CREDENTIALS", key = "POL_{0}_JOB_CLUSTER_AZ".format(ENVIRONMENT))

# COMMAND ----------

# MAGIC %md
# MAGIC ##Process-Ingest-Agreement-Document

# COMMAND ----------

url = 'https://%s/api/2.0/jobs/create' % (DOMAIN) 

payload = json.dumps({
        "name": "Process-Ingest-Agreement-Document",
        "email_notifications": {
            "on_start": [
                "lakshminarayanan.sp@avasoft.com",
                "sharmili.a@avasoft.com"
            ],
            "on_success": [
                "lakshminarayanan.sp@avasoft.com",
                "sharmili.a@avasoft.com"
            ],
            "on_failure": [
                "lakshminarayanan.sp@avasoft.com",
                "sharmili.a@avasoft.com"                 
            ]
        },
        "timeout_seconds": 0,
        "max_concurrent_runs": 1,
        "tasks": [
            {
                "task_key": "Process-Ingest-Agreement-Document-RACDB-to-Stage",
                "notebook_task": {
                    "notebook_path": "/Repos/Databricks_POC/rac_dataops_cicd/ETL_Jobs/test_NB",
                    "source": "WORKSPACE"
                },
                "job_cluster_key": "Cluster_A",
                "timeout_seconds": 0,
            },
        ],
  "job_clusters": [
    {
                "job_cluster_key": "Cluster_A",
                "new_cluster": {
                    "spark_version": "10.4.x-scala2.12",
                    "aws_attributes": {
                        "first_on_demand": 1,
                        "availability": "SPOT_WITH_FALLBACK",
                        "zone_id": "us-west-2b",
                        "spot_bid_price_percent": 100,
                        "ebs_volume_type": "GENERAL_PURPOSE_SSD",
                        "ebs_volume_count": 3,
                        "ebs_volume_size": 100
                    },
                    "node_type_id": "m4.large",
                    "spark_env_vars": {
                        "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
                    },
                    #"enable_elastic_disk": false,
                    "runtime_engine": "STANDARD",
                    "num_workers": 8
                }
            }
  ]
})
headers = {
  'Authorization': 'Bearer %s' % TOKEN,
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
