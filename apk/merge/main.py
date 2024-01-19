def bag_command(args, unknown):
    print("merge bag command")
    from .merge_bag import main as bag_main

    bag_main(args, unknown)


def record_command(args, unknown):
    print("1. receive merge record files command")
    print("2. generate convert record files to bag files shell script")
    from .merge_record import main as record_main

    record_main(args, unknown)
    print("3. shell script generated")
    print("4. please into container and run the shell script")


def add_arguments(parser):
    subparsers = parser.add_subparsers(title="capture commands")

    # bag
    bag_parser = subparsers.add_parser("bag", help="merge bags")
    bag_parser.set_defaults(func=bag_command)

    # record
    record_parser = subparsers.add_parser("record", help="merge records")
    record_parser.set_defaults(func=record_command)
