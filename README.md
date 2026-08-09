
# MEMORANDUM: The Ultimate Geeklog 2.2.2 Plugin Development & Modernization Guide

**TO:** Lead Developers, Software Engineers, and Plugin Maintainers
**FROM:** System Architecture & Security Team
**DATE:** August 5, 2026
**SUBJECT:** Comprehensive Technical Specifications for Plugin Modernization (PHP 8+ & Geeklog 2.2.2)

---

## TABLE OF CONTENTS

1. Executive Summary & Architectural Shift
2. PHP 8 Strictness & Legacy Code Refactoring
3. The Core Rendering Engine: Deprecating Sandwich Layouts
4. Advanced Asset Management (CSS, JS, & JSON Bridge)
5. Database API & Query Optimization
6. Security Posture: XSS, CSRF, and Access Control
7. The Template API (PHPLib Template integration)
8. Plugin Lifecycle: Installation, Upgrades, Migrations, and Persistent Storage
9. Integrating with Core Hooks (The Plugin API)
10. Error Handling and Logging
11. Addendum: Ongoing Refinements and Strict Security Patterns

---

## 1. Executive Summary & Architectural Shift

The transition to Geeklog 2.2.2 represents the most significant architectural evolution in the platform's history. Driven by the deprecation of PHP 7.4 and the aggressive strictness of PHP 8.x, the core CMS has been heavily refactored.

Legacy plugins built prior to 2022 will fail critically in this environment. The traditional paradigms of echoing HTML headers dynamically, relying on implicit variable initialization, and bypassing CSRF tokens are no longer supported. This document serves as the definitive specification for refactoring legacy plugins and architecting new ones. Compliance with these standards is mandatory for all deployments to ensure system stability, security, and UI/UX consistency across the Denim UIkit theme.

---

## 2. PHP 8 Strictness & Legacy Code Refactoring

PHP 8 introduced breaking changes that severely impact older procedural code. Developers must audit and refactor all plugin files against the following rules.

### 2.1. Variable Initialization and Array Access

PHP 8 converts many previous `E_NOTICE` and `E_WARNING` errors into `Fatal Errors`.

* **Implicit Initialization:** You can no longer append to a string or push to an array that has not been explicitly declared.
* **Curly Brace Array Access:** Using `$array{$index}` is deprecated and removed. You must use `$array[$index]`.

**Legacy Code (Will Crash in PHP 8):**

```php
function get_user_data($id) {
    if ($id > 0) {
        $html .= "<div>User ID: " . $id . "</div>"; // Fatal Error: Undefined variable $html
    }
    $data{0} = 'Admin'; // Fatal Error: Array and string offset access syntax with curly braces is no longer supported
    return $html;
}

```

**Modern Code:**

```php
function get_user_data(int $id): string {
    $html = ''; // Explicit initialization
    $data = []; // Explicit initialization
    if ($id > 0) {
        $html .= "<div>User ID: " . $id . "</div>";
    }
    $data[0] = 'Admin'; // Standard array access
    return $html;
}

```

### 2.2. Null Parameters in Native String Functions

Functions like `strlen()`, `htmlspecialchars()`, `strpos()`, and `explode()` will throw a `TypeError` if passed a `null` value. Database fetches often return `null` for empty fields.

**Modern Fix:** Always coalesce or cast variables before string operations.

```php
$db_value = DB_getItem($_TABLES['maintenance'], 'message', "id = 1"); // May return null
// Bad: $length = strlen($db_value);
$length = strlen((string) $db_value); 
// Or
$safe_value = $db_value ?? '';
$length = strlen($safe_value);

```

### 2.3. Deprecated Functions

* **`create_function()`:** Removed. Replace with anonymous functions (Closures).
* **`each()`:** Removed. Replace `while (list($key, $val) = each($array))` with `foreach ($array as $key => $val)`.
* **Constructors:** PHP 4 style constructors (methods with the same name as the class) will throw errors. Rename them to `__construct()`.

---

## 3. The Core Rendering Engine: Deprecating Sandwich Layouts

The old `COM_siteHeader()` and `COM_siteFooter()` functions caused header-already-sent errors, complicated SEO metadata injection, and broke responsive layouts. They are removed. You must use `COM_createHTMLDocument()`.

