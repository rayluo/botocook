import os

import boto3
from boto3.s3.transfer import ReadFileChunk
from botocore.utils import calculate_tree_hash


PART_SIZE = 1024*1024

def multipart_upload(filename, part_size=PART_SIZE):
    glacier = boto3.resource('glacier', region_name='us-west-2')
    # There's no error if the vault already exists so we don't
    # need to catch any exceptions here.
    vault = glacier.create_vault(vaultName='botocore-integ-test-vault')
    file_size = os.path.getsize(filename)

    # Initiate a multipart upload
    multipart_upload = vault.initiate_multipart_upload(
        archiveDescription='multipart upload', partSize=str(part_size))
    try:
        # Upload each part
        for i in range(file_size/part_size+1):
            range_from = i*part_size
            range_to = min((i+1)*part_size-1, file_size-1)
            body = ReadFileChunk.from_filename(filename, range_from, part_size)
            multipart_upload.upload_part(
                body=body, range='bytes %d-%d/*' % (range_from, range_to))

        # Complete a multipart upload transaction
        response = multipart_upload.complete(
            checksum=calculate_tree_hash(open(filename, 'rb')),  # NEEDED
            archiveSize=str(file_size))
        return vault.Archive(response['archiveId'])
    except:
        multipart_upload.abort()
        raise

def test():
    filename = 'temp.txt'
    open(filename, 'wb').write(b'a'*(PART_SIZE+1))
    try:
        archive = multipart_upload(filename)

        # Clean up test upload. You do not need this in your real code
        archive.delete()
    finally:
        os.remove(filename)

if __name__ == '__main__':
    test()
