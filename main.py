import database.models

from ui.dashboard import dashboard

from ui.company import (
    create_company,
    view_companies,
    update_company,
    delete_company
)

from accounting.ledger import (
    create_ledger,
    view_ledgers,
    update_ledger,
    delete_ledger
)

from accounting.vouchers import (
    add_voucher,
    view_vouchers,
    delete_voucher
)

from inventory.items import (
    add_item,
    view_inventory,
    update_inventory,
    delete_inventory
)

from accounting.reports import (
    balance_sheet,
    trial_balance,
    profit_loss
)

from accounting.gst import calculate_gst

from ui.invoice import generate_invoice

from reports.exports import (
    export_ledgers,
    export_inventory
)


print("\nDatabase tables ready\n")


while True:

    dashboard()

    choice = input("Enter Choice: ")

    try:

        # =========================================
        # COMPANY
        # =========================================

        if choice == "1":

            name = input("Company Name: ")
            address = input("Address: ")
            gst = input("GST Number: ")

            create_company(
                name,
                address,
                gst
            )

        elif choice == "2":

            view_companies()

        elif choice == "3":

            cid = input("Company ID: ")

            name = input("New Name: ")

            address = input("New Address: ")

            gst = input("New GST Number: ")

            update_company(
                cid,
                name,
                address,
                gst
            )

        elif choice == "4":

            cid = input("Company ID: ")

            delete_company(cid)

        # =========================================
        # LEDGERS
        # =========================================

        elif choice == "5":

            company_id = input("Company ID: ")

            name = input("Ledger Name: ")

            group_name = input("Ledger Group: ")

            balance = float(
                input("Opening Balance: ")
            )

            create_ledger(
                company_id,
                name,
                group_name,
                balance
            )

        elif choice == "6":

            view_ledgers()

        elif choice == "7":

            ledger_id = input("Ledger ID: ")

            name = input("New Ledger Name: ")

            group_name = input("New Group: ")

            balance = float(
                input("New Balance: ")
            )

            update_ledger(
                ledger_id,
                name,
                group_name,
                balance
            )

        elif choice == "8":

            ledger_id = input("Ledger ID: ")

            delete_ledger(ledger_id)

        # =========================================
        # VOUCHERS
        # =========================================

        elif choice == "9":

            voucher_type = input(
                "Voucher Type: "
            )

            ledger_id = input(
                "Ledger ID: "
            )

            amount = float(
                input("Amount: ")
            )

            narration = input(
                "Narration: "
            )

            add_voucher(
                voucher_type,
                ledger_id,
                amount,
                narration
            )

        elif choice == "10":

            view_vouchers()

        elif choice == "11":

            voucher_id = input(
                "Voucher ID: "
            )

            delete_voucher(voucher_id)

        # =========================================
        # INVENTORY
        # =========================================

        elif choice == "12":

            name = input("Item Name: ")

            quantity = int(
                input("Quantity: ")
            )

            price = float(
                input("Price: ")
            )

            add_item(
                name,
                quantity,
                price
            )

        elif choice == "13":

            view_inventory()

        elif choice == "14":

            item_id = input("Item ID: ")

            name = input("New Item Name: ")

            quantity = int(
                input("New Quantity: ")
            )

            price = float(
                input("New Price: ")
            )

            update_inventory(
                item_id,
                name,
                quantity,
                price
            )

        elif choice == "15":

            item_id = input("Item ID: ")

            delete_inventory(item_id)

        # =========================================
        # REPORTS
        # =========================================

        elif choice == "16":

            balance_sheet()

        elif choice == "17":

            trial_balance()

        elif choice == "18":

            profit_loss()

        # =========================================
        # GST
        # =========================================

        elif choice == "19":

            amount = float(
                input("Amount: ")
            )

            gst_percent = float(
                input("GST Percentage: ")
            )

            result = calculate_gst(
                amount,
                gst_percent
            )

            print("\nGST DETAILS\n")

            print(
                "Original Amount:",
                result["original"]
            )

            print(
                "GST Amount:",
                result["gst"]
            )

            print(
                "Final Amount:",
                result["total"]
            )

        # =========================================
        # INVOICE
        # =========================================

        elif choice == "20":

            customer_name = input(
                "Customer Name: "
            )

            item_name = input(
                "Item Name: "
            )

            amount = float(
                input("Amount: ")
            )

            gst_percent = float(
                input("GST Percentage: ")
            )

            generate_invoice(
                customer_name,
                item_name,
                amount,
                gst_percent
            )

        # =========================================
        # EXPORTS
        # =========================================

        elif choice == "21":

            export_ledgers()

            export_inventory()

        # =========================================
        # EXIT
        # =========================================

        elif choice == "22":

            print("\nExiting Program...\n")

            break

        else:

            print("\nInvalid Choice\n")

    except Exception as e:

        print("\nERROR OCCURRED\n")

        print(e)

    input("\nPress Enter To Continue...")