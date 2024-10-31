import argparse
import os


def recursive_delete(sftp, remote_path, exclude_dirs=[], keep_files=[]):
    """Recursively deletes files and directories on an SFTP server, excluding specified directories and keeping specified files.

    Args:
        sftp: An open SFTP connection.
        remote_path: The path to the directory to delete.
        exclude_dirs (list, optional): A list of directory names to exclude. Defaults to [].
        keep_files (list, optional): A list of filenames to keep. Defaults to [].
    """

    for entry in sftp.listdir(remote_path):
        full_path = os.path.join(remote_path, entry)

        if sftp.isdir(full_path):
            if entry not in exclude_dirs:
                recursive_delete(sftp, full_path, exclude_dirs, keep_files)
                if sftp.listdir(full_path) == []:
                    try:
                        print(f"Try Deleted directory: {full_path}")
                        sftp.rmdir(full_path)
                        print(f"Deleted directory")
                    except OSError as o:
                        print(f"Error deleting directory: {o}")
        elif entry not in keep_files:
            print(f"Try Deleting file: {full_path}")
            sftp.remove(full_path)
            print(f"Deleted file")


def main():
    parser = argparse.ArgumentParser(
        description="Recursively delete files on an SFTP server, excluding specified directories and keeping specified files"
    )
    parser.add_argument("host", type=str, help="SFTP host")
    parser.add_argument("username", type=str, help="SFTP username")
    parser.add_argument("password", type=str, help="SFTP password")
    parser.add_argument("remote_path", type=str, help="Remote path to delete")
    parser.add_argument(
        "--exclude_dirs", nargs="+", type=str, help="List of directory names to exclude"
    )
    parser.add_argument(
        "--keep_files", nargs="+", type=str, help="List of filenames to keep"
    )
    args = parser.parse_args()

    with pysftp.Connection(
        host=args.host, username=args.username, password=args.password
    ) as sftp:
        exclude_dirs = args.exclude_dirs or []
        keep_files = args.keep_files or []
        recursive_delete(sftp, args.remote_path, exclude_dirs, keep_files)


if __name__ == "__main__":
    main()