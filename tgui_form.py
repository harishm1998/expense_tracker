#!/usr/bin/env python3

import termuxgui as tg
import sys

with tg.Connection() as c:
    a = tg.Activity(c, dialog=True)

    layout = tg.LinearLayout(a)

    # Title
    title = tg.TextView(a, "Add Expense", layout)
    title.settextsize(25)
    title.setmargin(10)

    # Amount
    tv_amt = tg.TextView(a, "Amount", layout)
    #print("dir tTextView",dir(tg.TextView))
    et_amt = tg.EditText(a, "", layout)

    # Category Spinner
    tv_cat = tg.TextView(a, "Category", layout)
    categories = [
        "Select a category", "Food", "Transportation", "Housing",
        "Entertainment", "Utilities", "Healthcare", "Shopping", "Other"
    ]
    spinner = tg.Spinner(a, layout)
    #print(dir(spinner))
    spinner.setlist(categories)
    #spinner.setselection(0)

    # Description
    tv_desc = tg.TextView(a, "Description (optional)", layout)
    et_desc = tg.EditText(a, "", layout)

    # Date (as simple text field for now)
    tv_date = tg.TextView(a, "Date (YYYY-MM-DD)", layout)
    et_date = tg.EditText(a, "", layout)

    # Submit button
    btns = tg.LinearLayout(a, layout, False)
    add_btn = tg.Button(a, "Add Expense", btns)
    cancel_btn = tg.Button(a, "Cancel", btns)

    # Event loop
    for ev in c.events():
        if ev.type == tg.Event.destroy and ev.value["finishing"]:
            sys.exit()

        if ev.type == tg.Event.click and ev.value["id"] == add_btn:
            amt = et_amt.gettext()
            cat = categories[cat_spinner.getselection()]
            desc = et_desc.gettext()
            date = et_date.gettext()

            if amt.strip() == "" or cat == "Select a category" or date.strip() == "":
                a.toast("Please fill in required fields", long=True)
            else:
                # You can later log or store this data
                print(f"Amount: {amt}, Category: {cat}, Description: {desc}, Date: {date}")
                a.toast("Expense added!", long=False)
                a.finish()

        if ev.type == tg.Event.click and ev.value["id"] == cancel_btn:
            a.finish()
