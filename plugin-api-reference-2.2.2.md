# Geeklog 2.2.2 Plugin API Reference

This reference summarizes the main Geeklog Plugin APIs that a plugin can implement, based on `lib-plugins.php`.

Geeklog generally looks for functions following this naming convention:

```php
plugin_<api>_<plugin>()
```

Where `<plugin>` is the plugin's short name.

Not every API is required. A plugin should only implement the APIs it actually needs.

---

## 1. Installation, Upgrade, and Lifecycle

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_autoinstall_<plugin>()` | Describes the plugin's automatic installation settings and dependencies | Usually `$plugin` when called through `PLG_getParams()` |
| `plugin_autouninstall_<plugin>()` | Describes tables, variables, groups, features, blocks, and other data to remove during uninstall | None |
| `plugin_upgrade_<plugin>()` | Performs a plugin upgrade | None |
| `plugin_chkVersion_<plugin>()` | Checks or reports the current plugin code version | None |
| `plugin_migrate_<plugin>()` | Lets the plugin adapt after site URL or path changes | `$old_conf` |
| `plugin_enablestatechange_<plugin>()` | Called before the plugin is enabled or disabled | `$enable` |
| `plugin_pluginstatechange_<plugin>()` | Notifies the plugin when another plugin changes state | `$type, $status` |
| `plugin_configchange_<plugin>()` | Notifies the plugin when Core or plugin configuration changes | `$group [, $changes]` |
| `plugin_clearcache_<plugin>()` | Lets the plugin clear its own cache | None |
| `plugin_runScheduledTask_<plugin>()` | Runs a plugin scheduled task | None |

Possible `$status` values include:

```text
enabled
disabled
installed
uninstalled
upgraded
```

---

## 2. Interface, Administration, and Menus

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_getmenuitems_<plugin>()` | Adds plugin entries to the site menu | None |
| `plugin_cclabel_<plugin>()` | Adds the plugin to Command & Control | None |
| `plugin_getadminoption_<plugin>()` | Adds entries to the administrator menu | None |
| `plugin_getuseroption_<plugin>()` | Adds entries to the user menu | None |
| `plugin_geticon_<plugin>()` | Returns the plugin icon URL | None |
| `plugin_getdocumentationurl_<plugin>()` | Returns the URL of plugin documentation | `$file` |
| `plugin_getconfigtooltip_<plugin>()` | Provides help text for a configuration option | `$id` |
| `plugin_ismoderator_<plugin>()` | Reports whether the current user is a moderator for the plugin | None |
| `plugin_centerblock_<plugin>()` | Displays plugin content in the center area | `$where, $page, $topic` |
| `plugin_getBlockLocations_<plugin>()` | Declares template locations where blocks can appear | None |
| `plugin_getBlocks_<plugin>()` | Returns dynamic blocks | `$side, $topic` |
| `plugin_getBlocksConfig_<plugin>()` | Returns dynamic block configuration data | `$side, $topic` |

For `plugin_centerblock_<plugin>()`, `$where` may be:

| Value | Location |
|---:|---|
| `0` | Entire page |
| `1` | Top |
| `2` | After the featured story |
| `3` | Bottom |

---

## 3. Templates, HTML, CSS, and Metadata

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_templatesetvars_<plugin>()` | Adds or modifies variables in Geeklog templates | `$templateName, $template` |
| `plugin_getheadercode_<plugin>()` | Adds code to the document header, such as JavaScript, CSS, or meta-related markup | None |
| `plugin_getfootercode_<plugin>()` | Adds code to the page footer | None |
| `plugin_getmetatags_<plugin>()` | Adds metadata to a page | `$type, $id` |
| `plugin_getstructureddatatypes_<plugin>()` | Declares Structured Data types supported by the plugin | None |

Known `$templateName` values include:

```text
header
footer
storytext
featuredstorytext
archivestorytext
story
comment
registration
contact
emailstory
loginblock
loginform
search
```

---

## 4. Content and Item Information

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_getiteminfo_<plugin>()` | Returns information about a plugin item | `$id, $what, $uid, $options` |
| `plugin_getrelateditems_<plugin>()` | Returns related content | `$tids, $max, $trim` |
| `plugin_itemsaved_<plugin>()` | Receives notification when an item is created or modified | `$id, $type, $old_id, $sub_type` |
| `plugin_itemdeleted_<plugin>()` | Receives notification when an item is deleted | `$id, $type, $sub_type` |
| `plugin_itemdisplay_<plugin>()` | Adds content when an item is displayed | `$id, $type` |
| `plugin_itemPreSave_<plugin>()` | Reviews or rejects an item before saving | `$type, $content` |
| `plugin_idToURL_<plugin>()` | Returns an item URL even if the item no longer exists | `$sub_type, $item_id` |

