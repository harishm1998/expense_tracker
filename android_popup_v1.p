#!/usr/bin/env python3

import termuxgui.oo as tgo
import time

class ExpenseTrackerLayout(tgo.LinearLayout):
    def __init__(self, activity: tgo.Activity):
        super().__init__(activity)

        # Amount input
        tgo.TextView(self.a, "Amount", self)
        self.amount_input = tgo.EditText(self.a, parent=self)

        # Category selection
        tgo.TextView(self.a, "Category", self)
        self.categories = ["Food", "Transportation", "Housing", "Entertainment", "Utilities", "Healthcare", "Shopping", "Other"]
        self.category_spinner = tgo.Spinner(self.a, parent=self)
        self.category_spinner.setentries(self.categories)

        # Description input
        tgo.TextView(self.a, "Description (optional)", self)
        self.description_input = tgo.EditText(self.a, parent=self)

        # Date picker
        tgo.TextView(self.a, "Date", self)
        self.date_picker = tgo.EditText(self.a, parent=self)

        # Submit button
        self.submit_button = tgo.Button(self.a, "Add Expense", self)
        self.submit_button.on_click = self.on_submit

    def on_submit(self, event, view):
        amount = self.amount_input.gettext()
        category = self.categories[self.category_spinner.getselecteditemposition()]
        description = self.description_input.gettext()
        date = self.date_picker.gettext()
        self.a.toast(f"Expense Added:\nAmount: {amount}\nCategory: {category}\nDescription: {description}\nDate: {date}")

class ExpenseTrackerActivity(tgo.Activity):
    def __init__(self, c, t):
        super().__init__(c, t)
        ExpenseTrackerLayout(self)

with tgo.Connection() as c:
    c.launch(ExpenseTrackerActivity)
    c.event_loop()
