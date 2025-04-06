import termuxgui as tg
import time

def main():
    with tg.Connection() as c:
        a = tg.Activity(c)

        # Root layout
        root = tg.LinearLayout(a)

        # Amount input
        tg.TextView(a, "Amount", root)
        amount_input = tg.EditText(a, parent=root,text="amount")
        #amount_input.sethint("Enter amount")
        #amount_input.setinputtype("numberDecimal")

        # Category selection
        # Category selection
        tg.TextView(a, "Category", root)
        category_spinner = tg.Spinner(a, parent=root)
        categories = ["Food", "Transportation", "Housing", "Entertainment", "Utilities", "Healthcare", "Shopping", "Other"]
        category_spinner.setentries(categories)

        # Description input
        tg.TextView(a, "Description (optional)", root)
        description_input = tg.EditText(a, parent=root)
        #description_input.sethint("Enter description")

        # Date picker
        tg.TextView(a, "Date", root)
        date_picker = tg.EditText(a, parent=root)
        #date_picker.sethint("YYYY-MM-DD")
        #date_picker.setinputtype("date")

        # Submit button
        submit_button = tg.Button(a, "Add Expense", root)

        # Event listener for the submit button
        def on_submit(event):
            amount = amount_input.gettext()
            category = categories[category_spinner.getselecteditemposition()]
            description = description_input.gettext()
            date = date_picker.gettext()
            # Handle the collected data as needed
            a.toast(f"Expense Added:\nAmount: {amount}\nCategory: {category}\nDescription: {description}\nDate: {date}")

        submit_button.setonclicklistener(on_submit)

        # Keep the application running
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