### 3.1. Building the Document Payload

Your plugin script must accumulate all HTML into a single variable, then pass it to the document creator.

```php
<?php
require_once '../../lib-common.php';

// 1. Validation
$plugin_name = 'maintenance';
if (!in_array($plugin_name, $_PLUGINS)) {
    COM_handle404();
    exit;
}

// 2. Initialize variables
$display = '';
$page_title = 'Maintenance Dashboard';

// 3. Build content using Core Blocks
$display .= COM_startBlock("System Status", '', COM_getBlockTemplate('_msg_block', 'header'));
$display .= "<div class=\"uk-alert uk-alert-warning\">Maintenance mode is currently active.</div>";
$display .= COM_endBlock(COM_getBlockTemplate('_msg_block', 'footer'));

// 4. Document Options Array
$doc_options = [
    'pagetitle'  => $page_title,
    'menu'       => 'maintenance', // Highlights the current menu item
    'rightblock' => false,         // Hide right column for a wider UI
    'leftblock'  => true,          // Keep navigation
    'breadcrumbs'=> [
        ['url' => $_CONF['site_url'], 'title' => 'Home'],
        ['url' => '', 'title' => $page_title]
    ]
];

// 5. Final Output
echo COM_createHTMLDocument($display, $doc_options);
?>

```

---

## 4. Advanced Asset Management (CSS, JS, & JSON Bridge)

Hardcoding `<script>` or `<link>` tags in your `$display` variable violates CSP (Content Security Policy) and breaks asset minification. Use the global `$_SCRIPTS` class.

### 4.1. Injecting CSS and Javascript

Assets must be injected **before** `COM_createHTMLDocument()` is called.

```php
global $_SCRIPTS;

// CSS Injection
// Args: Plugin Name, Path from public_html
$_SCRIPTS->setCSSFile('maintenance', '/maintenance/css/admin.css');

// JS Injection
// Args: Plugin Name, Path, Load in Footer (boolean)
// Always load in footer to prevent render-blocking.
$_SCRIPTS->setJavaScriptFile('maintenance', '/maintenance/js/dashboard.js', true);

// Loading Core Libraries (e.g., UIkit or jQuery)
$_SCRIPTS->setJavaScriptLibrary('jquery');
$_SCRIPTS->setJavaScriptLibrary('uikit');

```

### 4.2. The PHP-to-JS JSON Bridge (Security Critical)

Do not render PHP variables directly into inline JS strings. This creates XSS vulnerabilities. Map your PHP variables to an array, encode to JSON, and inject it as a constant.

**The PHP Side:**

```php
global $_CONF, $_SCRIPTS, $LANG_MAINTENANCE;

$js_config = [
    'apiEndpoint' => $_CONF['site_url'] . '/plugins/maintenance/api.php',
    'csrfToken'   => SEC_createToken(), // Secure token for AJAX calls
    'strings'     => [
        'confirm' => $LANG_MAINTENANCE['confirm_delete'],
        'error'   => $LANG_MAINTENANCE['ajax_error']
    ]
];

// JSON encode safely
$json_payload = json_encode($js_config, JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_HEX_AMP);

// Inject as an inline script
$inline_js = "const MaintenanceCfg = {$json_payload};";
$_SCRIPTS->setJavaScript($inline_js, true);

```

**The JS Side (`dashboard.js`):**

```javascript
document.addEventListener('DOMContentLoaded', () => {
    if (typeof MaintenanceCfg !== 'undefined') {
        const btn = document.getElementById('saveBtn');
        btn.addEventListener('click', () => {
            if (confirm(MaintenanceCfg.strings.confirm)) {
                // Execute AJAX using MaintenanceCfg.apiEndpoint and MaintenanceCfg.csrfToken
            }
        });
    }
});

```

---

## 5. Database API & Query Optimization

Geeklog supports multiple database drivers (MySQL, PostgreSQL). Do not use native PHP functions like `mysqli_query()`. Always use the Geeklog `DB_*` API to ensure compatibility and leverage the core query cache.

### 5.1. Standard Operations

