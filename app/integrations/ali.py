import alibabacloud_oss_v2 as oss

def upload_to_ali_oss(file_path, file_name):
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = 'cn-shanghai'

    client = oss.Client(cfg)

    bucket_name = "jakatest-shanghai"
    key="ai-collect/" + file_name
    result = client.put_object_from_file(oss.PutObjectRequest(
            bucket=bucket_name,
            key=key,
            acl="public-read"
        ),
        file_path
    )

    if result.status_code == 200:
        return True

    return False