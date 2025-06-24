# api/config.py

import boto3
import os

ssm = boto3.client("ssm", region_name="us-east-1")

def get_param(name: str, with_decryption=False) -> str:
    return ssm.get_parameter(Name=name, WithDecryption=with_decryption)["Parameter"]["Value"]

# 👇 This must be at the top level, not inside any function
os.environ["DATABASE_URL"] = get_param("DATABASE_URL")
os.environ["SECRET_KEY"] = get_param("SECRET_KEY")

print("[config] Loaded DATABASE_URL and SECRET_KEY")