```php
global $_TABLES;

// 1. SELECT Multiple Rows
$sql = "SELECT id, status, message FROM {$_TABLES['maintenance']} WHERE is_active = 1";
$result = DB_query($sql);

$active_items = [];
// Use DB_fetchArray to iterate
while ($row = DB_fetchArray($result)) {
    $active_items[] = $row;
}

// 2. SELECT Single Value
// DB_getItem is optimized for retrieving a single column value
$current_status = DB_getItem($_TABLES['maintenance'], 'status', "id = 1");

// 3. Count Rows
$total_logs = DB_count($_TABLES['maintenance_logs'], 'id', "severity = 'critical'");

```

### 5.2. Preventing SQL Injections

Never trust `$_POST` or `$_GET`. Always wrap variables in `DB_escape_string()`. If expecting an integer, cast it.

```php
// Unsafe (DO NOT USE):
// $sql = "UPDATE table SET name = '{$_POST['name']}' WHERE id = {$_GET['id']}";

// Safe:
$clean_name = DB_escape_string($_POST['name']);
$clean_id   = (int) $_GET['id'];

$sql = "UPDATE {$_TABLES['maintenance']} SET name = '{$clean_name}' WHERE id = {$clean_id}";
DB_query($sql);

```

---

## 6. Security Posture: XSS, CSRF, and Access Control

Geeklog has strict security enforcement. Code failing to implement tokens or proper filters will not pass code review.

### 6.1. XSS (Cross-Site Scripting) Prevention

When receiving data from forms, sanitize it before saving to the database. When outputting data to the screen, escape it.

* **Input Sanitization:** `COM_applyFilter($_POST['variable'])`
* `COM_applyFilter($var)` strips HTML and special characters.
* `COM_applyFilter($var, true)` allows basic safe HTML (if configured by admin).


* **Output Escaping:** Always use `htmlspecialchars($string, ENT_QUOTES, 'UTF-8')` before echoing user data into HTML attributes or tags.

### 6.2. CSRF (Cross-Site Request Forgery) Tokens

All forms that modify data (POST requests) MUST include a CSRF token.

**Step 1: Inject Token into the Form (PHP/HTML)**

```php
// Assuming you are using the Template engine (see section 7)
$tpl->set_var('gltoken', SEC_createToken());

```

```html
<!-- Inside your .thtml file -->
<form action="save.php" method="POST">
    <input type="hidden" name="gltoken" value="{gltoken}" />
    <!-- rest of form -->
</form>

```

**Step 2: Validate Token on Submission (PHP)**

```php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!SEC_checkToken()) {
        COM_accessLog("CSRF attempt blocked in maintenance plugin. IP: " . $_SERVER['REMOTE_ADDR']);
        echo COM_refresh($_CONF['site_admin_url'] . '/plugins/maintenance/index.php?msg=csrf_error');
        exit;
    }
    // Proceed with safe database writes
}

```

### 6.3. Access Control (ACL)

Protect admin pages and API endpoints using `SEC_hasRights()`.

```php
// Check if user has the specific plugin admin right
if (!SEC_hasRights('maintenance.admin')) {
    // Standard function to display a "Permission Denied" UI
    echo COM_createHTMLDocument(COM_startBlock($MESSAGE[30]) . $MESSAGE[80] . COM_endBlock(), ['pagetitle' => $MESSAGE[30]]);
    exit;
}

```

---

## 7. The Template API (PHPLib Template integration)

Do not mix heavy HTML markup within your PHP files. Use Geeklog's Template class to parse `.thtml` files. This separates logic from presentation and allows site administrators to override your plugin's views via their theme.

### 7.1. Template Initialization

Store your templates in `plugins/maintenance/templates/`.

```php
// Initialize Template Object pointing to your plugin's template folder
$tpl_path = $_CONF['path'] . 'plugins/maintenance/templates/';
$tpl = new Template($tpl_path);

// Define which file to load and assign it a handle ('admin_dashboard')
$tpl->set_file('admin_dashboard', 'dashboard.thtml');

// Set a simple variable
$tpl->set_var('welcome_message', 'Welcome to the Dashboard');

```

### 7.2. Handling Loops (Blocks)

To render a list (e.g., a table of logs), you define a `BEGIN` and `END` block in your HTML, and loop through it in PHP.

**HTML (`dashboard.thtml`):**