### `plugin_getiteminfo_<plugin>()`

The `$what` parameter may request properties such as:

```text
date-created
date-modified
description
excerpt
id
title
url
likes
```

The optional `$options` array may include:

```php
$options['sub_type'];
$options['filter'];
$options['filter']['topic-ids'];
$options['filter']['date-created'];
```

---

## 5. Content Events

| Plugin API | Event | Parameters |
|---|---|---|
| `plugin_itemsaved_<plugin>()` | Item saved or modified | `$id, $type, $old_id, $sub_type` |
| `plugin_itemdeleted_<plugin>()` | Item deleted | `$id, $type, $sub_type` |
| `plugin_submissionsaved_<plugin>()` | Submission saved | `$type` |
| `plugin_submissiondeleted_<plugin>()` | Submission deleted | `$type` |
| `plugin_itemdisplay_<plugin>()` | Item displayed | `$id, $type` |

Geeklog 2.2.2 supports `$sub_type` for item save and delete notifications.

---

## 6. Search

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_searchtypes_<plugin>()` | Adds plugin search types to Geeklog search | None |
| `plugin_dopluginsearch_<plugin>()` | Searches plugin content | `$query, $dateStart, $dateEnd, $topic, $type, $author, $keyType, $page, $perPage` |
| `plugin_searchformat_<plugin>()` | Adjusts title, description, or URL in search results | `$id, $contentType, $content` |

Possible `$contentType` values:

```text
title
description
url
```

Possible `$keyType` values:

```text
all
phrase
any
```

---

## 7. Comments

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_getcommenturlid_<plugin>()` | Returns the URL and identifier used to view comments for an item | `$id` |
| `plugin_commentenabled_<plugin>()` | Reports whether comments are enabled for an item | `$id` |
| `plugin_deletecomment_<plugin>()` | Deletes a comment | `$cid, $id [, $returnBoolean]` |
| `plugin_savecomment_<plugin>()` | Saves a comment | `$title, $comment, $id, $pid, $postMode` |
| `plugin_displaycomment_<plugin>()` | Displays comments | `$id, $cid, $title, $order, $format, $page, $view` |
| `plugin_commentPreSave_<plugin>()` | Reviews or rejects a comment before saving | `$uid, &$title, &$comment, $sid, $pid, $type, &$postMode` |
| `plugin_moderationcommentapprove_<plugin>()` | Handles comment approval | `$id, $cid` |
| `plugin_getwhatsnewcomment_<plugin>()` | Returns recent comments | `$numReturn, $uid` |

---

## 8. Submissions and Moderation

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_submissioncount_<plugin>()` | Returns the number of pending submissions | None |
| `plugin_submit_<plugin>()` | Displays the plugin submission form | None |
| `plugin_savesubmission_<plugin>()` | Saves a user submission | `$A` |
| `plugin_moderationvalues_<plugin>()` | Returns moderation settings and identifiers | None |
| `plugin_moderationapprove_<plugin>()` | Approves a submission | `$id` |
| `plugin_moderationdelete_<plugin>()` | Deletes or rejects a submission | `$id` |
| `plugin_moderationcommentapprove_<plugin>()` | Handles approval of a comment submission | `$id, $cid` |

---

## 9. Users and Groups

| Plugin API | Event | Parameters |
|---|---|---|
| `plugin_user_create_<plugin>()` | User account created | `$uid` |
| `plugin_user_delete_<plugin>()` | User account deleted | `$uid` |
| `plugin_user_login_<plugin>()` | User logged in | `$uid` |
| `plugin_user_logout_<plugin>()` | User logged out | `$uid` |
| `plugin_user_login_max_invalid_<plugin>()` | Maximum invalid login attempts reached | `$uid` |
| `plugin_user_changed_<plugin>()` | User profile or preferences changed | `$uid` |
| `plugin_group_changed_<plugin>()` | Group created, edited, or deleted | `$grp_id, $mode` |
| `plugin_usercontributed_<plugin>()` | Reports whether a user contributed content to the plugin | `$uid` |

Possible `$mode` values:

```text
new
edit
delete
```

---

## 10. User Profile Extensions

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_profilevariablesedit_<plugin>()` | Adds variables or fields to the profile edit template | `$uid, $template` |
| `plugin_profileblocksedit_<plugin>()` | Adds blocks to the profile edit page | `$uid` |
| `plugin_profileextrassave_<plugin>()` | Saves plugin-specific profile fields | `$uid` |
| `plugin_profilevariablesdisplay_<plugin>()` | Adds variables when displaying a user profile | `$uid, $template` |
| `plugin_profileblocksdisplay_<plugin>()` | Adds blocks when displaying a user profile | `$uid` |

