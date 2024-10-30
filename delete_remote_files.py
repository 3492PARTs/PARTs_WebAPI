import pysftp
import argparse


def recursive_delete(sftp, remote_path, files_to_keep=[]):
    """Recursively deletes files and directories on an SFTP server, excluding files in the provided list.

    Args:
        sftp: An open SFTP connection.
        remote_path: The path to the directory to delete.
        files_to_keep (list, optional): A list of filenames (without directory path) to keep within the directory. Defaults to [].
    """

    for entry in sftp.listdir(remote_path):
        full_path = remote_path + "/" + entry

        if sftp.isdir(full_path):
            recursive_delete(sftp, full_path, files_to_keep)
            if not any(
                f in full_path for f in files_to_keep
            ):  # Check if directory is empty (excluding kept files)
                print(f"Try Deleted directory: {full_path}")
                sftp.rmdir(full_path)
                print(f"Deleted directory: {full_path}")
        elif entry not in files_to_keep:  # Check if file is not in the keep list
            print(f"Try Deleting file: {full_path}")
            sftp.remove(full_path)
            print(f"Deleting file: {full_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Recursively delete files on an SFTP server, excluding a list"
    )
    parser.add_argument("host", type=str, help="SFTP host")
    parser.add_argument("username", type=str, help="SFTP username")
    parser.add_argument("password", type=str, help="SFTP password")
    parser.add_argument("remote_path", type=str, help="Remote path to delete")
    parser.add_argument(
        "--keep", nargs="+", type=str, help="List of filenames to keep (excluding path)"
    )
    args = parser.parse_args()

    with pysftp.Connection(
        host=args.host, username=args.username, password=args.password
    ) as sftp:
        files_to_keep = args.keep or []  # Handle empty list from argument

        recursive_delete(sftp, args.remote_path, files_to_keep)


if __name__ == "__main__":
    main()
