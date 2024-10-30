import pysftp
import argparse
import os


def upload_directory(sftp, local_dir, remote_dir):
    """
    Recursively uploads a local directory and its contents to an SFTP server.

    Args:
        sftp (pysftp.Connection): An open SFTP connection.
        local_dir (str): The path to the local directory to upload.
        remote_dir (str): The path on the SFTP server to upload the directory to.

    Raises:
        OSError: If an error occurs during the upload process.
    """

    for entry in os.listdir(local_dir):
        local_path = os.path.join(local_dir, entry)
        remote_path = os.path.join(remote_dir, entry)

        if os.path.isdir(local_path):
            try:
                sftp.mkdir(
                    remote_path
                )  # Create the remote directory if it doesn't exist
            except OSError:
                # Handle potential existing directory errors gracefully (e.g., continue uploading)
                pass
            upload_directory(sftp, local_path, remote_path)
        else:
            try:
                sftp.put(local_path, remote_path)
                print(f"Uploaded: {local_path} -> {remote_path}")
            except OSError as e:
                print(f"Error uploading {local_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Upload a directory to an SFTP server")
    parser.add_argument("host", type=str, help="SFTP host")
    parser.add_argument("username", type=str, help="SFTP username")
    parser.add_argument("password", type=str, help="SFTP password")
    parser.add_argument("local_dir", type=str, help="Local directory to upload")
    parser.add_argument(
        "remote_dir", type=str, help="Remote directory on the SFTP server"
    )
    args = parser.parse_args()

    try:
        with pysftp.Connection(
            host=args.host, username=args.username, password=args.password
        ) as sftp:
            upload_directory(sftp, args.local_dir, args.remote_dir)
    except (pysftp.ConnectionException, OSError) as e:
        print(f"Error connecting to SFTP server or uploading directory: {e}")


if __name__ == "__main__":
    main()