```html
<div class="uk-overflow-auto">
    <table class="uk-table uk-table-striped">
        <thead>
            <tr><th>Date</th><th>Action</th></tr>
        </thead>
        <tbody>
            <!-- BEGIN log_row -->
            <tr>
                <td>{log_date}</td>
                <td>{log_action}</td>
            </tr>
            <!-- END log_row -->
        </tbody>
    </table>
</div>

```

**PHP Logic:**

```php
// Define the block logic
$tpl->set_block('admin_dashboard', 'log_row', 'log_rows_output');

$sql = "SELECT date, action FROM {$_TABLES['maintenance_logs']} LIMIT 10";
$result = DB_query($sql);

if (DB_numRows($result) > 0) {
    while ($row = DB_fetchArray($result)) {
        // Set variables for this specific row
        $tpl->set_var('log_date', $row['date']);
        $tpl->set_var('log_action', htmlspecialchars($row['action'], ENT_QUOTES));
        
        // Parse the block and append it to the output string
        $tpl->parse('log_rows_output', 'log_row', true); 
    }
} else {
    // Clear the block if no data exists
    $tpl->set_var('log_rows_output', '<tr><td colspan="2">No logs found</td></tr>');
}

// Finalize the entire template
$tpl->parse('output', 'admin_dashboard');
$html_content = $tpl->finish($tpl->get_var('output'));

echo COM_createHTMLDocument($html_content, ['pagetitle' => 'Dashboard']);

```

---

## 8. Plugin Lifecycle: Installation, Upgrades, and Migrations

The `autoinstall.php` file manages the schema. When pushing a new version, you must write a sequential upgrade path.

### 8.1. The Upgrade Matrix

Geeklog handles plugin upgrades by passing the currently installed version to your upgrade function. You must use a `switch` statement without `break;` to allow sequential cascading upgrades.

```php
// In autoinstall.php
function plugin_upgrade_maintenance($current_version) {
    global $_TABLES;

    $installed_version = $current_version;

    // Use a switch statement dropping through versions sequentially
    switch ($installed_version) {
        
        case '1.0.0':
            // Upgrade logic from 1.0.0 to 1.1.0
            $sql = "ALTER TABLE {$_TABLES['maintenance']} ADD COLUMN `ip_whitelist` VARCHAR(255) NULL AFTER `status`";
            DB_query($sql);
            
            $installed_version = '1.1.0';
            // Notice: NO break statement here. We want it to cascade if necessary.

        case '1.1.0':
            // Upgrade logic from 1.1.0 to 2.0.0 (Geeklog 2.2.2 compatibility)
            // Example: Add a new config option
            require_once $_CONF['path_system'] . 'classes/config.class.php';
            $c = config::get_instance();
            
            // Add new config value for timeout
            $c->add('timeout', 5000, 'text', 0, 0, null, 10, true, 'maintenance', 0);
            
            $installed_version = '2.0.0';

        case '2.0.0':
            // Current version reached.
            break;
            
        default:
            // Unknown version logic
            return false;
    }

    // Update the version in the core plugins table
    if ($installed_version != $current_version) {
        $sql = "UPDATE {$_TABLES['plugins']} SET pi_version = '{$installed_version}' WHERE pi_name = 'maintenance'";
        DB_query($sql);
    }

    return true;
}

```

### 8.2. Persistent Plugin Data and `$_CONF['path_data']` (Geeklog 2.2.2)

Persistent plugin data **must not be stored under `$_CONF['path_data']` in Geeklog 2.2.2** unless the core behavior changes and the lifecycle of this directory is explicitly documented.

