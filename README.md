# Sale Order Enhancement Module

This custom Odoo module provides advanced enhancements to the Sale Order workflow, including user role management, field-level permissions, automated workflows, and configurable restrictions.

## 🚀 Features

### 1. User Type Creation: `Sale Admin`
- A new user group named **"Sale Admin"** is created specifically for managing advanced sales operations.

### 2. Custom Field Addition: `Manager Reference`
- A new text field **"Manager Reference"** is added to the Sale Order.
- The field is:
  - **Visible** to all user types.
  - **Editable** only by users in the **Sale Admin** group.

### 3. Sale Order Limit Setting
- A configurable **float field** named **"Sale Order Limit"** is introduced under the **Sales Settings** tab.
- Allows setting a threshold for Sale Order amount approval.

### 4. Sale Order Confirmation Restriction
- Users with the **Sale Admin** role can confirm Sale Orders that **exceed** the defined **Sale Order Limit**.
- Other users will be restricted from confirming high-value Sale Orders.

### 5. Automated Workflow (Optional)
- A boolean field **"Auto Workflow"** is added to the Sale Order form.
- If enabled:
  - Automatically triggers the full flow: **Sale → Delivery → Invoice → Payment** upon Sale Order confirmation.
  - Handles mixed-product quotations.
  - Creates **separate deliveries per product**, with **identical products grouped in a single delivery**.

---

## ⚙️ Installation

1. Copy the module folder into your Odoo `addons` directory.
2. Restart the Odoo server.
3. Update the app list and install the module from the Apps menu.

---

## 🛡 Permissions

- **Sale Admin**: Full control including editing `Manager Reference`, confirming large orders, and enabling Auto Workflow.
- **Regular Users**: Can view all Sale Orders but have limited control based on configuration.

---# Zinfog
