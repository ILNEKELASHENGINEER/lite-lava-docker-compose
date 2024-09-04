import argparse
import json
import subprocess

from urllib.error import URLError
from urllib.request import urlopen
#updated by nekelash
parser = argparse.ArgumentParser(description="submit LAVA jobs for Uhnder")
parser.add_argument('--jobid-file', type=argparse.FileType("w"), help="output file for the list of created job ids")
parser.add_argument('--metadata-file', type=argparse.FileType("r"), help="set the metadata file location")
parser.add_argument('-u', '--callback-url', type=str, help="specify the callback URL")
parser.add_argument('--callback-secret', type=str, help="specify the secret token to use for the callback")
args, unknown = parser.parse_known_args()

if args.metadata_file and (not args.callback_url or not args.callback_secret):
    print("--callback-url and --callback-secret must be set with --metadata-file")
    exit(1)

# Run lqa with the given arguments
result = subprocess.run(['lqa'] + unknown, stderr=subprocess.PIPE)

if result.returncode != 0:
    print(f"lqa returned an error: {result.returncode}")
    exit(1)

submitted = []
for job in result.stderr.decode('utf-8').splitlines():
    # Add Job ID to the list
    try:
        job_id = int(job.split(' ')[-1])
        submitted.append(job_id)

        if args.metadata_file:
            # Load metadata for phabbridge
            try:
                metadata = json.load(args.metadata_file)
            except Exception as e:
                print(f"Cannot load metadata file {e}")
                continue

            # Notify the phab bridge about the job
            requestdata = {
                'status_string': 'submitted',
                'metadata': metadata,
                'id': job_id,
                'token': args.callback_secret
            }#updated by nekelash

            print("Request Data:", requestdata)  # Print request data for debugging

            try:
                urlopen(args.callback_url, data=json.dumps(requestdata).encode('UTF-8'))
            except URLError:
                pass
#updated by nekelash

    except Exception as e:
        print(f"Error processing job: {e}")
        continue

if args.jobid_file:
    json.dump({"jobids": submitted}, args.jobid_file)

print(submitted[0])
#updated by nekelash
