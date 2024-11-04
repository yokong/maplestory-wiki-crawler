import json
from config import ITEM_CONFIG, NPC_CONFIG, MAP_CONFIG
import item_download
from utils import setup_logging


def display_menu():
    print("\n=== MapleStory Asset Downloader ===")
    print("1. Download Items")
    print("2. Download NPCs")
    print("3. Download Maps")
    print("0. Exit")
    return input("Please select an option (0-3): ")


def display_config(config):
    print("\nCurrent configuration:")
    print(json.dumps(config, indent=2))
    confirm = input(
        "\nDo you want to proceed with this configuration? (y/n): ")
    return confirm.lower() == 'y'


def main():
    setup_logging()

    while True:
        choice = display_menu()

        if choice == '0':
            print("Goodbye!")
            break

        elif choice == '1':
            print("\n=== Item Download Selected ===")
            if display_config(ITEM_CONFIG):
                print("\nStarting item download...")
                item_download.start_download()
            else:
                print("Download cancelled.")

        elif choice == '2':
            print("\n=== NPC Download Selected ===")
            print("Feature not implemented yet.")
            # if display_config(NPC_CONFIG):
            #     npc_download.start_download()

        elif choice == '3':
            print("\n=== Map Download Selected ===")
            print("Feature not implemented yet.")
            # if display_config(MAP_CONFIG):
            #     map_download.start_download()

        else:
            print("\nInvalid option. Please try again.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
