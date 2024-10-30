import pysftp
import argparse


def recursive_delete(sftp, remote_path):
    """Recursively deletes files and directories on an SFTP server.

    Args:
        sftp: An open SFTP connection.
        remote_path: The path to the directory to delete.
    """

    for entry in sftp.listdir(remote_path):
        full_path = remote_path + "/" + entry

        if sftp.isdir(full_path):
            recursive_delete(sftp, full_path)
            sftp.rmdir(full_path)
        else:
            sftp.remove(full_path)

        print(f"Deleting {full_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Recursively delete files on an SFTP server"
    )
    parser.add_argument("host", type=str, help="SFTP host")
    parser.add_argument("username", type=str, help="SFTP username")
    parser.add_argument("password", type=str, help="SFTP password")
    parser.add_argument("remote_path", type=str, help="Remote path to delete")
    args = parser.parse_args()

    with pysftp.Connection(
        host=args.host, username=args.username, password=args.password
    ) as sftp:
        recursive_delete(sftp, args.remote_path)


if __name__ == "__main__":
    main()
