# AJAX Subform Configuration Guide

## Overview

This document provides post-import configuration steps for forms that use AJAX Subform to auto-populate fields.

---

## imCampaignDistPt - Distribution Point Details

**Goal**: When user selects a distribution point in `distPointCode`, automatically populate Point Name, Type, and District.

### How It Works

1. User selects a distribution point from `distPointCode` dropdown
2. AJAX Subform (`imDistPtDetails`) reloads based on selected value
3. Bean Shell Form Binder queries `md45DistribPoint` and returns field values
4. Subform displays the values in readonly text fields
5. On save, "Submit Child Data To Parent" copies values to hidden fields in parent form
6. Hidden fields persist the data to the database

### Required Forms

| Form ID | Purpose |
|---------|---------|
| `imDistPtDetails` | Subform with readonly fields (loaded via Bean Shell) |
| `imCampaignDistPt` | Parent form with hidden fields + AJAX Subform element |

### Data Flow

```
User selects distPointCode
        ↓
AJAX Subform reloads imDistPtDetails
        ↓
Bean Shell queries md45DistribPoint WHERE c_code = selected value
        ↓
Returns: distPointName, distPointType, districtCode
        ↓
Subform displays values (readonly text fields)
        ↓
On Save: "Submit Child Data To Parent" → hidden fields in parent
        ↓
Hidden fields saved to imCampaignDistPt table
```

---

## Step 1: Configure Bean Shell Form Binder on imDistPtDetails

1. Open **App Composer** → **Forms** → `imDistPtDetails`
2. Click **Edit** to open Form Builder
3. Click **Form Properties** (gear icon at top)
4. Go to **Advanced** → **Load Binder**
5. Select: `Bean Shell Form Binder`
6. Paste this script in the **Script** field:

```java
import java.util.HashMap;
import org.joget.apps.app.service.AppUtil;
import org.joget.apps.form.dao.FormDataDao;
import org.joget.apps.form.model.FormRow;
import org.joget.apps.form.model.FormRowSet;
import org.joget.commons.util.LogUtil;

String distPointCode = "#requestParam.distPointCode#";
HashMap result = new HashMap();

if (distPointCode != null && !distPointCode.isEmpty() && !distPointCode.startsWith("#")) {
    try {
        FormDataDao formDataDao = (FormDataDao) AppUtil.getApplicationContext().getBean("formDataDao");

        String condition = "WHERE c_code = ?";
        String[] params = new String[]{distPointCode};

        FormRowSet rowSet = formDataDao.find(
            "md45DistribPoint",
            "app_fd_md45DistribPoint",
            condition,
            params,
            null, null, 0, 1
        );

        if (rowSet != null && !rowSet.isEmpty()) {
            FormRow row = rowSet.get(0);
            result.put("distPointName", row.getProperty("name"));
            result.put("distPointType", row.getProperty("pointType"));
            result.put("districtCode", row.getProperty("districtCode"));
        }
    } catch (Exception e) {
        LogUtil.error(getClass().getName(), e, "Error loading distribution point");
    }
}

return result;
```

7. Click **OK** to close properties
8. Click **Save** to save the form

---

## Step 2: Add AJAX Subform to imCampaignDistPt

1. Open **App Composer** → **Forms** → `imCampaignDistPt`
2. Click **Edit** to open Form Builder
3. From the left palette, expand **Enterprise** section
4. Drag **AJAX Subform** element onto the form
5. Position it **after** the `distPointCode` field (Distribution Point selectBox)
6. Double-click the AJAX Subform to open properties
7. Configure as follows:

| Property | Value |
|----------|-------|
| **ID** | `distPointDetails` |
| **Label** | `Distribution Point Details` |
| **Form** | `imDistPtDetails` |
| **Control Field** | `distPointCode` |
| **Parent Subform ID** | *(leave empty)* |
| **Load Data When Control Field Is Empty** | `No` (unchecked) |
| **Submit Child Data To Parent** | `Yes` (checked) |
| **Readonly** | `No` (unchecked) |

8. Click **OK** to close properties
9. Click **Save** to save the form

---

## Verification

After configuration:

1. Navigate to `imCampaignDistPt` form in the app
2. Select a campaign from the Campaign dropdown
3. Select a distribution point from the Distribution Point dropdown
4. **Expected**: Point Name, Type, and District fields should auto-populate
5. Change the distribution point selection
6. **Expected**: Fields should update automatically
7. Clear the distribution point selection
8. **Expected**: Fields should clear
9. Save a record and reload
10. **Expected**: Data should persist correctly

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Fields don't populate | Check Bean Shell script for errors in Joget logs |
| "Error loading distribution point" in logs | Verify table name `app_fd_md45DistribPoint` exists |
| AJAX Subform doesn't reload | Verify Control Field is exactly `distPointCode` |
| 404 errors | Ensure `imDistPtDetails` form exists and is saved |

---

## Notes

- The subform `imDistPtDetails` does not store data directly - it displays loaded values
- The Bean Shell script queries `md45DistribPoint` using the selected code
- Field IDs in the subform must match the keys in the HashMap returned by Bean Shell
- **Critical**: Field IDs in subform must match hidden field IDs in parent form for "Submit Child Data To Parent" to work
- Parent form has hidden fields (`distPointName`, `distPointType`, `districtCode`) that receive and persist the data
