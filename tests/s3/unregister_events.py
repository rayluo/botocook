# You will NOT need this when working with S3.
# It is a workaround when working with 3rd party service.
# This recipe came from https://github.com/boto/boto3/issues/259
import boto3
from botocore.utils import fix_s3_host

def how_to_unregister(bucket_name):
    resource = boto3.resource('s3')
    resource.meta.client.meta.events.unregister('before-sign.s3', fix_s3_host)

    bucket = resource.Bucket(bucket_name)

    # boto3.set_stream_logger('botocore')
    for o in bucket.objects.all():
        print(o)
        break

def main():  # It is purposely NOT a test case, because bucket_name is pending
    how_to_unregister('your_bucket_name')

if __name__ == '__main__':
    main()