This recommendation follows [Geeklog issue #1171](https://github.com/Geeklog-Core/geeklog/issues/1171), which documents that the administrator **Clear Cache** action in Geeklog 2.2.2 performs a broad cleanup of `$_CONF['path_data']`.

The current core sequence includes:

```php
Geeklog\Cache::clear();

$leave_dirs = array('cache', 'layout_cache', 'layout_css');
$leave_files = array('cacert.pem', 'README');

COM_cleanDirectory(
    $_CONF['path_data'],
    $leave_dirs,
    $leave_files
);

PLG_clearCache();
```

As a consequence, a directory such as:

```text
data/myplugin/
```

can be removed when an administrator selects **Clear Cache**, even when it contains persistent application data rather than cache files.

The plugin cache hook is executed only after the cleanup, so a plugin cannot use `PLG_clearCache()` to protect its persistent directory.

Legacy Geeklog plugins and themes have historically used subdirectories of the private `data/` directory because it provides a convenient location outside the public Web root.

Developers modernizing these extensions must therefore audit all uses of `$_CONF['path_data']` and clearly distinguish **persistent data** from **cache or temporary data**.

#### Modern Storage Standard

* **Persistent data:** Store it in a dedicated private location outside both `$_CONF['path_data']` and `$_CONF['path_html']`, or use the database when appropriate.
* **Configuration values:** Prefer Geeklog's native Configuration API instead of custom JSON or PHP configuration files whenever practical.
* **Cache data:** Treat cache content as disposable.
* **Do not use `data/cache/<plugin>/` for persistent data.** `Geeklog\Cache::clear()` may remove its contents.
* **Public media:** Store only files that must be Web-accessible under explicitly controlled directories in `public_html`, with strict extension, MIME, filename, permission, and upload validation.
* **Secrets and private files:** Never place API credentials, private JSON stores, logs, internal state, or other sensitive files under the public Web root.

A dedicated private plugin-data directory can, for example, be constructed outside `path_data`:

```php
$pluginDataRoot = rtrim($_CONF['path'], '/\\')
    . DIRECTORY_SEPARATOR . 'plugin-data'
    . DIRECTORY_SEPARATOR . 'myplugin'
    . DIRECTORY_SEPARATOR;
```

A custom location may also be supported, but it must be validated.

At minimum:

* reject null bytes;
* reject `..` path traversal sequences;
* require an absolute path or a trusted path derived from Geeklog configuration;
* ensure persistent storage is outside `$_CONF['path_html']`;
* ensure persistent storage is outside `$_CONF['path_data']` while issue #1171 remains relevant.

#### Migrating Legacy `data/<plugin>/` Storage

When modernizing a plugin that previously stored persistent data in:

```text
data/myplugin/
```

do **not** simply change the storage path.

Existing installations may already contain important data there.

The upgrade process should:

1. Detect the legacy storage directory.
2. Create the new private storage directory with restrictive permissions.
3. Copy or migrate files using validated relative paths.
4. Validate migrated files before considering the migration successful.
5. Record the migration state so it is not repeated unnecessarily.
6. Preserve the legacy copy until the new storage has been verified.
7. Avoid deleting user data automatically after a failed or partial migration.

Example:

```php
$legacyRoot = rtrim($_CONF['path_data'], '/\\')
    . DIRECTORY_SEPARATOR . 'myplugin'
    . DIRECTORY_SEPARATOR;

$newRoot = rtrim($_CONF['path'], '/\\')
    . DIRECTORY_SEPARATOR . 'plugin-data'
    . DIRECTORY_SEPARATOR . 'myplugin'
    . DIRECTORY_SEPARATOR;

if (is_dir($legacyRoot) && !is_dir($newRoot)) {
    // Create the destination securely, then perform a validated,
    // non-destructive migration before switching the plugin to $newRoot.
}
```

Do not rely on `rename()` as the only migration strategy without validation and recovery handling.

Filesystem permissions, cross-filesystem moves, interrupted requests, or partial failures must not leave the plugin without access to its persistent data.

#### Compatibility Rule

Until Geeklog provides an official persistent-storage API or changes the cleanup behavior described in issue #1171, plugin developers should assume:

> **Everything stored directly under `$_CONF['path_data']` may be treated as disposable by Geeklog's Clear Cache operation.**

This rule is intentionally conservative.

It protects modernized plugins on unpatched Geeklog 2.2.2 installations and reduces the risk of administrators losing application data through an action presented as cache maintenance.


---

## 9. Integrating with Core Hooks (The Plugin API)

Plugins interact with Geeklog by defining functions with specific prefixes: `plugin_hookname_pluginname()`.

### 9.1. Essential Hooks

* **`plugin_user_delete_maintenance($uid)`**: Called when a user is deleted from the CMS. Your plugin MUST use this to clean up related foreign keys.
```php
function plugin_user_delete_maintenance(int $uid): void {
    global $_TABLES;
    // Clean up logs associated with the deleted user
    $sql = "DELETE FROM {$_TABLES['maintenance_logs']} WHERE uid = {$uid}";
    DB_query($sql);
}

```


* **`plugin_autotags_maintenance($op, $content, $autotag)`**: Allows your plugin to parse custom shortcodes (like `[maintenance:status]`) embedded in articles.
* **`plugin_session_started_maintenance()`**: Triggered on every page load when a session begins. Use this for global checks (e.g., intercepting traffic to show a maintenance page). *Warning: Code here runs on every page. Keep it highly optimized.*

---

## 10. Error Handling and Logging

Do not use `die()` or `exit()` with raw text messages. This breaks the UI and prevents proper error tracking.

* **Logging Errors:** Use `COM_errorLog()`. This writes to `logs/error.log` securely.
```php
if (!$result) {
    COM_errorLog("Maintenance Plugin Error: Failed to fetch configuration. SQL: {$sql}");
    // Display a clean error to the user
    $display = COM_startBlock("System Error") . "An internal error occurred." . COM_endBlock();
    echo COM_createHTMLDocument($display);
    exit;
}

```


* **Access Violations:** Use `COM_accessLog()` to log unauthorized attempts to access plugin administration.

---

## 11. Addendum: Ongoing Refinements and Strict Security Patterns

As Geeklog and PHP continue to evolve, the following specific edge cases and strict coding patterns must be adhered to during plugin development and refactoring:

### 11.1. Date Functions (PHP 8.1+ Compatibility)

The `strftime()` function is officially deprecated as of PHP 8.1. Its continued use will generate deprecation notices and eventually trigger fatal errors under strict server configurations.

* **Legacy Code:** `strftime('%Y')`
* **Modern Standard:** Always use the native `date()` function for standard time formatting (e.g., `date('Y')`).

### 11.2. Language Arrays and Null Coalescing (PHP 8 Strictness)

Under PHP 8, referencing an undefined key in a language array (e.g., `$LANG_FOOBAR_1['missing_key']`) will throw a `Warning`, which can break UI rendering or interrupt JSON/AJAX responses. This commonly occurs when a plugin's core code is updated but the localized language files (like `french.php`) have not yet been synced by translators.

* **Modern Standard:** Always use the Null Coalescing Operator (`??`) to provide a safe, hardcoded fallback string when accessing language variables.
* **Implementation:**
```php
// Unsafe (Will throw a Warning if the key is missing):
$welcome = $LANG_FOOBAR_1['welcome'];

// Safe (PHP 8 compliant):
$welcome = $LANG_FOOBAR_1['welcome'] ?? 'Default welcome message';

```



### 11.3. CSRF Form Token Naming

All HTML forms that submit or modify data must include a CSRF token. Crucially, the Geeklog core validation function `SEC_checkToken()` specifically looks for the `gltoken` key in the `$_POST` payload.

* **Modern Standard:** Your hidden input field must specifically be named `gltoken`. Generic names (like `token` or `csrf_token`) will cause the core validation to fail, rejecting valid form submissions.
* **Implementation:**
```html
<input type="hidden" name="gltoken" value="<?php echo SEC_createToken(); ?>" />

```



### 11.4. Standardized Access Control Rejection

When protecting administration pages and secure endpoints via `SEC_hasRights()`, you must gracefully handle unauthorized access by logging the specific attempt and using the core UI messaging variables (`$MESSAGE`) for consistency across the CMS.

* **Modern Standard:** Use `COM_showMessageText` for the UI, `COM_accessLog` for security auditing, and `COM_output` to render the page before exiting the script.
* **Implementation:**
```php
global $MESSAGE, $_USER;

if (!SEC_hasRights('foobar.admin')) {
    $display = COM_showMessageText($MESSAGE[29], $MESSAGE[30]);
    $display = COM_createHTMLDocument($display, array('pagetitle' => $MESSAGE[30]));

    $username = isset($_USER['username']) ? $_USER['username'] : 'Anonymous';
    COM_accessLog("User {$username} tried to illegally access the foobar administration screen.");

    COM_output($display);
    exit;
}

```

**End of Memorandum.**
*Compliance with these standards is expected for all PRs submitted to the Geeklog-Plugins repository.*