---

## 11. Autotags

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_autotags_<plugin>()` | Declares and parses plugin autotags | Depends on `$type` |

Geeklog may call it for discovery:

```php
plugin_autotags_<plugin>($type);
```

And for parsing:

```php
plugin_autotags_<plugin>('parse', $content, $autotag);
```

Or with contextual information:

```php
plugin_autotags_<plugin>('parse', $content, $autotag, $parameters);
```

Possible modes include:

```text
tagname
permission
nopermission
closetag
parse
```

The contextual `$parameters` array may contain:

```php
$parameters['type'];
$parameters['id'];
```

---

## 12. RSS and Atom Feeds

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_getfeednames_<plugin>()` | Declares feeds supported by the plugin | None |
| `plugin_getfeedcontent_<plugin>()` | Returns feed content | `$feed, &$link, &$update_data, $feedType, $feedVersion` |
| `plugin_feedupdatecheck_<plugin>()` | Determines whether a feed must be regenerated | `$feed, $topic, $update_data, $limit, $updated_type, $updated_topic, $updated_id` |
| `plugin_feedElementExtensions_<plugin>()` | Adds extension elements to feed items | `$contentType, $contentID, $feedType, $feedVersion, $topic, $fid` |
| `plugin_feedNSExtensions_<plugin>()` | Adds XML namespace extensions | `$contentType, $feedType, $feedVersion, $topic, $fid` |
| `plugin_feedExtensionTags_<plugin>()` | Adds extension tags to feed metadata | `$contentType, $feedType, $feedVersion, $topic, $fid` |

---

## 13. What's New and Statistics

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_whatsnewsupported_<plugin>()` | Declares support for Geeklog's What's New block | None |
| `plugin_getwhatsnew_<plugin>()` | Returns new plugin content | None |
| `plugin_getwhatsnewcomment_<plugin>()` | Returns recent comments | `$numReturn, $uid` |
| `plugin_statssummary_<plugin>()` | Returns summarized plugin statistics | None |
| `plugin_showstats_<plugin>()` | Returns legacy or detailed statistics output | `$showSiteStats` |

---

## 14. Sitemap and SEO

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_collectSitemapItems_<plugin>()` | Returns plugin URLs for XML sitemap generation | `$uid, $limit` |
| `plugin_getmetatags_<plugin>()` | Adds page metadata | `$type, $id` |
| `plugin_getiteminfo_<plugin>()` | Provides title, URL, description, dates, and related item information | `$id, $what, $uid, $options` |
| `plugin_getstructureddatatypes_<plugin>()` | Declares supported Structured Data types | None |

A sitemap item may contain:

```php
[
    'url'           => 'https://example.com/item',
    'date-modified' => 1234567890,
    'change-freq'   => 'weekly',
    'priority'      => 0.8
]
```

---

## 15. Spam and Security

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_checkforSpam_<plugin>()` | Checks content for spam | `$comment, $action, $permanentLink, $commentType, $commentAuthor, $commentAuthorEmail, $commentAuthorURL` |
| `plugin_spamaction_<plugin>()` | Handles an action after spam detection | `$content, $action` |
| `plugin_onSpeeding_<plugin>()` | Reacts when a Geeklog speed limit is reached | `$type, $property, $last` |

Possible speeding types include:

```text
login
submit
error-404
error-spam
error-speedlimit
```

`plugin_onSpeeding_<plugin>()` is available in Geeklog 2.2.2.

---

## 16. Likes and Dislikes

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_likesenabled_<plugin>()` | Reports whether Likes/Dislikes are enabled for an item type | `$sub_type, $id` |
| `plugin_likeslabel_<plugin>()` | Returns the plural label of the likeable item type | `$sub_type` |
| `plugin_canuserlike_<plugin>()` | Checks whether a user may perform a Like/Dislike action | `$sub_type, $id, $uid, $ip` |
| `plugin_itemlikesaction_<plugin>()` | Receives notification after a Like/Dislike action | `$sub_type, $item_id, $action` |
| `plugin_getItemLikeURL_<plugin>()` | Returns the URL of the liked item | `$sub_type, $item_id` |

Possible return values for `plugin_likesenabled_<plugin>()`:

| Value | Meaning |
|---:|---|
| `0` | Disabled |
| `1` | Likes and Dislikes |
| `2` | Likes only |

---

## 17. reCAPTCHA

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_supportsRecaptcha_<plugin>()` | Declares forms and reCAPTCHA versions supported by the plugin | None |

Example structure:

```php
[
    'type'    => 'submission',
    'version' => RECAPTCHA_SUPPORT_V3,
    'form_id' => 'submission-form'
]
```

Supported constants include:

```php
RECAPTCHA_NO_SUPPORT
RECAPTCHA_SUPPORT_V2
RECAPTCHA_SUPPORT_V2_INVISIBLE
RECAPTCHA_SUPPORT_V3
```

---

## 18. Pingback and Trackback

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_handlepingoperation_<plugin>()` | Authorizes or rejects a pingback or trackback operation | `$id, $operation` |

Possible `$operation` values:

```text
acceptByID
acceptByURI
delete
```

---

## 19. Web Services

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_wsEnabled_<plugin>()` | Reports whether web services are enabled for the plugin | None |
| `service_<action>_<plugin>()` | Implements a web service action | `$args, &$output, &$svc_msg` |

Geeklog invokes these services through `PLG_invokeService()`.

---

## 20. Language Support

| Plugin API | Purpose | Parameters |
|---|---|---|
| `plugin_getlanguageoverrides_<plugin>()` | Declares language arrays that may be overridden by Geeklog's Language Override Manager | None |

Multilingual URL information is handled separately through configuration values such as:

```php
$_CONF['langurl_<plugin>'];
```

---

# Recommended APIs for a Modern Geeklog 2.2.2 Plugin

| Priority | Plugin API | Why It Matters |
|---|---|---|
| High | `plugin_getiteminfo_<plugin>()` | Standard interface for describing plugin content |
| High | `plugin_templatesetvars_<plugin>()` | Template integration |
| High | `plugin_getmetatags_<plugin>()` | SEO and metadata |
| High | `plugin_collectSitemapItems_<plugin>()` | XML sitemap and indexing |
| High | `plugin_itemsaved_<plugin>()` | Content lifecycle notifications |
| High | `plugin_itemdeleted_<plugin>()` | Content deletion notifications |
| High | `plugin_getadminoption_<plugin>()` | Administration integration |
| High | `plugin_cclabel_<plugin>()` | Command & Control integration |
| Medium | `plugin_dopluginsearch_<plugin>()` | Geeklog search integration |
| Medium | `plugin_searchtypes_<plugin>()` | Search type registration |
| Medium | `plugin_autotags_<plugin>()` | Cross-content integration |
| Medium | `plugin_getrelateditems_<plugin>()` | Related-content support |
| Medium | `plugin_getheadercode_<plugin>()` | Header JS/CSS/markup |
| Medium | `plugin_getfootercode_<plugin>()` | Footer JavaScript or markup |
| Medium | `plugin_clearcache_<plugin>()` | Proper cache management |
| Medium | `plugin_runScheduledTask_<plugin>()` | Background-style scheduled processing |
| Medium | `plugin_configchange_<plugin>()` | Reacting to configuration changes |
| Medium | `plugin_idToURL_<plugin>()` | Stable item URL resolution |
| Medium | `plugin_onSpeeding_<plugin>()` | Geeklog 2.2.2 security integration |
| Optional | Likes APIs | For likeable content |
| Optional | Comment APIs | For comment-enabled content |
| Optional | Feed APIs | For RSS or Atom support |
| Optional | reCAPTCHA API | For public forms |
| Optional | Web Services APIs | For external/API access |

---

# Suggested Plugin Audit Matrix

This API reference can also be used by an auditing tool such as Monitor or GPTK.

Example:

| Plugin API | Detected | Recommended | Status |
|---|---:|---:|---|
| `plugin_getiteminfo_videos` | Yes | Yes | OK |
| `plugin_collectSitemapItems_videos` | Yes | Yes | OK |
| `plugin_getmetatags_videos` | No | Yes | Review |
| `plugin_itemsaved_videos` | Yes | Yes | OK |
| `plugin_idToURL_videos` | No | Yes for Geeklog 2.2.2 | Review |
| `plugin_onSpeeding_videos` | No | Only if needed | Optional |

Such an auditor could scan `functions.inc`, detect implemented Geeklog APIs, validate parameter counts and order, identify legacy signatures, and suggest relevant Geeklog 2.2.2 APIs.

---

## Source

Based on Geeklog `lib-plugins.php` for Geeklog 2.2.x / 2.2.2.
